"""One exact, user-authorized withdrawal; never a general short-playlist exception."""
from pathlib import Path
import copy
import json
import hashlib
import re
import publication_recovery as r
import validate_daily_recommendations as v

DAY = '2026-11-06'
IDENTITY = 'apple_music:cn:714861225'
MANIFEST = 'Music/Daily/manifests/' + DAY + '.json'
NOTE = 'Music/Daily/' + DAY + '.md'
PREPARED = '.recommendation/transactions/music/' + DAY + '.json'
RECORD = '.recommendation/transaction-corrections/music/' + DAY + '/withdraw-714861225.json'
FAILURE = '.recommendation/transaction-runs/music/' + DAY + '/qa-blocked-1793927282462.json'
ORIGINAL_MANIFEST = 'b0b271bf1c9a1e083e8756b841c43e18e02ab11a'
ORIGINAL_NOTE = 'dd3c2eb9fb31ed5df1f0fd75a6c27a550ad79978'
BUNDLE_BLOB = 'd9f3cb56b20e0dbbf4841d0e84eb6c91254bab55'
BUNDLE_DIGEST = '92b8be6108ad5f3c0b40d9b43949ace9d0f8fcb18719d46b5afcac139c1ce1c6'
FAILURE_BLOB = '67f48ab45bcf701cec781f97d3d5ffb2d71a03db'
FIRST_MANIFEST = 'Music/Daily/manifests/2026-09-21.json'
FIRST_BLOB = '125ab7faf9a2fd4c08812b1bffc57686f65a1e4d'
RETAINED_IDS = ['1847866026', '1329457872', '914055072', '410742021']
VAULT = 'ZJFILOVE/obsidian-vault:'
START, END = '<!-- AUTO:START -->', '<!-- AUTO:END -->'


def original(root):
    from publication_bundle import verify
    raw = (root / PREPARED).read_bytes()
    r.require(r.blob_sha(raw) == BUNDLE_BLOB, 'withdrawal original PREPARED bytes changed')
    bundle = v.strict_json(raw.decode()); verify(bundle)
    r.require(bundle['bundle_sha256'] == BUNDLE_DIGEST, 'withdrawal original bundle changed')
    manifest, note = bundle['payloads'][VAULT + MANIFEST], bundle['payloads'][VAULT + NOTE]
    r.require(r.blob_sha(manifest.encode()) == ORIGINAL_MANIFEST and r.blob_sha(note.encode()) == ORIGINAL_NOTE,
              'withdrawal original payload changed')
    return bundle, manifest, note


def corrected_manifest(original_text):
    doc = v.strict_json(original_text)
    r.require(r.blob_sha(original_text.encode()) == ORIGINAL_MANIFEST, 'withdrawal requires exact original manifest')
    removed = doc['tracks'][2]
    r.require(removed['canonical_id'] == 'Brian Eno::An Ending (Ascent)' and
              removed['apple_music']['song_id'] == '714861225', 'withdrawal original occurrence mismatch')
    result = copy.deepcopy(doc); result['tracks'] = [t for i, t in enumerate(result['tracks']) if i != 2]
    r.require([t['apple_music']['song_id'] for t in result['tracks']] == RETAINED_IDS, 'withdrawal retained selection mismatch')
    return json.dumps(result, ensure_ascii=False, indent=2) + '\n'


def corrected_note(original_text):
    r.require(r.blob_sha(original_text.encode()) == ORIGINAL_NOTE, 'withdrawal requires exact original note')
    note = re.sub(r'(?ms)^## 3\. Brian Eno — An Ending \(Ascent\)\n.*?(?=^## 4\.)', '', original_text, count=1)
    note = note.replace('# Daily 5 — 2026-11-06：', '# 每日推荐（撤回后保留 4 首）— 2026-11-06：')
    note = note.replace('今天的五首不追求', '保留的四首不追求').replace('，再让氛围电子把时间拉慢', '')
    note = note.replace('**今日优先：An Ending (Ascent)；今日探索：Fado Final。**',
        '**撤回说明：原第 3 首与 9 月 21 日推荐重复，已撤回；其余四首按原顺序保留，不补选。原发布 QA 仍为失败。**\n\n**今日探索：Fado Final。**')
    a = note.index('## 今日聆听建议\n'); z = note.index(END, a)
    note = note[:a] + ('## 今日聆听建议\n\n按保留的四首顺序听：先比较华语独立歌曲与钢琴三重奏的空间和推进方式，再将《La chanson》与《Fado Final》连听，留意辅音、元音、颤音和伴奏回应的位置。\n\n') + note[z:]
    # All four retained song sections and original heading numbers stay exact.
    r.require(v.MUSIC_SONG_RE.findall(note) == RETAINED_IDS, 'withdrawal note order mismatch')
    r.require(note.split(START)[0] == original_text.split(START)[0] and
              note.split(END)[1] == original_text.split(END)[1], 'withdrawal changed text outside AUTO block')
    return note


