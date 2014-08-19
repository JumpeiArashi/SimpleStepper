#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SimpleStepper backend main script.
"""

import os
import json

import boto.ec2
import tornado.web
import tornado.ioloop

CONFIG_FILE_PATHS = [
    './config.json',
    '/etc/SimpleStepper/config.json',
    '/opt/SimpleStepper/config.json',
]

CONFIG = {
    'PORT': 8080,
    'REGION_NAME': None,
    'AWS_ACCESS_KEY_ID': None,
    'AWS_SECRET_ACCESS_KEY': None,
    'TARGET_SECURITY_GROUP_IDS': list(),
    'KEEP_SECURITY_GROUP_ELEMENTS': list(),
}


# handlers
class SGHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.region_name = CONFIG['REGION_NAME']
        self.aws_access_key_id = CONFIG['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = CONFIG['AWS_SECRET_ACCESS_KEY']
        self.target_security_group_ids = CONFIG['TARGET_SECURITY_GROUP_IDS']
        self.keep_elements = CONFIG['KEEP_SECURITY_GROUP_ELEMENTS']

    def get(self):
        conn = boto.ec2.connect_to_region(
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        result = dict()
        return conn.get_all_security_groups(
            group_ids=self.target_security_group_ids
        )


# dispatch URLs
SIMPLE_STEPPER = tornado.web.Application([
    (r"/allowAllIPs", SGHandler)
])


# utilities
class SimpleStepperException(BaseException):
    def __init__(self, message):
        super(SimpleStepperException, self).__init__(message)


def validate_config(config):
    checking_keys = [
        'region_name',
        'aws_access_key_id',
        'aws_secret_access_key',
        'target_security_group_ids',
        'keep_security_group_elements',
    ]
    for entry in checking_keys:
        if not entry in [element.lower() for element in config.keys()]:
            raise SimpleStepperException(
                '{0} is require parameter in configuration file.'
                ''.format(entry)
            )
    return True


def import_config_json(checking_paths):
    result = dict()
    flag = False

    for entry in checking_paths:
        if os.path.exists(entry):
            flag = True
            with open(entry) as config_json:
                config_json = json.loads(config_json.read())
            for key, value in config_json.iteritems():
                result[key.upper()] = value
            break

    if not flag:
        raise SimpleStepperException(
            '"config.json" does not exist!!!'
        )
    return result

if __name__ == '__main__':
    CONFIG.update(import_config_json(CONFIG_FILE_PATHS))
    validate_config(CONFIG)
    SIMPLE_STEPPER.listen(CONFIG['PORT'])
    tornado.ioloop.IOLoop.instance().start()