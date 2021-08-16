import random as r
import math
import time


def time_wrap(function):
    def wrapper(self, *args, **kwargs):
        start = time.time()
        function(self, *args, **kwargs)
        end = time.time()
        print(f'Function "{function.__name__}", time = {end - start}')
    return wrapper


class Matrix(list):
    enter = None
    game = False
    exit = None
    player = None
    visible = set()
    memorized = set()
    areas = []
    wall_indexes = {0: 2, 1: 3, 2: 0, 3: 1}
    orientation_coefficients = ((1, 0), (0, 1), (-1, 0), (0, -1))

    def __init__(self, height, width, tile_height, tile_width):
        self.tile_height, self.tile_width = tile_height, tile_width
        super().__init__()
        self._create_walls_1(height, width)
        self.generate_function = self._create_walls_1

    # @staticmethod
    # def get_tiles(_iter):
    #     kind = type(_iter)
    #     filtered = [i for i in _iter if type(i) == Tile]
    #     return kind(filtered)

    def _build(self, height, width, default=None):
        for i in range(height):
            lst = list()
            for j in range(width):
                lst.append(Tile(j, i, height=self.tile_height, width=self.tile_width, default=default))
            self.append(lst)

    def _create_walls_1(self, height, width):
        self._build(height, width, True)
        self.enter = r.choice(self[0])
        self._generate()
        # time_wrap(self._find_closed)
        self.areas = [[tile for line in self for tile in line]]

    # @time_wrap
    def _generate(self):
        unvisited = {tile for line in self for tile in line}
        stack = [self.enter]
        big = 1
        while unvisited:
            adjoining_unvisited = self._find_adjoining_unvisited(stack[-1], unvisited)
            if adjoining_unvisited:
                orientation, next_tile = r.choice(list(adjoining_unvisited.items()))
                self._set_wall(*stack[-1].pos, orientation, False)
                unvisited.discard(next_tile)
                stack.append(next_tile)
            else:
                if len(stack) > big:
                    big = len(stack)
                    self.exit = stack[-1]
                stack.pop()

    def _find_adjoining_unvisited(self, tile, unvisited):
        adjoining_unvisited = {}
        for i, wall in enumerate(tile.walls):
            neighbour = self._find_neighbour(*tile.pos, i)
            if neighbour and neighbour in unvisited:
                adjoining_unvisited[i] = neighbour
        return adjoining_unvisited

    def _create_walls_0(self, height, width):
        self._build(height, width)
        self._create_box()
        self._randomize_walls()
        self._find_closed()
        self.enter = r.choice(self[0])
        self.exit = r.choice(self[-1])

    def _create_box(self):
        for i, _ in enumerate(self[0]):
            self._set_wall(0, i, 2)
        for i, _ in enumerate(self[-1]):
            self._set_wall(-1, i, 0)
        for i, _ in enumerate(self):
            self._set_wall(i, 0, 3)
            self._set_wall(i, -1, 1)

    def _randomize_walls(self):
        for i, line in enumerate(self):
            for j, tile in enumerate(line):
                walls = tile.walls
                if any([i is None for i in walls]):
                    nones = [i for i, v in enumerate(walls) if v is None]
                    for none in nones:
                        self._set_wall(i, j, none, r.choice((True, False)))

    def _set_wall(self, height, width, orientation, wall=True):
        tile_row = self[height]
        tile_row[int(width)].walls[orientation] = wall
        neighbour = self._find_neighbour(height, width, orientation)
        if neighbour:
            neighbour_index = self.wall_indexes[orientation]
            neighbour.walls[neighbour_index] = wall

    def _find_neighbour(self, height, width, orientation):
        try:
            neighbour_pos = self._find_neighbour_pos(height, width, orientation)
            neighbour = self.get_tile(neighbour_pos)
            return neighbour
        except IndexError:
            return None

    def _find_neighbour_pos(self, height, width, orientation):
        coefficient = self.orientation_coefficients[orientation]
        neighbour_coords = (height + coefficient[0], round(width + coefficient[1]))
        neighbour_coords = tuple(map(int, neighbour_coords))
        bad_conditions = (
            neighbour_coords[0] + height == -1,
            neighbour_coords[1] + int(width) == -1,
            neighbour_coords[0] > len(self) - 1,
            neighbour_coords[1] > len(self[0]) - 1
        )
        if any(bad_conditions):
            raise IndexError
        return neighbour_coords

    def _find_closed(self):
        areas = []
        for i, line in enumerate(self):
            for j, tile in enumerate(line):
                if tile not in [a for b in areas for a in b]:
                    area = self._get_area(i, j, [tile])
                    # area_color = (r.random(), r.random(), r.random())
                    areas.append(area)
        self.areas = areas

    def _get_area(self, i, j, layer):
        new_tiles = []
        for tile in layer:
            for orientation, wall in enumerate(tile.walls):
                neighbour = self._check_neighbour(layer, new_tiles, tile, orientation)
                if neighbour:
                    new_tiles.append(neighbour)
        if new_tiles:
            layer.extend(new_tiles)
            self._get_area(i, j, layer)
        return layer

    def _check_neighbour(self, layer, new_tiles, tile, orientation):
        if not tile.walls[orientation]:
            neighbour = self._find_neighbour(tile.y, tile.x, orientation)
            if neighbour and neighbour not in [*layer, *new_tiles]:
                return neighbour

    def reload(self, height, width):
        if not height:
            height = len(self)
        if not width:
            width = len(self[0])
        self.clear()
        self.visible.clear()
        self.memorized.clear()
        self.generate_function(height, width)
        if self.game:
            self._play()

    def play(self):
        if self.game:
            self.destroy_game()
        else:
            self._play()

    def _play(self):
        self.game = True
        self.enter = r.choice(self[0])
        self.exit = r.choice(self[-1])
        self.player = self.enter.pos
        self.enter.walls[2] = False
        self.exit.walls[0] = False
        # while not self.enter_area in self.exit_area:
        # for i in range(20):
        #     self.unite_areas()
        self.refresh_memorized()

    def unite_areas(self):
        area_copy = self.enter_area[:]
        r.shuffle(area_copy)
        for tile in area_copy:
            self._unite_first_possible(tile, self.enter_area)
            break
        self._find_closed()
        pass

    def _unite_first_possible(self, tile, area):
        for i, wall in enumerate(tile.walls):
            if wall:
                neighbour = self._find_neighbour(*tile.pos, i)
                if neighbour:
                    if neighbour not in area:
                        self._set_wall(*tile.pos, i, False)
                        break
                else:
                    continue

    @property
    def enter_area(self):
        return [area for area in self.areas if self.enter in area][0]

    @property
    def exit_area(self):
        return [area for area in self.areas if self.exit in area][0]

    def refresh_memorized(self):
        self.refresh_visible()
        self.memorized |= self.visible

    def refresh_visible(self):
        self.visible.clear()
        self.visible.add(self.player)
        player_tile = self.get_tile(self.player)
        possible_orientations = [i for i, wall in enumerate(player_tile.walls) if not wall]
        for i in possible_orientations:
            line = self._get_visible_line(i)
            self.visible = self.visible.union(line)
    
    def _get_visible_line(self, orientation):
        line = [self.player]
        last = self.get_tile(line[-1])
        while not last.walls[orientation]:
            try:
                neighbour = self._find_neighbour_pos(*line[-1], orientation)
                if neighbour:
                    line.append(neighbour)
                    last = self.get_tile(line[-1])
            except IndexError:
                break
        return line

    def destroy_game(self):
        self.game = False
        self.enter.walls[2] = True
        if self.exit:
            self.exit.walls[0] = True
            self.exit = None
        self.player = None

    def get_tile(self, tile):
        # width = int(tpl[1]) if type(tpl) == int else int(tpl[1]) + 1
        if type(tile) == tuple:
            return self[tile[0]][int(tile[1])]
        else:
            return tile

    @staticmethod
    def get_coords(tile):
        if type(tile) == tuple:
            return tile
        else:
            return tile.pos

    # @staticmethod
    # def rd(x, y=0):
    #     m = int('1' + '0' * y)
    #     q = x * m
    #     c = int(q)
    #     i = int((q - c) * 10)
    #     if i >= 5:
    #         c += 1
    #     return int(c / m)

    def move_orientation(self, x, y):
        if self._check_move(x, y):
            difference_x = x - self.player[1]
            difference_y = y - self.player[0]
            all_zeroes = all((difference_x == 0, difference_y == 0))
            all_not_zeroes = all((difference_x != 0, difference_y != 0))
            if not all_zeroes and not all_not_zeroes:
                orientations = {difference_x == 0 and difference_y > 0: 'top',
                                difference_x > 0 and difference_y == 0: 'right',
                                difference_x == 0 and difference_y < 0: 'down',
                                difference_x < 0 and difference_y == 0: 'left'}
                return orientations[True]

    def _check_move(self, x, y):
        try:
            self[y][x]
        except IndexError:
            return
        if self[y][x].pos in self.visible:
            return True

    def move(self, orientation):
        player_tile = self.get_tile(self.player)
        if not player_tile.walls[orientation]:
            try:
                neighbour = self._find_neighbour_pos(self.player[0], self.player[1], orientation)
                if neighbour:
                    self.player = neighbour
            except IndexError:
                if player_tile == self.exit:
                    return 'win'
                elif player_tile == self.enter:
                    pass
        self.refresh_memorized()


