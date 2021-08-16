from math import ceil

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Line


class ImageButton(ButtonBehavior, Image):
    """Button with image functionality"""
    drop = None

    def __init__(self, switch=False, with_drop=False, disabled=False,
                 background_normal=None, background_down=None, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.active = True
        self.switch = switch
        if switch:
            self.deactivate()
        self.background_normal = self.source = background_normal
        self.background_down = background_down
        if disabled:
            self.disable()
        if with_drop:
            self.on_release = self._drop_on_release

    def disable(self):
        self.disabled = True
        self.color = (.5, .5, .5, 1)

    def enable(self):
        self.disabled = False
        self.color = (1, 1, 1, 1)

    def activate(self):
        self.active = True
        self.color = (.6, .6, 1, 1)

    def deactivate(self):
        self.active = False
        self.color = (1, 1, 1, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            if self.switch:
                if not self.active:
                    self.activate()
                else:
                    self.deactivate()
            else:
                self.color = (.7, .9, 1, 1)
            self.on_press()

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            if not self.switch:
                self.color = (1, 1, 1, 1)
            self.on_release()


class Controller(ImageButton):
    background_normal = './images/controller.png'

    @staticmethod
    def ys(x0, y0, x1, y1):
        x = x0
        for dot in range(int(x0), int(x1) + 1):
            width = abs(x1 - x0)
            height = abs(y0 - y1)
            if y0 > y1:
                y = y0 - height / width * (x - x0)
            else:
                y = height / width * (x - x0) + y0
            yield x, ceil(y)
            x += 1

    def find_orientation(self, touch):
        top_left = self.ys(self.x, self.top, self.right, self.y)
        down_left = self.ys(self.x, self.y, self.right, self.top)
        conditions = {
            touch.x <= self.center_x and touch.y <= self.center_y: (down_left, ('down', 'left')),
            touch.x <= self.center_x and touch.y >= self.center_y: (top_left, ('left', 'top')),
            touch.x >= self.center_x and touch.y <= self.center_y: (top_left, ('down', 'right')),
            touch.x >= self.center_x and touch.y >= self.center_y: (down_left, ('right', 'top'))
        }
        line, orientations = conditions[True]
        filtered_line = filter(lambda x_y: ceil(x_y[0]) == ceil(touch.x), line)
        line_dot = list(filtered_line)[0]
        index = int(touch.y > line_dot[1])
        return orientations[index]

    def draw_line(self, generator):
        with self.canvas:
            Color(1, 0, 1)
            points = list(generator)
            Line(points=points)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            self.color = (.7, .9, 1, 1)
            # top_left = self.ys(self.x, self.top, self.right, self.y)
            # down_left = self.ys(self.x, self.y, self.right, self.top)
            # self.draw_line(top_left)
            # self.draw_line(down_left)
            orientation = self.find_orientation(touch)
            self.parent.parent.move(orientation)
