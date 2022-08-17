#!/bin/bash
echo 'Uninstalling CloudHealthAgent on Amazon Linux...'
sudo wget -O - https://s3.amazonaws.com/remote-collector/agent/uninstall_cht_perfmon.sh | sudo sh