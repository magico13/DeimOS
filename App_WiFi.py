from app import App
import utils
from utils import COLORS
from App_Keyboard import App_Keyboard

import pygame
from wifi import Cell, Scheme
from subprocess import call
import traceback

class App_WiFi(App):
    networks = []
    Run = True
    Keyboard = None
    def __init__(self):
        super(App_WiFi, self).__init__()
        self.Buttons, self.Texts = utils.load(self, 'App_WiFi.json')
        self.dirty = False
        self.ssid = ''
        self.passkey = ''
        self.encrypted = False

    def FirstDraw(self, screen):
        #Draw the background
        self.DrawBackground(screen)
        self.GetButtonByID('btnConnect').SetVisible(self.validate())
            
        super(App_WiFi, self).FirstDraw(screen)

    def Draw(self, screen):
        if self.Keyboard != None:
            if not self.Keyboard.Initialized:
                self.Keyboard.FirstDraw(screen)
                return True
            return self.Keyboard.Draw(screen)
        worked = False
        if self.dirty: #redraw
            self.FirstDraw(screen)
            self.dirty = False
            worked = True
        worked |= super(App_WiFi, self).Draw(screen)
        return worked

    def EventLoop(self, events):
        if self.Keyboard != None:
            self.Keyboard.EventLoop(events)
            if self.Keyboard.Complete:
                if not self.Keyboard.Cancelled: 
                    self.passkey = self.Keyboard.Text
                    self.GetTxtByID('txtPass').SetText('*'*len(self.passkey))
                    print('Passkey: {}'.format(self.passkey))
                self.Keyboard = None
                self.dirty = True
            return
            
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
            button = utils.Button('btnNetwork{}'.format(i), (50, 100+i*50), (250, 40), COLORS.BLUE, '{}{}'.format('{E}' if net.encrypted else '', net.ssid), COLORS.WHITE, self.Select, 30)
            self.Buttons.append(button)
            print('{} - {} - {} - {}'.format(i, net.ssid, net.quality, net.encrypted))
        self.dirty = True
        print('Scan complete')
        popup = utils.TextPopup('{} networks found!'.format(numNetworks), 10, 48)
        self.PopUps.append(popup)
            

    def Select(self, btnID):
        i = int(btnID[10:])
        print(i)
        net = self.networks[i]
        print('Selected Network: {}'.format(net.ssid))
        self.ssid = net.ssid
        self.passkey = ''
        if net.encrypted:
            #draw the keyboard
            self.Keyboard = App_Keyboard('Enter passcode for {}:'.format(net.ssid))
        self.GetTxtByID('txtSSID').SetText(self.ssid)
        self.GetTxtByID('txtPass').SetText('None')
        self.encrypted = net.encrypted
        
    def Connect(self, btnID):
        print(btnID)
        if not self.validate(): return
        #this is where we just insert it into wpa_supplicant ourselves
        #then call 'wpa_cli -i wlan0 reconfigure'
        errored = False
        try:
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as wpa:
                wpa.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
                wpa.write('update_config=1\n')
                wpa.write('country=US\n\n')
                wpa.write('network={\n')
                wpa.write('    ssid="{}"\n'.format(self.ssid))
                if self.encrypted:
                    wpa.write('    psk="{}"\n'.format(self.passkey))
                    wpa.write('    key_mgmt=WPA-PSK\n')
                else:
                    wpa.write('    key_mgmt=NONE\n')
                wpa.write('}\n')
            call(['wpa_cli', '-i', 'wlan0', 'reconfigure'])
        except:
            errored = True
            print('Exception thrown when trying to configure network')
            traceback.print_exc()
            
        self.ssid = ''
        self.passkey = ''
        self.encrypted = False
        self.GetTxtByID('txtSSID').SetText('None' if not errored else 'ERROR')
        self.GetTxtByID('txtPass').SetText('None')
        self.dirty = True
        
            

    def validate(self):
        return self.ssid != '' and (not self.encrypted or self.passkey != '')    

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
