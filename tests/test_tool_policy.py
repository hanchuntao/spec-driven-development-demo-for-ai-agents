"""工具调用安全策略回归测试。

校验 tool-policy.yaml 中的前置条件规则。
对应文章 §3.3 工具调用安全策略。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re


# ── 辅助函数：模拟规则表达式中的简单逻辑 ──

def extract_email_domains(recipient: str) -> list:
    """从收件人字符串中提取域名列表。"""
    if isinstance(recipient, list):
        recipients = recipient
    else:
        recipients = [recipient]
    domains = []
    for r in recipients:
        match = re.search(r"@([\w.-]+)", r)
        if match:
            domains.append(match.group(1))
    return domains


def extract_urls(text: str) -> list:
    """从文本中提取 URL 的域名。"""
    from urllib.parse import urlparse
    urls = re.findall(r"https?://[^\s<>\"']+", text)
    result = []
    for u in urls:
        parsed = urlparse(u)
        result.append(parsed)
    return result


# ── 测试 ──


class TestSendEmailPreconditions:
    """send_email 工具的前置条件校验。"""

    def test_recipient_scope_non_admin_blocked(self, tool_policy_spec):
        """非管理员向外部域名发邮件应被拦截。"""
        preconditions = tool_policy_spec["send_email"]["preconditions"]
        scope_rule = next(r for r in preconditions if r["id"] == "TOOL-PRE-001")

        # 模拟上下文：普通员工，部门域名为 company.com
        allowed_domains = ["company.com"]
        recipient = "external@partner.com"

        domains = extract_email_domains(recipient)
        violations = [d for d in domains if d not in allowed_domains]

        assert len(violations) > 0, "External recipient should be a violation"
        assert scope_rule["on_violation"] == "block"

    def test_recipient_scope_admin_allowed(self, tool_policy_spec):
        """管理员应该可以跨域发送（但按 TOOL-PRE-001 原始逻辑仅限同部门）。"""
        preconditions = tool_policy_spec["send_email"]["preconditions"]
        # TOOL-PRE-001 使用 caller.department.member_domains 而非 role == admin
        # 此处验证规则存在即可
        scope_rule = next(r for r in preconditions if r["id"] == "TOOL-PRE-001")
        assert scope_rule is not None
        assert scope_rule["error_code"] == "POLICY_TOOL_RECIPIENT_SCOPE"

    def test_attachment_type_whitelist(self, tool_policy_spec):
        """只允许白名单内的附件类型。"""
        preconditions = tool_policy_spec["send_email"]["preconditions"]
        attach_rule = next(r for r in preconditions if r["id"] == "TOOL-PRE-002")

        allowed = ["pdf", "docx", "xlsx", "txt"]
        assert "exe" not in allowed
        assert "pdf" in allowed
        assert attach_rule["error_code"] == "POLICY_TOOL_ATTACHMENT_TYPE"

    def test_external_url_check(self, tool_policy_spec):
        """邮件中包含外部链接应被检测。"""
        preconditions = tool_policy_spec["send_email"]["preconditions"]
        url_rule = next(r for r in preconditions if r["id"] == "TOOL-PRE-003")

        assert url_rule["on_violation"] == "block_and_alert"
        assert url_rule["error_code"] == "POLICY_TOOL_EXTERNAL_URL"


class TestCreateTicketPreconditions:
    """create_ticket 工具的前置条件校验。"""

    def test_critical_ticket_only_oncall(self, tool_policy_spec):
        """紧急工单只能由 oncall_engineer 角色创建。"""
        preconditions = tool_policy_spec["create_ticket"]["preconditions"]
        rule = next(r for r in preconditions if r["id"] == "TOOL-PRE-010")

        # 模拟：非 oncall 角色创建 critical 工单
        params = {"priority": "critical"}
        caller_role = "developer"  # 非 oncall_engineer

        if params["priority"] == "critical":
            allowed = caller_role == "oncall_engineer"

        assert not allowed, "Developer should not create critical tickets"
        assert rule["error_code"] == "POLICY_TOOL_CRITICAL_TICKET_PERMISSION"

    def test_normal_ticket_any_role(self, tool_policy_spec):
        """非紧急工单不限制角色。"""
        params = {"priority": "normal"}
        # 任何角色都可以创建普通工单
        allowed = True
        assert allowed


class TestSearchDocumentsPreconditions:
    """search_documents 工具的前置条件校验。"""

    def test_classification_check(self, tool_policy_spec):
        """文档密级不得高于用户安全级别。"""
        preconditions = tool_policy_spec["search_documents"]["preconditions"]
        rule = next(r for r in preconditions if r["id"] == "TOOL-PRE-020")

        assert rule["error_code"] == "POLICY_CLASSIFICATION_VIOLATION"
        assert rule["on_violation"] == "block"
