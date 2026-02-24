# SAGE Eval Copilot Instructions

## Scope
- Package `isage-eval` (`sage_eval`) is an L3 evaluation library.
- Provides reusable metrics, profilers, and LLM judge implementations.

## Critical rules
- This is not a benchmark runner; keep experiment orchestration out of this repo.
- Keep runtime-neutral design and avoid L4+ dependencies.
- Flownet-aligned ecosystem direction; do not add `ray` imports/dependencies.
- In conda environments, use `python -m pip`.
- No silent fallback logic.

## Architecture focus
- Metrics (`metrics/`), profilers (`profiler/`), judges (`judge/`), registration (`_register.py`).
- Keep APIs typed and composable for upstream benchmark repos.

## Workflow
1. Make minimal implementation changes.
2. Add unit tests for edge cases and API behavior.
3. Keep docs/examples aligned with public API.
