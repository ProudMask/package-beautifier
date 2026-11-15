# Package Beautifier

A small CLI that suggests playful Python distribution names and optionally checks their project metadata on PyPI. Validates and normalizes names, distinguishes registry lookup failures from missing metadata, and supports reproducible offline examples. Python 3.10 or later; no third-party packages required.

## Try offline first

```bash
python main.py my_analytics --count 3 --seed 42 --offline
python -m unittest discover -s tests -v
```

Offline mode performs no network requests; every result is labeled `not_checked`. The same seed reproduces the suggestions on the same Python runtime. At most eight suggestions are supported, one per distinct suffix. Suggestions are procedural, not AI-generated.

## Check PyPI

```bash
python main.py my-analytics --count 3 --seed 42
```

This checks the normalized input and each suggestion against `https://pypi.org/pypi/NAME/json`, with a 10-second timeout per request. No package is installed, uploaded, or reserved. There are at most nine sequential lookups per invocation and no automatic retries.

| Status | Meaning |
| --- | --- |
| `found` | Project metadata returned with the expected normalized name |
| `not_found` | The endpoint returned HTTP 404 |
| `unknown` | Network failure, non-404 error status, or malformed/unexpected metadata |
| `not_checked` | Offline generation only |

**A 404 does not guarantee that a name can be registered.** This is a point-in-time metadata lookup, not a reservation or availability guarantee. Network failures never become an availability claim. If any lookup is inconclusive, the CLI prints the report but exits with status 1; invalid arguments exit with status 2.

## Naming rules and API

Names must begin and end with an ASCII letter or number and can contain internal dots, underscores, or hyphens. Outer whitespace is trimmed. Comparison lowercases names and collapses runs of `-`, `_`, and `.` to a hyphen. For example, `My__Analytics` becomes `my-analytics`.

```python
from main import suggest_names, check_package_existence, LookupFailed

names = suggest_names('my_analytics', count=3, seed=42)
# check_package_existence returns True/False or raises LookupFailed.
```

The existing generate_funny_name helper remains available. Importing the module does not prompt, print, or access the network. The global pseudorandom stream is not reseeded.

## Verification and scope

Tests mock registry responses and require no network. They cover normalization, invalid names, successful lookups, 404/429/500 handling, timeouts, malformed metadata, seeded suggestions, and the offline CLI. Live PyPI integration has not been tested for this update. No claim is made about trademarks, name suitability, registration policy, or ML performance.

## References

- [PyPA name validation and normalization](https://packaging.python.org/en/latest/specifications/name-normalization/)
- [PyPI JSON API](https://docs.pypi.org/api/json/)
