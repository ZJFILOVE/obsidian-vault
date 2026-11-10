// Run this complete body in functions.exec with the existing GitHub connector.
// Set these values from the authorized task. Pin the reviewed deployed commit.
// This bootstraps exact stdlib-only source bytes; no checkout, shell network or token.
// Resume the SAME cell with functions.wait if it yields. Never replay cached refs.
const SOURCE_COMMIT = "SET_REVIEWED_40_CHARACTER_COMMIT";
const RUN_DATE = "YYYY-MM-DD";
const CACHE = ".connector-cache/music";
const OUTPUT = `.connector-output/music/${RUN_DATE}-prepare-${Date.now()}.json`;
if (!/^[0-9a-f]{40}$/.test(SOURCE_COMMIT)) throw Error("Pin a reviewed source commit");
if (!/^\d{4}-\d{2}-\d{2}$/.test(RUN_DATE)) throw Error("Set an authorized operation date");
const PYTHON = String.raw`import base64, hashlib, json, os, re, runpy, sys, tempfile, uuid
from pathlib import Path

FILES = ['scripts/' + name + '.py' for name in (
    'connector_music_history', 'music_connector', 'music_identity', 'music_publication',
    'music_withdrawal', 'publication_bundle', 'publication_recovery',
    'check_remote_music_snapshot', 'discovery_recovery', 'validate_daily_recommendations',
    'validate_journal')]
FILES += ['scripts/connector_host_bridge.js', 'docs/music-connector.md', '.recommendation/policy.json']

def need(ok, message):
    if not ok: raise ValueError(message)

def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def unpack(response):
    need(isinstance(response, dict) and not response.get('isError'), 'connector source read failed')
    value = response
    if 'structuredContent' in value:
        value = json.loads(value['structuredContent']['content'])
    need(isinstance(value, dict), 'invalid source response')
    return value

def commit_bytes(value, expected):
    """Verify pinned raw commit using bootstrap stdlib code, before any import."""
    import datetime, itertools
    need(value.get('sha') == expected, 'source commit mismatch')
    def check(raw):
        need(oid('commit', raw) == expected, 'source commit hash mismatch')
        headers, sep, _ = raw.partition(b'\n\n')
        need(sep and headers.startswith(b'tree '), 'invalid source commit headers')
        trees = [line[5:].decode('ascii') for line in headers.split(b'\n') if line.startswith(b'tree ')]
        parents = [line[7:].decode('ascii') for line in headers.split(b'\n') if line.startswith(b'parent ')]
        need(len(trees) == 1 and trees[0] == value['tree']['sha'], 'source commit tree mismatch')
        need(all(re.fullmatch('[0-9a-f]{40}', x) for x in trees + parents), 'invalid source commit object ID')
        if 'parents' in value:
            need(parents == [x['sha'] for x in value['parents']], 'source commit parent mismatch')
        return raw
    if isinstance(value.get('raw_base64'), str):
        return check(base64.b64decode(value['raw_base64'], validate=True))
    verification = value.get('verification') or {}
    payload, signature = verification.get('payload'), verification.get('signature')
    candidates = []
    if isinstance(payload, str):
        candidates.append(payload.encode())
        if isinstance(signature, str):
            head, sep, body = payload.partition('\n\n'); need(sep, 'invalid signed source payload')
            sig = 'gpgsig ' + signature.replace('\n', '\n ').rstrip(' ')
            if sig.endswith('\n'): sig = sig[:-1]
            candidates.append((head + '\n' + sig + '\n\n' + body).encode())
    for raw in candidates:
        if oid('commit', raw) == expected: return check(raw)
    need(not signature, 'signed source commit reconstruction failed')
    tree = value['tree']['sha']; parents = [x['sha'] for x in value['parents']]
    need(all(re.fullmatch('[0-9a-f]{40}', x) for x in [tree] + parents), 'invalid source metadata ID')
    prefix = 'tree ' + tree + '\n' + ''.join('parent ' + x + '\n' for x in parents)
    def person(key, zone):
        item = value[key]
        need(all(isinstance(item.get(k), str) and '\n' not in item[k] for k in ('name','email','date')), 'invalid source identity')
        timestamp = int(datetime.datetime.fromisoformat(item['date'].replace('Z','+00:00')).timestamp())
        return f"{key} {item['name']} <{item['email']}> {timestamp} {zone}\n"
    zones = list(dict.fromkeys(['+0000','+0800'] + [f'{sign}{m//60:02d}{m%60:02d}' for sign in ('+','-') for m in range(841)]))
    message = value['message']; need(isinstance(message, str), 'source message missing')
    messages = list(dict.fromkeys([message, message+'\n', message.rstrip('\n'), message.rstrip('\n')+'\n']))
    for pairs in (((z,z) for z in zones), itertools.product(zones,zones)):
        for author_zone, committer_zone in pairs:
            head = prefix + person('author', author_zone) + person('committer', committer_zone) + '\n'
            for msg in messages:
                raw = (head + msg).encode()
                if oid('commit', raw) == expected: return check(raw)
    raise ValueError('cannot reconstruct exact pinned source commit')

def tree_entries(response, expected):
    value = unpack(response)
    need(value.get('sha') == expected and value.get('truncated') is False, 'source tree missing/truncated')
    chunks = []; result = {}
    for row in value['tree']:
        name, mode, kind, sha = (row[k] for k in ('path', 'mode', 'type', 'sha'))
        need(name not in ('', '.', '..') and '/' not in name and '\0' not in name and name not in result, 'invalid source tree path')
        need((mode, kind) in (('040000','tree'),('100644','blob'),('100755','blob'),('120000','blob'),('160000','commit')), 'invalid source mode')
        need(re.fullmatch('[0-9a-f]{40}', sha), 'invalid source SHA')
        chunks.append(((name + ('/' if kind == 'tree' else '')).encode(), mode.lstrip('0').encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(sha)))
        result[name] = row
    need(oid('tree', b''.join(raw for _, raw in sorted(chunks))) == expected, 'source tree hash mismatch')
    return result

def blob_bytes(response, expected):
    need(isinstance(response, dict) and not response.get('isError'), 'connector source blob failed')
    structured = response.get('structuredContent')
    if isinstance(structured, dict) and isinstance(structured.get('content'), str):
        raw = structured['content'].encode('utf-8')
        if oid('blob', raw) == expected: return raw
    value = unpack(response)
    need(value.get('sha') == expected and value.get('encoding') == 'base64', 'source blob metadata mismatch')
    raw = base64.b64decode(''.join(value['content'].split()), validate=True)
    need(value.get('size') == len(raw) and oid('blob', raw) == expected, 'source blob hash mismatch')
    return raw

def install_blob(response, expected, target):
    raw = blob_bytes(response, expected)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream: stream.write(raw)
    need(oid('blob', target.read_bytes()) == expected, 'written source blob hash mismatch')
    return {'blob_sha': expected, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

def rpc(url):
    request = {'type':'github_read', 'id':uuid.uuid4().hex, 'url':url}
    print(json.dumps(request), flush=True)
    line = sys.stdin.readline(); need(line, 'missing live connector response')
    reply = json.loads(line); need(reply.get('id') == request['id'], 'wrong connector response ID')
    response = reply.get('response'); need(isinstance(response, dict) and not response.get('isError'), 'connector failed')
    return response

def bootstrap(source_commit, fetch, parent):
    need(re.fullmatch('[0-9a-f]{40}', source_commit), 'pin a reviewed source commit')
    parent = parent.absolute()
    for component in [*reversed(parent.parents), parent]:
        need(not component.is_symlink(), 'symlink source runtime parent')
        need(not component.exists() or component.is_dir(), 'non-directory source runtime parent')
    parent.mkdir(parents=True, exist_ok=True)
    need(not parent.is_symlink(), 'symlink source runtime parent')
    runtime = Path(tempfile.mkdtemp(prefix='music-', dir=parent)).resolve()
    proof = runtime / '.source'; proof.mkdir()
    api = 'https://api.github.com/repos/ZJFILOVE/obsidian-vault/git/'
    responses = {}; trees = {}
    def get(kind, sha):
        key = kind + '/' + sha
        if key not in responses:
            response = fetch(api + key); responses[key] = response
            path = proof / (key + '.json'); path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x') as stream: json.dump(response, stream, ensure_ascii=False)
        return responses[key]
    commit = unpack(get('commits', source_commit))
    raw_commit = commit_bytes(commit, source_commit)
    (proof / 'commit.raw').write_bytes(raw_commit)
    root = commit['tree']['sha']; rows = {}
    for path in FILES:
        tree = root; parts = path.split('/')
        for i, part in enumerate(parts):
            if tree not in trees: trees[tree] = tree_entries(get('trees', tree), tree)
            row = trees[tree].get(part); need(row is not None, 'source file missing: ' + path)
            if i < len(parts) - 1:
                need(row['type'] == 'tree', 'non-directory source path'); tree = row['sha']
            else:
                need(row['type'] == 'blob' and row['mode'] in ('100644','100755'), 'source is not a regular file')
                rows[path] = install_blob(get('blobs', row['sha']), row['sha'], runtime / path)
    sys.path.insert(0, str(runtime / 'scripts'))
    manifest = {'repository':'ZJFILOVE/obsidian-vault', 'source_commit':source_commit, 'source_tree':root,
                'files':rows, 'objects':sorted(responses), 'source':'existing GitHub connector', 'git_used':False}
    (proof / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return runtime, manifest

def main():
    terminal = None
    if sys.stdin.isatty():
        import termios
        terminal = termios.tcgetattr(sys.stdin.fileno()); attrs = termios.tcgetattr(sys.stdin.fileno())
        attrs[3] &= ~(termios.ICANON | termios.ECHO); attrs[6][termios.VMIN] = 1; attrs[6][termios.VTIME] = 0
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, attrs)
    try:
        source_commit, day, cache, output = sys.argv[1:]
        cache = str(Path(cache).resolve()); output = str(Path(output).resolve())
        runtime, manifest = bootstrap(source_commit, rpc, Path('.connector-runtime'))
        print(json.dumps({'type':'source', 'source_commit':source_commit, 'source_tree':manifest['source_tree'],
                          'runtime':str(runtime), 'manifest':str(runtime / '.source/manifest.json'), 'files':len(manifest['files'])}), flush=True)
        sys.argv = ['music_connector.py', 'prepare', '--cache', cache, '--date', day, '--output', output]
        runpy.run_path(str(runtime / 'scripts/music_connector.py'), run_name='__main__')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'type':'result', 'status':'blocked_source_bootstrap', 'error':str(exc), 'repository_writes_performed':0}), flush=True)
        raise SystemExit(1)
    finally:
        if terminal is not None: termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, terminal)

if __name__ == '__main__': main()
`;
const quote = value => "'" + value.replace(/'/g, "'\"'\"'") + "'";
const started = await tools.exec_command({
  cmd: `python -c ${quote(PYTHON)} ${[SOURCE_COMMIT, RUN_DATE, CACHE, OUTPUT].map(quote).join(" ")}`,
  tty: true, yield_time_ms: 1000, max_output_tokens: 2000
});
let result = started, pending = "", calls = 0;
const sessionId = started.session_id;
for (;;) {
  pending += result.output || "";
  const lines = pending.split(/\r?\n/); pending = lines.pop();
  let request = null;
  for (const line of lines) {
    if (!line.trim()) continue;
    const message = JSON.parse(line);
    if (message.type === "source") { text(message); continue; }
    if (message.type === "result") {
      let completion = result;
      while (completion.session_id) {
        completion = await tools.write_stdin({session_id: sessionId, chars: "", yield_time_ms: 1000, max_output_tokens: 2000});
      }
      if (!Number.isInteger(completion.exit_code)) throw Error("CLI completion not confirmed");
      text({...message, process_exit_code: completion.exit_code}); exit();
    }
    if (message.type !== "github_read" || request !== null) throw Error("Unexpected RPC message");
    if (!/^https:\/\/api\.github\.com\/repos\/ZJFILOVE\/(obsidian-vault|music-daily)\/git\/(ref\/heads\/main|(commits|trees|blobs)\/[0-9a-f]{40})$/.test(message.url)) throw Error("Out-of-scope connector URL");
    request = message;
  }
  if (!sessionId) throw Error("CLI exited without a result: " + pending);
  if (request) {
    const response = await tools.mcp__codex_apps__github_fetch({url: request.url});
    // Preserve the original result, not a hand-written export or old ref file.
    const reply = JSON.stringify({id: request.id, response}) + "\n";
    result = await tools.write_stdin({session_id: sessionId, chars: reply,
      yield_time_ms: 1000, max_output_tokens: 2000});
    calls++;
    if (calls % 100 === 0) notify({connector_reads: calls, status: "collecting_verified_objects"});
  } else {
    result = await tools.write_stdin({session_id: sessionId, chars: "", yield_time_ms: 1000, max_output_tokens: 2000});
  }
}
