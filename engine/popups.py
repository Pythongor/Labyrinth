from functools import partial
from os import listdir
import json

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.treeview import TreeView
from kivy.uix.colorpicker import ColorPicker
from kivy.graphics import Color, Rectangle
from kivy.uix.settings import SettingsWithNoMenu, SettingOptions, SettingSpacer
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from .crutches import ImageButton, LineBreakButton


class ColorPopup(Popup):
    picker = ColorPicker(size_hint=(1, .7), pos_hint={'x': 0, 'y': .3})
    random_btn = LineBreakButton(size_hint=(.5, .15), pos_hint={'x': 0, 'y': .15}, text='Random')
    tiles = Widget(size_hint=(None, None), size=(100, 50))
    choose_btn = LineBreakButton(size_hint=(1, .15), pos_hint={'x': 0, 'y': 0}, text='Choose')
    maze = None
    color = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._add_content()
        self._set_content()

    def _add_content(self):
        layout = RelativeLayout()
        tile_layout = AnchorLayout(size_hint=(.5, .15), pos_hint={'x': .5, 'y': .15},
                                   anchor_x='center', anchor_y='center')
        tile_layout.add_widget(self.tiles)
        for widget in (self.picker, self.random_btn, self.choose_btn, tile_layout):
            layout.add_widget(widget)
        self.content = layout

    def _set_content(self):
        self.random_btn.on_release = self.random_color
        self.choose_btn.on_release = self.choose
        self.picker.bind(color=self.draw_tiles)

    def draw_tiles(self, _=None, color=None):
        self.tiles.canvas.clear()
        source = f'atlas://images/{self.maze.landscape}_atlas/tile_'
        with self.tiles.canvas:
            Color(*color, group='color')
            Rectangle(size=(25, 25), source=source + '1001', pos=(self.tiles.x, self.tiles.y + 25), group='color')
            Rectangle(size=(25, 25), source=source + '1010', pos=(self.tiles.x + 25, self.tiles.y + 25), group='color')
            Rectangle(size=(25, 25), source=source + '1000', pos=(self.tiles.x + 50, self.tiles.y + 25), group='color')
            Rectangle(size=(25, 25), source=source + '1110', pos=(self.tiles.x + 75, self.tiles.y + 25), group='color')
            Rectangle(size=(25, 25), source=source + '0111', pos=self.tiles.pos, group='color')
            Rectangle(size=(25, 25), source=source + '1011', pos=(self.tiles.x + 25, self.tiles.y), group='color')
            Rectangle(size=(25, 25), source=source + '0010', pos=(self.tiles.x + 50, self.tiles.y), group='color')
            Rectangle(size=(25, 25), source=source + '1110', pos=(self.tiles.x + 75, self.tiles.y), group='color')

    def open(self):
        super().open()
        self.color = self.maze.main_color
        self.picker.set_color(self.color)
        self.draw_tiles(color=self.color)

    def random_color(self):
        random_color = self.maze.get_color()
        self.picker.set_color(random_color)

    def choose(self):
        self.maze.main_color = self.picker.color
        self.maze.draw()
        self.dismiss()

    def on_background_color(self, _, color):
        for widget in (self.random_btn, self.choose_btn):
            widget.background_color = color


class LandscapePopup(Popup):
    VALUES = 'pit', 'prison', 'storage', 'green_maze', 'highway'
    maze = None
    open_btn = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_content()

    def add_content(self):
        layout = BoxLayout(orientation='vertical', padding=10)
        for value in self.VALUES:
            sub_layout = BoxLayout(padding=10)
            btn = LineBreakButton(size_hint_x=1.9,  background_color=self.background_color,
                                  on_release=partial(self.change_landscape, value))
            image = Image(source=f'atlas://images/{value}_atlas/tile_1111', size=(64, 64))
            sub_layout.add_widget(btn)
            sub_layout.add_widget(image)
            layout.add_widget(sub_layout)
        self.content = layout

    def change_landscape(self, value, _):
        self.open_btn.text = self.maze.manager.lng(value)
        self.maze.landscape = value
        self.maze.draw()
        self.dismiss()

    def on_background_color(self, _, __):
        for sub_layout in self.content.children:
            sub_layout.children[1].background_color = self.background_color


