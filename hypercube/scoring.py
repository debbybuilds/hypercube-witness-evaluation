"""Strict local response scoring with explicit collection denominators."""
from datetime import datetime, timezone
import json
import re
from .validation import validate_instance, check_path


def strict_json(text):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate JSON key')
            obj[key] = value
        return obj
    def constant(value):
        raise ValueError(f'nonstandard JSON constant: {value}')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def score_response(instance, raw):
    validate_instance(instance)
    if type(raw) is not str:
        raise ValueError('received response must be a string')
    obj = None
    json_only = False
    try:
        obj = strict_json(raw)
        json_only = True
    except (ValueError, RecursionError):
        match = re.fullmatch(r'\s*```(?:json)?\s*(.*?)\s*```\s*',raw,re.S)
        if match:
            try:
                obj = strict_json(match.group(1))
            except (ValueError, RecursionError):
                pass
    path = obj.get('path') if type(obj) is dict else None
    check = check_path(instance,path)
    schema = (type(obj) is dict and set(obj)=={'path'} and type(path) is list
              and all(type(v) is str for v in path))
    return {'json_only':json_only,'schema_compliant':schema,
            'valid_path':check['valid'],'path_check':check}


def model_identity(record):
    """Keep user-reported app labels separate from exact provider identifiers."""
    provider = record.get('provider')
    if type(provider) is not str or not provider.strip():
        raise ValueError('provider must be a nonempty string')
    mode = record.get('identity_resolution', 'exact_model_id')
    if mode == 'exact_model_id':
        model_id = record.get('model_id')
        if type(model_id) is not str or not model_id.strip():
            raise ValueError('model_id must be a nonempty exact identifier')
        return provider, model_id, mode, None
    if mode == 'display_label_only':
        label = record.get('display_label')
        if 'model_id' not in record or record['model_id'] is not None:
            raise ValueError('display-label records must leave exact model_id null')
        if type(label) is not str or not label.strip():
            raise ValueError('display_label must be a nonempty string')
        return provider, None, mode, label
    raise ValueError('unknown identity_resolution')


def _validate_attempt(a, slot):
    if type(a) is not dict:
        raise ValueError('attempt must be an object')
    for key in ('attempt_id','slot_id'):
        if type(a.get(key)) is not str or not a[key].strip():
            raise ValueError(f'{key} must be a nonempty string')
    model_identity(a)
    if a.get('prompt_sha256') != slot['prompt_sha256']:
        raise ValueError('prompt hash does not match scheduled prompt')
    if a.get('tool_policy') != 'none' or a.get('fresh_context') is not True:
        raise ValueError('pilot requires no tools or browsing and a fresh context')
    for key in ('requested_settings','returned_settings'):
        if key not in a or (a[key] is not None and type(a[key]) is not dict):
            raise ValueError(f'{key} must be an object or null when unknown')
    timestamp = a.get('timestamp_utc')
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z','+00:00'))
    except (ValueError,AttributeError,TypeError) as exc:
        raise ValueError('timestamp_utc must be an ISO 8601 UTC time') from exc
    if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
        raise ValueError('timestamp_utc must include a UTC offset')
    if a.get('status') == 'received':
        if type(a.get('raw')) is not str or a.get('error') is not None:
            raise ValueError('received attempt needs raw string and no transport error')
    elif a.get('status') == 'transport_error':
        if a.get('raw') is not None or type(a.get('error')) is not str or not a['error'].strip():
            raise ValueError('transport_error needs error text and null raw response')
    else:
        raise ValueError('status must be received or transport_error')


def summarize(schedule, attempts, instances):
    slots = {s['slot_id']:s for s in schedule}
    if len(slots) != len(schedule):
        raise ValueError('schedule contains duplicate slots')
    if type(attempts) is not list:
        raise ValueError('attempts must be a list')
    for s in schedule:
        if s['instance_id'] not in instances:
            raise ValueError('scheduled instance missing')
        validate_instance(instances[s['instance_id']])
    by_id, effective, model_identities, audited = {}, {}, {}, []
    for a in attempts:
        if type(a) is not dict or type(a.get('slot_id')) is not str or a['slot_id'] not in slots:
            raise ValueError('unknown or missing slot_id')
        slot = slots[a['slot_id']]
        _validate_attempt(a,slot)
        aid = a['attempt_id']
        if aid in by_id:
            raise ValueError('duplicate attempt_id')
        identity = model_identity(a)
        model = slot['model']
        if model in model_identities and model_identities[model] != identity:
            raise ValueError('a model slot cannot change provider/model identifier')
        model_identities[model] = identity
        previous = effective.get(a['slot_id'])
        replaces = a.get('replaces_attempt_id')
        if previous is None and replaces is not None:
            raise ValueError('replacement must follow an existing attempt in the same slot')
        if previous is not None:
            if replaces != previous['attempt_id'] or previous['status'] != 'transport_error':
                raise ValueError('only the latest transport failure may be replaced; preserve the chain')
        score = score_response(instances[slot['instance_id']],a['raw']) if a['status']=='received' else None
        audited.append(dict(a,score=score))
        by_id[aid] = audited[-1]
        effective[a['slot_id']] = audited[-1]
    groups = []
    for model,n in sorted({(s['model'],s['n']) for s in schedule}):
        selected = [s for s in schedule if (s['model'],s['n'])==(model,n)]
        outcomes = [effective[s['slot_id']] for s in selected if s['slot_id'] in effective]
        received = [a for a in outcomes if a['status']=='received']
        fields = {name:sum(a['score'][name] for a in received)
                  for name in ('json_only','schema_compliant','valid_path')}
        count = len(received)
        identity = model_identities.get(model)
        group = {'model':model,'n':n,'provider':identity[0] if identity else None,
                 'model_id':identity[1] if identity else None,
                 'identity_resolution':identity[2] if identity else None,
                 'display_label':identity[3] if identity else None,
                 'planned':len(selected),'received':count,
                 'never_attempted':len(selected)-len(outcomes),
                 'transport_failed':sum(a['status']=='transport_error' for a in outcomes),
                 'transport_error_events':sum(a['status']=='transport_error' and slots[a['slot_id']]['model']==model
                                              and slots[a['slot_id']]['n']==n for a in audited),
                 'correct':fields['valid_path'],
                 'correct_per_planned_collection_progress':fields['valid_path']/len(selected)}
        for field in fields:
            group[field+'_passed'] = fields[field]
            group[field+'_rate_observed'] = fields[field]/count if count else None
        groups.append(group)
    return {'measurement_status':'responses scored' if any(g['received'] for g in groups) else 'no responses collected',
            'denominator_note':'Observed rates use received responses only. correct_per_planned_collection_progress is collection progress, not accuracy. Repeated trials are clustered by instance.',
            'groups':groups,'attempts':audited}
