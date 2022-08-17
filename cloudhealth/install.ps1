Write-Output 'Installing CloudHealthAgent on Windows...'
CloudHealthAgent.exe /S /v"/l* install.log /qn CLOUDNAME=aws CHTAPIKEY={{ssm:cloudhealth_key}}"