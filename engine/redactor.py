from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import ScatterPlane

from .generator_bars import VerticalBar, HorizontalBar
from .matrix import Matrix
from .maze import Maze
from .manager import Manager
from .crutches import CoverImage


class MazeScatterPlane(ScatterPlane):
    do_rotation = False
    auto_bring_to_front = False

    def __init__(self, maze, **kwargs):
        self.maze = maze
        super().__init__(**kwargs)

    def x_transform(self, x):
        if self.x > x:
            self.x = x
        else:
            width = self.maze.width * self.scale
            if width < self.width:
                self.x = x
            elif width + self.x < self.width:
                self.x = self.width - width

    def y_transform(self, y):
        if self.y > y:
            self.y = y
        else:
            height = self.maze.height * self.scale
            if height < self.height:
                self.y = y
            elif height + self.y < self.height:
                self.y = self.height - height

    def focus_on_player(self, width=True, height=True):
        center = (self.width / 2 - self.x, self.height / 2 - self.y)
        player_pos = [i * self.scale for i in self.to_window(*self.maze.objects['player'].pos)]
        difference = (center[0] - player_pos[0], center[1] - player_pos[1])
        if width:
            self.x += difference[0]
        if height:
            self.y += difference[1]


class Redactor(RelativeLayout):
    full_scroll = False

    def __init__(self, height, width, tile_size, **kwargs):
        self.matrix = Matrix(height, width, tile_size, tile_size)
        self.manager = Manager(self.matrix)
        self.vbar = VerticalBar(self.manager, orientation='vertical', size_hint=(.1, None),
                                pos_hint={'left': 0, 'y': .1}, size_hint_min=(70, None), padding=10, y=100)
        self.hbar = HorizontalBar(self.manager, size_hint=(1, .1), pos_hint={'x': 0, 'bottom': 1},
                                  size_hint_min=(None, 65), padding=10)
        self.substrate = CoverImage(source='atlas://data/images/defaulttheme/action_bar', color=(1, 0, 1, 1))
        self.manager.redactor = self
        size = (len(self.matrix) * self.matrix.tile_width, len(self.matrix[0]) * self.matrix.tile_height)
        self.maze = Maze(self.manager, self.matrix, self, pos=(60, 60), size_hint=(None, None), size=size)
        self.scatter = MazeScatterPlane(self.maze, scale_max=1, scale_min=.25, scale=.5)
        self.WIDGETS = (self.substrate, self.scatter, self.vbar, self.hbar)
        super().__init__(**kwargs)
        self.manager.setting()
        self.bind(size=self.resize)
        self._add_widgets()
        self._set_controls()
        self.change_bar_widgets('generator')

    def _set_controls(self):
        self.scatter.add_widget(self.maze)
        # self.scatter.fbind('on_touch_up', self.scatter_transform)
        self.vbar.set_controls()
        self.hbar.set_controls()

    def _add_widgets(self):
        for widget in self.WIDGETS:
            self.add_widget(widget)

    def start(self):
        for widget in (self.hbar, self.vbar, self.manager):
            widget.start()

    def change_bar_widgets(self, mode):
        self.vbar.clear_widgets()
        self.hbar.clear_widgets()
        self.vbar.add_widgets(mode)
        self.hbar.add_widgets(mode)

    def resize(self, _=None, __=None):
        height = self.height / 10
        if height > 45:
            self.hbar.height = height
        else:
            self.hbar.height = 45
        if self.hbar.height <= 60:
            self.vbar.pos_hint.pop('y', None)
            self.vbar.y = 60
        else:
            self.vbar.pos_hint['y'] = .1
        self.vbar.height = self.height - self.hbar.height - 10
        self.scatter_transform()

    def scatter_transform(self, _=None, __=None, width=True, height=True):
        x, y = self.manager.full_scroll_pos
        if width:
            self.scatter.x_transform(x)
        if height:
            self.scatter.y_transform(y)
        self.scatter.width = self.width - y
        self.scatter.height = self.height - x

    @property
    def full_scroll_pos(self):
        if self.full_scroll:
            return self.x, self.y
        else:
            return self.vbar.width, self.hbar.height

    def make_scroll_not_full(self):
        self.add_widget(self.vbar)
        self.add_widget(self.hbar)
        self.resize()
        self.scatter_transform()
        # self.scatter.x += self.vbar.width
        # self.scatter.y += self.hbar.height

    def make_scroll_full(self):
        self.remove_widget(self.vbar)
        self.remove_widget(self.hbar)
        self.scatter_transform()
        # self.scatter.x -= self.vbar.width
        # self.scatter.y -= self.hbar.height

    def focus_on_player(self):
        player_pos = [i * self.scatter.scale for i in self.to_window(*self.maze.objects['player'].pos)]
        player_rt = (player_pos[0] + self.maze.objects['player'].width,
                     player_pos[1] + self.maze.objects['player'].height)
        player_xyrt = (*player_pos, *player_rt)
        edges_xyrt = (self.full_scroll_pos[0] - self.scatter.x, self.full_scroll_pos[1] - self.scatter.y,
                      self.right - self.scatter.x, self.top - self.scatter.y)
        if player_xyrt[0] - 20 < edges_xyrt[0] or player_xyrt[2] + 20 > edges_xyrt[2]:
            self.scatter.focus_on_player(height=False)
            self.scatter_transform(height=False)
        if player_xyrt[1] - 20 < edges_xyrt[1] or player_xyrt[3] + 20 > edges_xyrt[3]:
            self.scatter.focus_on_player(width=False)
            self.scatter_transform(width=False)
