"""Project scaffolding and a small Studio starter."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from .canvas import Rect
from .widgets import Button, Label, Panel
from .window import Window


BLANK = '''\
from amfwx import Label, Window

window = Window("Neues AMFWX-Projekt", 800, 600)
window.layout.add(Label("Hallo AMFWX"))
window.run()
'''

FORM = '''\
from amfwx import Button, Label, LineEdit, Window

window = Window("Formular", 640, 420)
window.layout.add(Label("Name"))
name = LineEdit("")
window.layout.add(name)
window.layout.add(Button("Speichern", on_click=lambda: print(name.text())))
window.run()
'''

DASHBOARD = '''\
from amfwx import Label, TableView, Window

window = Window("Dashboard", 900, 600)
window.layout.add(Label("Dashboard"))
window.layout.add(TableView(["Spalte A", "Spalte B"],
                            [["1", "2"], ["3", "4"]]))
window.run()
'''

TEMPLATES = {
    "blank": ("Leeres Fenster", BLANK),
    "form": ("Formular", FORM),
    "dashboard": ("Dashboard", DASHBOARD),
}


class ProjectError(RuntimeError):
    pass


class Project:
    def __init__(self, directory, name, template):
        self.directory = Path(directory)
        self.name = name
        self.template = template

    @property
    def app(self):
        return self.directory / "app.py"

    def files(self):
        return sorted(path.name for path in self.directory.iterdir()
                      if path.is_file())

    def read(self, name="app.py"):
        return (self.directory / name).read_text(encoding="utf-8")


class Studio:
    def templates(self):
        return sorted(TEMPLATES)

    def create_project(self, directory, name, template="blank"):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", str(name)):
            raise ProjectError("ungueltiger Projektname")
        if template not in TEMPLATES:
            raise ProjectError(f"unbekannte Vorlage: {template}")
        project_dir = Path(directory) / name
        project_dir.mkdir(parents=True, exist_ok=True)
        description, source = TEMPLATES[template]
        (project_dir / "app.py").write_text(source, encoding="utf-8")
        (project_dir / "README.md").write_text(
            f"# {name}\n\n{description}\n\n```powershell\npython app.py\n```\n",
            encoding="utf-8")
        (project_dir / ".gitignore").write_text(
            "__pycache__/\n*.pyc\nbuild/\ndist/\n", encoding="utf-8")
        return Project(project_dir, name, template)

    def open_project(self, directory):
        directory = Path(directory)
        if not (directory / "app.py").exists():
            raise ProjectError("app.py fehlt")
        return Project(directory, directory.name, "existing")


class StudioWindow(Window):
    def __init__(self, studio=None, projects_dir="projects"):
        super().__init__("AMFWX Studio", 760, 420)
        self.studio = studio or Studio()
        self.projects_dir = Path(projects_dir)
        self.panel = Panel()
        self.panel.parent = self
        self.root.add(self.panel)
        self.panel.arrange(Rect(20, 20, 720, 380))
        y = 30
        for template in self.studio.templates():
            label = Label(TEMPLATES[template][0])
            label.parent = self.panel
            label.arrange(Rect(30, y, 240, 24))
            self.panel.children.append(label)
            button = Button("Erstellen")
            button.parent = self.panel
            button.arrange(Rect(280, y - 2, 120, 30))
            button.on_click = (lambda t=template: self._create(t))
            self.panel.children.append(button)
            y += 44

    def _create(self, template):
        index = len(list(self.projects_dir.glob("*"))) + 1
        return self.studio.create_project(self.projects_dir,
                                          f"project{index}", template)
