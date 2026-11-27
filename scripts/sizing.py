"""Capacity profiles and approved figures shared by the site and PDF."""
import json
import math
from pathlib import Path


PROFILES = json.loads((Path(__file__).resolve().parents[1] / 'src/sizing.json').read_text())


def metrics(product):
    profile = PROFILES[product['sizing_profile']]
    values = product.get('verified_sizing', {})
    unknown = values.keys() - {entry['key'] for entry in profile['metrics']}
    if unknown:
        raise ValueError(f"{product['slug']}: unknown sizing metrics {sorted(unknown)}")

    for entry in profile['metrics']:
        approved = values.get(entry['key'])
        if entry.get('published_only') and approved is None:
            continue
        if approved is not None:
            lower = approved.get('value')
            upper = approved.get('upper', lower)
            if (
                any(type(n) not in (int, float) or not math.isfinite(n) or n <= 0 for n in (lower, upper))
                or upper < lower
                or approved.get('unit') not in entry['units']
                or not approved.get('source', '').strip()
                or (entry.get('requires_basis') and not approved.get('basis', '').strip())
            ):
                raise ValueError(f"{product['slug']}: invalid verified figure for {entry['key']}")
        yield entry, approved


def units_text(metric):
    return ' or '.join(metric['units'])


def value_text(approved):
    lower = approved['value']
    upper = approved.get('upper', lower)
    amount = f'{lower:,}' if upper == lower else f'{lower:,}–{upper:,}'
    return f'{amount} {approved["unit"]}'


def enquiry_profile(product):
    return {
        'guidance': PROFILES[product['sizing_profile']]['guidance'],
        'metrics': [
            {key: entry[key] for key in ('key', 'label', 'units')}
            for entry, _ in metrics(product)
        ],
    }
