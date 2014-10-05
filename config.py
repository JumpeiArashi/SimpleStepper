#!/usr/bin/env python
# -*- coding: utf-8 -*-

port = 8080
region_name = 'AWS_REGION_NAME'
aws_access_key_id = 'YOUR_AWS_ACCESS_KEY_ID'
aws_secret_access_key = 'YOUR_AWS_SECRET_ACCESS_KEY'
security_group_defines = {
    'sg-XXXXXXXX': [
        {'tcp': 22},
        {'tcp': 80}
    ],
    'sg-YYYYYYYY': [
        {'tcp': 3306},
        {'udp': 11211}
    ]
}
