from math import floor
import time

from kivy.clock import Clock
from kivy.uix.popup import Popup

# from .matrix import Matrix, HexagonalMatrix
from .crutches import LineBreakBehavior
from .popups import WinPopup


class Manager:
    LANGUAGES = ('English', 'Français', 'Italiano', 'Deutsch', 'Español', 'Português', 'Русский', 'Svenska')
    LANGUAGE_DICTIONARY = {
        'language': ('Language', 'Langue', 'Lingua', 'Sprache', 'Lengua', 'Língua', 'Язык', 'Språk'),
        'win': ('You win!', 'Vous gagnez!', 'Vinci!', 'Du gewinnst!',
                'Tú ganas!', 'Você ganha!', 'Вы выиграли!', 'Du vinner!'),
        'stop': ('Stop', 'Pause', 'Pausa', 'Pause', 'Pausa', 'Pausa', 'Пауза', 'Paus'),
        'continue': ('Continue', 'Continuer', 'Continuare', 'Fortsetzen',
                     'Continuar', 'Continuar', 'Продолжить', 'Fortsätta'),
        'choose color': ('Choose color', 'Choisir la couleur', 'Scegliere il colore', 'Farbe auswählen',
                         'Elegir el color', 'Escolher cor', 'Выберите цвет', 'Välj färg'),
        'choose landscape': ('Choose landscape', 'Choisir le terrain', 'Scegliere il territorio',
                             'Landschaft auswählen', 'Elegir el terreno', 'Escolher terreno', 'Выберите местность',
                             'Välj landskap'),
        'choose skin': ('Choose skin', 'Choisir le personnage', 'Scegliere il personaggio', 'Charakter auswählen',
                        'Elegir el personaje', 'Escolher personagem', 'Выберите персонажа', 'Välj personlighet'),
        'game mod': ('Game mode', 'Mode de jeu', 'Modalità di gioco', 'Spielmodus',
                     'Modo de juego', 'Modo do jogo', 'Режим игры', 'Spelläge'),
        'exit game mod': ('Exit game mode', 'Quitter mode de jeu', 'Esci dal gioco', 'Spiel beenden',
                          'Salir del juego', 'Sair do jogo', 'Выйти из режима игры', 'Avsluta spelläge'),
        'angles 0': ('angles', 'angles', 'angoli', 'winkeln', 'àngulos', 'ângulos', 'угла', 'vinklar'),
        'angles 1': ('angles', 'angles', 'angoli', 'winkeln', 'àngulos', 'ângulos', 'углов', 'vinklar'),
        'width': ('Width', 'Largeur', 'Larghezza', 'Breite', 'Anchura', 'Largura', 'Ширина', 'Bredd'),
        'height': ('Height', 'Hauteur', 'Altezza', 'Höhe', 'Altura', 'Altura', 'Высота', 'Höjd'),
        'color': ('Color', 'Couleur', 'Colore', 'Farbe', 'Color', 'Cor', 'Цвет', 'Färg'),
        'prison': ('Prison', 'Prison', 'Prigione', 'Gefängnis', 'Prisión', 'Prisão', 'Темница', 'Fängelse'),
        'pit': ('Pit', 'Trous', 'Fossa', 'Grube', 'Fosa', 'Fosso', 'Норы', 'Grop'),
        'storage': ('Storage', 'Entrepôt', 'Stoccaggio', 'Lagerhaus', 'Almacenamiento', 'Entreposto', 'Склад', 'Lager'),
        'green_maze': ('Green maze', 'Labyrinthe vert', 'Labirinto verde', 'Grünes Labyrinth',
                       'Laberinto verde', 'Labirinto verde', 'Зелёный лабиринт', 'Grön labyrint'),
        'highway': ('Highway', 'Autoroute', 'Pista', 'Autobahn', 'Autopista', 'Estrada', 'Трасса', 'Spår'),
        'random': ('Random', 'Aléatoire', 'Casuale', 'Zufällig', 'Aleatorio', 'Aleatório', 'Случайный', 'Slumpmässig'),
        'choose': ('Choose', 'Choisir', 'Scegliere', 'Auswählen', 'Elegir', 'Escolher', 'Выбрать', 'Välja'),
        'reload': ('Reload', 'Recharger', 'Ricaricare', 'Nachladen',
                   'Recargar', 'Recarregar', 'Перезагрузить', 'Ladda om'),
        'settings': ('Settings', 'Paramètres', 'Impostazioni', 'Einstellungen',
                     'Configuraciones', 'Parâmetros', 'Настройки', 'Inställningar'),
        'cancel': ('Cancel', 'Annuler', 'Annullare', 'Abbrechen', 'Anular', 'Anular', 'Отмена', 'Annullera'),
        'again': ('Play again', 'Encore une fois', 'Di nuovo', 'Wieder', 'De nuevo', 'De novo', 'Играть ещё', 'Igen'),
        'score': ('Score', 'Résultat', 'Resultato', 'Resultat', 'Resultado', 'Resultado', 'Счёт', 'Resultat'),
        'time': ('Time', 'Temps', 'Tempo', 'Zeit', 'Tiempo', 'Tempo', 'Время', 'Tid'),
        'record': ('New record', 'Nouveau record', 'Nuovo record', 'Neuer Rekord',
                   'Nuevo récord', 'Novo recorde', 'Новый рекорд', 'Nytt rekord')
    }

    app = None
    redactor = None
    hbar = None
    vbar = None
    maze = None
    full_scroll = False
    time = None
    timer = None
    timer_stop = False
    win_popup = WinPopup(size_hint=(None, None), size=(270, 400))

    def __init__(self, matrix):
        self.matrix = matrix

    def start(self):
        self.hbar.x_slider.bind(value=self.refresh_slider_label)
        self.vbar.y_slider.bind(value=self.refresh_slider_label)
        self.hbar.x_slider.value = len(self.matrix[0])
        self.vbar.y_slider.value = len(self.matrix)
        self.localize()
        self.hbar.on_background_color()

    def lng(self, key):
        language = self.app.config.get('user data', 'language')
        index = self.LANGUAGES.index(language)
        return self.LANGUAGE_DICTIONARY[key][index]

    def setting(self):
        self.maze.fbind('on_touch_up', self.maze_touch_up)
        self.hbar.game_btn.on_release = self.game
        self.hbar.generator_btn.on_release = self.game
        self.hbar.stop_btn.on_release = self.stop_or_continue
        self.win_popup.to_generator_btn.on_release = self.to_generator
        self.win_popup.again_btn.on_release = self.play_again
        # self.hbar.angle_spinner.bind(text=self.change_angles)
        self.redactor.scatter.fbind('on_touch_up', self.scatter_transform)

    def localize(self):
        texts = self._localize_dict()
        for widget, key in texts.items():
            if isinstance(widget, Popup):
                widget.title = self.lng(key)
            elif isinstance(widget, LineBreakBehavior):
                widget.real_text = self.lng(key)
            else:
                widget.text = self.lng(key)
        # values = (f"4 {self.lng('angles 0')}", f"6 {self.lng('angles 1')}")
        # self.hbar.angle_spinner.text = f"4 {self.lng('angles 0')}"
        # self.hbar.angle_spinner.values = values
        self.refresh_slider_label(self.hbar.x_slider, self.hbar.x_slider.value)
        self.refresh_slider_label(self.vbar.y_slider, self.vbar.y_slider.value)
        # print(self.app.config.write())

    def _localize_dict(self):
        land_sublayouts = self.hbar.landscape_popup.content.children
        dct = {
            self.hbar.stop_btn: 'stop',
            self.hbar.generator_btn: 'exit game mod',
            self.hbar.settings_btn: 'settings',
            self.hbar.game_btn: 'game mod',
            self.vbar.color_btn: 'color',
            self.hbar.landscape_btn: 'prison',
            self.vbar.color_popup: 'choose color',
            self.hbar.landscape_popup: 'choose landscape',
            # self.hbar.skin_popup: 'choose skin',
            self.win_popup: 'win',
            self.win_popup.again_btn: 'again',
            self.win_popup.to_generator_btn: 'exit game mod',
            self.vbar.color_popup.random_btn: 'random',
            self.vbar.color_popup.choose_btn: 'choose',
            land_sublayouts[0].children[1]: 'highway',
            land_sublayouts[1].children[1]: 'green_maze',
            land_sublayouts[2].children[1]: 'storage',
            land_sublayouts[3].children[1]: 'prison',
            land_sublayouts[4].children[1]: 'pit',
            self.hbar.reload_btn: 'reload'
        }
        return dct

    def scatter_transform(self, _=None, __=None):
        if not self.matrix.game:
            self.redactor.scatter_transform()

    @property
    def full_scroll_pos(self):
        if self.full_scroll:
            return self.redactor.x, self.redactor.y
        else:
            return self.vbar.width, self.hbar.height

    def refresh_slider_label(self, slider, value):
        if slider == self.hbar.x_slider:
            width = self.lng('width')
            self.hbar.x_slider_label.text = f'{width}: {value}'
        elif slider == self.vbar.y_slider:
            height = self.lng('height')
            self.vbar.y_slider_label.text = f'{height}: {value}'
            texture = self.vbar.y_slider_label.texture
            if texture:
                print(self.vbar.y_slider_label.texture_size)
                # texture.mag_filter = texture.min_filter = 'nearest'

    def init_score_label(self):
        tiles_count = len(self.matrix) * len(self.matrix[0])
        score = self.app.config.getdefault('scores', str(tiles_count), '23:59:59')
        record_t = time.strptime(score, '%H:%M:%S')
        current_t = time.strptime(self.time, '%H:%M:%S')
        record_str = f'\n{self.lng("record")}!' if current_t < record_t else ''
        text = f'{self.lng("time")}: {self.vbar.timer_lbl.text}{record_str}'
        self.win_popup.score_lbl.text = text
        if record_str:
            self.app.config.set('scores', str(tiles_count), self.time)
            self.app.config.write()

    def to_generator(self):
        self.game()
        self.win_popup.dismiss()
        self.timer_stop = False

    def play_again(self):
        self.win_popup.dismiss()
        # self.redactor.change_bar_widgets('game')
        self.timer_stop = False
        self.reload()
        self.timer_stop = False
        self.start_timer()

    def maze_touch_up(self, _, touch):
        # print(touch)
        if self.matrix.game and not self.timer_stop:
            self._game_maze_touch(touch)
        elif touch.is_double_tap:
            if self.full_scroll:
                self.redactor.make_scroll_not_full()
                self.full_scroll = False
            else:
                self.redactor.make_scroll_full()
                self.full_scroll = True

    def _game_maze_touch(self, touch):
        x = floor(touch.x / self.matrix.tile_width)
        y = floor(touch.y / self.matrix.tile_height)
        orientation = self.matrix.move_orientation(x, y)
        if orientation:
            while (y, x) != self.matrix.player:
                self.move(orientation)
                if self.matrix.player == self.matrix.get_coords(self.matrix.exit):
                    self.win()
                    break

    def win(self):
        self.timer_stop = True
        self.init_score_label()
        self.win_popup.open()

    def move(self, orientation):
        self.maze.move(orientation)
        self.redactor.focus_on_player()

    def reload(self):
        height = self.vbar.y_slider.value
        width = self.hbar.x_slider.value
        self.maze.reload(height, width)
        self.redactor.scatter.size = self.maze.size
        self.redactor.scatter_transform()
        self.app.config.setall('user data', {'height': height, 'width': width})
        self.app.config.write()

    def recolor(self, color):
        for widget in (self.hbar.reload_btn, self.vbar, self.hbar, self.hbar.landscape_popup, self.win_popup,
                       self.vbar.color_popup, self.hbar.settings_popup):
            widget.background_color = color

    def game(self, _=None, __=None):
        if self.matrix.game:
            self.redactor.change_bar_widgets('generator')
            self.maze.game()
            self.redactor.scatter_transform()
        else:
            self.redactor.change_bar_widgets('game')
            self.maze.reload()
            self.maze.game()
            self.redactor.scatter.focus_on_player()
            self.redactor.scatter_transform(width=False)
            self.refresh_sliders()
            self.start_timer()

    def refresh_sliders(self):
        self.vbar.y_slider.value = len(self.matrix)
        self.hbar.x_slider.value = len(self.matrix[0])

    # def change_angles(self, _, text):
    #     classes = {4: Matrix, 6: HexagonalMatrix}
    #     matrix_cls = classes[int(text[0])]
    #     self.change_matrix(matrix_cls)
    #     self.maze.reload()
    #     self.maze.draw()
    #     self.refresh_sliders()

    def change_matrix(self, matrix_cls):
        height, width = len(self.matrix), len(self.matrix[0])
        tile_height, tile_width = self.matrix.tile_height, self.matrix.tile_width
        self.matrix = matrix_cls(height, width, tile_height, tile_width)
        self.maze.matrix = self.redactor.matrix = self.matrix

    def start_timer(self):
        start = time.time()
        stop_moment = None
        stop_time = 0

        def timer_callback(_):
            nonlocal stop_moment, stop_time
            if self.timer_stop:
                if not stop_moment:
                    stop_moment = time.time()
            else:
                end = time.time()
                if stop_moment:
                    stop_time += end - stop_moment
                    stop_moment = None
                time_in_game = (end - start) - stop_time
                struct_time = time.gmtime(time_in_game)
                self.time = time.strftime(f'%H:%M:%S', struct_time)
                self.vbar.timer_lbl.text = self.time

        self.timer = Clock.schedule_interval(timer_callback, 0.01)

    def stop_or_continue(self, _=None, __=None):
        stop, cont = self.lng('stop'), self.lng('continue')
        switch = {stop: cont, cont: stop}
        self.hbar.stop_btn.text = switch[self.hbar.stop_btn.text]
        self.timer_stop = not self.timer_stop
        self.maze.pause_mod = not self.maze.pause_mod
        self.maze.draw()
