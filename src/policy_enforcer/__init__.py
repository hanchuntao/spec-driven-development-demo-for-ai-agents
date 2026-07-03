# src/policy_enforcer — Agent Policy Enforcer Runtime
#
# 从 Spec 生成的策略执行器，嵌入 Agent Runtime 作为中间件层。
# 架构：
#   LLM Inference → Policy Enforcer (precondition) → Tool Executor
#                                                 → Policy Enforcer (postcondition) → Response
#
# 核心组件：
#   - PatternRuleEngine: 确定性正则规则引擎
#   - SemanticRuleEngine: 语义分析引擎（本地分类器）
#   - InputSafetyChecker: 输入安全检查器（组合以上两者）
#   - CallChainMonitor: 工具调用链监控器
