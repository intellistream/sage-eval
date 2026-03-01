# sage-eval

SAGE L3 评估组件库，提供可组合的 `Metric`、`Profiler`、`LLM Judge` 实现。

- PyPI: `isage-eval`
- Import: `sage_libs.sage_eval`
- Layer: L3 (evaluation library, not benchmark)

## 边界与约束

- 本仓库只提供评测组件实现，不承载执行平台调度职责。
- 依赖 `sage.libs.eval` 接口层并在导入时注册实现。
- 采用 fail-fast：不保留 fallback / shim / 兼容分支。

## 当前组件

### Metrics

- `AccuracyMetric`
- `BLEUMetric`
- `F1Metric`

### Profilers

- `LatencyProfiler`
- `ThroughputProfiler`

### Judges

- `FaithfulnessJudge`
- `RelevanceJudge`

## 安装

```bash
pip install isage-eval
```

## 快速使用

```python
from sage_libs.sage_eval import AccuracyMetric, LatencyProfiler, RelevanceJudge

metric = AccuracyMetric()
metric_result = metric.compute([1, 0, 1], [1, 1, 1])

profiler = LatencyProfiler()
with profiler:
    _ = sum(range(10000))

def mock_llm(_: str) -> str:
    return "SCORE: 0.9\nREASONING: Relevant response."

judge = RelevanceJudge(llm_fn=mock_llm)
judge_result = judge.judge(
    response="Paris is the capital of France.",
    question="What is the capital of France?",
)
```

## License

Apache 2.0
