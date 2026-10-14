import copy
import unittest
import check_remote_music_snapshot as m


def node(rows, nodes):
    oid=m.tree_sha(rows);nodes[oid]={'sha':oid,'tree':rows,'truncated':False};return oid

def entry(name, oid, folder=False):
    return {'path':name,'sha':oid,'type':'tree' if folder else 'blob','mode':'040000' if folder else '100644'}

def fixture(state='a'*40, manifest='b'*40, note=True):
    def repo(is_vault):
        nodes={};st=node([entry('tracks.json',state if is_vault else 'a'*40)],nodes)
        if is_vault:
            ms=node([entry('2026-10-12.json',manifest)],nodes)
            d=[entry('state',st,True),entry('manifests',ms,True)]
            if note:d.append(entry('2026-10-12.md','c'*40))
            daily=node(d,nodes);music=node([entry('Daily',daily,True)],nodes);root=node([entry('Music',music,True)],nodes)
        else:
            month=node([entry('2026-10-12.json','b'*40)],nodes);year=node([entry('10',month,True)],nodes)
            rec=node([entry('2026',year,True)],nodes);root=node([entry('recommendations',rec,True),entry('state',st,True)],nodes)
        return {'head_before':'d'*40,'head_after':'d'*40,'commit':{'sha':'d'*40,'tree':{'sha':root}},'trees':nodes}
    return {'schema_version':1,'music':repo(False),'vault':repo(True)}


class MirrorTests(unittest.TestCase):
    def test_empty_git_tree(self):self.assertEqual(m.tree_sha([]),'4b825dc642cb6eb9a060e54bf8d69288fbee4904')
    def test_valid(self):self.assertEqual(m.audit(fixture())['manifests'],1)
    def test_read_only(self):
        x=fixture();old=copy.deepcopy(x);m.audit(x);self.assertEqual(x,old)
    def test_state_mismatch(self):
        with self.assertRaises(ValueError):m.audit(fixture(state='e'*40))
    def test_manifest_mismatch(self):
        with self.assertRaises(ValueError):m.audit(fixture(manifest='e'*40))
    def test_missing_note(self):
        with self.assertRaises(ValueError):m.audit(fixture(note=False))
    def test_head_race(self):
        x=fixture();x['vault']['head_after']='e'*40
        with self.assertRaises(ValueError):m.audit(x)
    def test_wrong_pinned_commit(self):
        x=fixture();x['vault']['commit']['sha']='e'*40
        with self.assertRaises(ValueError):m.audit(x)
    def test_truncated(self):
        x=fixture();oid=x['vault']['commit']['tree']['sha'];x['vault']['trees'][oid]['truncated']=True
        with self.assertRaises(ValueError):m.audit(x)
    def test_incomplete_not_marked_truncated(self):
        x=fixture();oid=x['vault']['commit']['tree']['sha'];x['vault']['trees'][oid]['tree']=[]
        with self.assertRaises(ValueError):m.audit(x)
    def test_missing_subtree(self):
        x=fixture();oid=x['vault']['commit']['tree']['sha'];child=x['vault']['trees'][oid]['tree'][0]['sha'];del x['vault']['trees'][child]
        with self.assertRaises(ValueError):m.audit(x)
    def test_duplicate_tree_entry(self):
        x=fixture();oid=x['vault']['commit']['tree']['sha'];rows=x['vault']['trees'][oid]['tree'];rows.append(rows[0])
        with self.assertRaises(ValueError):m.audit(x)
    def test_fake_entry_oid(self):
        with self.assertRaises(ValueError):m.tree_sha([entry('hello','x'*40)])
    def test_recursive_response_not_silently_accepted(self):
        with self.assertRaises(ValueError):m.tree_sha([entry('a/b','a'*40)])
    def test_ci_is_not_content_qa(self):self.assertIn('editorial quality',m.audit(fixture())['not_certified'])

if __name__=='__main__':unittest.main()
