Add-Type -AssemblyName UIAutomationClient
$lines=Get-Content dialog_host_hwnd.txt
$h=[IntPtr][long]$lines[0]; $b=[IntPtr][long]$lines[1]
$el=[System.Windows.Automation.AutomationElement]::FromHandle($h)
$cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,'Aktion')
$btn=$el.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$cond)
Write-Host "button=$($btn -ne $null) type=$($btn.Current.ControlType.ProgrammaticName) off=$($btn.Current.IsOffscreen)"
$btn.GetSupportedPatterns() | ForEach-Object {$_.ProgrammaticName} | Out-String
try{$inv=$btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern); Write-Host "invoke=$($inv -ne $null)"}catch{Write-Host "error=$($_.Exception.Message)"}