# class SkinPopup(Popup):
#     maze = None
#     open_btn = None
#
#     def set_content(self):
#         layout = GridLayout(rows=3)
#         for file in listdir('./images/players'):
#             # size = (self.maze.matrix.tile_width, self.maze.matrix.tile_height)
#             size = 64, 64
#             btn = ImageButton(background_normal='./images/players/'+file, size_hint=(None, None), size=size)
#             btn.on_release = partial(self.image_function, btn.background_normal)
#             layout.add_widget(btn)
#         self.content = layout
#
#     def image_function(self, source):
#         self.maze.sources['player'] = source
#         self.maze.draw()
#         self.open_btn.icon = source
#         self.dismiss()


class SettingsPopup(Popup):
    manager = None
    settings = SettingsWithNoMenu()
    content = settings
    config = None
    settings_dict = [{
                "type": "options",
                "section": "user data",
                "options": [
                    "English",
                    "Français",
                    "Italiano",
                    "Deutsch",
                    "Español",
                    "Português",
                    "Русский",
                    "Svenska"
                ],
                "key": "language"
            }]

    class StyledSettingOptions(SettingOptions):
        def _create_popup(self, instance):
            content = ScrollView(height=200)
            box = BoxLayout(orientation='vertical', spacing='5dp',
                            # size_hint=(1, None)
                            )
            # content.add_widget(box)
            popup_width = min(0.95 * Window.width, dp(500))
            parent_popup = self.parent.parent.parent.parent.parent.parent.parent
            self.popup = popup = Popup(content=box, title=self.title, size_hint=(None, None),
                                       size=(popup_width, '400dp'), background_color=parent_popup.background_color)
            popup.height = len(self.options) * dp(55) + dp(150)
            box.add_widget(Widget(size_hint_y=None, height=1))
            uid = str(self.uid)
            for option in self.options:
                state = 'down' if option == self.value else 'normal'
                btn = ToggleButton(text=option, state=state, group=uid, height=100, font_name='Font.ttf',
                                   bold=True, background_color=parent_popup.background_color)
                btn.bind(on_release=self._set_option)
                box.add_widget(btn)
            box.add_widget(SettingSpacer())
            cancel = parent_popup.manager.lng('cancel')
            btn = Button(text=cancel, size_hint_y=None, height=dp(50), background_color=parent_popup.background_color)
            btn.bind(on_release=popup.dismiss)
            box.add_widget(btn)
            popup.open()

    def start(self):
        self.config = self.manager.app.config
        self.settings.on_config_change = self.on_config_change
        self.settings.register_type('options', self.StyledSettingOptions)
        self.add_panel()
        self.bind(size=self.settings_background)
        self.bind(pos=self.settings_background)
        self.bind(background_color=self.settings_background)
        self.settings_background()

    def color_tone(self, coefficient):
        return [*[i * coefficient for i in self.background_color[:3]], 1]

    def settings_background(self, _=None, __=None):
        self.settings.canvas.before.children[0] = Color(*self.color_tone(.5))
        self.set_style()

    def add_panel(self):
        title = self.manager.lng('language')
        data = self.settings_dict.copy()
        data[0]['title'] = title
        json_data = json.dumps(data)
        self.settings.add_json_panel(self.manager.lng('settings'), self.config, data=json_data)
        self.settings.interface.current_panel.background_color = self.background_color

    def set_style(self):
        for w in self.settings.interface.walk():
            if 'Label' in str(type(w)):
                if w.text == self.manager.lng('settings'):
                    w.color = self.background_color
                elif '\n[size=13sp][color=999999][/color][/size]' in w.text:
                    w.text = w.text.replace('\n[size=13sp][color=999999][/color][/size]', '')
                    w.color = self.color_tone(.25)
                else:
                    w.color = self.color_tone(.25)

    def on_config_change(self, config, section, option, value):
        if option == 'language':
            self.manager.localize()
            self.reload_panel()
        self.set_style()

    def reload_panel(self):
        self.settings.remove_widget(self.settings.interface)
        self.settings.add_interface()
        self.add_panel()


class WinPopup(Popup):
    to_generator_btn = Button()
    again_btn = Button()
    score_lbl = Label()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = BoxLayout(orientation='vertical')
        self.content.add_widget(self.score_lbl)
        self.content.add_widget(self.again_btn)
        self.content.add_widget(self.to_generator_btn)

    def on_background_color(self, _, color):
        for widget in (self.to_generator_btn, self.again_btn):
            widget.background_color = color
