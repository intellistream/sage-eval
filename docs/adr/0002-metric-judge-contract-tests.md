# ADR 0002: Reinforce metric/judge contract tests

## Status

Accepted

## Context

Issue `intellistream/sage-eval#5` 要求强化 `metric/judge` 对外契约稳定性。

当前仓库已完成边界清理（无兼容分支），但仍需要更明确的合同测试来锁定外部行为，避免后续重构造成静默漂移。

## Decision

新增 `tests/test_issue5_metric_judge_contracts.py`，覆盖以下合同：

1. **Metric 合同**
   - 结果对象保持 `name/score/metadata` 与 `value` alias。
   - `metric_type` 返回稳定枚举值（accuracy/bleu/f1_score）。
   - `AccuracyMetric(top_k)` 的排序候选语义可回归。
   - `F1Metric` 对非法 `average` 参数 fail-fast。

2. **Judge 合同**
   - `JudgmentResult.to_dict()` 输出键集合稳定。
   - `FaithfulnessJudge` 解析缺失 `SCORE` 时使用默认分值行为可回归。
   - `RelevanceJudge` 缺失 `llm_fn`/`question` 时保持 fail-fast 异常语义。
   - `context=None` 时 prompt 占位文本行为固定。

## Consequences

- 对外 API 行为被测试锁定，降低无意变更风险。
- 不新增兼容层、shim 或 fallback 分支。
- 后续修改若破坏契约，将在测试阶段被立即发现。

## Verification

- `ruff check tests/test_issue5_metric_judge_contracts.py docs/adr/0002-metric-judge-contract-tests.md`
- `pytest -q tests/test_issue5_metric_judge_contracts.py`
