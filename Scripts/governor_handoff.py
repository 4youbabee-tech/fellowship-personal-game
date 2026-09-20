"""Validate evidence scope without treating a previous green build as current proof."""
import re


def validate_handoff(governor):
    errors = []
    handoff = governor.get('session_handoff', {})
    snapshot = handoff.get('validation_snapshot', {})
    baseline = snapshot.get('last_green', {})
    latest = snapshot.get('latest_observed', {})
    for name, record in [('last_green', baseline), ('latest_observed', latest)]:
        if not re.fullmatch(r'[0-9a-f]{40}', str(record.get('sha', ''))):
            errors.append('Handoff %s requires an exact commit SHA' % name)
        for gate in ('pre_unreal', 'unreal'):
            evidence = record.get(gate, {})
            if evidence.get('status') not in ('SUCCESS', 'FAILURE', 'CANCELLED', 'PENDING', 'IN_PROGRESS'):
                errors.append('Handoff %s/%s has invalid status' % (name, gate))
            if not isinstance(evidence.get('run_id'), int) or evidence.get('run_id', 0) <= 0:
                errors.append('Handoff %s/%s requires a workflow run ID' % (name, gate))
            if evidence.get('sha') != record.get('sha'):
                errors.append('Handoff %s/%s mixes evidence from another SHA' % (name, gate))
    if any(baseline.get(k, {}).get('status') != 'SUCCESS' for k in ('pre_unreal', 'unreal')):
        errors.append('Last green baseline requires both workflows to succeed')
    if handoff.get('source_head') != baseline.get('sha'):
        errors.append('Legacy verified handoff must refer to the same last-green baseline')
    if not handoff.get('next_actions') or not handoff.get('unverified_acceptance'):
        errors.append('Handoff must retain next actions and unverified experiential acceptance')
    return errors


def evidence_summary(governor, checkout_sha=''):
    snapshot = governor['session_handoff']['validation_snapshot']
    baseline, latest = snapshot['last_green'], snapshot['latest_observed']
    lines = ['Last verified baseline: ' + baseline['sha'],
             'Latest observed: %s | Pre-Unreal=%s | Unreal=%s' % (
                 latest['sha'], latest['pre_unreal']['status'], latest['unreal']['status'])]
    if checkout_sha and checkout_sha != latest['sha']:
        lines.append('This checkout is newer/different: recorded evidence does not certify it.')
    lines.append('Machine evidence does not approve visuals, performance or pacing.')
    return '\n'.join(lines)
