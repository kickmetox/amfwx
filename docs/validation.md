# Form validation

```python
from amfwx import Form, LineEdit, email, min_length, required

form = Form()
form.add("name", LineEdit(""), [required, min_length(3)])
form.add("mail", LineEdit(""), [email])

if not form.validate():
    print(form.errors())
```

Validators:

- `required`
- `min_length`
- `max_length`
- `pattern`
- `email`
- `integer`
- `number_range`

`Form.values()` returns all field values.