class HexagonalMatrix(Matrix):
    tile_height = 40
    tile_width = 40
    wall_indexes = {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
    # orientation_coefficients = ((1, 0.5), (0, 1), (-1, 0.5), (-1, -0.5), (0, -0.5), (1, -0.5))
    orientation_coefficients = ((1, 0.5), (0, 1), (-1, 0.5), (-1, -1), (0, -1), (1, -1))

    # def get_tile(self, tpl):
    #     # width = int(tpl[1]) if type(tpl) == int else int(tpl[1]) + 1
    #     return self[tpl[0]][int(tpl[1])]

    def _build(self, height, width, default=None):
        for i in range(height):
            lst = list()
            # if i % 2:
            #     lst.append('left edge wall')
            for j in range(width):
                tile_width = j + 0.5 if i % 2 else j
                lst.append(Tile(tile_width, i, 6, 40, 40, default))
            # if not i % 2:
            #     lst.append('right edge wall')
            self.append(lst)
        self.size = (width * 40, height * 40)

    def _create_walls_1(self, height, width):
        self._build(height, width, True)
        self.enter = r.choice(self[0])
        # time_wrap(self._generate)
        # time_wrap(self._find_closed)
        self.test()
        self.areas = [[tile for line in self for tile in line]]

    # def _create_box(self):
    #     for i, _ in enumerate(self[0]):
    #         self._set_wall(0, i, 2)
    #         self._set_wall(0, i, 3)
    #     for i, _ in enumerate(self[-1]):
    #         self._set_wall(-1, i, 0)
    #         self._set_wall(-1, i, 5)
    #     for i, _ in enumerate(self):
    #         self._set_wall(i, 0, 4)
    #         self._set_wall(i, -1, 1)
    #         if not i % 2:
    #             self._set_wall(i, 0, 3)
    #             self._set_wall(i, 0, 5)
    #         else:
    #             self._set_wall(i, -1, 0)
    #             self._set_wall(i, -1, 2)
    #     self.test()

    def test(self):
        for i in range(6):
            self._set_wall(5, 5, i, False)
            self._set_wall(10, 10, i, False)
            # neighbour_coords = self._find_neighbour(5, 5, i)
            # neighbour = self.get_tile(neighbour_coords)
            # neighbour.walls = [True, True, True, True, True, True]
            # neighbour_coords = self._find_neighbour(10, 10, i)
            # neighbour = self.get_tile(neighbour_coords)
            # neighbour.walls = [True, True, True, True, True, True]


class Tile:
    def __init__(self, x, y, kind=4, height=30, width=30, default=None):
        self.x, self.y, self.kind, *self.size = x, y, kind, height, width
        self.walls = [default for _ in range(kind)]

    def __repr__(self):
        return f'Tile {self.x}:{self.y}'

    @property
    def pos(self):
        return self.y, self.x

    @property
    def name(self):
        string = ''.join([str(int(bool(i))) for i in self.walls])
        return string

    @property
    def sources(self):
        strings = [str(int(bool(i))) for i in self.walls]
        line_strings = [f"./images/{'_' * i}{string}{'_' * (3 - i)}.png" for i, string in enumerate(strings)]
        return line_strings
