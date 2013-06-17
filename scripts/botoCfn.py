#!/bin/env python

import sys
import boto
import time
import yaml
from pprint import pprint
import inspect

cfn = boto.connect_cloudformation()

stacks = []
#for s in cfn.list_stacks():
    #pprint(pprint(s.__dict__))
stack = cfn.describe_stacks('PuppetClassuser-01')
pprint( stack[0] )
pprint( inspect.getmembers(stack[0], predicate=inspect.ismethod) )
print stack[0].outputs
o = {}
for pair in stack[0].outputs:
    print pair.key
    print pair.value
