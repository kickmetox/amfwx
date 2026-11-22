Add-Type -AssemblyName UIAutomationClient
$lines=Get-Content uia_patterns_handles.txt
$eh=[IntPtr][long]$lines[1]
$edit=[System.Windows.Automation.AutomationElement]::FromHandle($eh)
Write-Host "name=$($edit.Current.Name) type=$($edit.Current.ControlType.ProgrammaticName) bounds=$($edit.Current.BoundingRectangle)"
