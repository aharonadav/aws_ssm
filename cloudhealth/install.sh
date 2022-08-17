#!/bin/bash
echo 'Installing CloudHealthAgent on Amazon Linux...'
sudo wget https://s3.amazonaws.com/remote-collector/agent/v24/install_cht_perfmon.sh -O install_cht_perfmon.sh;
sudo sh install_cht_perfmon.sh 24 {{ssm:cloudhealth_key}} aws;