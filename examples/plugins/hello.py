"""Example AMFWX plugin."""

from amfwx.plugins import Plugin


class HelloPlugin(Plugin):
    name = "hello"
    version = "1.0"

    def __init__(self):
        self.activated = False

    def activate(self, app=None):
        self.activated = True
        return self

    def deactivate(self):
        self.activated = False


PLUGIN = HelloPlugin()
