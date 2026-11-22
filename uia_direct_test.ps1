Add-Type -AssemblyName UIAutomationClient
$lines=Get-Content uia_patterns_handles.txt
$hwnd=[IntPtr][long]$lines[0]; $eh=[IntPtr][long]$lines[1]; $ch=[IntPtr][long]$lines[2]
$main=[System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
$edit=[System.Windows.Automation.AutomationElement]::FromHandle($eh)
Write-Host "edit name='$($edit.Current.Name)' type=$($edit.Current.ControlType.ProgrammaticName) auto=$($edit.Current.AutomationId)"
$edit.GetSupportedPatterns() | ForEach-Object {$_.ProgrammaticName} | Out-String
if($edit){$vp=$edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern); Write-Host "value=$($vp.Current.Value)"; $vp.SetValue('neu'); Start-Sleep -Milliseconds 300; Write-Host "new=$($vp.Current.Value)"}
$check=[System.Windows.Automation.AutomationElement]::FromHandle($ch)
Write-Host "check name='$($check.Current.Name)' type=$($check.Current.ControlType.ProgrammaticName)"
