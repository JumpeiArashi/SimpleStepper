#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SimpleStepper backend main script.
"""

import httplib
import json
import os

import boto.ec2
import boto.exception
import tornado.httpserver
import tornado.options
import tornado.web
import tornado.ioloop
import tornado_cors


# define options
tornado.options.define(
    'config_file',
    default='./config.py',
    help='Configuration file path.'
)
tornado.options.define(
    'port',
    default=8080,
    help='Listen port number.'
)
tornado.options.define(
    'region_name',
    default='us-east-1',
    help='AWS region name.'
)
tornado.options.define(
    'aws_access_key_id',
    default='AWS_ACCESS_KEY_ID',
    help='AWS access_key_id.'
)
tornado.options.define(
    'aws_secret_access_key',
    default='AWS_SECRET_ACCESS_KEY',
    help='AWS secret_access_key.'
)
tornado.options.define(
    'target_security_group_ids',
    default=list(),
    help='Target security group ids.'
)
tornado.options.define(
    'development',
    default=False,
    help='If you are developer, set true to this option.'
)


# handlers
class SGHandler(tornado.web.RequestHandler):

    def initialize(self,
                   region_name,
                   aws_access_key_id,
                   aws_secret_access_key,
                   target_security_group_ids):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.target_security_group_ids = target_security_group_ids

    def get(self):
        result = list()
        try:
            conn = boto.ec2.connect_to_region(
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            response = conn.get_all_security_groups(
                group_ids=self.target_security_group_ids
            )
            for entry in response:
                result.append(
                    {
                        'name': entry.name,
                        'id': entry.id,
                        'rules': [
                            {
                                'source': element.grants.__str__(),
                                'port': '{0} - {1}'.format(
                                    element.from_port,
                                    element.to_port
                                )
                            }
                            for element in entry.rules
                        ]
                    }
                )
            result = {
                'results': result
            }
            self.finish(json.dumps(result))
        except boto.exception.EC2ResponseError as exception:
            self.set_status(httplib.BAD_REQUEST)
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': exception.error_message
                }
            )
        except Exception as exception:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': exception.__str__()
                }
            )

    def post(self):
        try:
            remote_ip = None
            if (
                'X-FORWARDED-FOR' in
                [entry.upper() for entry in self.request.headers.keys()]
            ):
                remote_ip = self.request.headers.get('X-FORWARDED-FOR')
            else:
                remote_ip = self.request.remote_ip

            if remote_ip is None:
                self.set_status(httplib.INTERNAL_SERVER_ERROR)
                self.finish(
                    {
                        'status_code': self.get_status(),
                        'message': 'Sorry, could not get Your IP Address.'
                    }
                )
            conn = boto.ec2.connect_to_region(
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            response = conn.get_all_security_groups(
                group_ids=self.target_security_group_ids
            )
            for entry in response:
                entry.authorize(
                    ip_protocol='tcp',
                    from_port=22,
                    to_port=22,
                    cidr_ip=('{0}/32'.format(remote_ip))
                )
            message = (
                'Your IP {ip} is appended to {sg}'
                ''.format(
                    ip=remote_ip,
                    sg=tornado.options.options.target_security_group_ids
                )
            )
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': message
                }
            )

        except boto.exception.EC2ResponseError as exception:
            self.set_status(httplib.BAD_REQUEST)
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': exception.error_message
                }
            )

        except Exception as exception:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': exception.__str__()
                }
            )

    def delete(self):
        try:
            conn = boto.ec2.connect_to_region(
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            results = list()
            current_sgs = conn.get_all_security_groups(
                group_ids=self.target_security_group_ids
            )
            for sg in current_sgs:
                for rule in sg.rules:
                    for cidr_ip in rule.grants:
                        results.append(
                            {
                                'ip_protocol': rule.ip_protocol,
                                'from_port': rule.from_port,
                                'to_port': rule.to_port,
                                'cidr_ip': str(cidr_ip)
                            }
                        )
                        sg.revoke(
                            ip_protocol=rule.ip_protocol,
                            from_port=rule.from_port,
                            to_port=rule.to_port,
                            cidr_ip=cidr_ip
                        )
            self.finish(
                json.dumps({
                    'results': results
                })
            )

        except boto.exception.EC2ResponseError as exception:
            self.set_status(httplib.BAD_REQUEST)
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': exception.error_message
                }
            )

        except Exception as exception:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.finish(
                {
                    'status_code': self.get_status(),
                    'message': exception.__str__()
                }
            )


# dispatch URLs
class SimpleStepper(tornado.web.Application):
    def __init__(self):
        handlers = [
            (
                r"/api/inboundRules", SGHandler,
                {
                    "region_name":
                        tornado.options.options.region_name,
                    "aws_access_key_id":
                        tornado.options.options.aws_access_key_id,
                    "aws_secret_access_key":
                        tornado.options.options.aws_secret_access_key,
                    "target_security_group_ids":
                        tornado.options.options.target_security_group_ids
                }
            )
        ]
        settings = dict()
        super(SimpleStepper, self).__init__(handlers=handlers, **settings)


# development
class DevelopmentSimpleStepper(
    tornado_cors.CorsMixin,
    SimpleStepper
):
    CORS_ORIGIN = '*'


def main():
    tornado.options.parse_command_line()
    if os.path.exists(tornado.options.options.config_file):
        tornado.options.parse_config_file(tornado.options.options.config_file)
    else:
        raise OSError('{0}: No such file or directory.')

    if tornado.options.options.development:
        SIMPLE_STEPPER = tornado.httpserver.HTTPServer(
            DevelopmentSimpleStepper()
        )
    else:
        SIMPLE_STEPPER = tornado.httpserver.HTTPServer(SimpleStepper())
    SIMPLE_STEPPER.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
