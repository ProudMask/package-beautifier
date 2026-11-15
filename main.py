"""Suggest package names and optionally check their PyPI JSON API status."""
import argparse
import json
import random
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SUFFIXES = ('py', 'inator', 'inator3000', 'tron', 'ware', 'ify', 'oodles', 'licious')


class LookupFailed(RuntimeError):
    """The registry did not provide a reliable lookup result."""


def normalize_name(name):
    if not isinstance(name, str):
        raise ValueError('Package name must be text')
    name = name.strip()
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?', name, flags=re.ASCII):
        raise ValueError('Use ASCII letters/numbers with internal dots, underscores, or hyphens; start and end with a letter or number')
    return re.sub(r'[-_.]+', '-', name).lower()


def check_package_existence(package_name):
    """Return True/False for a matching 200/404; raise for inconclusive lookups."""
    name = normalize_name(package_name)
    request = Request(f'https://pypi.org/pypi/{name}/json', headers={'Accept': 'application/json', 'User-Agent': 'package-beautifier-portfolio/1.0'})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
        actual_name = payload.get('info', {}).get('name') if isinstance(payload, dict) else None
        if not actual_name or normalize_name(actual_name) != name:
            raise LookupFailed('PyPI returned unexpected project metadata')
        return True
    except HTTPError as exc:
        if exc.code == 404:
            return False
        raise LookupFailed(f'PyPI lookup failed with HTTP {exc.code}') from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise LookupFailed('PyPI lookup failed due to a network error or timeout') from exc
    except (ValueError, AttributeError) as exc:
        raise LookupFailed('PyPI returned invalid project metadata') from exc


def generate_funny_name(package_name, rng=None):
    name = normalize_name(package_name)
    rng = rng if rng is not None else random.SystemRandom()
    return name + rng.choice(SUFFIXES)


def suggest_names(package_name, count=3, seed=None):
    name = normalize_name(package_name)
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= len(SUFFIXES):
        raise ValueError(f'Count must be an integer between 1 and {len(SUFFIXES)}')
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise ValueError('Seed must be an integer or None')
    return [name + suffix for suffix in random.Random(seed).sample(SUFFIXES, count)]


def lookup_status(name, offline):
    if offline:
        return {'name': name, 'status': 'not_checked'}
    try:
        return {'name': name, 'status': 'found' if check_package_existence(name) else 'not_found'}
    except LookupFailed as exc:
        return {'name': name, 'status': 'unknown', 'reason': str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    parser.add_argument('--count', type=int, default=3)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--offline', action='store_true', help='Generate suggestions without any network lookups')
    args = parser.parse_args()
    try:
        name = normalize_name(args.name)
        suggestions = suggest_names(name, args.count, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    report = {'query': lookup_status(name, args.offline), 'suggestions': [lookup_status(candidate, args.offline) for candidate in suggestions], 'note': 'not_found means no project metadata was returned by this endpoint; it does not guarantee the name can be registered.'}
    print(json.dumps(report, indent=2))
    return 1 if any(item['status'] == 'unknown' for item in [report['query'], *report['suggestions']]) else 0


if __name__ == '__main__':
    raise SystemExit(main())
