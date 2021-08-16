from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.dropdown import DropDown
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import BorderImage, Color
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty
from kivy.uix.behaviors.cover import CoverBehavior
from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.core.window import Window


class ImageButton(ButtonBehavior, Image):
    """Button with image functionality"""
    drop = None
    keep_ratio = BooleanProperty(False)
    allow_stretch = BooleanProperty(True)
    active = BooleanProperty(True)

    def __init__(self, switch=False, with_drop=False, disabled=False,
                 background_normal=None, background_down=None, **kwargs):
        super().__init__(**kwargs)
        self.switch = switch
        if switch:
            self.deactivate()
        texture = Image(source=background_normal).texture
        texture.mag_filter = texture.min_filter = 'nearest'
        self.texture = texture
        self.background_normal = background_normal
        self.background_down = background_down
        if disabled:
            self.disable()
        if with_drop:
            self.on_release = self._drop_on_release

    def disable(self):
        self.disabled = True
        self.color = .5, .5, .5, 1

    def enable(self):
        self.disabled = False
        self.color = 1, 1, 1, 1

    def activate(self):
        self.active = True
        self.color = .6, .6, 1, 1

    def deactivate(self):
        self.active = False
        self.color = 1, 1, 1, 1

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            if self.switch:
                if not self.active:
                    self.activate()
                else:
                    self.deactivate()
            else:
                self.color = .7, .9, 1, 1
            self.on_press()

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            if not self.switch:
                self.color = 1, 1, 1, 1
            self.on_release()

    def _drop_on_release(self):
        for widget in Window.children:
            if type(widget) == DropDown:
                widget.dismiss()
                break
        else:
            self.drop.open(self)


class CoverImage(CoverBehavior, Image):
    pass

    def __init__(self, **kwargs):
        super(CoverImage, self).__init__(**kwargs)
        # texture = self._coreimage.texture
        # self.reference_size = texture.size
        # self.texture = texture


