#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json
import logging

import tests.test_SGHandler.base


class TestCase(tests.test_SGHandler.base.BaseSGHandlerTestCase):

    def test_unauthorized(self):
        """
        This case when failed to AWS authentication.
        """
        self.http_client.fetch(
            self.get_url(self.test_inbound_rules_url),
            self.stop,
            method='POST',
            body=json.dumps({})
        )
        response = self.wait()
        logging.debug(response)
        json_response = json.loads(response.body)

        self.assertEqual(response.code, httplib.BAD_REQUEST)
        self.assertEqual(json_response.get('status_code'), httplib.BAD_REQUEST)
