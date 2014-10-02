#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
import tornado.web

import simple_stepper

class BaseSGHandlerTestCase(tornado.testing.AsyncHTTPTestCase):

    test_inbound_rules_url = '/test/api/inboundRules'

    def get_app(self):
        return tornado.web.Application(
            handlers=[
                (
                    self.test_inbound_rules_url, simple_stepper.SGHandler,
                    {
                        'region_name': 'us-east-1',
                        'aws_access_key_id': 'HOGEHOGE',
                        'aws_secret_access_key': 'FUGAFUGA',
                        'target_security_group_ids': ['sg-HOGEHOGE'],
                        'security_group_defines': {
                            'sg-XXXXXXXX': [
                                {'tcp': 22}
                            ]
                        }
                    }
                )
            ]
        )
