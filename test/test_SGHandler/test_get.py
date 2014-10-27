#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json
import logging

import boto.ec2
import moto
import nose.tools

import simple_stepper

import test.test_SGHandler.base


class TestCase(test.test_SGHandler.base.BaseSGHandlerTestCase):

    def test_unauthorized(self):
        """
        This case when failed to AWS authentication.
        """
        self.http_client.fetch(
            self.get_url(self.test_inbound_rules_url),
            self.stop
        )
        response = self.wait()
        logging.debug(response)
        json_response = json.loads(response.body)

        self.assertEqual(response.code, httplib.BAD_REQUEST)
        self.assertEqual(json_response.get('status_code'), httplib.BAD_REQUEST)


class TestUtilsForGetMethod(object):

    @moto.mock_ec2
    def test_parse_security_groups(self):
        conn = boto.ec2.connect_to_region(
            region_name='us-east-1'
        )
        name = 'TESTING_SECURITY_GROUP'
        security_group = conn.create_security_group(
            name=name,
            description='Testing security group'
        )

        protocol = 'tcp'
        port = 22
        cidr_ip = '192.192.192.192/32'
        checked = {
            'results': [
                {
                    'name': name,
                    'id': security_group.id,
                    'rules': [
                        {
                            'source': cidr_ip,
                            'protocol': protocol,
                            'port': '{port} - {port}'.format(port=port)
                        }
                    ]
                }
            ]
        }
        logging.debug(checked)

        security_group.authorize(
            ip_protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_ip=cidr_ip
        )

        result = simple_stepper.parse_security_groups(
            conn=conn,
            security_group_ids=[security_group.id]
        )
        logging.debug(result)
        nose.tools.eq_(
            result,
            checked
        )
