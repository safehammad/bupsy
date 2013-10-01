import random
import string

from kivy.config import Config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.animation import  Animation
from kivy.core.audio import SoundLoader


# Number of letters in play
LETTER_COUNT = 2


def sign(x):
    """Mathematical signum."""
    if x == 0:
        return 0
    return abs(x) / x


def rand_color():
    """Return a random hue with full saturation and brightness."""
    return Color(random.random(), 1, 1, mode='hsv').rgba


class LetterGenerator(object):
    """Generate random letters with their associated sounds."""
    sounds = {letter: SoundLoader.load('data/{}.wav'.format(letter)) for letter in string.lowercase}

    @classmethod
    def next_letter(cls):
        letter = random.choice(string.lowercase)
        return letter, cls.sounds[letter]


class Letter(Label):
    """Letter widget."""
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, *args, **kwargs):
        super(Letter, self).__init__(*args, **kwargs)
        self.color = rand_color()
        self.font_name = 'DroidSans'
        self.font_size = 150
        self.bold = True
        self.size = 150, 150
        self.text, self.sound = LetterGenerator.next_letter()
        self.alive = True
        self.next_stage = 1

    def touch(self, callback):
        func = 'stage_{}'.format(self.next_stage)
        result = getattr(self, func)(callback)
        self.sound.play()
        self.next_stage += 1

    def stage_1(self, callback):
        a = Animation(font_size=self.font_size * 2, t='out_elastic', duration=0.9)
        # Resizing occurs with fixed x, y so rebase center to original location.
        old_center = self.center
        self.size = Vector(*self.size) * 2
        self.center = old_center
        a.start(self)

    def stage_2(self, callback):
        a = Animation(font_size=1, duration=0.5)
        a &= Animation(opacity=0, duration=0.5)
        a.on_complete = callback
        a.start(self)
        self.alive = False

    def move(self):
        """Move the letter one tick."""
        self.center = Vector(*self.velocity) + self.center


class BupsyGame(Widget):
    """Main window"""
    running = False

    def initialise(self):
        self.btn_start = Button(text='[color=ffffff][b]Start[/b][/color]', font_size=50, on_release=self.start, markup=True, background_color=(0.8, 0.1, 0, 1), background_normal='')
        self.btn_start.width += self.btn_start.width
        self.btn_start.center = self.width / 2, self.height / 2
        self.btn_stop = Button(text=u'[color=ffffff][b]\u03a6[/b][/color]', font_size=50, on_release=self.pause, right=self.right, y=0, markup=True, opacity=0.5, background_color=(0, 0, 0, 0))
        self.add_widget(self.btn_start)

        # Letters in play
        self.letters = []

    def start(self, w):
        self.remove_widget(self.btn_start)
        self.add_widget(self.btn_stop)
        for i in range(LETTER_COUNT):
            self.new_letter()
        self.running = True

    def pause(self, w):
        for letter in self.letters:
            self.remove_widget(letter)
        self.letters = []
        self.remove_widget(self.btn_stop)
        self.add_widget(self.btn_start)
        self.running = False

    def new_letter(self):
        letter = Letter()
        letter.velocity = random.choice([-2, 2]), random.choice([-2, 2])
        letter.center = random.randint(50, self.width - 50), random.randint(50, self.height - 50)
        self.add_widget(letter)
        self.letters.append(letter)

    def update(self, dt):
        if not self.running:
            return

        for letter in self.letters:
            letter.move()

        # Bounce ball off sides
        for letter in self.letters:
            if letter.x < self.x:
                letter.velocity_x = abs(letter.velocity_x)
            elif letter.right > self.right:
                letter.velocity_x = -abs(letter.velocity_x)
            if letter.y < self.y:
                letter.velocity_y = abs(letter.velocity_y)
            if letter.top > self.top:
                letter.velocity_y = -abs(letter.velocity_y)

    def on_touch_down(self, touch):
        super(BupsyGame, self).on_touch_down(touch)
        if not self.running:
            return
        for letter in self.letters:
            if letter.alive and letter.collide_point(*touch.pos):
                letter.touch(self.callback)

    def callback(self, letter):
        """Callback to be called when final letter interaction sequence is over."""
        self.remove_widget(letter)
        self.new_letter()


class BupsyApp(App):
    def build(self):
        Config.set('graphics', 'fullscreen', 'auto')
        self.game = BupsyGame()
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)
        return self.game

    def on_start(self):
        self.game.initialise()


if __name__ == '__main__':
    BupsyApp().run()
