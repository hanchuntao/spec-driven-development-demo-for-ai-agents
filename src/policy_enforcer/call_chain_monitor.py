"""调用链监控器（桩代码）。

追踪 Agent 在多轮对话中的工具调用序列，
检测危险调用链模式（如"读文档→发邮件到外部域名"），
并在命中白名单豁免规则时精确放行。

当前实现为桩——记录调用序列并在 check 时返回通过。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CallChainResult:
    """调用链检查结果。"""

    blocked: bool
    error_code: Optional[str] = None
    whitelist_matched: Optional[str] = None  # 命中的白名单规则 ID


class CallChainMonitor:
    """工具调用链监控器。

    维护一个滑动窗口（最近 N 轮调用），检测链式模式。
    黑名单规则（CHAIN-*）触发拦截，白名单（WL-*）豁免放行。

    设计原则：
      - 白名单优先于黑名单：先查豁免，再查拦截
      - 所有豁免放行都有审计日志
    """

    def __init__(self, spec: Dict[str, Any]):
        """从 Spec 加载调用链策略。

        Args:
            spec: call_chain_policies 策略字典（含 rules 和 whitelist）。
        """
        self.rules: List[Dict[str, Any]] = spec.get("rules", [])
        self.whitelist: List[Dict[str, Any]] = spec.get("whitelist", [])
        self.call_history: List[Dict[str, Any]] = []  # 最近 N 轮调用记录
        self.window_size: int = 5

    def record_call(self, tool_name: str, params: Dict[str, Any]):
        """记录一次工具调用。

        Args:
            tool_name: 工具名称。
            params: 调用参数。
        """
        self.call_history.append({"tool": tool_name, "params": params})
        if len(self.call_history) > self.window_size:
            self.call_history.pop(0)

    def check(self, current_tool: str, params: Dict[str, Any]) -> CallChainResult:
        """检查当前调用是否触发链式策略。

        流程：
          1. 将当前调用加入待检查序列
          2. 匹配黑名单规则
          3. 命中黑名单后检查白名单豁免
          4. 返回结果

        Args:
            current_tool: 即将调用的工具名称。
            params: 调用参数。

        Returns:
            CallChainResult，包含是否拦截及原因。
        """
        # 桩实现：生产环境替换为实际链式匹配逻辑
        return CallChainResult(blocked=False)

    def reset(self):
        """重置调用历史（新会话开始时调用）。"""
        self.call_history.clear()
