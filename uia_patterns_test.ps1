Add-Type -AssemblyName UIAutomationClient
$h=(Get-Content uia_patterns_hwnd.txt -Raw).Trim()
$el=[System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$h)
function Find($name){$c=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,$name); return $el.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$c)}
$edit=Find 'Name'; $check=Find 'An'
Write-Host "edit=$($edit -ne $null) type=$($edit.Current.ControlType.ProgrammaticName) name=$($edit.Current.Name)"
$edit.GetSupportedPatterns() | ForEach-Object {$_.ProgrammaticName} | Out-String
if($edit){$vp=$edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern); Write-Host "value=$($vp.Current.Value)"; $vp.SetValue('neu'); Start-Sleep -Milliseconds 300; Write-Host "newvalue=$($vp.Current.Value)"}
Write-Host "check=$($check -ne $null) type=$($check.Current.ControlType.ProgrammaticName)"
$check.GetSupportedPatterns() | ForEach-Object {$_.ProgrammaticName} | Out-String
if($check){$tp=$check.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern); Write-Host "state=$($tp.Current.ToggleState)"; $tp.Toggle(); Start-Sleep -Milliseconds 300; Write-Host "newstate=$($tp.Current.ToggleState)"}
