#!/bin/bash
yum install -y git
git clone https://github.com/nrdlngr/prewarm.git /tmp/prewarm
cd /tmp/prewarm
/bin/bash start_script.sh