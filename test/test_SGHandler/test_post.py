#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json
import logging

import boto.ec2
import moto
import moto.ec2
import nose.tools
import tornado.httpclient
import tornado.testing

import simple_stepper

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

    #Utils for POST method
    def test_get_remote_ip_no_reverse_proxy(self):
        global_ip = '192.192.192.192'
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

    def test_get_remote_ip_from_x_forwarded_for(self):
        global_ip = '192.192.192.192'
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

    @moto.mock_ec2
    def test_authorize_ips(self):
        remote_ip = '192.192.192.192'
        security_group_defines = dict()
        conn = boto.ec2.connect_to_region(
            region_name='us-east-1'
        )
        security_group_1 = conn.create_security_group(
            name='TESTING_SECURITY_GROUP_1',
            description='testing security group 1'
        )
        security_group_2 = conn.create_security_group(
            name='TESTING_SECURITY_GROUP_2',
            description='testing security group 2'
        )
        security_group_defines[security_group_1.id] = [
            {'tcp': 22},
            {'tcp': 80}
        ]
        security_group_defines[security_group_2.id] = [
            {'tcp': 3306},
            {'udp': 8080},
            {'udp': 11211}
        ]
        security_groups = simple_stepper.authorize_ips(
            conn=conn,
            remote_ip=remote_ip,
            security_group_defines=security_group_defines
        )

        for entry in security_groups:
            logging.debug(entry.__dict__)

            security_group_defines_port_numbers = list()
            security_group_defines_protocols = list()
            for define in security_group_defines[entry.id]:
                security_group_defines_port_numbers.extend(
                    define.values()
                )
                security_group_defines_protocols.extend(
                    define.keys()
                )
            for rule in entry.rules:
                self.assertTrue(
                    rule.ip_protocol in security_group_defines_protocols
                )
                self.assertTrue(
                    rule.from_port in security_group_defines_port_numbers
                )
                self.assertTrue(
                    rule.to_port in security_group_defines_port_numbers
                )

            if entry.name == 'TESTING_SECURITY_GROUP_1':
                logging.debug(entry.__dict__)
                self.assertEqual(
                    len(entry.rules),
                    len(security_group_defines[security_group_1.id])
                )

            elif entry.name == 'TESTING_SECURITY_GROUP_2':
                logging.debug(entry.__dict__)
                self.assertEqual(
                    len(entry.rules),
                    len(security_group_defines[security_group_2.id])
                )
            else:
                raise Exception(
                    (
                        'Maybe test got unexpected security group {0}.'
                        ''.format(entry.name)
                    )
                )
