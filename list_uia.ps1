Add-Type -AssemblyName UIAutomationClient
$h=(Get-Content uia_patterns_hwnd.txt -Raw).Trim()
$el=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$h)
$all=$el.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
for($i=0;$i -lt $all.Count;$i++){ $c=$all.Item($i); Write-Host "$i name='$($c.Current.Name)' type=$($c.Current.ControlType.ProgrammaticName)"}
