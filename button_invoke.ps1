Add-Type -AssemblyName UIAutomationClient
$h=(Get-Content button_hwnd.txt -Raw).Trim()
$el=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$h)
$cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,'Aktion')
$btn=$el.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$cond)
Write-Host "button=$($btn -ne $null) type=$($btn.Current.ControlType.ProgrammaticName)"
if($btn){try{$inv=$btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern); Write-Host "invoke=$($inv -ne $null)"}catch{Write-Host "error=$($_.Exception.Message)"}}
