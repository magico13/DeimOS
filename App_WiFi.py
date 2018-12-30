from app import App
import utils
from utils import COLORS

import pygame
from wifi import Cell, Scheme

class App_WiFi(App):
    networks = []
    dirty = False
    Run = True
    def __init__(self):
        super(App_WiFi, self).__init__()
        self.Buttons, self.Texts = utils.load(self, 'App_WiFi.json')

    def FirstDraw(self, screen):
        #Draw the background
        self.DrawBackground(screen)
        super(App_WiFi, self).FirstDraw(screen)

    def Draw(self, screen):
        worked = False
        if self.dirty: #redraw
            self.FirstDraw(screen)
            self.dirty = False
            worked = True
        worked |= super(App_WiFi, self).Draw(screen)
        return worked

    def EventLoop(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.MouseClick(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Run = False
        return

    def Scan(self, btnID):
        print('Scanning for networks')
        for s in Scheme.all():
            s.delete()
        #clear out all previous network buttons
        for button in self.Buttons:
            if button.NAME.startswith('btnNetwork'):
                self.Buttons.remove(button)
        self.networks = sorted(list(Cell.all('wlan0')), reverse=True, key=lambda x: x.signal)
        numNetworks = len(self.networks)
        for i in range(numNetworks):
            net = self.networks[i]
            button = utils.Button('btnNetwork{}'.format(i), (50, 100+i*50), (250, 40), COLORS.BLUE, '{}'.format(net.ssid), COLORS.WHITE, self.Connect, 30)
            self.Buttons.append(button)
            print('{} - {} - {} - {}'.format(i, net.ssid, net.quality, net.encrypted))
        self.dirty = True
        print('Scan complete')
        popup = utils.TextPopup('{} networks found!'.format(numNetworks), 10, 48)
        self.PopUps.append(popup)
            

    def Connect(self, btnID):
        print('Connecting')
        i = int(btnID[10:])
        print(i)
        net = self.networks[i]
        print('Network: {}'.format(net.ssid))
        #this is where we just insert it into wpa_supplicant ourselves
        #then call 'wpa_cli -i wlan0 reconfigure'

if __name__=="__main__":
    #os.environ["SDL_FBDEV"] = "/dev/fb1"
    #os.environ["SDL_MOUSEDRV"] = "TSLIB"
    #os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
    #os.environ["SDL_VIDEODRIVER"] = "fbcon"

    pygame.init()
    pygame.mouse.set_visible(True)
    screen = pygame.display.set_mode((800, 480), 0, 32)
    app = App_WiFi()
    app.FirstDraw(screen)
    pygame.display.update()
    PyClock = pygame.time.Clock()
    while app.Run:
        app.EventLoop(pygame.event.get())
        if app.Draw(screen):
            pygame.display.update()
        PyClock.tick(2)
