import unittest
from nose.tools import raises, assert_equal, assert_true, assert_false

# import parliament
from parliament import analyze_policy_string, is_arn_match
from parliament.statement import is_valid_region, is_valid_account_id


class TestResourceFormatting(unittest.TestCase):
    """Test class for resource formatting"""

    def test_resource_bad(self):
        policy = analyze_policy_string(
            """{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "s3:listallmybuckets",
        "Resource": "s3"}}"""
        )
        assert_equal(len(policy.findings), 1)

    def test_resource_good(self):
        policy = analyze_policy_string(
            """{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "s3:getobject",
        "Resource": "arn:aws:s3:::my_corporate_bucket/*"}}"""
        )
        print(policy.findings)
        assert_equal(len(policy.findings), 0)

    def test_is_valid_region(self):
        assert_true(is_valid_region(""), "Empty regions are allowed")
        assert_true(is_valid_region("us-east-1"), "This region is allowed")
        assert_false(is_valid_region("us-east-1f"), "This is an AZ, not a region")
        assert_false(is_valid_region("us-east-*"), "No regexes in regions")
        assert_false(is_valid_region("us"), "Not a valid region")
        assert_false(is_valid_region("us-east-1-f"), "Not a valid region")
        assert_true(is_valid_region("us-gov-east-1"), "This is a valid govcloud region")

    def test_is_valid_account_id(self):
        assert_true(is_valid_account_id(""), "Empty account id is allowed")
        assert_true(is_valid_account_id("000000001234"), "This account id is allowed")
        assert_false(is_valid_account_id("abc"), "Account id must have 12 digits")
        assert_false(
            is_valid_account_id("00000000123?"), "Regex not allowed in account id"
        )

    def test_arn_match(self):
        assert_true(is_arn_match("object", "arn:*:s3:::*/*", "arn:*:s3:::*/*"))
        assert_true(is_arn_match("object", "*", "arn:*:s3:::*/*"))
        assert_true(is_arn_match("object", "arn:*:s3:::*/*", "*"))
        assert_true(is_arn_match("object", "arn:*:s3:::*/*", "arn:aws:s3:::*personalize*"))
        assert_true(is_arn_match("bucket", "arn:*:s3:::mybucket", "arn:*:s3:::mybucket"))
        assert_false(
            is_arn_match("bucket", "arn:*:s3:::mybucket", "arn:*:s3:::mybucket/*"),
            "Bucket and object types should not match",
        )
        assert_false(
            is_arn_match("object", "arn:*:s3:::*/*", "arn:aws:s3:::examplebucket"),
            "Object and bucket types should not match",
        )
        assert_true(is_arn_match("bucket", "arn:*:s3:::mybucket*", "arn:*:s3:::mybucket2"))
        assert_true(is_arn_match("bucket", "arn:*:s3:::*", "arn:*:s3:::mybucket2"))
        assert_false(
            is_arn_match("object", "arn:*:s3:::*/*", "arn:aws:logs:*:*:/aws/cloudfront/*")
        )
        assert_false(
            is_arn_match("object", "arn:aws:s3:::*/*", "arn:aws:logs:*:*:/aws/cloudfront/*")
        )
        assert_true(
            is_arn_match("cloudfront", 
                "arn:aws:logs:*:*:/aws/cloudfront/*",
                "arn:aws:logs:us-east-1:000000000000:/aws/cloudfront/test",
            )
        )