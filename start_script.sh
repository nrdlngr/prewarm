#!/bin/bash
yum install -y fio
cat config.txt | while read line
do 
	python prewarm.py $line
	sleep 15
done