from .frouge import FlammeRougeEnv

from nicegui import ui

class Gui(ui.label):

    def __init__(self, env: FlammeRougeEnv):
        super.__init__(env.name)
        self.env = env


