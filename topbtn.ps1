Add-Type -AssemblyName UIAutomationClient
$el=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$args[0])
Write-Host "type=$($el.Current.ControlType.ProgrammaticName) name=$($el.Current.Name)"
try{$inv=$el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern); Write-Host "invoke=$($inv -ne $null)"}catch{Write-Host "error=$($_.Exception.Message)"}
