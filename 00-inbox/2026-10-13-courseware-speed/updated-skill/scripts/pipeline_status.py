#!/usr/bin/env python3
"""Read-only routing hints; recorded states never establish deliverability."""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import evidence
import pdstate
import deliver


def read(path):
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def inspect(project):
    root = Path(project).resolve()
    if not root.is_dir():
        raise FileNotFoundError('工程目录不存在: ' + str(root))
    manifest = evidence.collect_inputs(str(root))
    digest = evidence.content_digest(manifest)
    pdfs = {n: evidence.sha256_file(str(root / (n + '.pdf'))) for n in ('student', 'teacher')}
    run = read(root / '.pd/run.json')
    tasks = []
    raw_tasks = run.get('tasks') if isinstance(run.get('tasks'), dict) else {}
    slices = run.get('slices') if isinstance(run.get('slices'), list) else []
    ids = list(dict.fromkeys([str(s) for s in slices] + list(raw_tasks)))
    for tid in ids:
        task = raw_tasks.get(tid) or raw_tasks.get(pdstate.norm_task(tid)) or {}
        if not isinstance(task, dict):
            task = {}
        try:
            current = pdstate.current_input_digest(str(root), pdstate.norm_task(tid), task)
        except (OSError, ValueError, TypeError, AttributeError):
            current = None
        tasks.append({'task_id': tid, 'status': task.get('status', 'missing'),
                      'input_digest': task.get('input_digest'), 'current_input_digest': current,
                      'stale': not current or current != task.get('input_digest')})
    missing_maps = [n for n in ('source-map.md', 'dependency-map.md', 'coverage-map.md')
                    if not (root / n).is_file()]
    technical = []
    for script, name in deliver.CHECKS:
        report = read(root / '.pd/reports' / name)
        problems = []
        try:
            deliver.verify_report(script, name, report or None, str(root), digest, pdfs, problems)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            problems.append('报告核验失败: ' + str(exc))
        allowed = ('pass', 'review') if name == 'compare.json' else ('pass',)
        if report.get('status') not in allowed:
            problems.append('报告状态未满足技术检查要求')
        technical.append({'report': name, 'status': report.get('status'),
                          'bindings_match': not problems, 'problems': problems})
    required = run.get('required_acceptance_scopes')
    acceptance = []
    if isinstance(required, dict):
        for scope, qids in required.items():
            rec = read(root / '.pd/acceptance' / (scope + '.json'))
            problems = []
            try:
                problems.extend(evidence.validate_acceptance_json(rec, digest, pdfs['student']))
                if rec.get('schema_version') != 2 or rec.get('scope') != scope:
                    problems.append('验收 schema/scope 不匹配')
                if rec.get('conclusion') != 'PASS':
                    problems.append('尚无当前 PASS 记录')
                if not pdfs['student'] or rec.get('student_pdf_sha256') != pdfs['student']:
                    problems.append('学生 PDF 不存在或哈希不匹配')
                if not isinstance(qids, list) or set(qids) - set(rec.get('reviewed_qids', [])):
                    problems.append('必需 qid 覆盖不完整')
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                problems.append('验收记录格式无效: ' + str(exc))
            acceptance.append({'scope': scope, 'record_matches': not problems, 'problems': problems})
    checkpoint = read(root / '.pd/pipeline-state.json')
    checkpoint_problems = []
    if checkpoint:
        if checkpoint.get('schema_version') != 1:
            checkpoint_problems.append('断点 schema_version 不是 1')
        if not run.get('run_id') or checkpoint.get('run_id') != run.get('run_id'):
            checkpoint_problems.append('断点 run_id 不匹配')
        if checkpoint.get('input_digest') != digest:
            checkpoint_problems.append('断点 input_digest 已过期')
        artifacts = checkpoint.get('artifacts')
        if isinstance(artifacts, dict):
            artifacts = [{'path': p, 'sha256': h} for p, h in artifacts.items()]
        if not isinstance(artifacts, list):
            checkpoint_problems.append('断点缺少 artifacts 哈希清单')
        else:
            for item in artifacts:
                try:
                    path = (root / item['path']).resolve()
                    path.relative_to(root)
                    if not item.get('sha256') or evidence.sha256_file(str(path)) != item['sha256']:
                        checkpoint_problems.append('断点产物哈希不匹配: ' + str(item['path']))
                except (OSError, ValueError, TypeError, KeyError):
                    checkpoint_problems.append('断点产物路径或记录无效')
    running = [t['task_id'] for t in tasks if t['status'] == 'running']
    if not run or missing_maps:
        route = 'new/planning'
        action = '补齐三张映射表和运行契约；已有正确文件保留。'
    elif run.get('schema_version') != 2 or not tasks or any(t['stale'] or t['status'] not in ('checked', 'accepted') for t in tasks):
        route = 'writing'
        action = '核对运行契约及 stale/未完成切片；按 pdstate 实际流程续作，本工具不迁移或标状态。'
    elif not all(t['bindings_match'] for t in technical):
        route = 'technical'
        action = '补齐或刷新缺失、过期的技术证据，再运行 deliver.py --preflight。'
    elif not acceptance or not all(a['record_matches'] for a in acceptance):
        route = 'preflight_and_acceptance'
        action = '先运行 deliver.py --preflight --skip-checks，技术预检成功后安排独立教学验收。'
    else:
        route = 'delivery_validation'
        action = '运行 deliver.py --check-only 验证全部门禁；需要交付时再运行 deliver.py --skip-checks。'
    if running:
        action = '先核实 running 任务是否仍有在途执行者，禁止重复派发：' + ', '.join(running) + '。' + action
    return {'project': str(root), 'run_id': run.get('run_id'), 'input_digest': digest,
            'missing_maps': missing_maps, 'tasks': tasks, 'technical_reports': technical,
            'acceptance': acceptance, 'checkpoint': {'present': bool(checkpoint),
            'bindings_match': bool(checkpoint) and not checkpoint_problems,
            'stage': checkpoint.get('stage'), 'problems': checkpoint_problems},
            'route': route, 'next_action': action,
            'notice': '仅核对记录并建议下一步；未核验全部交付门禁，不宣称完成或 PASS。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--json', action='store_true', help='输出 JSON 到 stdout，不写文件')
    args = parser.parse_args()
    try:
        data = inspect(args.project)
    except (OSError, ValueError) as exc:
        if args.json:
            print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        else:
            print('[pipeline-status] ' + str(exc))
        return 2
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print('[pipeline-status] %s | run=%s | digest=%s' %
              (data['route'], data['run_id'] or '未建立', data['input_digest'][:12]))
        if data['missing_maps']:
            print('缺少映射: ' + ', '.join(data['missing_maps']))
        for task in data['tasks']:
            print('任务 %s: %s%s | current=%s' % (task['task_id'], task['status'],
                  ' / stale' if task['stale'] else '', (task['current_input_digest'] or '未知')[:12]))
        print('技术报告: ' + '; '.join(t['report'] + (' 绑定匹配' if t['bindings_match'] else ' 待刷新') for t in data['technical_reports']))
        print('验收记录: ' + ('; '.join(a['scope'] + (' 记录匹配' if a['record_matches'] else ' 待验收') for a in data['acceptance']) or '必需范围尚未登记'))
        print('断点: ' + ('绑定匹配' if data['checkpoint']['bindings_match'] else '缺失或不可复用'))
        print('下一步: ' + data['next_action'])
        print(data['notice'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
