
This article explain how you can easily deploy your CloudHealth agent using System Manager and ensure compliance of your installation using AWS State Manager.

At the end of the article you will have achieved the following goals:

Deploy CloudHealth agent Package on all platforms (Windows, Amazon Linux, Ubuntu)
Control and manage the correct state of your instances making sure CloudHealth agent is deployed everywhere on any instances even the new ones.

CloudHealth by VMware delivers intelligent insights that help you optimize costs, improve governance, and strengthen your cloud security posture.
The common usage in AWS Cloud is EC2 Service and On-Demand instances. EC2 instances are virtual servers on the cloud and comes in a different hardware resources (CPU, Memory, Network usage, etc.)
Sometimes the client selecting an EC2 instance that his usage is much lower than what he really need, now the user need to pay for an instance with high resources while he really using only 10% of the resources.
Since the user pays according to the instance type, by selecting an instance with lower resources he will pay less.

The way for getting this value and to locate the instances that are "Under utilization", is to install CloudHealth Agent on each EC2 instance and to retrieve the analysis output and the recommandations under one screen in CloudHealth.

CloudHealth Agent
==================
# Prerequisites
Use a user or an instance role with IAM permissions.

Add tag "ssm:true" to all instances.
(This can be done easily by "AWS Tag Editor Service".)

# Install CloudHealth Agent:
Execute the script "ssm_role.py"
This script will add the required policies to the EC2 role on all instances with the tag key/value "ssm:true", for allowing the SSM permissions.
The script is compatible with:
 - Instances without EC2 role
 - Instances with EC2 role with permissions of SSM
 - Instance with EC2 role without permissions of SSM

# S3
Create a folder named "CloudHealthDistributor"
Upload all your packages to s3://<BUCKETNAME>/CloudHealthDistributor

CloudHealthDistributor
		    |-------- CloudHealthPackage_AMAZON.zip
		    |-------- CloudHealthPackage_ AMAZON.zip
		    |-------- CloudHealthPackage_UBUNTU.zip
		    |-------- manifest.json

# Create SSM Distributor
Go to : AWS Systems Manager > Distributor > Create package (Advanced)

1. Add any name you want for your Dist
2. Select your S3 bucket
3. Add "CloudHealthDistributor" s3 key prefix
4. Select "New manifest"
5. Paste your manifest.json content (Attached file)
6. Create package

# Install agent using SSM
Go to : AWS Systems Manager > Distributor > "Owned by me"
- Select your package and click on "Install one time"
- On "Version" type: 1.0
- Select your targets
- Install


===============================================================================
* BUILD YOUR OWEN PACKAGE

# Cloudhealth
Create the CloudHealth agent Package for all platforms including Install and Uninstall Scripts
Upload the package in AWS Systems Manager Distributor
Create an Association with State Manager (System Manager) to constantly control that CloudHealth agent is present and automatically install it if it’s not the case
1. Create your CloudHealth agent Package for Distributor (System Manager)
AWS Systems Manager Distributor lets you package your own software to install on AWS Systems Manager managed instances. As per as the documentation you first need to create a Zip file containing your install and uninstall scripts as well as the files you want to install on your instances in order to use it in Distributor Please have a look at the installation instructions on the CloudHealth documentation before proceeding

1.1 Create the Windows Package:

Windows package will contain three files:

Install.ps1
Uninstall.ps1
CloudHealthAgent.exe
Put the following text in Install.ps1 file:

