#!/usr/bin/env python3
"""Music-only, no-Git prepare/freeze with an actual live connector RPC transport.

stdin/stdout are a line-delimited request/response bridge to the host's authorized
GitHub connector. No subprocess, network client, credential, or remote write.
An offline cache is NOT a live ref callback and cannot pass this command alone.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import tempfile
import uuid
import connector_music_history as h
import music_identity as m
import music_publication as p
import publication_bundle as b
import publication_recovery as r


def prepare(cache, day, fetch, *, work_parent=None):
    b.v.iso_day(day)
    heads=h.read_heads(fetch)
    repos={key:h.Repository(key,head,cache,fetch).collect() for key,head in heads.items()}
    # A unique disposable materialization, not a fake repository or Git checkout.
    with tempfile.TemporaryDirectory(prefix='connector-music-',dir=work_parent) as tmp:
        history=h.materialize(repos,Path(tmp)/'inputs');roots=history.roots;root=roots['vault']
        history.validate_root(root)
        snapshot={'schema_version':1,**{key:repo.snapshot() for key,repo in repos.items()}}
        m.incident(root)
        index=m.index(root,history=history)
        r.require(index['status']=='complete_available_git_history','incomplete permanent music identity evidence')
        obs=p.observations(roots,day);path=root/m.PREPARED/(day+'.json')
        if path.exists():
            bundle=b.load_prepared(path)
            gate=m.recovery_gate(root,bundle,snapshot,heads,obs,history=history)
            mode='resume_existing_bundle';digest=bundle['bundle_sha256'];planner=gate['planner']
            r.require(planner['status']!='blocked','existing publication conflicts; do not reselect')
        else:
            r.require(day not in index['prepared'] and not any(x['date']==day for x in index['records']),
                      'existing/retired exposure requires original bundle recovery or explicit adoption review')
            r.require(all(x['status']=='missing' for k,x in obs.items() if not k.endswith('state/tracks.json')),
                      'dated artifacts without PREPARED require adoption review; do not reselect')
            gate=p.mirror.audit(snapshot);mode='ready_before_selection';digest=None;planner=None;bundle=None
        r.require(h.read_heads(fetch)==heads,'remote HEAD changed during connector preparation')
        report={'schema_version':1,'backend':'github_connector_no_git','date':day,'mode':mode,'heads':heads,
                'snapshot':snapshot,'observations':obs,'identity_index':index,'bundle_sha256':digest,
                'planner':planner,'gate':gate,'original_bundle':bundle,
                'original_prepared_blob_sha':r.blob_sha(path.read_bytes()) if path.exists() else None,
                'bundle_health':{'status':'music_only_history_verified','other_projects':'not_evaluated_or_changed'},
                'history_objects':{key:{'commits':len(repo.commits),'trees':len(repo.trees),'blobs':len(repo.blobs)} for key,repo in repos.items()},
                'content_qa':'not_evaluated','repository_writes_performed':0,
                'scheduler_execution':'not_verified'}
    return report,repos


def freeze(preflight, cache, manifest_text, note_text, fetch, *, work_parent=None):
    r.require(preflight.get('schema_version')==1 and preflight.get('backend')=='github_connector_no_git' and
              preflight.get('mode')=='ready_before_selection',
              'new music freeze requires ready_before_selection; recover an existing bundle instead')
    current,repos=prepare(cache,preflight['date'],fetch,work_parent=work_parent)
    r.require(current['mode']=='ready_before_selection' and current['heads']==preflight['heads'] and
              current['identity_index']['index_sha256']==preflight['identity_index']['index_sha256'],
              'pre-selection evidence is stale; rerun prepare and recheck the retained candidate selection')
    with tempfile.TemporaryDirectory(prefix='connector-freeze-',dir=work_parent) as tmp:
        history=h.materialize(repos,Path(tmp)/'inputs')
        bundle=p.build_bundle(current,history.roots['vault'],history.roots['music'],manifest_text,note_text,history=history)
        history.validate_root(history.roots['vault'])
        r.require(h.read_heads(fetch)==current['heads'],'remote HEAD changed before frozen output')
    return bundle


class ConnectorRPC:
    """One single-use request ID per LIVE tool call, including every ref read.

    Host must call github.fetch({url: request.url}) after receiving the request,
    and reply {id: request.id, response: <unchanged tool result>}. Replayable
    timestamps or pre-created ref files are intentionally not an input option.
    """
    def __init__(self, inp=None, out=None): self.inp=inp or sys.stdin;self.out=out or sys.stdout
    def __call__(self,url):
        request={'type':'github_read','id':uuid.uuid4().hex,'url':url}
        print(json.dumps(request),file=self.out,flush=True)
        raw=self.inp.readline();r.require(raw,'connector response missing; no live ref proof')
        response=b.v.strict_json(raw)
        r.require(response.get('id')==request['id'],'mismatched/replayed connector response')
        result=response.get('response')
        r.require(isinstance(result,dict) and not result.get('isError'),'connector read failed')
        return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','freeze'))
    parser.add_argument('--cache',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--date');parser.add_argument('--preflight',type=Path)
    parser.add_argument('--manifest',type=Path);parser.add_argument('--note',type=Path)
    args=parser.parse_args(argv)
    # exec_command requires a PTY for interactive stdin. Disable its canonical
    # 4096-byte line limit and echo before any connector response is delivered.
    terminal=None
    if sys.stdin.isatty():
        import termios
        terminal=termios.tcgetattr(sys.stdin.fileno())
        attrs=termios.tcgetattr(sys.stdin.fileno())
        attrs[3] &= ~(termios.ICANON | termios.ECHO)
        attrs[6][termios.VMIN]=1;attrs[6][termios.VTIME]=0
        termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,attrs)
    try:
        # Fail early, without connector reads, if output would clobber any evidence.
        r.require(not args.output.resolve().is_relative_to(args.cache.resolve()),'output must be outside evidence cache')
        r.require(not args.output.exists(),'output already exists; never overwrite original frozen output')
        transport=ConnectorRPC()
        if args.command=='prepare':
            r.require(args.date is not None,'--date required')
            result,_=prepare(args.cache,args.date,transport)
        else:
            r.require(all((args.preflight,args.manifest,args.note)),'--preflight, --manifest and --note required')
            result=freeze(b.v.strict_json(args.preflight.read_text()),args.cache,args.manifest.read_text(),args.note.read_text(),transport)
        p.write_output(args.output,result,[args.cache])
        print(json.dumps({'type':'result','status':result.get('mode','frozen_locally_not_published'),
                          'output':str(args.output),'bundle_sha256':result.get('bundle_sha256'),
                          'repository_writes_performed':0,'scheduler_execution':'not_verified'}),flush=True)
        return 0
    except (ValueError,KeyError,TypeError,OSError,AttributeError,RecursionError) as exc:
        print(json.dumps({'type':'result','status':'blocked_music_preparation','error':str(exc),'repository_writes_performed':0}),flush=True)
        return 1
    finally:
        if terminal is not None:
            termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,terminal)

if __name__=='__main__':raise SystemExit(main())
