#!/bin/env python

import sys
import boto
import time
import yaml
from pprint import pprint
import inspect
import route53
from datetime import datetime

def logger(mess):
    dt = datetime.now()
    sys.stdout.write(dt.strftime('%Y%m%d %H:%M:%S '))
    sys.stdout.write(mess)
    sys.stdout.write('\n')
    sys.stdout.flush()

def get_zid(r53,zone):

    response = r53.get_all_hosted_zones()
    for zinfo in response['ListHostedZonesResponse']['HostedZones']:
        zname = zinfo['Name']
        zid = zinfo['Id'].split("/")[-1]
        if zone == zname:
            return zid
    #route53.change_record(r53,zid,hostname,'CNAME',rrname,ttl=300)


cfn = boto.connect_cloudformation()

#for s in cfn.list_stacks():
    #pprint(pprint(s.__dict__))

r53 = boto.connect_route53()
z = 'puppetclass.taoslab.com.'
zid = get_zid(r53,z)
logger("Zone: "+z+" Id: "+zid)

for uid in range(1,2):
    stackname = 'puppet%02dStack' % uid
    stack = cfn.describe_stacks(stackname)
    for pair in stack[0].outputs:
        logger (stackname + ": " + pair.key + "=" + pair.value)
        if 'web' in pair.key:
            host = 'web%02d' % uid
            fqdn = host + '.puppetclass.taoslab.com.'
            logger(fqdn+' ('+pair.value+')')
            try:
                route53.add_record(r53,zid,fqdn,'A',pair.value, ttl=300)
            except:
                route53.change_record(r53,zid,fqdn,'A',pair.value, ttl=300)
        if 'jump' in pair.key:
            host = 'jump%02d' % uid
            fqdn = host + '.puppetclass.taoslab.com.'
            logger(fqdn+' ('+pair.value+')')
            try:
                route53.add_record(r53,zid,fqdn,'A',pair.value, ttl=300)
            except:
                route53.change_record(r53,zid,fqdn,'A',pair.value, ttl=300)

    time.sleep(1)

  