Write-Output 'Installing CloudHealthAgent on Windows...'
Start-Process CloudHealthAgent.exe -ArgumentList "/s, /v`"/l* install.log /qn CLOUDNAME=aws CHTAPIKEY=YOUAPIKEYHERE`""
Put the following text in Uninstall.ps1 file:

Write-Output 'Uninstalling CloudHealthAgent on Windows...'
Start-Process CloudHealthAgent.exe -ArgumentList "/x /s /v/qn" 
Get the CloudHealthAgent.exe files as explained in the documentation

Create a zip file with these 3 files, you will end-up with the following zip file content:

CloudHealthPackage_WINDOWS.zip
			|-------- install.ps1
			|-------- uninstall.ps1
			|-------- cloudhealthagent.exe
1.2 Create the Ubuntu and Amazon Linux Packages:

Amazon Linux and Ubuntu packages will each contain only two files:

Install.sh
Uninstall.sh
Both files can be the same for Amazon Linux and Ubuntu

Put the following text in install.sh file:

#!/bin/bash
echo 'Installing CloudHealthAgent on Amazon Linux...'
wget https://s3.amazonaws.com/remote-collector/agent/v20/install_cht_perfmon.sh -O install_cht_perfmon.sh;
sudo sh install_cht_perfmon.sh 20 YOUR_KEY_HERE_AS_PER_AS_CH_DOCUMENTATION aws;
Put the following text in uninstall.sh file:

#!/bin/bash
echo 'Uninstalling CloudHealthAgent on Amazon Linux...'
wget -O - https://s3.amazonaws.com/remote-collector/agent/uninstall_cht_perfmon.sh | sudo sh
Create two zip files with these 2 files you will end-up with the following two zip files content:

CloudHealthPackage_AMAZON.zip
                    |-------- install.sh
                    |-------- uninstall.sh
CloudHealthPackage_UBUNTU.zip
                    |-------- install.sh
                    |-------- uninstall.sh
1.3. Create your package Manifest and finalize your AWS System Manager Distributor package

Create a file called manifest.json, add it to the folder where you created the other zip files. In the end you should have a folder containing the following files:

MyCloudHealthPackageFolder
		    |-------- CloudHealthPackage_AMAZON.zip
		    |-------- CloudHealthPackage_ AMAZON.zip
		    |-------- CloudHealthPackage_UBUNTU.zip
		    |-------- manifest.json
For your manifest.json file you can simply use the same content as the one provided in the AWS documentation. At the beginning of the documentation there is a link to download the ExamplePackage.zip file. You just need to modify the following in the provided JSON file

The name of the Zip files (6 references in total)
The checksums for each Zip file (3 references in total)

To get the checksums use the command(Example):
shasum -a 256 CloudHealthPackage_WINDOWS.zip

Also be careful to note the version of the file in the manifest as you will need to use the same in AWS Systems Manager Distributor

Ex:     "version": "1.0",
2. Upload your Package in S3 and then in AWS System Manager Distributor
2.1. Simply create a bucket and upload all your files to the S3 bucket, you should end-up with something like this

bucket

2.2. Now create you package in Distributor

Open AWS System Manager Console, go to Distributor on the left Menu (Under the “Actions” section)
Click on “Create Package”, give your package a name like “CloudHealthAgentPackage”
Set the version to the same number you set in your Manifest.json as explained at the end of section 1.3 of this document
Specify the URL of the bucket you created in Step 2.1 of this document
For the manifest, select “Extract from package” and click “View Manifest File”, manifest file content will appear then
Click “Create Package” and wait for your package to be created successfully on next screen
3.Create an Associate using State Manager to install this package and ensure compliance of this installation
3.1. Create your Association

Open AWS System Manager Console, go to “State Manager” on the left Menu (Under the “Actions” section)
Click on “Create Associate”, give it a name like “CloudWatchAgentInstallationState”
Under “Document” Select “AWS-ConfigureAWSPackage” document with the radio button
Set the following “Parameters”
Action: Install
Name: CloudHealthAgentPackage (the name shall match exactly the name you used in Distributor)
Version: 1.0 (shall exactly match the version you used in Distributor)
Under “Targets” select “All managed instances” if you want all your EC2 to get your package (recommended)
Under “Specify Schedule”, set let the default schedule of 30 minutes or change it as you please
Choose a compliance severity and click “Create Association”
3.2 Wait for the association to execute once

Verify that everything is fine under the compliance section.

State Manager allow you to do two main things in this scenario

Verify that your package is installed as required
Install package if the association is not compliant (package not installed)
Using System Manager here allow you to get the full benefit of CloudHealth recommendations in terms of Right Sizing as it is required to deploy the Agent on all instances in order to collect all needed data to have precise insights of the EC2 instances utilization and make the right decisions.