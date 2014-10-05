#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json
import logging

import boto.ec2
import moto
import nose.tools

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
            method='DELETE'
        )
        response = self.wait()

        flag = True
        messages = list()

        if response.code != httplib.BAD_REQUEST:
            flag = False
            messages.append(
                'Status Code is not {0}.'.format(response.code)
            )

        if json.loads(response.body).get('status_code') != httplib.BAD_REQUEST:
            flag = False
            messages.append('Status Code in message body is not 400.')

        nose.tools.ok_(
            flag,
            msg='\n'.join(messages)
        )

    @moto.mock_ec2
    def test_revoke_all_rules(self):
        conn = boto.ec2.connect_to_region(
            region_name='us-east-1'
        )
        target_security_group_ids = list()
        security_group = conn.create_security_group(
            name='TESTING_SECURITY_GROUP_1',
            description='testing security group 1'
        )
        target_security_group_ids.append(security_group.id)
        security_group.authorize(
            ip_protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_ip='192.192.192.192/32'
        )
        logging.debug(security_group.rules)
        self.assertEqual(len(security_group.rules), 1)

        results = simple_stepper.revoke_all_rules(
            conn=conn,
            security_group_ids=target_security_group_ids
        )
        logging.debug(results)
        self.assertEqual(len(results['results']), 1)
        security_group = conn.get_all_security_groups(
            group_ids=target_security_group_ids
        )[0]
        self.assertEqual(len(security_group.rules), 0)
