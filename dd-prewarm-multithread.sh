#!/bin/bash
# the device name, specified as xvdx,
# and thread count are specified as command line arguments.
DEV_NAME=$1
THREAD_COUNT=$2

# We find the number of bytes on the device,
# and divide that by 512K to find the number of blocks.
BYTES=$(lsblk --bytes | grep $DEV_NAME | awk '{print $4}')
BLOCKS=$(expr $BYTES / 524288)

# The blocks are divided by the number of threads, so each
# thread does the same amount of work.
SKIP_SIZE=$(expr $BLOCKS / $THREAD_COUNT)

# Each thread is given an equal amount of work, and the dd reading begins.
i=0
while [ $i -lt $THREAD_COUNT ]
	do
		sudo dd if=/dev/$DEV_NAME of=/dev/null bs=512K count=$SKIP_SIZE skip=$(expr $i \* $SKIP_SIZE) &
		i=$[$i+1]
done