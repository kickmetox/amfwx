# JUCE compatibility

Small AMFWX-native JUCE interpretation.

```python
from amfwx.compat import juce

window = juce.DocumentWindow("Demo")
window.setContentOwned(juce.Label("label", "Hallo"))
button = juce.TextButton("button", "OK")
button.onClick(lambda: print("OK"))
window.addAndMakeVisible(button)
window.setVisible(True)
```

## Included

- `Component`
- `DocumentWindow`
- `ResizableWindow`
- `Label`
- `TextButton`
- `TextEditor`
- `Slider`
- `ComboBox`
- `ToggleButton`
- `Colour`

## Limits

- no JUCE audio/MIDI engine
- no `juce::Graphics` drawing API
- no ValueTree
- no native JUCE components
- no plugin host
