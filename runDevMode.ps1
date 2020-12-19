# Visit: https://windowsloop.com/enable-powershell-scripts-execution-windows-10/
#        https://4sysops.com/archives/set-powershell-execution-policy-with-group-policy/
$env:FLASK_APP = "todoer"
$env:FLASK_ENV = "development"
flask run