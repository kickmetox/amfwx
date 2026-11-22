# Studio / project starter

AMFWX includes a small project starter.

```python
from amfwx import Studio

studio = Studio()
project = studio.create_project("projects", "demo", "form")
print(project.files())
```

Templates:

- `blank`
- `form`
- `dashboard`

Each project gets:

- `app.py`
- `README.md`
- `.gitignore`

The optional `StudioWindow` offers buttons for each template.

## Limits

- no visual project editor
- no package manager
- no build system
- no template variables
- no plugin templates
