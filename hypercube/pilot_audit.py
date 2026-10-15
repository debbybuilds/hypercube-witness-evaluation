"""Rebuild the amended manual pilot from preserved user-pasted evidence."""
import csv
import io
from pathlib import Path
from .dataset import load_dataset
from .generation import digest, json_bytes
from .scoring import strict_json, score_response, model_identity
from .validation import check_path

DEFAULT_PILOT = Path('responses/cohorts/gpt-6-1-sol-light/pilot-20')


def audit_pilot(dataset, pilot):
    pilot = Path(pilot).resolve()
    cohort = pilot.parent
    _, instances, _ = load_dataset(dataset)
    sources = {}
    def read(relative):
        path = (pilot/relative).resolve()
        if not path.is_relative_to(cohort):
            raise ValueError('source path escapes the cohort directory')
        data = path.read_bytes()
        sources[str(path.relative_to(cohort))] = digest(data)
        return strict_json(data.decode('utf-8')), data
    manifest,_ = read('manifest.json')
    schedule, schedule_raw = read('schedule.json')
    if digest(schedule_raw) != manifest['schedule_sha256']:
        raise ValueError('schedule hash mismatch')
    if len(schedule) != manifest['planned_responses'] or len({s['slot_id'] for s in schedule}) != len(schedule):
        raise ValueError('invalid planned slots')
    expected = {f'{m}/{g}/1' for g in manifest['selected_instances'] for m in ('model_a','model_b')}
    if {s['slot_id'] for s in schedule} != expected or len(expected) != 20:
        raise ValueError('schedule must cover ten selected graphs, both models, once each')
    config,_ = read(manifest['model_config_file'])
    corrections,_ = read('record-corrections.json')
    replacements = {}
    superseded = set()
    for c in corrections:
        if c['slot_id'] in replacements or c['original_record'] in superseded:
            raise ValueError('duplicate correction mapping')
        old,old_raw = read(c['original_record'])
        new,_ = read(c['active_record'])
        if old['slot_id'] != c['slot_id'] or new['slot_id'] != c['slot_id']:
            raise ValueError('correction slot mismatch')
        if new.get('supersedes_record_sha256') != digest(old_raw):
            raise ValueError('superseded record hash mismatch')
        replacements[c['slot_id']] = c['active_record']
        superseded.add(c['original_record'])
    active = {}
    for retained in manifest['retained_records']:
        r,raw = read(retained['record_file'])
        if digest(raw) != retained['record_sha256']:
            raise ValueError('retained record hash mismatch')
        if r['slot_id'] != retained['original_slot_id']:
            raise ValueError('retained source slot mismatch')
        if retained['new_slot_id'] in active:
            raise ValueError('duplicate retained slot')
        active[retained['new_slot_id']] = (retained['record_file'],r)
    for path in sorted((pilot/'intake').glob('*.json')):
        relative = str(path.relative_to(pilot))
        if relative in superseded:
            continue
        r,_ = read(relative)
        slot = r.get('confirmed_slot_id') or r.get('slot_id')
        if not slot or slot in active:
            raise ValueError('duplicate or missing intake slot')
        active[slot] = (relative,r)
    if set(active) - expected:
        raise ValueError('intake contains an unplanned slot')
    for slot,relative in replacements.items():
        if slot not in active or active[slot][0] != relative:
            raise ValueError('active correction missing')
    rows = []
    for slot in schedule:
        key = slot['slot_id']
        if key not in active:
            continue
        relative,r = active[key]
        graph_id = slot['instance_id']
        if key != f'{slot["model"]}/{graph_id}/1' or instances[graph_id]['n'] != slot['n']:
            raise ValueError('slot identity or dimension mismatch')
        if r['prompt_sha256'] != slot['prompt_sha256']:
            raise ValueError('response prompt hash mismatch')
        prompt_path = Path(dataset)/'prompts'/f'{graph_id}.txt'
        if digest(prompt_path.read_bytes()) != slot['prompt_sha256']:
            raise ValueError('dataset prompt hash mismatch')
        if model_identity(r) != model_identity(config[slot['model']]):
            raise ValueError('record model attribution differs from cohort configuration')
        raw = r['raw']
        full = score_response(instances[graph_id],raw)
        # Diagnostic only: inspect the explicitly recorded final JSON line.
        # This never salvages an answer for the frozen full-response metric.
        try:
            obj = strict_json(raw if full['json_only'] else raw.strip().splitlines()[-1])
        except (ValueError,RecursionError,IndexError):
            obj = None
        path = obj.get('path') if type(obj) is dict else None
        if 'displayed_path' in r and path != r['displayed_path']:
            raise ValueError('recorded displayed path differs from raw reply')
        diagnostic = check_path(instances[graph_id],path)
        source_key = str((pilot/relative).resolve().relative_to(cohort))
        rows.append({'slot_id':key,'model':slot['model'],'display_label':r['display_label'],
                     'instance_id':graph_id,'n':slot['n'],'record_file':relative,
                     'record_sha256':sources[source_key],'raw_sha256':digest(raw.encode('utf-8')),
                     'original_slot_id':r.get('slot_id'),'actual_collection_position':r.get('actual_collection_position',r.get('schedule_position')),
                     'json_only':full['json_only'],'schema_compliant':full['schema_compliant'],
                     'formal_path_valid':full['valid_path'],'displayed_path_valid':diagnostic['valid'],
                     'displayed_path':path,'path_color':diagnostic.get('color'),'path_length':diagnostic.get('length'),
                     'run_timestamp_utc':r.get('model_run_timestamp_utc'),'fresh_context':r.get('fresh_context'),
                     'tool_policy':r.get('tool_policy'),
                     'diagnostic_basis':'Strict full JSON, or final JSON line checked separately; no effect on formal extraction score.'})
    groups=[]
    for model in ('model_a','model_b'):
        selected=[r for r in rows if r['model']==model]
        group={'model':model,'display_label':config[model]['display_label'],
               'planned':sum(s['model']==model for s in schedule),'received':len(selected)}
        for name,field in [('displayed_paths_valid','displayed_path_valid'),('json_only_passed','json_only'),('formal_path_passed','formal_path_valid')]:
            group[name]=sum(r[field] for r in selected)
        group['by_dimension']=[{'n':n,'received':sum(r['n']==n for r in selected),
                               'displayed_paths_valid':sum(r['n']==n and r['displayed_path_valid'] for r in selected),
                               'json_only_passed':sum(r['n']==n and r['json_only'] for r in selected)} for n in (3,4)]
        groups.append(group)
    return {'pilot_id':manifest['pilot_id'],'planned':len(schedule),'received':len(rows),'missing':len(schedule)-len(rows),
            'groups':groups,'rows':rows,'source_sha256':dict(sorted(sources.items())),
            'diagnostic_policy':'Displayed path validity checks the full JSON reply or final JSON line separately from the unchanged frozen response parser. Formal extraction failures are not evidence of an incorrect displayed path.',
            'limitations':['User-pasted responses, not authenticated provider traces.',
                           'Display labels are user-reported; exact model versions and app settings unknown.',
                           'Run times and context/tool controls are not independently verified.',
                           'Reduced workload/selection adopted after two responses were seen; not preregistered.',
                           'A collection-order deviation and one user transcription correction are preserved.',
                           'Earlier uncertain-model practice and off-schedule Claude response excluded.',
                           'Small feasibility pilot, no general model ranking or safety-performance inference.']}


def write_audit(report, output, check=False):
    output=Path(output)
    fields=['slot_id','model','display_label','instance_id','n','displayed_path_valid','json_only',
            'formal_path_valid','path_color','path_length','record_file','record_sha256']
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore',lineterminator='\n')
    writer.writeheader();writer.writerows(report['rows'])
    artifacts={'audit.json':json_bytes(report),'audit.csv':stream.getvalue().encode('utf-8')}
    if check:
        for name,data in artifacts.items():
            if not (output/name).is_file() or (output/name).read_bytes()!=data:
                raise ValueError(f'saved audit differs from recomputed evidence: {name}')
    else:
        output.mkdir(parents=True,exist_ok=True)
        for name,data in artifacts.items():(output/name).write_bytes(data)
