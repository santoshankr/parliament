import unittest
from nose.tools import (
    raises,
    assert_equal,
    assert_true,
    assert_false,
    assert_count_equal,
)

from parliament.statement import expand_action


class TestActionExpansion(unittest.TestCase):
    """Test class for expand_action function"""

    def test_expand_action_no_expansion(self):
        expanded_actions = expand_action("s3:listallmybuckets")
        assert_count_equal(
            expanded_actions, [{"service": "s3", "action": "ListAllMyBuckets"}]
        )

    def test_expand_action_with_expansion(self):
        expanded_actions = expand_action("s3:listallmybucke*")
        assert_count_equal(
            expanded_actions, [{"service": "s3", "action": "ListAllMyBuckets"}]
        )

    def test_expand_action_with_casing(self):
        expanded_actions = expand_action("iAm:li*sTuS*rs")
        assert_count_equal(
            expanded_actions, [{"service": "iam", "action": "ListUsers"}]
        )

    def test_expand_action_with_expansion_for_prefix_used_multiple_times(self):
        expanded_actions = expand_action("ses:Describe*")
        assert_count_equal(
            expanded_actions,
            [
                {"service": "ses", "action": "DescribeActiveReceiptRuleSet"},
                {"service": "ses", "action": "DescribeConfigurationSet"},
                {"service": "ses", "action": "DescribeReceiptRule"},
                {"service": "ses", "action": "DescribeReceiptRuleSet"},
            ],
        )

    def test_expand_action_with_permission_only_action(self):
        # There are 17 privileges list as "logs.CreateLogDelivery [permission only]"
        expanded_actions = expand_action("logs:GetLogDelivery")
        assert_count_equal(
            expanded_actions, [{"service": "logs", "action": "GetLogDelivery"}]
        )

    def test_exception_malformed(self):
        try:
            expand_action("malformed")
            assert False
        except ValueError as e:
            assert True

    def test_exception_bad_service(self):
        try:
            expand_action("333:listallmybuckets")
            assert False
        except ValueError as e:
            assert True

    def test_exception_bad_action(self):
        try:
            expand_action("s3:zzz")
            assert False
        except ValueError as e:
            assert True

    def test_exception_bad_expansion(self):
        try:
            expand_action("s3:zzz*")
            assert False
        except ValueError as e:
            assert True
