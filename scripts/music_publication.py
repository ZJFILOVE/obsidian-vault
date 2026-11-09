#!/usr/bin/env python3
"""Music-only prepare/freeze entrypoint. No repository, playlist or credential writes."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import publication_bundle as b
import publication_recovery as r
import music_identity as m
import check_remote_music_snapshot as mirror
from discovery_recovery import require_full_history


def remote_head(root):
    rows=m.git(root,'ls-remote','origin','refs/heads/main').decode().splitlines()
    r.require(len(rows)==1, 'remote main missing or unreadable')
    head,ref=rows[0].split();r.sha(head);r.require(ref=='refs/heads/main','unexpected remote ref')
    return head


def check_checkout(root, expected):
    require_full_history(root)
    r.require(m.git(root,'rev-parse','HEAD').decode().strip()==expected,
              'checkout HEAD differs from remote main; fetch full history and fast-forward/detach safely before selection')
    r.require(not m.git(root,'diff','HEAD','--name-only').strip(),'tracked checkout changes; use a clean checkout')
    # Python bytecode outside publication inputs is harmless. Uncommitted inputs
    # are not remote evidence and must never be treated as confirmed absence.
    extra=m.git(root,'ls-files','--others','--exclude-standard').decode().splitlines()
    r.require(not any(p.startswith(('Music/','recommendations/','state/','.recommendation/')) for p in extra),
              'uncommitted publication inputs; reconcile before preparing')


def tree_evidence(root, head, directories):
    raw=m.git(root,'cat-file','commit',head)
    r.require(hashlib.sha1(b'commit '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==head,'commit hash mismatch')
    root_sha=raw.splitlines()[0].split()[1].decode();trees={}
    def tree(oid):
        if oid not in trees:
            entries=[]
            for line in filter(None,m.git(root,'ls-tree','-z',oid).split(b'\0')):
                meta,name=line.split(b'\t',1);mode,kind,sha=meta.decode().split()
                entries.append(dict(mode=mode,type=kind,sha=sha,path=name.decode()))
            r.require(mirror.tree_sha(entries)==oid,'incomplete Git tree evidence')
            trees[oid]={'sha':oid,'tree':entries,'truncated':False}
        return trees[oid]['tree']
    def descend(oid):
        for row in tree(oid):
            if row['type']=='tree':descend(row['sha'])
    tree(root_sha)
    for path in directories:
        oid=root_sha
        for part in path.split('/'):
            row=next((x for x in tree(oid) if x['path']==part),None)
            r.require(row is not None and row['type']=='tree','required directory absent: '+path)
            oid=row['sha']
        descend(oid)
    return {'head_before':head,'head_after':head,'commit':{'sha':head,'tree':{'sha':root_sha}},'trees':trees}


def observations(roots, day):
    result={}
    for key in b.targets_for('music',day):
        repo,path=key.split(':',1);p=roots['music' if repo==b.MUSIC else 'vault']/path
        result[key]={'status':'ok','sha':r.blob_sha(p.read_bytes())} if p.exists() else {'status':'missing','confirmed':True}
    return result


def scoped_bundle_audit(root):
    """Only an explicitly located non-music data error is advisory.

    The independent full-ancestry music index remains mandatory. Unlocated
    errors (including shared code failures) are not guessed to be unrelated.
    """
    try:
        return {'global_bundles': b.audit_journal(root), 'warnings': []}
    except b.ProjectDataError as exc:
        r.require(exc.project == 'news-youtube-reddit', 'unclassified project data failure')
        return {'global_bundles': {'status': 'failed_other_project_data'},
                'warnings': [{'path': exc.path, 'error': str(exc)}]}
    except ValueError as exc:
        message = str(exc)
        prefix, separator, detail = message.partition(': ')
        path = Path(prefix)
        parts = path.parts
        if (separator and len(parts) == 4 and
                parts[:2] == ('.recommendation', 'transactions') and
                parts[2] in ('journal', 'english', 'news-youtube-reddit') and
                path.suffix == '.json'):
            return {'global_bundles': {'status': 'failed_other_project_data'},
                    'warnings': [{'path': prefix, 'error': detail}],
                    'scope': 'music gates remain mandatory; global failure is not a global pass'}
        raise


def prepare(vault_root, music_root, day):
    b.v.iso_day(day)
    roots={'vault':Path(vault_root).resolve(),'music':Path(music_root).resolve()}
    r.require(roots['vault']!=roots['music'],'two distinct checkouts required')
    heads={k:remote_head(root) for k,root in roots.items()}
    for key,root in roots.items():check_checkout(root,heads[key])
    snapshot={'schema_version':1,
              'vault':tree_evidence(roots['vault'],heads['vault'],['Music/Daily']),
              'music':tree_evidence(roots['music'],heads['music'],['recommendations','state'])}
    bundle_health=scoped_bundle_audit(roots['vault']);m.incident(roots['vault'])
    index=m.index(roots['vault'])
    r.require(index['status']=='complete_available_git_history','incomplete permanent music identity evidence')
    obs=observations(roots,day)
    path=roots['vault']/m.PREPARED/(day+'.json')
    if path.exists():
        bundle=b.load_prepared(path)
        gate=m.recovery_gate(roots['vault'],bundle,snapshot,heads,obs)
        mode='resume_existing_bundle';digest=bundle['bundle_sha256']
        planner=gate['planner'];r.require(planner['status']!='blocked','existing publication conflicts; do not reselect')
    else:
        # A retired reservation or published artifact forbids fresh selection.
        r.require(day not in index['prepared'] and not any(x['date']==day for x in index['records']),
                  'existing/retired exposure requires original bundle recovery or explicit adoption review')
        r.require(all(x['status']=='missing' for k,x in obs.items() if not k.endswith('state/tracks.json')),
                  'dated artifacts without PREPARED require adoption review; do not reselect')
        gate=mirror.audit(snapshot);mode='ready_before_selection';digest=None;planner=None
    r.require({k:remote_head(root) for k,root in roots.items()}==heads,'remote HEAD changed during preparation')
    return {'schema_version':1,'date':day,'mode':mode,'roots':{k:str(p) for k,p in roots.items()},
            'heads':heads,'snapshot':snapshot,'observations':obs,'identity_index':index,
            'bundle_health':bundle_health,'bundle_sha256':digest,'planner':planner,'gate':gate,'content_qa':'not_evaluated',
            'repository_writes_performed':0}


def freeze(preflight, vault_root, music_root, manifest_text, note_text):
    r.require(preflight.get('schema_version')==1 and preflight.get('mode')=='ready_before_selection',
              'new music freeze requires ready_before_selection; recover an existing bundle instead')
    current=prepare(vault_root,music_root,preflight['date'])
    r.require(current['mode']=='ready_before_selection' and current['heads']==preflight['heads'] and
              current['identity_index']['index_sha256']==preflight['identity_index']['index_sha256'],
              'pre-selection evidence is stale; rerun prepare and recheck the retained candidate selection')
    doc=b.v.strict_json(manifest_text);r.require(doc.get('date')==current['date'],'manifest date differs from prepared date')
    state=b.v.strict_json((Path(vault_root)/m.STATE).read_text());after=copy.deepcopy(state)
    for t in doc['tracks']:
        r.require(t['canonical_id'] not in after['recommended'],'permanent canonical reuse')
        after['recommended'][t['canonical_id']]={'first_recommended':current['date'],'last_recommended':current['date'],'count':1}
    state_text=json.dumps(after,ensure_ascii=False,indent=2)+'\n';payloads={};targets=[];baselines={}
    for key,stage in b.targets_for('music',current['date']).items():
        repo,path=key.split(':',1);root=Path(music_root) if repo==b.MUSIC else Path(vault_root);p=root/path
        payloads[key]=state_text if path.endswith('state/tracks.json') else note_text if path.endswith('.md') else manifest_text
        baselines[key]=p.read_text() if p.exists() else None
        targets.append({'repository':repo,'path':path,'stage':stage,'base_sha':r.blob_sha(p.read_bytes()) if p.exists() else None,
                        'target_sha':r.blob_sha(payloads[key].encode())})
    plan={'schema_version':1,'project':'music','date':current['date'],'operation_id':'music:'+current['date'],
          'exposed_resource_ids':[t['canonical_id'] for t in doc['tracks']],'targets':targets}
    bundle=b.freeze(plan,payloads,music_root=Path(vault_root),mirror_snapshot=current['snapshot'],expected_heads=current['heads'])
    b.check_baselines(bundle,baselines)
    r.require({k:remote_head(Path(p)) for k,p in current['roots'].items()}==current['heads'],'remote HEAD changed before frozen output')
    return bundle


def write_output(path, data, roots):
    path=path.resolve()
    r.require(not any(path.is_relative_to(Path(root).resolve()) for root in roots),'output must be outside both repositories')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:stream.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('prepare','freeze'):
        p=sub.add_parser(name);p.add_argument('--vault-root',type=Path,required=True);p.add_argument('--music-root',type=Path,required=True)
        p.add_argument('--output',type=Path,required=True)
        if name=='prepare':p.add_argument('--date',required=True)
        else:
            p.add_argument('--preflight',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--note',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='prepare':result=prepare(args.vault_root,args.music_root,args.date)
        else:result=freeze(b.v.strict_json(args.preflight.read_text()),args.vault_root,args.music_root,args.manifest.read_text(),args.note.read_text())
        write_output(args.output,result,[args.vault_root,args.music_root])
        print(json.dumps({'status':result.get('mode','frozen_locally_not_published'),'output':str(args.output),
                          'bundle_sha256':result.get('bundle_sha256'),'content_qa':'not_evaluated','repository_writes_performed':0}));return 0
    except (OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError) as exc:
        print(json.dumps({'status':'blocked_music_preparation','error':str(exc),'repository_writes_performed':0}));return 1

if __name__=='__main__':raise SystemExit(main())
