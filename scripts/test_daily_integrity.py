"""Negative regressions for IDs, source/history coverage and append-only safety."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import validate_daily_recommendations as v
import check_daily_integrity as h
import test_daily_validator as original


class BoundaryTests(unittest.TestCase):
    def test_youtube_fake_host_rejected(self):
        self.assertEqual(v.YT_RE.findall('https://notyoutube.com/watch?v=abcdefghijk'), [])
    def test_youtube_long_id_rejected(self):
        self.assertEqual(v.YT_RE.findall('https://youtube.com/watch?v=abcdefghijkx'), [])
    def test_youtube_query_suffix_accepted(self):
        self.assertEqual(v.YT_RE.findall('https://www.youtube.com/watch?v=abcdefghijk&t=2'), ['abcdefghijk'])
    def test_reddit_fake_host_rejected(self):
        self.assertEqual(v.REDDIT_RE.findall('https://notreddit.com/r/test/comments/abc123/'), [])
    def test_reddit_id_suffix_rejected(self):
        self.assertEqual(v.REDDIT_RE.findall('https://reddit.com/r/test/comments/abc123_bad/'), [])
    def test_malformed_music_metadata_url_fails(self):
        original.ValidatorRegressionTests().run_music(mutate=lambda s:s.replace('/song/12345670','/song/12345670.fake'),expect_failure=True)

    def test_music_url_cannot_cross_line(self):
        note = 'https://music.apple.com/cn/song/498945944\nAlbum: x/y\n## 4. another'
        self.assertEqual(v.MUSIC_SONG_RE.findall(note), ['498945944'])
    def test_music_short_url(self):
        self.assertEqual(v.MUSIC_SONG_RE.findall('https://music.apple.com/cn/song/12345678'), ['12345678'])
    def test_music_slug_url(self):
        self.assertEqual(v.MUSIC_SONG_RE.findall('https://music.apple.com/cn/song/title/12345678'), ['12345678'])
    def test_music_markdown_url(self):
        self.assertEqual(v.MUSIC_SONG_RE.findall('[song](https://music.apple.com/cn/song/12345678)'), ['12345678'])
    def test_music_does_not_truncate_invalid_id(self):
        self.assertEqual(v.MUSIC_SONG_RE.findall('https://music.apple.com/cn/song/12345678wrong'), [])
    def test_music_does_not_accept_extra_path(self):
        self.assertEqual(v.MUSIC_SONG_RE.findall('https://music.apple.com/cn/song/12345678/other'), [])
    def test_music_does_not_accept_query(self):
        self.assertEqual(v.MUSIC_SONG_RE.findall('https://music.apple.com/cn/song/12345678?other=1'), [])
    def test_empty_frontmatter_does_not_capture_next_field(self):
        self.assertIsNone(v.frontmatter_value('---\nmanifest:\nsource: ChatGPT\n---\n', 'manifest'))
    def test_crlf_frontmatter(self):
        self.assertEqual(v.frontmatter_value('---\r\ndate: 2026-10-12\r\n---\r\n', 'date'), '2026-10-12')
    def test_official_weekend_source(self):
        for label in ['Official page + transcript', 'Official video', 'Official episode page']:
            self.assertEqual(v.extract_source_url(f'**{label}:** https://example.com/item'), 'https://example.com/item')
    def test_invalid_calendar_date(self):
        with self.assertRaises(ValueError): v.iso_day('2026-02-30')
    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError): v.strict_json('{"x":1,"x":2}')
    def test_nonfinite_json(self):
        with self.assertRaises(ValueError): v.strict_json('{"x":NaN}')
    def test_misplaced_music_heading_fails_even_with_correct_total(self):
        def mutate(note):
            note = note.replace('### 编曲与音色\narrangement\n', '', 1)
            return note.replace('## 2. Track', '## 2. Track\n### 编曲与音色\nmisplaced', 1)
        original.ValidatorRegressionTests().run_music(mutate=mutate, expect_failure=True)

    def test_misplaced_album_fails_even_with_correct_total(self):
        def mutate(note):
            note = note.replace('**Album:** Album 0\n', '', 1)
            return note.replace('## 2. Track', '## 2. Track\n**Album:** Album 0', 1)
        original.ValidatorRegressionTests().run_music(mutate=mutate, expect_failure=True)


class HistoryTests(unittest.TestCase):
    def read(self, lines, key='video_id', bad=False):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'history.jsonl'; path.write_text(lines, encoding='utf-8')
            with contextlib.redirect_stderr(io.StringIO()):
                if bad:
                    with self.assertRaises(SystemExit): v.validate_jsonl(path,key)
                else: return v.validate_jsonl(path,key)
    def test_valid_history(self):
        self.assertEqual(len(self.read('{"date":"2026-10-12","video_id":"abcdefghijk"}\n')), 1)
    def test_nonobject_history(self):self.read('[]',bad=True)
    def test_empty_history(self):self.read('',bad=True)
    def test_wrong_id_type(self):self.read('{"date":"2026-10-12","video_id":123}',bad=True)
    def test_short_id(self):self.read('{"date":"2026-10-12","video_id":"abc"}',bad=True)
    def test_invalid_history_date(self):self.read('{"date":"2026-02-30","video_id":"abcdefghijk"}',bad=True)
    def test_duplicate_same_day_append(self):
        row='{"date":"2026-10-12","video_id":"abcdefghijk"}\n';self.read(row+row,bad=True)
    def test_duplicate_json_keys_fail(self):
        self.read('{"date":"2026-10-12","video_id":"abcdefghijk","video_id":"abcdefghijl"}',bad=True)
    def test_missing_source_host(self):
        self.read('{"date":"2026-10-12","source_url":"https:///broken"}','source_url',bad=True)
    def test_missing_history_registration(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            v.require_recorded(Path('note.md'),'2026-10-12',{'new'},set())
    def test_retired_youtube_history_blocks_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);ids=['abcdefghij'+str(i) for i in range(5)]
            (root/'2026-10-12.md').write_text('\n'.join('https://youtube.com/watch?v='+x for x in ids))
            rows=[{'date':'2026-10-12','video_id':x} for x in ids]+[{'date':'2026-09-10','video_id':ids[0]}]
            with patch.object(v,'YOUTUBE_DIR',root),patch.object(v,'ROOT',root),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                v.validate_youtube(rows)
    def test_jsonl_prefix_preserved(self):h.preserve_prefix(b'a\n',b'a\nb\n','history')
    def test_jsonl_rewrite_rejected(self):
        with self.assertRaises(ValueError):h.preserve_prefix(b'a\n',b'b\n','history')
    def test_jsonl_deletion_rejected(self):
        with self.assertRaises(ValueError):h.preserve_prefix(b'a\nb\n',b'a\n','history')
    def test_newline_boundary(self):
        with self.assertRaises(ValueError):h.preserve_prefix(b'a',b'ab','history')
    def test_state_append(self):h.preserve_state({'recommended':{'old':1}},{'recommended':{'old':1,'new':1}})
    def test_state_value_change(self):
        with self.assertRaises(ValueError):h.preserve_state({'recommended':{'old':1}},{'recommended':{'old':2}})
    def test_state_delete_retired(self):
        with self.assertRaises(ValueError):h.preserve_state({'recommended':{'retired':1}},{'recommended':{}})
    def test_base_must_be_sha(self):
        with self.assertRaises(ValueError):h.check_append_only(Path('.'),'--all')


class EnglishTests(unittest.TestCase):
    def check(self, missing=None, duplicate=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);daily=root/'Daily'
            for name in ('Daily','Translation','Vocabulary','Weekly/TV'): (root/name).mkdir(parents=True)
            for name in ('Daily','Translation','Vocabulary'):
                if name!=missing:(root/name/'2026-10-12.md').write_text('Source: https://example.com/daily')
            url='https://example.com/daily' if duplicate else 'https://example.com/tv'
            (root/'Weekly/TV/2026-10-10.md').write_text('---\nsource_url: '+url+'\n---\n')
            rows=[{'date':'2026-10-12','source_url':'https://example.com/daily'}, {'date':'2026-10-10','source_url':url}]
            with patch.object(v,'ENGLISH_DIR',daily),contextlib.redirect_stderr(io.StringIO()):return v.validate_english(rows)
    def test_weekend_is_included(self):self.assertEqual(self.check(),2)
    def test_missing_translation_fails(self):
        with self.assertRaises(SystemExit):self.check('Translation')
    def test_missing_vocabulary_fails(self):
        with self.assertRaises(SystemExit):self.check('Vocabulary')
    def test_weekend_daily_duplicate_fails(self):
        with self.assertRaises(SystemExit):self.check(duplicate=True)


class LocalAuditTests(unittest.TestCase):
    def fixture(self,root):
        for name,key in h.HISTORIES.items():
            path=root/f'.recommendation/history/{name}.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
            value={'video_id':'abcdefghijk','post_id':'abc123','source_url':'https://example.com/item'}[key]
            path.write_text(json.dumps({'date':'2026-10-12',key:value})+'\n')
        folder=root/'Music/Daily';(folder/'manifests').mkdir(parents=True);(folder/'state').mkdir()
        tracks=[{'position':i+1,'artist':'Artist','title':str(i),'canonical_id':'Artist::'+str(i),
                 'apple_music':{'song_id':str(12345000+i),'url':'https://music.apple.com/cn/song/'+str(12345000+i),'storefront':'cn'}} for i in range(5)]
        state={'schema_version':1,'provider':'apple_music','recommended':{t['canonical_id']:1 for t in tracks}}
        state['recommended']['Retired::old']=1
        (folder/'state/tracks.json').write_text(json.dumps(state))
        (folder/'manifests/2026-10-12.json').write_text(json.dumps({'date':'2026-10-12','tracks':tracks}))
        (folder/'2026-10-12.md').write_text('\n'.join(t['apple_music']['url'] for t in tracks))
    def run_audit(self,change=None):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            if change:change(root)
            return h.audit(root,'2026-09-11')
    def test_valid_local_snapshot(self):self.assertEqual(self.run_audit()['music']['retired_entries_retained'],1)
    def test_orphan_note_fails(self):
        with self.assertRaises(ValueError):self.run_audit(lambda r:(r/'Music/Daily/2026-10-13.md').write_text('orphan'))
    def test_missing_note_fails(self):
        with self.assertRaises(ValueError):self.run_audit(lambda r:(r/'Music/Daily/2026-10-12.md').unlink())
    def test_note_id_mismatch_fails(self):
        with self.assertRaises(ValueError):self.run_audit(lambda r:(r/'Music/Daily/2026-10-12.md').write_text('broken'))
    def test_deleted_exposure_fails(self):
        def delete(root):
            p=root/h.STATE;doc=json.loads(p.read_text());del doc['recommended']['Artist::0'];p.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):self.run_audit(delete)
    def test_strict_historical_repeat_fails(self):
        def append(root):
            p=root/'.recommendation/history/youtube.jsonl';p.write_text(p.read_text()+'{"date":"2026-10-13","video_id":"abcdefghijk"}\n')
        with self.assertRaises(ValueError):self.run_audit(append)
    def test_git_baseline_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            subprocess.run(['git','init','-q',str(root)],check=True)
            def git(*args):return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.PIPE)
            git('add','.');git('-c','user.name=Regression','-c','user.email=regression@example.invalid','-c','commit.gpgsign=false','commit','-qm','fixture')
            base=git('rev-parse','HEAD').decode().strip()
            h.check_append_only(root,base)
            path=root/'.recommendation/history/english.jsonl';path.write_text('')
            with self.assertRaises(ValueError):h.check_append_only(root,base)


if __name__=='__main__':unittest.main()
