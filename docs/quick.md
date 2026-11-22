# Declarative Quick UI

AMFWX has a small declarative layer with reactive state.

```python
from amfwx.quick import HStack, ListState, QuickView, Text, VStack

state = ListState(["A", "B"])
view = QuickView("Quick", lambda items: [
    VStack(Text("Liste"), *[Text(item) for item in items]),
    HStack(Text("Links"), Text("Rechts")),
], state=state)
state.append("C")
view.run()
```

## Components

- `State`
- `ListState`
- `Stack`
- `VStack` / `HStack`
- `ForEach`
- `QuickView`
- `Text` / `TextField` / `Button_`

## Behavior

- state changes rebuild the widget tree
- nested stacks use `BoxLayout`
- `ForEach` calls the builder with `(item, index)` or `item`
- `QuickView` uses one window and one event loop

## Limits

- full rebuild on every change
- no diffing/virtual DOM
- no async state
- no hot reload yet
- no component lifecycle
