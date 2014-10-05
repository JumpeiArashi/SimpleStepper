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
    'security_group_defines',
    default=dict(),
    help='Target security group allow rule defines'
)
tornado.options.define(
    'development',
    default=False,
    help='If you are developer, set true to this option.'
)


# utils
def parse_security_groups(conn, security_group_ids):
    """
    Parse raw security group values with following format (json like).
    {
      "results": [
        {
          "name": "security-group01",
          "id": "sg-XXXXXXXX",
          "rules": [
            {
              "source": "127.0.0.1/32",
              "protocol": "tcp",
              "port": "22 - 22"
            },
            {
              "source": "127.0.0.1/32",
              "protocol": "tcp",
              "port": "80 - 80"
            }
          }
        ]
      ]
    }

    :param conn: AWS connection object
    :type conn: boto.ec2.EC2Connection
    :param security_group_ids: AWS security group ids
    :type security_group_ids: list
    :return: Parsed security group rules (json like)
    :rtype: dict
    """
    result = list()
    response = conn.get_all_security_groups(
        group_ids=security_group_ids
    )
    for raw_security_group in response:
        security_group = dict()
        security_group['name'] = raw_security_group.name
        security_group['id'] = raw_security_group.id
        security_group['rules'] = list()
        for rule in raw_security_group.rules:
            for entry in rule.grants:
                security_group['rules'].append(
                    {
                        'source': str(entry),
                        'protocol': rule.ip_protocol,
                        'port': '{0} - {1}'.format(
                            rule.from_port,
                            rule.to_port
                        )
                    }
                )
        result.append(security_group)
    result = {
        'results': result
    }
    return result


def get_remote_ip(request_obj):
    """
    :param request_obj:
    Client HTTP request object.
    In using this method in RequestHandler, this param will be 'self.request'
    :type request_obj: tornado.httpclient.HTTPRequest
    :return: Remote IP Address (Client IP Address).
    :rtype: str
    """
    x_forwarded_for = 'X-Forwarded-For'
    headers = [entry.title() for entry in request_obj.headers.keys()]
    if x_forwarded_for in headers:
        remote_ip = request_obj.headers.get(
            x_forwarded_for.upper(),
            request_obj.headers.get(
                x_forwarded_for.title()
            )
        )
    else:
        remote_ip = request_obj.remote_ip

    return remote_ip


def authorize_ips(conn, remote_ip, security_group_defines):
    """
    Add allow inbound rules to target security group ids.
    :param conn: AWS connection object
    :type conn: boto.ec2.EC2Connection
    :param remote_ip: Target IP Address. "Not" cider. e.g: 192.168.10.1
    :type remote_ip: str
    :param security_group_defines:
    Allow rule defines of target security groups.
    This param has dict type object which has
    "AWS security group ID" as key, and port number list as value.
    e.g:
    {
        "sg-XXXXXXXX": [
            {"tcp": 20},
            {"tcp": 80},
            {"tcp": 8080},
            {"tcp": 443}
        ],
        'sg-YYYYYYYY': [
            {"tcp": 5439},
            {"udp": 6380}
        ]
    }
    """
    target_security_group_ids = security_group_defines.keys()
    security_groups = conn.get_all_security_groups(
        group_ids=target_security_group_ids
    )
    for security_group in security_groups:
        for entry in security_group_defines[security_group.id]:
            for protocol, port in entry.items():
                security_group.authorize(
                    ip_protocol=protocol,
                    from_port=port,
                    to_port=port,
                    cidr_ip='{0}/32'.format(remote_ip)
                )

    return security_groups


# handlers
class SGHandler(tornado.web.RequestHandler):

    def initialize(self,
                   region_name,
                   aws_access_key_id,
                   aws_secret_access_key,
                   target_security_group_ids,
                   security_group_defines):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.target_security_group_ids = target_security_group_ids
        self.security_group_defines = security_group_defines
        self.conn = None

    def get_ec2_connection(self):
        if self.conn is None:
            self.conn = boto.ec2.connect_to_region(
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )

    def get(self):
        try:
            self.get_ec2_connection()
            parsed_security_groups = parse_security_groups(
                conn=self.conn,
                security_group_ids=self.security_group_defines.keys()
            )
            self.finish(json.dumps(parsed_security_groups))
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
            remote_ip = get_remote_ip(request_obj=self.request)
            if remote_ip is None:
                self.set_status(httplib.INTERNAL_SERVER_ERROR)
                self.finish(
                    {
                        'status_code': self.get_status(),
                        'message': 'Sorry, could not get Your IP Address.'
                    }
                )

            self.get_ec2_connection()
            authorize_ips(
                conn=self.conn,
                remote_ip=remote_ip,
                security_group_defines=self.security_group_defines
            )
            message = (
                'Your IP address {ip} is appended to {sg}.'
                ''.format(
                    ip=remote_ip,
                    sg=self.security_group_defines.keys()
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
            self.get_ec2_connection()
            results = list()
            current_sgs = self.conn.get_all_security_groups(
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


class DevelopmentSGHandler(
    tornado_cors.CorsMixin,
    SGHandler
):
    CORS_ORIGIN = '*'


def main():
    tornado.options.parse_command_line()
    if os.path.exists(tornado.options.options.config_file):
        tornado.options.parse_config_file(tornado.options.options.config_file)
    else:
        raise OSError('{0}: No such file or directory.')

    # handler options
    host_pattern = r'.*'

    SIMPLE_STEPPER_APP = tornado.web.Application()
    if not tornado.options.options.development:
        SIMPLE_STEPPER_APP.add_handlers(
            host_pattern=host_pattern,
            host_handlers=[
                (
                    r'/api/inboundRules', SGHandler,
                    {
                        "region_name":
                            tornado.options.options.region_name,
                        "aws_access_key_id":
                            tornado.options.options.aws_access_key_id,
                        "aws_secret_access_key":
                            tornado.options.options.aws_secret_access_key,
                        "target_security_group_ids":
                            tornado.options.options.target_security_group_ids,
                        "security_group_defines":
                            tornado.options.options.security_group_defines
                    }
                )
            ]
        )
    else:
        SIMPLE_STEPPER_APP.add_handlers(
            host_pattern=host_pattern,
            host_handlers=[
                (
                    r'/api/inboundRules', DevelopmentSGHandler,
                    {
                        "region_name":
                            tornado.options.options.region_name,
                        "aws_access_key_id":
                            tornado.options.options.aws_access_key_id,
                        "aws_secret_access_key":
                            tornado.options.options.aws_secret_access_key,
                        "target_security_group_ids":
                            tornado.options.options.target_security_group_ids,
                        "security_group_defines":
                            tornado.options.options.security_group_defines
                    }
                )
            ]
        )
    SIMPLE_STEPPER = tornado.httpserver.HTTPServer(
        SIMPLE_STEPPER_APP
    )
    SIMPLE_STEPPER.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
