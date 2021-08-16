import random as r

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
from kivy.properties import ListProperty

from .matrix import Matrix, HexagonalMatrix


class Maze(Widget):
    main_color = ListProperty()
    pause_mod = False
    color_group = None
    color = False
    area_colors = None
    landscape = 'prison'
    player_source = './images/players/escaped.png'
    objects = {'player': None, 'finish': None}
    sources = {'player': './images/players/escaped.png', 'finish': './images/finish.png'}
    player_sources = {}

    def __init__(self, manager, matrix, redactor, **kwargs):
        self.manager, self.matrix, self.redactor = manager, matrix, redactor
        self.manager.maze = self
        super().__init__(**kwargs)
        self._set_size()
        self.recolor()
        self.switch_paint()

    def _set_size(self):
        if self.matrix_type == 4:
            self.width = len(self.matrix[0]) * self.matrix.tile_width
            self.height = len(self.matrix) * self.matrix.tile_height
        elif self.matrix_type == 6:
            self.width = len(self.matrix[0]) * self.matrix.tile_width * 1.3 + self.matrix.tile_width * .66667
            self.height = len(self.matrix) * self.matrix.tile_height + self.matrix.tile_height * 0.25

    @property
    def matrix_type(self):
        if type(self.matrix) == Matrix:
            return 4
        elif type(self.matrix) == HexagonalMatrix:
            return 6

    def on_main_color(self, _, __):
        color = [*self.main_color[:3], 1]
        self.manager.recolor(color)

    @staticmethod
    def get_color():
        color = r.random(), r.random(), r.random()
        while sum(color) < 1.5:
            color = r.random(), r.random(), r.random()
        return color

    @staticmethod
    def memorized_color(color):
        return tuple([i / 2 for i in color])

    def _add_area_colors(self):
        self.area_colors = []
        for _ in self.matrix.areas:
            area_color = self.get_color()
            self.area_colors.append(area_color)

    def draw(self):
        self.clear_widgets()
        self.canvas.before.clear()
        self._draw_matrix()
        if self.matrix.player:
            self.add_object('player')
        if self.matrix.exit:
            if self.matrix.get_coords(self.matrix.exit) in self.matrix.visible:
                self.add_object('finish')
            # elif self.matrix.get_coords(self.matrix.exit) in self.matrix.memorized:
            #     pass
        self._remove_color()

    def _remove_color(self):
        if self.color:
            self.color_group = self.canvas.before.get_group('color')
            self.canvas.before.remove_group('color')
        else:
            self.canvas.before.remove_group('main')

    def _draw_matrix(self):
        for i, area in enumerate(self.matrix.areas):
            area_color = self.area_colors[i]
            for tile in area:
                if self.matrix.game:
                    if tile.pos in self.matrix.visible:
                        self._draw_tile(tile, area_color)
                    elif tile.pos in self.matrix.memorized:
                        self._draw_tile(tile, area_color, True)
                else:
                    self._draw_tile(tile, area_color)

    def _draw_tile(self, tile, _, memorized=False):
        with self.canvas.before:
            main = self.main_color
            if memorized:
                main = self.memorized_color(main)
            if self.pause_mod:
                main = self.memorized_color(main)
            Color(*main, group='main')
            pos = self.get_tile_pos(tile)
            source = f'atlas://images/{self.landscape}_atlas/tile_{tile.name}'
            # source = f'./images/storage/test.png'
            Rectangle(size=tile.size, pos=pos, source=source, group='tiles')

    def get_tile_pos(self, tile):
        if self.matrix_type == 4:
            return tile.x * self.matrix.tile_width, tile.y * self.matrix.tile_height
        elif self.matrix_type == 6:
            return tile.x * self.matrix.tile_width * 1.3, tile.y * self.matrix.tile_height

    def add_object(self, string):
        object = {
            'player': self.matrix.player,
            'finish': self.matrix.exit
        }[string]
        pos = self.get_object_pos(object)
        if self.objects[string]:
            self.objects[string].pos = pos
        else:
            color = (.5, .5, .5, 1) if self.pause_mod else (1, 1, 1, 1)
            size = (self.matrix.tile_height, self.matrix.tile_width)
            texture = Image(source=self.sources[string]).texture
            texture.mag_filter = texture.min_filter = 'nearest'
            self.objects[string] = Image(size=size, pos=pos, color=color, allow_stretch=True,
                                         texture=self.get_sharp_texture(self.sources[string]))
        self.add_widget(self.objects[string])

    @staticmethod
    def get_sharp_texture(source):
        texture = Image(source=source).texture
        texture.mag_filter = texture.min_filter = 'nearest'
        return texture

    def get_object_pos(self, object):
        tile_width = self.matrix.tile_width
        tile_height = self.matrix.tile_height
        object_pos = self.matrix.get_coords(object)
        width = object_pos[1] * tile_width
        height = object_pos[0] * tile_height
        return width, height

    def _add_labels(self):
        for i, line in enumerate(self.matrix):
            for j, tile in enumerate(line):
                pos = (j * self.matrix.tile_height + 25, i * self.matrix.tile_width + 25)
                label = Label(pos=pos, text=f'{i}:{j}', size_hint=(None, None), font_size='10sp')
                self.add_widget(label)

    def reload(self, height=None, width=None):
        self.matrix.reload(height, width)
        self._set_size()
        self.objects['player'] = None
        self._add_area_colors()
        self.draw()

    def game(self):
        self.matrix.play()
        self.draw()

    def recolor(self):
        self.main_color = self.get_color()
        self._add_area_colors()
        # self.draw()

    def move(self, orientation):
        index = ('top', 'right', 'down', 'left').index(orientation)
        self.matrix.move(index)
        self.draw()

    def switch_paint(self, _=None, __=None):
        if self.color:
            self.canvas.before.clear()
            self.clear_widgets()
            if self.matrix.player:
                self.add_object('player')
            else:
                self.remove_widget(self.objects['player'])
            self._draw_matrix()
            self.canvas.before.remove_group('main')
            self.color = False
        else:
            self.canvas.before.clear()
            if self.matrix.player:
                self.add_object('player')
            else:
                self.remove_widget(self.objects['player'])
            self._draw_matrix()
            self.color_group = self.canvas.before.get_group('color')
            self.canvas.before.remove_group('color')
            self.color = True
