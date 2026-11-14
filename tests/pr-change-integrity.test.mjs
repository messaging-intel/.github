import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';

const workflowPath = path.join(process.cwd(), '.github/workflows/pr-change-integrity.yml');

function extractGuard() {
  const workflow = readFileSync(workflowPath, 'utf8');
  const marker = '        run: |\n';
  const offset = workflow.indexOf(marker);
  assert.notEqual(offset, -1, 'missing PR validation run block');
  const body = [];
  for (const line of workflow.slice(offset + marker.length).split('\n')) {
    if (line === '') body.push('');
    else if (line.startsWith('          ')) body.push(line.slice(10));
    else break;
  }
  assert.ok(body.some((line) => line.includes('git merge-base')));
  return body.join('\n');
}

const guard = extractGuard();

function git(directory, ...args) {
  const result = spawnSync('git', args, { cwd: directory, encoding: 'utf8' });
  assert.equal(result.status, 0, 'git setup failed: ' + args[0]);
  return result.stdout.trim();
}

function fixture(candidate = 'baseline\nclean\n', mainOnly) {
  // Isolated temporary repositories; never mutate the checkout under test.
  const directory = mkdtempSync(path.join(tmpdir(), 'msgint-pr-integrity-'));
  git(directory, 'init', '-b', 'main');
  git(directory, 'config', 'user.name', 'Synthetic Test');
  git(directory, 'config', 'user.email', 'test@example.invalid');
  writeFileSync(path.join(directory, 'fixture.txt'), 'baseline\n');
  git(directory, 'add', 'fixture.txt');
  git(directory, 'commit', '-m', 'base');
  let baseSha = git(directory, 'rev-parse', 'HEAD');
  git(directory, 'switch', '-c', 'feature');
  writeFileSync(path.join(directory, 'fixture.txt'), candidate);
  git(directory, 'add', 'fixture.txt');
  git(directory, 'commit', '-m', 'candidate');
  const headSha = git(directory, 'rev-parse', 'HEAD');
  if (mainOnly !== undefined) {
    git(directory, 'switch', 'main');
    writeFileSync(path.join(directory, 'main-only.txt'), mainOnly);
    git(directory, 'add', 'main-only.txt');
    git(directory, 'commit', '-m', 'main advanced independently');
    baseSha = git(directory, 'rev-parse', 'HEAD');
  }
  return { directory, baseSha, headSha };
}

function validate(f, extra = {}) {
  return spawnSync('bash', ['-c', guard], {
    cwd: f.directory,
    encoding: 'utf8',
    env: { ...process.env, BASE_SHA: f.baseSha, HEAD_SHA: f.headSha, ...extra },
  });
}

test('clean additions pass', () => assert.equal(validate(fixture()).status, 0));
test('unresolved conflict marker fails', () => {
  assert.notEqual(validate(fixture('baseline\n<<<<<<< HEAD\n')).status, 0);
});
test('whitespace errors fail without echoing source', () => {
  const result = validate(fixture('baseline\nsynthetic sensitive text  \n'));
  assert.notEqual(result.status, 0);
  assert.doesNotMatch(result.stdout + result.stderr, /synthetic sensitive text/);
});
test('synthetic token-like strings fail without echoing values', () => {
  const token = 'gh' + 'p_' + 'X'.repeat(40);
  const result = validate(fixture('baseline\n' + token + '\n'));
  assert.notEqual(result.status, 0);
  assert.ok(!(result.stdout + result.stderr).includes(token));
});
test('PEM-style key headers fail without exposing source', () => {
  const marker = '-----BEGIN ' + 'PRIVATE KEY-----';
  const result = validate(fixture('baseline\n' + marker + '\n'));
  assert.notEqual(result.status, 0);
  assert.ok(!(result.stdout + result.stderr).includes(marker));
});
test('main-only divergent changes are ignored by merge-base scan', () => {
  const token = 'gh' + 'p_' + 'X'.repeat(40);
  assert.equal(validate(fixture('baseline\nclean\n', 'main-only: ' + token + '\n')).status, 0);
});
test('malformed refs fail closed', () => {
  const f = fixture();
  assert.notEqual(validate(f, { BASE_SHA: 'invalid' }).status, 0);
  assert.notEqual(validate(f, { HEAD_SHA: 'invalid' }).status, 0);
});
