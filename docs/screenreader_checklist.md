# Screenreader checklist

Automated audit:

```powershell
python tools\a11y_audit.py --output dist\a11y.json
```

Manual NVDA check:

1. Start NVDA.
2. Open the demo app.
3. Tab through every control.
4. Verify each control announces a name, role and state.
5. Check buttons with Space/Enter.
6. Check edit fields with typing and cursor movement.
7. Check radio/checkbox state changes.
8. Check list selection.
9. Check focus order and focus rectangle.
10. Check high-contrast theme.

Manual Narrator check:

1. Enable Narrator.
2. Repeat the same steps.
3. Check Scan Mode and Forms Mode.

Not covered automatically:

- pronunciation
- actual speech output
- screenreader-specific focus behavior
- full WCAG certification
- third-party AT compatibility matrix

This project provides a provider tree and audit, not a formal
accessibility certification.
