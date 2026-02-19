# SAGE Eval (isage-eval) - Copilot Instructions

## 🚨 Runtime Direction (Cross-Repo)

- `sageFlownet` is the runtime component that replaces `Ray` in the SAGE ecosystem.
- Eval code should remain runtime-neutral, but any runtime/scheduling guidance must align with Flownet.
- Do NOT add new `ray` imports/dependencies.

## 🚨 Installation Consistency (Cross-Repo)

- 在 conda 环境中，**必须**使用 `python -m pip`，不要直接使用 `pip`。
- 若流程依赖 SAGE 主仓库能力，先在 `SAGE/` 执行 `./quickstart.sh --dev --yes`。
- SAGE quickstart 已安装核心独立 PyPI 依赖（如 `isagellm`、`isage-flownet`、`isage-vdb` 等），不要重复建议通过 extras 手动补装。
- `git push` 前必须确认本仓库 `pre-push` hooks 行为；部分仓库会在 push 时自动更新版本号并触发 PyPI/TestPyPI 发布。

## Package Identity

| 属性 | 值 |
|-----|-----|
| **PyPI 包名** | `isage-eval` |
| **导入名称** | `sage_eval` |
| **SAGE 架构层级** | **L3 (Algorithm Library)** |
| **版本格式** | 四段式 `0.0.0.x` |
| **仓库** | `intellistream/sage-eval` |

## 🚨 CRITICAL：这不是 Benchmark

**sage-eval 是评估工具库，不是 benchmark 框架。**

- ✅ **sage-eval**: 提供可复用的评估指标、Profiler、LLM Judge 的实现
- ❌ **NOT benchmark**: 不包含实验运行器、数据集管理、结果报告生成
- 📊 **Benchmark 项目**: 参考 `sage-benchmark`, `sage-agent-benchmark` 等独立仓库

**区别**:
```python
# ✅ sage-eval 提供的功能（可复用组件）
from sage_eval import F1Score, LatencyProfiler, PointwiseJudge

# ❌ sage-eval 不提供的功能（这些在 benchmark 仓库中）
# - Experiment runners
# - Dataset loaders
# - Benchmark configurations
# - Report generators
```

## 层级定位

这是一个 **L3 纯算法库**，提供评估指标、Profiler 和 LLM Judge 的实现。

### ✅ 允许的依赖

- Python 标准库
- `sage-common` (L1) - 通过 SAGE 框架使用时
- `sage-libs` 接口层 (L3) - 注册到 SAGE 工厂
- 轻量级第三方库：`numpy`, `scikit-learn`, `rouge-score` 等

### ❌ 禁止的依赖

- 任何 L4+ 层的包 (`sage-middleware`, `sage-kernel`)
- 网络服务、数据库连接
- 重型运行时后端

## 功能模块

### 1. 评估指标 (Metrics)

```python
from sage_eval import (
    F1Score, ExactMatch, BLEU, ROUGE,
    Recall, Precision, Accuracy
)

# F1 分数
f1 = F1Score()
score = f1.compute(predictions, references)

# ROUGE 分数
rouge = ROUGE()
scores = rouge.compute(predictions, references)
```

### 2. Profiler (性能分析)

```python
from sage_eval import Profiler, LatencyProfiler, MemoryProfiler

# 延迟分析
profiler = LatencyProfiler()
with profiler.measure("operation_name"):
    # 执行操作
    pass
report = profiler.report()
```

### 3. LLM Judge (LLM 评估)

```python
from sage_eval import LLMJudge, PairwiseJudge, PointwiseJudge

# 点式评估
judge = PointwiseJudge(model="gpt-4")
score = judge.evaluate(
    question="What is Python?",
    answer="Python is a programming language."
)

# 对比评估
judge = PairwiseJudge(model="gpt-4")
winner = judge.compare(answer_a, answer_b, question)
```

## 目录结构

```
sage-eval/
├── src/sage_eval/
│   ├── __init__.py
│   ├── _version.py      # 版本：__version__ = "0.0.0.x"
│   ├── _register.py     # 自动注册到 SAGE 工厂
│   ├── metrics/         # 评估指标
│   │   ├── text.py      # F1, EM, BLEU, ROUGE
│   │   ├── classification.py
│   │   └── retrieval.py # Recall@K, MRR, NDCG
│   ├── profiler/        # 性能分析
│   │   ├── latency.py
│   │   ├── memory.py
│   │   └── throughput.py
│   └── judge/           # LLM 评估
│       ├── base.py
│       ├── pointwise.py
│       └── pairwise.py
├── tests/
├── pyproject.toml
└── README.md
```

## 与 SAGE 主仓库的关系

### SAGE 侧 (`sage.libs.eval`)

SAGE 主仓库中的 `sage.libs.eval` 包含：

1. **接口层** (`sage.libs.eval.interface`)：
   - 抽象基类：`Metric`, `Profiler`, `Judge`
   - 工厂函数：`create_metric()`, `create_profiler()` 等

### 本包 (`sage_eval`) 提供

**具体实现**，通过 `_register.py` 自动注册到 SAGE 工厂。

## 常见问题修复指南

### 问题 1：指标计算维度不匹配

```python
# 确保预测和参考的长度一致
assert len(predictions) == len(references), "Length mismatch"
```

### 问题 2：LLM Judge API 密钥

LLM Judge 需要 API 密钥，但不应硬编码：
```python
# 从环境变量读取
import os
api_key = os.environ.get("OPENAI_API_KEY")
```

### 问题 3：Profiler 上下文管理

使用 context manager 确保资源正确释放：
```python
with profiler.measure("task"):
    do_something()
# 自动记录结束时间
```

## 测试

```bash
pytest tests/ -v
```

## 发布

```bash
# 版本递增：修改 src/sage_eval/_version.py
python -m build
twine upload dist/*
```
