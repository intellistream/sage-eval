# sage-eval

**SAGE 平台专用评估工具库** - L3 纯算法库，提供评估指标、性能分析器与 LLM 评审工具。

**PyPI**: `isage-eval`  
**Import**: `sage_eval`  
**Layer**: L3 (Algorithm Library)

> ⚠️ **注意**: 这是评估**工具库**，不是 benchmark。Benchmark 项目请参考 [sage-benchmark](https://github.com/intellistream/sage-benchmark) 及相关仓库。

## 功能模块

### 📊 评估指标 (Metrics)
- **文本指标**: F1 Score, Exact Match, BLEU, ROUGE
- **分类指标**: Precision, Recall, Accuracy
- **检索指标**: Recall@K, MRR, NDCG

### ⚡ 性能分析 (Profiler)
- **延迟分析**: LatencyProfiler
- **内存分析**: MemoryProfiler
- **吞吐量分析**: ThroughputProfiler

### 🤖 LLM 评审 (Judge)
- **点式评估**: PointwiseJudge
- **对比评估**: PairwiseJudge

## Installation
```bash
pip install isage-eval
```

## Quick Start

```python
from sage_eval import F1Score, ROUGE, LatencyProfiler, PointwiseJudge

# 计算 F1 分数
f1 = F1Score()
score = f1.compute(predictions, references)

# 性能分析
profiler = LatencyProfiler()
with profiler.measure("task_name"):
    # 执行操作
    pass
report = profiler.report()

# LLM 评审
judge = PointwiseJudge(model="gpt-4")
score = judge.evaluate(
    question="What is Python?",
    answer="Python is a programming language."
)
```

## Integration with SAGE

本包作为独立的 L3 算法库，可以单独使用或集成到 SAGE 框架中。在 SAGE 框架中，接口层位于 `sage.libs.eval`，本包通过 `_register.py` 自动注册实现。

## License
Apache 2.0
