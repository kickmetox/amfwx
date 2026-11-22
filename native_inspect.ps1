Add-Type -AssemblyName UIAutomationClient
$h=[IntPtr][long]$args[0]
$el=[System.Windows.Automation.AutomationElement]::FromHandle($h)
Write-Host "type=$($el.Current.ControlType.ProgrammaticName) name=$($el.Current.Name)"
$el.GetSupportedPatterns() | ForEach-Object {$_.ProgrammaticName} | Out-String
try{$inv=$el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern); Write-Host "invoke=$($inv -ne $null)"}catch{Write-Host "error=$($_.Exception.Message)"}
