"""输出合规策略回归测试。

校验 output-compliance.yaml 中的规则：
  - OUT-001: system prompt 泄露检测
  - OUT-002: 跨用户数据泄露
  - OUT-003: PII 检测与脱敏
  - OUT-SEM-001: 有害内容检测
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestOutputCompliancePatternRules:
    """OUT-001 ~ OUT-003 确定性规则校验。"""

    def test_out_001_system_prompt_leak_detection_exists(self, output_compliance_spec):
        """OUT-001 规则应存在且配置正确。"""
        rules = output_compliance_spec["pattern_rules"]
        out_001 = next(r for r in rules if r["id"] == "OUT-001")
        assert out_001["rule_type"] == "similarity"
        assert out_001["threshold"] == 0.6
        assert out_001["on_violation"] == "block_and_alert"
        assert out_001["error_code"] == "COMPLIANCE_PROMPT_LEAK"

    def test_out_002_cross_user_data_leak_exists(self, output_compliance_spec):
        """OUT-002 规则应存在且配置正确。"""
        rules = output_compliance_spec["pattern_rules"]
        out_002 = next(r for r in rules if r["id"] == "OUT-002")
        assert out_002["rule_type"] == "similarity"
        assert out_002["threshold"] == 0.5
        assert out_002["on_violation"] == "block_and_redact"
        assert out_002["error_code"] == "COMPLIANCE_CROSS_USER_LEAK"

    def test_out_003_pii_patterns(self, output_compliance_spec):
        """OUT-003 应包含银行卡号、手机号、身份证号的正则模式。"""
        rules = output_compliance_spec["pattern_rules"]
        out_003 = next(r for r in rules if r["id"] == "OUT-003")

        patterns = out_003["patterns"]
        assert len(patterns) >= 3, "Should have at least 3 PII patterns"
        # 银行卡号 (15-19 位)
        assert any("15,19" in p for p in patterns), "Missing bank card pattern"
        # 手机号 (11 位)
        assert any("11" in p for p in patterns), "Missing phone number pattern"
        # 身份证号
        assert any("身份证" in patterns[2] or "18" in patterns[2] for p in patterns), (
            "Missing ID card pattern"
        )
        assert out_003["on_violation"] == "redact"


class TestOutputComplianceSemanticRules:
    """OUT-SEM-001 语义规则校验。"""

    def test_out_sem_001_harmful_content_exists(self, output_compliance_spec):
        """OUT-SEM-001 应存在且配置正确。"""
        rules = output_compliance_spec["semantic_rules"]
        out_sem = next(r for r in rules if r["id"] == "OUT-SEM-001")
        assert out_sem["model"] == "local-safety-classifier-v3"
        assert out_sem["threshold"] == 0.9
        assert out_sem["on_violation"] == "block_and_alert"
        assert out_sem["error_code"] == "COMPLIANCE_HARMFUL_CONTENT"