class LineBreakBehavior(Label):
    real_text = StringProperty()
    font_name = 'Font.ttf'

    def __init__(self, real_text='', **kwargs):
        self.real_text = real_text
        super().__init__(**kwargs)
        self.bind(width=self.update_text)
        self.bind(real_text=self.update_text)
        self.bind(font_size=self.update_text)

    def update_text(self, _=None, __=None):
        # if Window.width <= 500:
        #     self.font_size = 13
        # else:
        #     self.font_size = 15
        self.text = self.break_lines(self.real_text)

    def break_lines(self, text):
        def line_break(word, width):
            if not lines[-1]:
                if width + 10 < self.width:
                    lines[-1] += word
                else:
                    line_break(word[:len(word) // 2], self.text_width(word[:len(word) // 2]))
                    lines.append('')
                    line_break(word[len(word) // 2:], self.text_width(word[len(word) // 2:]))
            elif self.text_width(lines[-1]) + space + width + 10 < self.width:
                lines[-1] += f' {word}'
            else:
                lines.append('')
                line_break(word, width)

        words = text.split()
        space = self.text_width(' ')
        widths = [(word, self.text_width(word)) for word in words]
        lines = ['']
        for word, width in widths:
            line_break(word, width)
        return '\n'.join(lines)

    # def line_break(self, text, width):
    #     pass

    def text_width(self, text):
        lbl = CoreLabel(text=text, font_size=self.font_size)
        lbl.refresh()
        if lbl.texture:
            return lbl.texture.width

    def on_background_color(self, _=None, bg=None):
        if sum(bg[:3]) > 1.5:
            self.color = 0, 0, 0, 1
        else:
            self.color = 1, 1, 1, 1


class LineBreakButton(LineBreakBehavior, Button):
    pass


class LineBreakSpinner(Spinner, LineBreakBehavior):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(width=self.update_texts)
        self.bind(real_text=self.update_texts)
        self.bind(font_size=self.update_texts)

    def update_texts(self, _=None, __=None):
        self.values = [self.break_lines(value) for value in self.values]

    def update_text(self, _=None, __=None):
        self.text = self.break_lines(self.text)


class NoBugActionBar(BoxLayout):
    overflow_drop = DropDown()
    mode = 'generator'
    background_color = ListProperty(None)
    started = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.cover)
        self.bind(size=self.cover)

    def start(self):
        self.bind(size=self.overflow)
        self.started = True

    def on_background_color(self, _=None, __=None):
        self.cover()
        if self.started:
            self.overflow()

    def cover(self, _=None, __=None):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            BorderImage(pos=self.pos, size=self.size, source='atlas://data/images/defaulttheme/action_bar')

    def add_widgets(self, string):
        widgets = {
            'generator': self.GENERATOR_WIDGETS,
            'game': self.GAME_WIDGETS
        }[string]
        self._add_widgets(widgets)
        self.mode = string

    def overflow(self, _=None, __=None):
        widgets = {
            'generator': self.GENERATOR_WIDGETS,
            'game': self.GAME_WIDGETS
        }[self.mode]
        self.clear_widgets()
        self.overflow_drop.clear_widgets()
        if self.orientation == 'horizontal':
            self.horizontal_overflow(widgets)
        else:
            self.vertical_overflow(widgets)

    def horizontal_overflow(self, widgets):
        padding = self.padding[0] + self.padding[2]
        if self.size_hint_min_sum(widgets)[0] + padding <= self.width:
            self._crutch_add_widgets(widgets)
        else:
            for i in range(len(widgets), -1, -1):
                overflow_btn = Button(size_hint_min_x=60, size_hint_min_y=45,
                                      on_release=self.overflow_drop.open, text='...')
                if i == 0:
                    for widget in widgets[i:]:
                        self.overflow_drop.add_widget(widget)
                    self._crutch_add_widgets((overflow_btn, ))
                elif self.size_hint_min_sum(widgets[:i])[0] + padding + 60 <= self.width:
                    for widget in widgets[i:]:
                        self.overflow_drop.add_widget(widget)
                    new_widgets = [*widgets[:i], overflow_btn]
                    self._crutch_add_widgets(new_widgets)
                    break

    def vertical_overflow(self, widgets):
        padding = self.padding[1] + self.padding[3]
        if self.size_hint_min_sum(widgets)[1] + padding <= self.height:
            self._crutch_add_widgets(widgets)
        else:
            for i in range(len(widgets), -1, -1):
                overflow_btn = Button(size_hint_min_x=60, size_hint_min_y=45,
                                      on_release=self.overflow_drop.open, text='...')
                if i == 0:
                    for widget in widgets[i:]:
                        self.overflow_drop.add_widget(widget)
                    self._crutch_add_widgets((overflow_btn,))
                elif self.size_hint_min_sum(widgets[:i])[1] + padding + 45 <= self.height:
                    for widget in widgets[i:]:
                        self.overflow_drop.add_widget(widget)
                    new_widgets = [overflow_btn, *widgets[:i]]
                    self._crutch_add_widgets(new_widgets)
                    break

    def _crutch_add_widgets(self, widgets):
        for w in widgets:
            if w.parent:
                w.parent.remove_widget(w)
        self._add_widgets(widgets)

    def _add_widgets(self, widgets):
        for widget in widgets:
            if not widget.size_hint_min_x:
                widget.size_hint_min_x = 60
            if not widget.size_hint_min_y:
                widget.size_hint_min_y = 45
            if isinstance(widget, Button) and self.background_color:
                widget.background_color = self.background_color
            self.add_widget(widget)

    def size_hint_min_sum(self, widgets=None):
        widgets = self.children if widgets is None else widgets
        size_hint_min_x = None
        size_hint_min_y = None
        for widget in widgets:
            min_width = self.widget_min(widget, 'width')
            min_height = self.widget_min(widget, 'height')
            size_hint_min_x = self.sum_with_none(size_hint_min_x, min_width)
            size_hint_min_y = self.sum_with_none(size_hint_min_y, min_height)
        return size_hint_min_x, size_hint_min_y

    @staticmethod
    def widget_min(widget, orientation):
        size_hint_min = {'width': 'size_hint_min_x', 'height': 'size_hint_min_y'}[orientation]
        s_h_min = widget.__getattribute__(size_hint_min)
        return s_h_min if s_h_min else widget.__getattribute__(orientation)

    @staticmethod
    def sum_with_none(first, second):
        if first is None and second is None:
            return
        elif first is None:
            return second
        elif second is None:
            return first
        else:
            return first + second
