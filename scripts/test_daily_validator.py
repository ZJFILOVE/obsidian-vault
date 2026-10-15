"""Regression tests: presentation variants must not weaken content or ID checks."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import validate_daily_recommendations as v

class ValidatorRegressionTests(unittest.TestCase):
    def test_plain_source(self):
        self.assertEqual(v.extract_source_url('Source: https://example.com/item'), 'https://example.com/item')
    def test_bold_source(self):
        self.assertEqual(v.extract_source_url('**Source URL:** https://example.com/item'), 'https://example.com/item')
    def test_frontmatter_source(self):
        self.assertEqual(v.extract_source_url('---\nsource_url: "https://example.com/item"\n---\n'), 'https://example.com/item')
    def test_missing_source_is_not_invented(self):
        self.assertIsNone(v.extract_source_url('Other link: https://example.com/item'))
    def run_music(self, style='bold', mutate=None, expect_failure=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'Music/Daily';folder.mkdir(parents=True)
            ids=[str(12345670+i) for i in range(5)]
            blocks=[]
            for i,sid in enumerate(ids):
                if style=='list':
                    meta=f'- Album: Album {i}\n- Apple Music CN: https://music.apple.com/cn/song/{sid}\n- song_id: `{sid}`\n'
                elif style=='plain':
                    meta=f'Album: Album {i}\nApple Music: https://music.apple.com/cn/song/{sid}\nsong_id: {sid}\n'
                else:
                    meta=f'**Album:** Album {i}\n**Apple Music：中国大陆区** https://music.apple.com/cn/song/{sid}\n**song_id:** `{sid}`\n'
                blocks.append(f'## {i+1}. Track\n'+meta+'\n### 为什么今天推荐\nwhy\n### 编曲与音色\narrangement\n### 具体聆听点\nlisten\n')
            note='---\nmanifest: Music/Daily/manifests/2026-10-12.json\n---\n'+''.join(blocks)
            if mutate:note=mutate(note)
            (folder/'2026-10-12.md').write_text(note)
            (folder/'manifests').mkdir()
            (folder/'manifests/2026-10-12.json').write_text(json.dumps({'tracks':[{'title':str(i),'apple_music':{'song_id':sid},'analysis_summary':'A'*35,'listening_cue':'B'*20} for i,sid in enumerate(ids)]}))
            oldroot,olddir=v.ROOT,v.MUSIC_DIR;v.ROOT,v.MUSIC_DIR=root,folder
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    if expect_failure:
                        with self.assertRaises(SystemExit):v.validate_music()
                    else:self.assertEqual(v.validate_music(),5)
            finally:v.ROOT,v.MUSIC_DIR=oldroot,olddir
    def test_bold_metadata(self):self.run_music()
    def test_list_metadata(self):self.run_music('list')
    def test_plain_metadata(self):self.run_music('plain')
    def test_missing_album_still_fails(self):self.run_music(mutate=lambda s:s.replace('**Album:** Album 0','**Album:**'),expect_failure=True)
    def test_wrong_song_id_still_fails(self):self.run_music(mutate=lambda s:s.replace('**song_id:** `12345670`','**song_id:** `99999999`'),expect_failure=True)
    def test_wrong_storefront_still_fails(self):self.run_music(mutate=lambda s:s.replace('/cn/song/12345670','/us/song/12345670'),expect_failure=True)
    def test_missing_section_still_fails(self):self.run_music(mutate=lambda s:s.replace('### 编曲与音色','### other',1),expect_failure=True)
    def test_path_escape_still_fails(self):self.run_music(mutate=lambda s:s.replace('Music/Daily/manifests/2026-10-12.json','../../outside.json'),expect_failure=True)

if __name__=='__main__':unittest.main()
