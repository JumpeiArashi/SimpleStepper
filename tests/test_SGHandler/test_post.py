#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json
import logging

import nose.tools
import tornado.httpclient
import tornado.testing

import simple_stepper

import tests.test_SGHandler.base


class MockHttpRequest(object):

    def __init__(self, headers=None, remote_ip='10.0.0.254'):
        if headers is None:
            self.headers = dict()
        self.remote_ip = remote_ip


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

    #Utils for POST method
    def test_get_remote_ip_no_reverse_proxy(self):
        global_ip = '192.192.192.192/32'
        request = tornado.httpclient.HTTPRequest(
            url=self.test_inbound_rules_url
        )
        setattr(request, 'remote_ip', global_ip)
        remote_ip = simple_stepper.get_remote_ip(request_obj=request)
        logging.debug(remote_ip)

        nose.tools.eq_(
            global_ip,
            remote_ip
        )

    #Utils for POST method
    def test_get_remote_ip_from_x_forwarded_for(self):
        global_ip = '192.192.192.192/32'
        request = tornado.httpclient.HTTPRequest(
            url=self.test_inbound_rules_url,
            headers={
                'X-Forwarded-For': global_ip
            }
        )
        remote_ip = simple_stepper.get_remote_ip(request_obj=request)
        logging.debug(remote_ip)

        nose.tools.eq_(
            global_ip,
            remote_ip
        )

