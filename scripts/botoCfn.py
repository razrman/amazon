#!/bin/env python

import sys
import boto
import time
import yaml
from pprint import pprint

cfn = boto.connect_cloudformation()

stacks = []
for s in cfn.list_stacks():
    pprint(pprint(s.__dict__))


