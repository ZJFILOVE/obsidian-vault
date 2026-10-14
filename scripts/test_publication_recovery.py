import copy
import unittest
import publication_recovery as p


class RecoveryTests(unittest.TestCase):
    def plan(self):
        return {'schema_version':1,'project':'music','date':'2026-10-12','operation_id':'music:2026-10-12',
                'exposed_resource_ids':['Artist::Track'],
                'targets':[{'repository':'ZJFILOVE/music-daily','path':'state/tracks.json','base_sha':'a'*40,'target_sha':'b'*40,'stage':1},
                           {'repository':'ZJFILOVE/obsidian-vault','path':'Music/Daily/state/tracks.json','base_sha':'a'*40,'target_sha':'b'*40,'stage':2}]}
    def observed(self,first='a',second='a'):
        return {'ZJFILOVE/music-daily:state/tracks.json':{'status':'ok','sha':first*40},
                'ZJFILOVE/obsidian-vault:Music/Daily/state/tracks.json':{'status':'ok','sha':second*40}}
    def test_ready_first_stage(self):
        plan=self.plan();result=p.inspect(plan,self.observed(),p.digest(plan));self.assertEqual(result['next_stage'],1)
    def test_partial_two_repo_write_resumes_only_missing(self):
        plan=self.plan();result=p.inspect(plan,self.observed('b','a'),p.digest(plan))
        self.assertEqual([d['action'] for d in result['decisions']],['no_op','update']);self.assertEqual(result['next_stage'],2)
    def test_lost_response_is_noop(self):
        plan=self.plan();self.assertEqual(p.inspect(plan,self.observed('b','b'),p.digest(plan))['status'],'artifacts_match')
    def test_changed_file_is_conflict(self):
        plan=self.plan();result=p.inspect(plan,self.observed('c','a'),p.digest(plan))
        self.assertEqual(result['status'],'blocked');self.assertIsNone(result['next_stage'])
    def test_forbidden_read_is_not_create(self):
        plan=self.plan();plan['targets'][0]['base_sha']=None;obs=self.observed();obs['ZJFILOVE/music-daily:state/tracks.json']={'status':'error','http_status':403}
        self.assertEqual(p.inspect(plan,obs,p.digest(plan))['status'],'blocked')
    def test_unconfirmed_404_is_not_create(self):
        plan=self.plan();plan['targets'][0]['base_sha']=None;obs=self.observed();obs['ZJFILOVE/music-daily:state/tracks.json']={'status':'missing'}
        self.assertEqual(p.inspect(plan,obs,p.digest(plan))['status'],'blocked')
    def test_confirmed_missing_new_file_is_create(self):
        plan=self.plan();plan['targets'][0]['base_sha']=None;obs=self.observed();obs['ZJFILOVE/music-daily:state/tracks.json']={'status':'missing','confirmed':True}
        self.assertEqual(p.inspect(plan,obs,p.digest(plan))['decisions'][0]['action'],'create')
    def test_deleted_existing_file_is_conflict(self):
        plan=self.plan();obs=self.observed();obs['ZJFILOVE/music-daily:state/tracks.json']={'status':'missing','confirmed':True}
        self.assertEqual(p.inspect(plan,obs,p.digest(plan))['decisions'][0]['action'],'conflict')
    def test_missing_readback_blocks(self):
        plan=self.plan();self.assertEqual(p.inspect(plan,{},p.digest(plan))['status'],'blocked')
    def test_retry_cannot_change_selection(self):
        plan=self.plan();old=p.digest(plan);plan['exposed_resource_ids']=['Other::Track']
        with self.assertRaises(ValueError):p.inspect(plan,self.observed(),old)
    def test_duplicate_targets_rejected(self):
        plan=self.plan();plan['targets'].append(copy.deepcopy(plan['targets'][0]))
        with self.assertRaises(ValueError):p.validate(plan)
    def test_wrong_business_date_rejected(self):
        plan=self.plan();plan['date']='2026-10-13'
        with self.assertRaises(ValueError):p.validate(plan)
    def test_path_escape_rejected(self):
        plan=self.plan();plan['targets'][0]['path']='../outside'
        with self.assertRaises(ValueError):p.validate(plan)
    def test_no_false_full_qa(self):
        plan=self.plan();result=p.inspect(plan,self.observed('b','b'),p.digest(plan))
        self.assertEqual(result['content_qa'],'not_evaluated');self.assertEqual(result['github_writes_performed'],0)
    def test_known_git_blob(self):self.assertEqual(p.blob_sha(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')


if __name__=='__main__':unittest.main()
