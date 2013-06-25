#!/bin/env python

import boto
import time
ec2 = boto.connect_ec2()
for uid in range(1,20):
    keyname = "puppet%02d" % uid
    key_pair = ec2.create_key_pair(keyname)
    key_pair.save('~/.ssh')
    time.sleep(1)


