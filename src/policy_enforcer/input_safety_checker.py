"""输入安全检查器。

组合 PatternRuleEngine 和 SemanticRuleEngine，
按"正则先行、语义兜底"的分层策略执行输入安全检查。

这是 test_input_safety.py 直接调用的入口。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .pattern_rules import MatchedRule, PatternRuleEngine
from .semantic_rules import SemanticRuleEngine


@dataclass
class InputSafetyResult:
    """输入安全检查的最终结果。"""

    blocked: bool
    flagged: bool
    matched_rules: List[MatchedRule] = field(default_factory=list)


class InputSafetyChecker:
    """输入安全检查器。

    执行流程：
      1. 提取 messages 中所有 user role 的 content
      2. Pattern 层：正则规则（零延迟）
      3. Semantic 层：语义分析（仅 pattern 层通过后执行）

    Usage:
        spec = yaml.safe_load(open("specs/input-safety-policy.yaml"))
        checker = InputSafetyChecker(spec["input_safety"])
        result = checker.check({"messages": [{"role": "user", "content": "..."}]})
        if result.blocked:
            print(f"Blocked by rules: {[r.id for r in result.matched_rules]}")
    """

    def __init__(self, spec: Dict[str, Any]):
        """初始化检查器。

        Args:
            spec: input_safety 策略字典（含 pattern_rules 和 semantic_rules）。
        """
        self.pattern_engine = PatternRuleEngine(spec)
        self.semantic_engine = SemanticRuleEngine(spec)

    def check(self, request: Dict[str, Any]) -> InputSafetyResult:
        """检查请求中的所有用户消息。

        提取 request["messages"] 中 role == "user" 的所有 content，
        拼接后依次通过 pattern 层和 semantic 层。

        Args:
            request: 包含 messages 数组的请求字典。

        Returns:
            InputSafetyResult，包含拦截状态和匹配到的规则。
        """
        user_texts = [
            msg["content"]
            for msg in request.get("messages", [])
            if msg.get("role") == "user"
        ]
        combined_text = "\n".join(user_texts)

        # 第一层：确定性正则
        pattern_result = self.pattern_engine.check(combined_text)
        if pattern_result.blocked:
            return InputSafetyResult(
                blocked=True,
                flagged=pattern_result.flagged,
                matched_rules=pattern_result.matched_rules,
            )

        # 第二层：语义分析（仅 pattern 层通过后执行）
        semantic_result = self.semantic_engine.check(combined_text)

        return InputSafetyResult(
            blocked=semantic_result.blocked,
            flagged=pattern_result.flagged or semantic_result.flagged,
            matched_rules=pattern_result.matched_rules,
        )
