#!/usr/bin/env python
"""

Replace the named stack in AWS for CI/CD testing of salt code.

"""

import sys
import os
import yaml
from optparse import OptionParser
from jinja2 import Environment, FileSystemLoader
import boto
from datetime import date, datetime
from pprint import pprint
import socket
import time
import route53


def render_jinja (jinja2file):

    TEMPLATE_DIR = os.path.dirname(jinja2file)
    BASENAME = os.path.basename(jinja2file)

    j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),trim_blocks=True)
    output = j2_env.get_template(BASENAME).render()
    return output


def get_last_stack(cfn, stack_name):
    stacks = []
    # Iterates the stack list and find the stack which we are looking for.
    for s in cfn.list_stacks():
        if stack_name in s.stack_name:
            stacks.append(s.stack_name)

    if len(stacks) == 0:
        raise ValueError("Oops no Stacks "+stack_name)

    return sorted(stacks)[-1]


def get_next_stack(cfn, stack_name):

    d = date.today()
    today = d.strftime("%Y%m%d")
    try:
        laststack = get_last_stack(cfn,stack_name)
        (tdate,tserial) = laststack[len(stack_name):].split('-')
    except:
        (tdate, tserial) = (today,1)

    if tdate != today:
        nserial = 1
    else:
        nserial = int(tserial)+1
    serial = "%02d" % nserial
    NEXTSTACK = stack_name+today+'-'+serial
    return NEXTSTACK


def get_id(cfn,stack,resource):
    r = cfn.describe_stack_resource(stack,resource)
    return r['DescribeStackResourceResponse']['DescribeStackResourceResult']['StackResourceDetail']['PhysicalResourceId']


def wait_for_stack(cfn,stack,status):

    done = False
    while not done:
        for s in cfn.list_stacks():
            if stack in s.stack_name and status == s.stack_status:
                done = True

        logger("Testing "+stack+" "+status)
        if done:
            logger("Stack "+stack+" "+status)
        else:
            time.sleep(15)


def test_hostname(hostname):
    try:
        ip = socket.gethostbyname(hostname)
    except socket.error:
        raise ValueError("Oops no hostname "+hostname)


def wait_for_www(hostname,port):
    test_hostname(hostname)
    ip = socket.gethostbyname(hostname)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    done = False
    while not done:
        result = sock.connect_ex((ip,port))
        if result == 0:
            logger("{0} port {1} Open!".format(hostname,port))
            done = True
        else:
            logger("Testing "+hostname+" port "+str(port))
            time.sleep(15)


def logger(mess):
    dt = datetime.now()
    sys.stdout.write(dt.strftime('%Y%m%d %H:%M:%S '))
    sys.stdout.write(mess)
    sys.stdout.write('\n')
    sys.stdout.flush()


def get_web_xface(ec2,id):
    reservations = ec2.get_all_instances(filters={'instance-id' : id})
    i = reservations[0].instances[0]
    return (i.networkInterfaceId,i.ip_address)


def get_available_eip(ec2):

    for r in ec2.get_all_network_interfaces():
        # pprint(r.__dict__)
        if hasattr(r,'publicIp') and r.status == 'available':
            return (r.id,r.private_ip_address,r.publicIp)
    logger ("No Elastic IPs available for new web")


def create_xface(ec2,subnet):
    nic = ec2.create_network_interface(subnet)
    # Wait a minute or two while it boots
    found = False
    while found == False:
        for r in ec2.get_all_network_interfaces():
            if r.id == nic.id:
                found = True
                break
        if found == True:
            break
        else:
            time.sleep(10)
    logger("New eip "+r.id+" Created")
    return (r.id,r.private_ip_address)


def update_cname_by_ip(r53,ip,hostname):

    response = r53.get_all_hosted_zones()
    zinfo = response['ListHostedZonesResponse']['HostedZones'][0]
    zid = zinfo['Id'].split("/")[-1]

    response = r53.get_all_rrsets(zid)

    for record in response:
        for rr in record.resource_records:
            if rr == ip:
                rrname = record.name

    if hostname[-1] != '.':
        hostname += '.'

    route53.change_record(r53,zid,hostname,'CNAME',rrname,ttl=300)


def delete_unused_eip(ec2):

    for r in ec2.get_all_network_interfaces():
        # pprint(r.__dict__)
        print r.private_ip_address
        print r.id
        print r.status
        if hasattr(r,'publicIp'):
            logger('Available EIP ' + r.publicIp)
        else:
            if r.status == 'available':
                logger ('Deleting unused ENI ' + r.id)
                ec2.delete_network_interface(r.id)


def main():
    parser = OptionParser(usage="usage: %prog [options] stackname template")
    parser.add_option('-d','--debug',help="Debug level",default=0)
    parser.add_option('-g','--user',help="VPN User",default='user-00')
    (options,args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    (stackin, templatein) = args

    try:
        templin = open (templatein,'r').read()
    except IOError:
        sys.stderr.write("File "+templatein+" Does not exist!\n")
        parser.print_help()
        sys.exit(1)

    NEXTSTACK = options.user + "Stack"

    cfn = boto.connect_cloudformation()

    cfn_template = render_jinja(templatein)

    try:
        cfn.validate_template(cfn_template)
    except boto.exception.BotoServerError, e:
        print e.error_message

    ec2 = boto.connect_ec2()

    params = [
        ('UserName', options.user),
        ('KeyName' , options.user),
        #('KeyName' , "user-00-key"),
    ]

    try:
        cfn.create_stack(NEXTSTACK,template_body=cfn_template,parameters=params)
    except boto.exception.BotoServerError, e:
        print e.error_message
        sys.exit(2)
    else:
        wait_for_stack(cfn,NEXTSTACK,'CREATE_COMPLETE')

if __name__ == "__main__":
    main()

