#!/bin/env python

import time
from os import system
from subprocess import call

for uid in range(1,2):

    user = "%02d" % uid
    keyname = "/home/ec2-user/.ssh/puppet%02d.pem" % uid
    jump = "jump"+user+".puppetclass.taoslab.com"

    c1 = "scp -q -i " + keyname + " " + keyname + " " + jump + ":~/.ssh/id_rsa"
    print c1
    system(c1)

    c1 = "ssh -i " + keyname + " " + jump + " 'chmod 600 ~/.ssh/id_rsa'" 
    print c1
    system(c1)

    for vm in ['web', 'dns', 'puppet', 'db']:
        c1 = "ssh -i " + keyname + " " + jump + " 'scp -o StrictHostKeyChecking=no ~/.ssh/id_rsa " + vm + ":~/.ssh/id_rsa'"
        print c1
        system(c1)
