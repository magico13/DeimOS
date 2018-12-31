from app import App
import utils
from utils import COLORS
import pygame
from pygame.locals import *

class App_Keyboard(App):
    Initialized = False
    Text = ''
    Complete = False
    Cancelled = False
    #map numbers/specials to their shifted versions
    CharMap = {
        '1': '!',
        '2': '@',
        '3': '#',
        '4': '$',
        '5': '%',
        '6': '^',
        '7': '&',
        '8': '*',
        '9': '(',
        '0': ')',
        '`': '~',
        '-': '_',
        '=': '+',
        '[': '{',
        ']': '}',
        '\\': '|',
        ';': ':',
        '\'': '"',
        ',': '<',
        '.': '>',
        '/': '?'
    }
    
    def __init__(self, prompt=''):
        global Cancelled
        global Text
        super(App_Keyboard, self).__init__()
        self.Buttons, self.Texts = utils.load(self, 'App_Keyboard.json')
        self.text = ''
        self.shift = False
        self.dirty = False
        self.Cancelled = False
        self.Text = ''
        self.GetTxtByID('txtPrompt').SetText(prompt)

    def FirstDraw(self, screen):
        #Draw the background
        self.DrawBackground(screen, COLORS.CYAN)
        entryBox = pygame.Surface((780, 50))
        entryBox.fill(COLORS.WHITE)
        screen.blit(entryBox, (10, 40))
        super(App_Keyboard, self).FirstDraw(screen)
        self.Initialized = True

    def Draw(self, screen):
        worked = super(App_Keyboard, self).Draw(screen)
        if self.dirty:
            self.dirty = False
            self.FirstDraw(screen)
            worked = True
        return worked    

    def EventLoop(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.MouseClick(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                key = event.key
                unic = event.unicode
                if (key == K_BACKSPACE):
                    self.text = self.text[:-1] #remove the last part
                elif (key == K_RETURN):
                    self.text += '\n'
                else:
                    self.text += unic
                self.dirty = True
                self.GetTxtByID('txtEntry').SetText(self.text)

    def key_press(self, btnID):
        split = btnID.split('_')
        if len(split) > 1:
            key = split[1] #bksp, enter, (r)shift, space
            if key == 'space': self.text += ' '
            elif key == 'enter': self.text += '\n'
            elif key == 'bksp': self.text = self.text[:-1] #remove the last character
            elif key == 'shift' or key == 'rshift': self.toggle_shift()
        else:
            #regular keys, like q w e r t y
            char = btnID[-1:] #take the last letter from the name
            if self.shift: char = self.get_shifted(char)
            self.text += char
        self.GetTxtByID('txtEntry').SetText(self.text)
        self.dirty = True
    
    def get_shifted(self, char):
        if char.isalpha(): char = char.upper()
        else:
            #numbers/characters get turned to special characters
            if char in self.CharMap:
                char = self.CharMap[char]
        return char
    
    def toggle_shift(self):
        self.shift = not self.shift #toggle shift
        self.GetButtonByID('btn_shift').COLOR = COLORS.RED if self.shift else COLORS.BLACK
        self.GetButtonByID('btn_rshift').COLOR = COLORS.RED if self.shift else COLORS.BLACK
        for button in self.Buttons:
            if button.OnClick != self.key_press: continue
            split = button.NAME.split('_')
            if len(split) == 1:
                char = button.NAME[-1:]
                if self.shift: char = self.get_shifted(char)
                button.TXT = char

    def cancel(self, btnID):
        print('Cancelled')
        self.Complete = True
        self.Cancelled = True
        #return to previous state

    def accept(self, btnID):
        self.Complete = True
        self.Text = self.text

if __name__=="__main__":
  #os.environ["SDL_FBDEV"] = "/dev/fb1"
  #os.environ["SDL_MOUSEDRV"] = "TSLIB"
  #os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
  #os.environ["SDL_VIDEODRIVER"] = "fbcon"

  pygame.init()
  screen = pygame.display.set_mode((800, 480), 0, 32)
  app = App_Keyboard('Enter some text!')
  app.FirstDraw(screen)
  PyClock = pygame.time.Clock()
  while True:
    app.EventLoop(pygame.event.get())
    app.Draw(screen)
    pygame.display.update()
    PyClock.tick(10)
