import time

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.graphics import PopMatrix, PushMatrix, Rotate

from .popups import *
from .crutches import NoBugActionBar, LineBreakButton, LineBreakSpinner


class RotatedLabel(Label):
    def __init__(self, angle=0, **kwargs):
        super().__init__(**kwargs)
        self.angle = angle
        with self.canvas.before:
            PushMatrix()
            self.rotate = Rotate(angle=self.angle, origin=[self.center[0], self.center[1] + .5])
        with self.canvas.after:
            PopMatrix()
        self.bind(texture_size=lambda x, y: self.size)


class VerticalBar(NoBugActionBar):
    background_color = ListProperty()
    color_popup = ColorPopup(size_hint=(None, None), size=(270, 400))
    color_btn = LineBreakButton(background_normal='')
    timer_lbl = Label(text='0.00', height=100)
    slider_layout = BoxLayout(size_hint_y=None, size_hint_min_y=100, size_hint_max_y=100)
    y_slider_label = Builder.load_string("""
Label:
    font_name: 'Font.ttf'
    size: self.texture_size
    canvas.before:
        PushMatrix
        Rotate:
            angle: 270
            origin: self.center
    canvas.after:
        PopMatrix
""")
    RotatedLabel(angle=270, font_name='Font.ttf')
    y_slider = Slider(min=3, max=70, step=1, orientation='vertical')
    GENERATOR_WIDGETS = (color_btn, slider_layout)
    GAME_WIDGETS = (timer_lbl,)

    def __init__(self, manager, **kwargs):
        self.manager = manager
        self.manager.vbar = self
        super().__init__(**kwargs)
        self.bind(size=self.cover)
        self.bind(pos=self.cover)
        self.slider_layout.add_widget(self.y_slider)
        self.slider_layout.add_widget(self.y_slider_label)
        self.add_widgets('generator')

    def set_controls(self):
        self.color_btn.on_release = self.color_popup.open
        self.color_popup.maze = self.parent.maze
        self.y_slider_label.texture_update()
        # self.y_slider_label.bind(size=self.y_slider_label.texture.size)


class HorizontalBar(NoBugActionBar):
    landscape_popup = LandscapePopup(size_hint=(None, None), size=(270, 400))
    # skin_popup = SkinPopup(size_hint=(None, None), size=(270, 400))
    settings_popup = SettingsPopup(size_hint=(None, None), size=(270, 400), title='')
    reload_btn = LineBreakButton(text='Reload')
    slider_layout = BoxLayout(orientation='vertical', size_hint_x=None, size_hint_min_x=100, size_hint_max_x=100)
    x_slider_label = Label(font_name='Font.ttf')
    x_slider = Slider(min=3, max=70, step=1)
    settings_btn = LineBreakButton()
    game_btn = LineBreakButton()
    generator_btn = LineBreakButton()
    stop_btn = LineBreakButton()
    landscape_btn = LineBreakButton()
    # skin_btn = LineBreakButton()
    # angle_spinner = LineBreakSpinner()
    GENERATOR_WIDGETS = (slider_layout, settings_btn, reload_btn, landscape_btn, game_btn)
    GAME_WIDGETS = (settings_btn, generator_btn, stop_btn)

    def __init__(self, manager, **kwargs):
        self.manager = manager
        self.manager.hbar = self
        self.settings_popup.manager = manager
        super().__init__(**kwargs)
        self._set_layouts()
        self.add_widgets('generator')

    def _set_layouts(self):
        self.slider_layout.add_widget(self.x_slider_label)
        self.slider_layout.add_widget(self.x_slider)

    def set_controls(self):
        self.reload_btn.on_release = self.manager.reload
        self.settings_btn.on_release = self.settings_popup.open
        self.landscape_btn.on_release = self.landscape_popup.open
        self.landscape_popup.maze = self.parent.maze
        self.landscape_popup.open_btn = self.landscape_btn
        # self.skin_btn.icon = self.parent.maze.player_source
        # self.skin_btn.on_release = self.skin_popup.open
        # self.skin_popup.open_btn = self.skin_btn
        # self.skin_popup.maze = self.parent.maze
        # self.skin_popup.set_content()
        # self.angle_spinner.bind(text=self.on_background_color)

    # def on_background_color(self, _=None, __=None):
    #     super().on_background_color()
    #     children = self.angle_spinner._dropdown.children[0].children
    #     for i in children:
    #         i.background_color = self.background_color
