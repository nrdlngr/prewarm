#!/usr/bin/env python
import string
import boto.ec2
import requests
import time
import os
import glob
import sys

# Volume settings
volume_size = '100'
v_type = 'io1'
v_iops = '3000'
v_snapshot = 'snap-09a4397a'


# FIO settings
rw = 'randread'
bs = sys.argv[1]
iodepth = sys.argv[2]

def get_available_devices():
    # Build available device list
    possible_devices = []
    for device_letter in string.ascii_lowercase:
        device_name = 'xvd' + device_letter
        possible_devices.append(device_name)
    # Find attached devices
    attached_devices = []
    for device in glob.glob('/sys/block/*'):
        attached_devices.append(device.lstrip('/sys/block/'))
    # Remove attached devices from available devices
    available_devices = [ x for x in possible_devices if x not in attached_devices ]
    return available_devices

# Find AZ for instance
az = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone/').text
region = az[:-1]

# Get instance ID
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id/').text

# Make connection to EC2
conn = boto.ec2.connect_to_region(region)

# Create volume
vol = conn.create_volume(volume_size, az, volume_type=v_type, iops=v_iops, snapshot=v_snapshot)
#vol = conn.create_volume(volume_size, az, volume_type=v_type)
volume_id = vol.id

print "Creating a " + volume_size + " GiB " + v_type + " volume..."

curr_vol = conn.get_all_volumes([volume_id])[0]
print "Waiting for " + volume_id
while True:
    time.sleep(1)
    if curr_vol.update() == 'available':
        print "Volume ready"
        time.sleep(5)
        break

# Find available device names
available_devices = get_available_devices()
dev_name = available_devices[0]
# Attach volume
print "Attaching volume at " + dev_name
conn.attach_volume(volume_id, instance_id, dev_name)
print "Waiting for " + volume_id
while True:
    time.sleep(1)
    if curr_vol.update() == 'in-use':
        print "Volume attached"
        break

# Wait for the device to show up on the instance
while True:
    time.sleep(1)
    if os.path.islink('/sys/block/' + dev_name):
        break
        
# Run FIO
cmd = "fio --filename=/dev/" + dev_name + " --name warm --direct=1 --rw=" + rw + " --bs=" + bs + " --iodepth=" + iodepth + " --output=" + volume_id + "-" + rw + bs + "iodepth" + iodepth
print "Running command: "
print cmd
os.system(cmd)

print "Running second pass"
cmd = cmd + "(second_pass)"
os.system(cmd)


# Detach volume
conn.detach_volume(volume_id)
print "Detaching " + volume_id
while True:
    time.sleep(1)
    if curr_vol.update() == 'available':
        break

# Delete volume
print "Deleting " + volume_id
conn.delete_volume(volume_id)