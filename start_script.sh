#!/bin/bash
sudo yum install -y fio
cat config.txt | while read line
do 
	sudo python prewarm.py $line &
	sleep 15
done