Add-Type -AssemblyName UIAutomationClient
$h=(Get-Content uia_action_hwnd.txt -Raw).Trim()
$el=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$h)
$cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,'Aktion')
$btn=$el.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$cond)
$btn.Current | Format-List ControlType,Name,IsEnabled,IsOffscreen,BoundingRectangle,FrameworkId,ClassName,AutomationId,ProcessId | Out-String
