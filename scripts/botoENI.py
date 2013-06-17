#!/bin/env python

import sys
import boto
import time
import yaml
from pprint import pprint

ec2 = boto.connect_ec2()

for r in ec2.get_all_network_interfaces():
    # pprint(r.__dict__)
    if hasattr(r,'publicIp'):
        #print r.private_ip_address
        #print r.publicIp
        #print r.id
        #print r.status
        sys.stdout.write('Elastic Ip is ' + r.id + '\n')
    else:
        if r.status == 'available':
            print r.id," in subnet ",r.subnet_id
            print "Available private subnet eni ",r.id
            # ec2.delete_network_interface(r.id)

subnet = 'subnet-8ee76ce7'

sys.stdout.write('Creating Network Interface in Subnet ' + subnet + '\n')

nic = ec2.create_network_interface(subnet)
print nic.id

# Wait a minute or two while it boots
found = False
while found == False:
    sys.stdout.write('Checking if done\n')
    for r in ec2.get_all_network_interfaces():
        print r.id," - ",nic.id
        if r.id == nic.id:
            found = True
            break
    if found == True:
        break
    else:
        time.sleep(10)
pprint(r.__dict__)

