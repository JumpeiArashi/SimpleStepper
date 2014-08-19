#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SimpleStepper backend main script.
"""

import httplib

import boto.ec2
import boto.exception
import tornado.options
import tornado.web
import tornado.ioloop


# command line options
tornado.options.define(
    'port',
    default=8080,
    help='Listen port number.'
)
tornado.options.define(
    'region_name',
    default='us-east-1',
    help='AWS region name.',
    group='AWS credential'
)
tornado.options.define(
    'aws_access_key_id',
    default='',
    help='AWS access key id.',
    group='AWS credential'
)
tornado.options.define(
    'aws_secret_access_key',
    default='',
    help='AWS secret access key.',
    group='AWS credential'
)
tornado.options.define(
    'target_security_group_ids',
    default=list(),
    help='Target security group ids of "SimpleStepper".'
)
tornado.options.define(
    'keep_security_group_elements',
    default=list(),
    help='Specified keeping security group entries.'
)


# handlers
class SGHandler(tornado.web.RequestHandler):

    def initialize(self,
                   region_name,
                   aws_access_key_id,
                   aws_secret_access_key,
                   target_security_group_ids,
                   keep_security_group_elements):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.target_security_group_ids = target_security_group_ids
        self.keep_security_group_elements = keep_security_group_elements

    def get(self):
        result = dict()
        try:
            conn = boto.ec2.connect_to_region(
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            response = conn.get_all_security_groups(
                group_ids=self.target_security_group_ids
            )
        except boto.exception.EC2ResponseError as exception:
            self.set_status(httplib.UNAUTHORIZED)
            self.write(
                {
                    'status_code': self.get_status(),
                    'message': exception.error_message
                }
            )
        except Exception as error:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.write(
                {
                    'status_code': self.get_status(),
                    'message': error.__str__()
                }
            )



# dispatch URLs
SIMPLE_STEPPER = tornado.web.Application([
    (
        r"/allowAllIPs", SGHandler,
        {
            "region_name": tornado.options.options.region_name,
            "aws_access_key_id": tornado.options.options.aws_access_key_id,
            "aws_secret_access_key":
            tornado.options.options.aws_secret_access_key,
            "target_security_group_ids":
            tornado.options.options.target_security_group_ids,
            "keep_security_group_elements":
            tornado.options.options.keep_security_group_elements,
        }
    )
])


if __name__ == '__main__':
    SIMPLE_STEPPER.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()