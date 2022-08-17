Write-Output 'Uninstalling CloudHealthAgent on Windows...'
Start-Process CloudHealthAgent.exe -ArgumentList "/x /s /v/qn" 