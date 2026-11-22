Add-Type -AssemblyName UIAutomationClient
$h=(Get-Content uia_action_hwnd.txt -Raw).Trim()
$el=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$h)
$cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,'Aktion')
$btn=$el.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$cond)
Write-Host "button=$($btn -ne $null)"
if($btn){
  try {
    $inv=$btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $inv.Invoke()
    Start-Sleep -Milliseconds 300
    Write-Host "clicked=$(Test-Path uia_clicked.txt)"
  } catch {
    Write-Host "pattern error: $($_.Exception.Message)"
  }
}
