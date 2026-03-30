# ADR 0001: Remove fallback registration and interface import compatibility branches

## Status

Accepted

## Context

Issue `intellistream/sage-eval#3` requires boundary normalization for the evaluation library:

- keep composable evaluation interfaces,
- avoid execution-platform binding logic,
- remove compatibility/fallback branches.

Audit findings before this change:

- metric/judge/profiler modules used `try/except ImportError` and downgraded base classes to `object`;
- `_register.py` used optional registration branch (`SAGE available -> register`, otherwise skip).

These patterns introduced compatibility fallback behavior and weakened fail-fast constraints.

## Decision

1. Remove all `ImportError` fallback branches from metric/judge/profiler modules.
2. Import `sage.libs.eval.interface.base` directly and fail fast if interface dependency is broken.
3. Remove optional registration path in `_register.py` and register components unconditionally at import.
4. Keep explicit regression tests for absence of fallback branches.

## Consequences

- Evaluation components keep a clear L3 interface-implementation boundary.
- Dependency errors surface immediately instead of being silently masked.
- Registration behavior is deterministic and testable.
