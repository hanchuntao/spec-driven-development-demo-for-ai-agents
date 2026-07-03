"""语义规则引擎（桩代码）。

在确定性正则规则全部通过后，对输入执行语义分析。
生产环境下应调用本地部署的轻量文本分类器（如 DistilBERT 微调模型）
或独立小模型做裁判（Judge Model），而非调用业务 LLM。

当前实现为桩——始终返回通过。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SemanticMatchResult:
    """语义规则匹配结果。"""

    blocked: bool
    flagged: bool
    matched_rules: List[str] = field(default_factory=list)


class SemanticRuleEngine:
    """语义分析引擎。

    设计原则：
      1. 与业务 LLM 隔离——语义分类器不共享上下文
      2. 仅接收 (system_prompt, user_input) 二元组
      3. 阈值可通过 A/B 测试持续校准

    当前为桩实现，返回通过状态。
    """

    def __init__(self, spec: Dict[str, Any]):
        """从 Spec 中加载 semantic_rules 配置。

        Args:
            spec: 包含 semantic_rules 节点的策略字典。
        """
        self.rules: List[Dict[str, Any]] = spec.get("semantic_rules", [])

    def check(self, text: str, system_prompt: str = "") -> SemanticMatchResult:
        """执行语义分析。

        Args:
            text: 用户输入文本。
            system_prompt: 当前 Agent 的 system prompt（用于意图偏差检测）。

        Returns:
            SemanticMatchResult，当前桩实现始终返回未拦截。
        """
        # 桩实现：生产环境替换为实际分类器调用
        return SemanticMatchResult(blocked=False, flagged=False)
