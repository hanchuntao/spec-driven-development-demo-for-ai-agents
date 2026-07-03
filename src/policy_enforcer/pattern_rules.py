"""确定性正则规则引擎。

从 Spec 加载 pattern_rules，在输入文本上执行正则匹配。
95% 的简单注入攻击在这一层被零延迟、零 token 成本拦截。
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MatchedRule:
    """匹配到的规则记录。"""

    id: str
    name: str
    error_code: str
    on_match: str  # block | flag_for_review | block_and_alert
    matched_pattern: str


@dataclass
class PatternMatchResult:
    """单条规则匹配结果。"""

    blocked: bool
    flagged: bool
    matched_rules: List[MatchedRule] = field(default_factory=list)


class PatternRuleEngine:
    """加载并执行确定性正则规则。

    按照 Spec 中定义的 pattern_rules 列表，对输入文本逐一匹配。
    支持三种 on_match 动作：
      - block: 直接拒绝请求
      - block_and_alert: 拒绝并发送告警
      - flag_for_review: 仅标记，不阻塞（如 Base64 检测）
    """

    def __init__(self, spec: Dict[str, Any]):
        """从 Spec 中加载 pattern_rules。

        Args:
            spec: 输入安全策略字典（input_safety 节点或其子集）。
        """
        self.rules: List[Dict[str, Any]] = spec.get("pattern_rules", [])

    def check(self, text: str) -> PatternMatchResult:
        """对输入文本执行所有正则规则。

        一旦命中 block 或 block_and_alert 规则，立即返回并终止后续检查。
        flag_for_review 规则不阻止继续匹配。

        Args:
            text: 待检查的文本内容。

        Returns:
            PatternMatchResult，包含是否被拦截、是否被标记及匹配到的规则列表。
        """
        result = PatternMatchResult(blocked=False, flagged=False)

        for rule in self.rules:
            on_match = rule.get("on_match", "block")
            for pattern in rule.get("patterns", []):
                if re.search(pattern, text):
                    matched = MatchedRule(
                        id=rule["id"],
                        name=rule["name"],
                        error_code=rule.get("error_code", ""),
                        on_match=on_match,
                        matched_pattern=pattern,
                    )
                    result.matched_rules.append(matched)

                    if on_match in ("block", "block_and_alert"):
                        result.blocked = True
                        return result  # 硬拦截，立即终止
                    elif on_match == "flag_for_review":
                        result.flagged = True

        return result