def expected_record(manifest, note):
    # The common contract uses the exact field names/values in music-daily's
    # .audit/2026-11-06-recording-withdrawal.json. Vault adds its note evidence.
    return {'schema_version': 1, 'correction_id': 'music-2026-11-06-withdraw-714861225',
            'action': 'withdraw_later_duplicate', 'date': DAY, 'provider': 'apple_music',
            'storefront': 'cn', 'song_id': '714861225', 'position': 3,
            'canonical_id': 'Brian Eno::An Ending (Ascent)',
            'original_manifest_blob': ORIGINAL_MANIFEST,
            'corrected_manifest_blob': r.blob_sha(manifest.encode()),
            'corrected_manifest_sha256': hashlib.sha256(manifest.encode()).hexdigest(),
            'retained_positions': [1, 2, 4, 5], 'original_bundle_sha256': BUNDLE_DIGEST,
            'original_prepared_blob': BUNDLE_BLOB, 'original_failure_receipt_blob': FAILURE_BLOB,
            'original_operation_status': 'blocked_current_publication',
            'reservation_policy': 'Keep every original exposure and canonical state value permanently reserved. No replacement song; no original success QA; no Apple Music mutation.',
            'original_note_blob_sha': ORIGINAL_NOTE, 'corrected_note_blob_sha': r.blob_sha(note.encode()),
            'retained_song_ids': RETAINED_IDS,
            'first_occurrence': {'date': '2026-09-21', 'position': 5, 'manifest_blob_sha': FIRST_BLOB},
            'historical_content_qa': 'failed', 'permanent_exclusion_retained': True,
            'reselection_performed': False}


def validate(root: Path):
    """Return None when no withdrawal exists; otherwise verify its exact scope."""
    path = root / RECORD
    if not path.exists(): return None
    bundle, old_manifest, old_note = original(root)
    manifest, note = corrected_manifest(old_manifest), corrected_note(old_note)
    doc = v.strict_json(path.read_text())
    r.require(doc == expected_record(manifest, note), 'withdrawal record scope or evidence changed')
    r.require((root / MANIFEST).read_bytes() == manifest.encode(), 'withdrawal corrected manifest changed')
    current_note = (root / NOTE).read_text()
    r.require(current_note.count(START) == current_note.count(END) == 1, 'withdrawal note AUTO markers changed')
    r.require(current_note.split(START)[1].split(END)[0] == note.split(START)[1].split(END)[0],
              'withdrawal corrected note selection or prose changed')
    r.require(r.blob_sha((root / FIRST_MANIFEST).read_bytes()) == FIRST_BLOB, 'withdrawal first occurrence changed')
    r.require(r.blob_sha((root / FAILURE).read_bytes()) == FAILURE_BLOB, 'withdrawal failure evidence changed')
    r.require(not (root / '.recommendation/runs/2026-11-06-music.json').exists(), 'withdrawal cannot certify original failure')
    state_path = 'Music/Daily/state/tracks.json'
    before = v.strict_json(bundle['payloads'][VAULT + state_path])['recommended']
    after = v.strict_json((root / state_path).read_text())['recommended']
    r.require(all(k in after and after[k] == value for k, value in before.items()), 'withdrawal removed or changed permanent exclusions')
    return doc


def count_for(root: Path, day: str):
    if day != DAY: return 5
    return 4 if validate(root) else 5
