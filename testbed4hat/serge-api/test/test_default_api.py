# coding: utf-8

"""
    Serge API

    API documentation for Serge server  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

import serge_client
from serge_client.api.default_api import DefaultApi  # noqa: E501
from serge_client.rest import ApiException


class TestDefaultApi(unittest.TestCase):
    """DefaultApi unit test stubs"""

    def setUp(self):
        self.api = DefaultApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_ip_get(self):
        """Test case for get_ip_get

        Get IP address  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
