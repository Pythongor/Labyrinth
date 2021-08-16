# import os
# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
# os.environ['KIVY_GRAPHICS'] = 'gif'


import os
from os.path import isfile
from configparser import RawConfigParser as PythonConfigParser

from kivy.app import App
from kivy.uix.screenmanager import Screen
# from kivy.graphics import cgl
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.logger import Logger

from engine.redactor import Redactor
#from logger import get_logger, get_handler

# print(cgl.cgl_get_backend_name())


class UTFConfigParser(ConfigParser):
    def write(self):
        if self.filename is None:
            return False
        try:
            with open(self.filename, 'w', encoding='utf-8') as fd:
                PythonConfigParser.write(self, fd)
        except IOError:
            Logger.exception('Unable to write the config <%s>' % self.filename)
            return False
        return True

    def read(self, filename):
        if not isinstance(filename, str):
            raise Exception('Only one filename is accepted ({})'.format(
                str.__name__))
        self.filename = filename
        old_vals = {sect: {k: v for k, v in self.items(sect)} for sect in
                    self.sections()}
        PythonConfigParser.read(self, filename, 'utf-8')
        f = self._do_callbacks
        for section in self.sections():
            if section not in old_vals:
                for k, v in self.items(section):
                    f(section, k, v)
                continue

            old_keys = old_vals[section]
            for k, v in self.items(section):
                if k not in old_keys or v != old_keys[k]:
                    f(section, k, v)


class MazeApp(App):
    redactor = None
    config = UTFConfigParser()
    screen = Screen()
    # try:
    #     handler = get_handler('logs/journal.log')
    # except FileNotFoundError:
    #     f = open('logs/journal.log', 'w')
    #     f.close()
    #     handler = get_handler('logs/journal.log')
    # logger = get_logger(handler)

    def build(self):
        self.config = UTFConfigParser()
        # self.logger.info("Program started")
        Clock.schedule_once(self.start)
        self.config.read('user data/config.ini')
        height = self.config.get('user data', 'height')
        width = self.config.get('user data', 'width')
        self.redactor = Redactor(int(height), int(width), 64)
        self.screen.add_widget(self.redactor)
        # logging.conf.add_section('graphics')
        self.config.setdefaults('user data', {'language': 'English', 'height': 30, 'width': 40})
        return self.screen

    def start(self, _):
        self.redactor.manager.app = self
        self.redactor.start()
        self.redactor.hbar.settings_popup.start()

    def on_stop(self):
        self.config.write()


if __name__ == '__main__':
    app = MazeApp()
    # logger = app.logger
    # should_roll_over = isfile('logs/journal.log')
    # if should_roll_over:
    #     app.handler.doRollover()
    app.run()
    # logger.info("Done!")
    # Config.set('graphics', 'width', '1270')
    # Config.set('graphics', 'height', '970')

    # Config.set('graphics', 'width', '1590')
    # Config.set('graphics', 'height', '880')
    # Config.set('graphics', 'fullscreen', 'False')
    # Config.write()

# import webcolors
# from kivy.app import App
# from kivy.uix.recycleview import RecycleView
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.button import Button
# from kivy.graphics import Color
#
#
# class ColorApp(App):
#     grid = GridLayout(cols=7, spacing=5)
#     recycle = RecycleView()
#     recycle.add_widget(grid)
#     for name, hex in webcolors.CSS3_NAMES_TO_HEX.items():
#         rgb = tuple(webcolors.hex_to_rgb(hex))
#         rgb = [i / 255 for i in rgb]
#         color = (1, 1, 1, 1) if sum(rgb[:3])/3 < .5 else (0, 0, 0, 1)
#         label = Button(text=name, color=color, background_color=(*rgb, 1), background_normal='')
#         grid.add_widget(label)
#
#     def build(self):я
#         return self.recycle
#
#
# if __name__ == '__main__':
#     ColorApp().run()


from kivy.lang import Builder

from kivy.app import App
from kivy.uix.button import Button


KV = """
Screen:

    Button:
        text: "Hello World"
        pos_hint: {"center_x": .5, "center_y": .5}
"""


class HelloWorld(App):
    def build(self):
        return Button()


HelloWorld().run()

