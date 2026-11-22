# Qt / PySide compatibility

Small AMFWX-native Qt interpretation.

```python
from amfwx.compat import qt

app = qt.QApplication([])
window = qt.QMainWindow(title="Demo")
central = qt.QWidget()
layout = qt.QVBoxLayout(central)
layout.addWidget(qt.QLabel("Hallo"))
button = qt.QPushButton("OK")
button.clicked.connect(lambda: print("OK"))
layout.addWidget(button)
window.setCentralWidget(central)
window.show()
app.exec()
```

## Included

- `QApplication`
- `QMainWindow`
- `QWidget`
- `QVBoxLayout`, `QHBoxLayout`
- `QLabel`
- `QPushButton`
- `QLineEdit`
- `QCheckBox`
- `QSlider`
- `QComboBox`
- `QProgressBar`
- `QTextEdit`

## Limits

- no Qt libraries
- no QML
- no signals/slots beyond `clicked`
- no designer `.ui` files
- no stylesheets
