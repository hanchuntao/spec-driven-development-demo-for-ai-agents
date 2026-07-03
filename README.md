# Spec-Driven Development for AI Agents

> 把 Agent 的行为边界写进契约 —— 从接口契约到安全边界

本项目是对文章《AI时代如何做SDD：把Agent的行为边界写进契约》的代码化实现。它将文章中的所有 YAML Spec、Python 测试和策略引擎桩代码组织为一个完整的 Demo 项目，展示如何在 AI Agent 系统中引入 **"三层 Spec 模型"** 来做行为边界约束。

## 项目背景

### 问题

在传统 API 服务中，OpenAPI Spec 足以约束"消息格式对不对"——字段类型、枚举范围、必填/可选。但在 LLM Agent 系统中，LLM 作为中间决策层引入了四个新的安全威胁维度：

| 威胁维度 | 传统 Spec 能覆盖吗？ | 缺失什么？ |
|---------|---------------------|-----------|
| **指令注入** | 否。`content: string` 无法区分安全输入和含注入指令的输入 | 缺少输入语义层契约 |
| **工具调用权限漂移** | 部分。无法约束"什么上下文下可以调用什么工具" | 缺少策略层前置/后置条件 |
| **输出合规逃逸** | 否。响应中的自由文本不受约束 | 缺少输出内容安全校验 |
| **多 Agent 协议退化** | 部分。无法约束跨 Agent 调用的信任链传递 | 缺少协议版本化和调用溯源 |

### 解决方案：三层 Spec 模型

```
审计层 Spec（Compliance Assertion）
  ↑ 依赖
策略层 Spec（Agent Policy Spec）  ← 本项目核心
  ↑ 依赖
接口层 Spec（OpenAPI / Protobuf Schema）
```

- **接口层**：定义数据形状（字段类型、枚举、范围）—— 传统 OpenAPI 已覆盖
- **策略层**：定义行为形状（工具调用前置条件、输入安全、输出合规、跨 Agent 通信）—— 这是 Agent SDD 的核心创新
- **审计层**：定义合规声明和攻击面监控 —— 提供"事后可验证"能力

每一层都是**可机器验证**的，不是给人看的文档，是给 CI 流水线执行的断言。

## 目录结构

```
spec-driven-development-demo-for-ai-agents/
├── README.md                           # 本文件
├── LICENSE                             # MIT
├── specs/                              # Spec 定义（YAML）
│   ├── agent-tools.openapi.yaml        # 主 OpenAPI Spec + x-agent-policy $ref
│   ├── input-safety-policy.yaml        # 输入安全策略（§3.2）
│   ├── tool-policy.yaml                # 工具调用安全策略（§3.3）
│   ├── call-chain-policy.yaml          # 调用链策略 + 白名单豁免（§3.3.3）
│   ├── output-compliance.yaml          # 输出合规策略（§3.4）
│   └── inter-agent-protocol.yaml       # 多 Agent 通信协议（§3.5）
├── src/                                # 策略执行器桩代码
│   └── policy_enforcer/
│       ├── __init__.py                 # 模块入口与架构说明
│       ├── pattern_rules.py            # 确定性正则规则引擎
│       ├── semantic_rules.py           # 语义分析引擎（桩）
│       ├── input_safety_checker.py     # 输入安全检查器（pattern + semantic）
│       └── call_chain_monitor.py       # 工具调用链监控器（桩）
├── tests/                              # 安全策略回归测试
│   ├── conftest.py                     # fixtures（Spec 加载、攻击样本）
│   ├── test_input_safety.py            # §3.2.1 — prompt 注入检测回归
│   ├── test_tool_policy.py             # §3.3 — 工具调用权限校验
│   └── test_output_compliance.py       # §3.4 — 输出合规检测
├── attack_corpus/                      # 攻击样本语料库
│   ├── prompt_injections.jsonl         # prompt 注入 payload
│   └── tool_abuse_scenarios.jsonl      # 工具滥用场景
└── .github/
    ├── workflows/
    │   ├── contract-test.yml           # 契约测试 CI
    │   └── safety-regression.yml       # 安全策略回归 CI
    └── CODEOWNERS                      # Spec 变更的 Review 策略
```

## 快速开始

### 前置条件

- Python 3.11+
- Git

### 安装

```bash
git clone https://github.com/hanchuntao/spec-driven-development-demo-for-ai-agents.git
cd spec-driven-development-for-ai-agents
pip install pytest pyyaml
```

### 运行测试

```bash
# 运行所有安全策略回归测试
pytest tests/ -v

# 只跑输入安全测试
pytest tests/test_input_safety.py -v

# 只跑工具策略测试
pytest tests/test_tool_policy.py -v

# 只跑输出合规测试
pytest tests/test_output_compliance.py -v
```

### 验证 Spec 文件格式

```bash
python -c "
import yaml
from pathlib import Path
for f in Path('specs').glob('*.yaml'):
    with open(f) as fh:
        data = yaml.safe_load(fh)
    print(f'OK: {f}')
"
```

## 核心设计原则

1. **正则先行，语义兜底**：95% 的简单注入攻击由零延迟正则规则拦截，仅复杂场景才走语义分析
2. **Spec 与代码同源**：策略执行器从 Spec 生成，策略变更 = Spec 变更 = 自动触发 CI 回归
3. **白名单显式声明**：调用链拦截默认拒绝，合法业务通过显式白名单豁免精确放行
4. **版本协商而非强制一致**：多 Agent 间采用最小兼容版本协商，策略变更不需要原子化部署

## License

MIT — 详见 [LICENSE](./LICENSE)

---

*本项目代码提取自《AI时代如何做SDD：把Agent的行为边界写进契约》一文*
