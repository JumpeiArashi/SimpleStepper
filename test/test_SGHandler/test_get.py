#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json

import nose.tools
import tornado.testing
import simple_stepper


class TestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return simple_stepper.Application()

    def test_unauthorized(self):
        """
        This case when failed to AWS authentication.
        """
        self.http_client.fetch(self.get_url('/api/inboundRules'), self.stop)
        response = self.wait()

        flag = True
        messages = list()

        if response.code != httplib.BAD_REQUEST:
            flag = False
            messages.append('Status Code is not 400.')

        if json.loads(response.body).get('status_code') != httplib.BAD_REQUEST:
            flag = False
            messages.append('Status Code in message body is not 400.')

        nose.tools.ok_(
            flag,
            msg='\n'.join(messages)
        )
