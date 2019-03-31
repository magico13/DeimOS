from datetime import datetime
import serial

from app import App
import utils
from utils import COLORS
import music_controller
from Panel_Music import Panel_Music

class App_Main(App):
    time = datetime.now()
    active_panel = None
    write = True

    def __init__(self):
        super(App_Main, self).__init__()
        self.Buttons, self.Texts = utils.load(self, 'App_Main.json')
        self.music = music_controller.music_controller()
        self.update_music_title()
        self.GetTxtByID('txtVolume').SetText('Volume: {}%'.format(self.music.volume))
        self.GetTxtByID('txtClock').SetText(self.time.strftime('%H:%M'))

        port = '/dev/ttyUSB0'
        try:
            self.arduino = serial.Serial(port, 115200, timeout=0) #instant read, don't wait for data
            self.GetButtonByID('btnVersion').set_text(color = COLORS.GREEN)
        except:
            print('Cannot connect to arduino on port: {}'.format(port))
            self.arduino = None
            self.GetButtonByID('btnVersion').set_text(color = COLORS.RED)


    def FirstDraw(self, screen):
        #Draw the background
        self.DrawBackground(screen, (0, 0, 0))
        
        super(App_Main, self).FirstDraw(screen)

    def EventLoop(self, events, touches):
        if self.music.update(): self.update_music_title()
                
        if (datetime.now().minute != self.time.minute):
            self.time = datetime.now()
            self.GetTxtByID('txtClock').SetText(self.time.strftime('%H:%M'))
        
        self.manage_arduino()

        if not self.active_panel:
            super(App_Main, self).EventLoop(events, touches)
        else:
            self.active_panel.EventLoop(events, touches)
            if self.active_panel.should_close:
                print('Closing music panel')
                self.active_panel = None
                self.update_music_title()

    def Draw(self, screen):
        worked = super(App_Main, self).Draw(screen)
        for button in self.Buttons:
            if worked: break
            worked |= button.updated
        for text in self.Texts:
            if worked: break
            worked |= text.updated
        if self.active_panel:
            worked |= self.active_panel.Draw(screen)
        if worked: self.FirstDraw(screen)
        if self.active_panel:
            if worked: self.active_panel.FirstDraw(screen)
        return worked

    def OnClosed(self):
        if self.arduino: self.arduino.close()
        return False

    def manage_arduino(self):
        if not self.arduino: return
        if self.write:
            self.arduino_write_int(1)
        if not self.arduino: return
        msg = self.arduino.readline().strip()
        if msg and b',0' not in msg:
            print('Msg: {}'.format(msg))

    def arduino_write_int(self, value):
        if not self.arduino: return
        try:
            self.arduino.write(bytes([value]))
            self.arduino.flush()
        except:
            print('Failed to write to arduino')
            self.arduino = None

    def musicPanel(self, btnID):
        if not self.active_panel:
            print('Newing up music panel')
            self.active_panel = Panel_Music(self.music)

    def systemsPanel(self, btnID):
        #Autogenerated Method Stub
        print('systemsPanel - {}'.format(btnID))

    def settingsPanel(self, btnID):
        #Autogenerated Method Stub
        print('settingsPanel - {}'.format(btnID))

    def musicPlay(self, btnID):
        if self.music.playing:
            self.music.pause()
        else:
            self.music.play()
        self.update_music_title()

    def musicSkip(self, btnID):
        self.music.skip_forward()
        self.update_music_title()

    def volumeAdjust(self, btnID):
        if btnID == 'btnVolDown':
            self.music.volume_down()
        elif btnID == 'btnVolUp':
            self.music.volume_up()
        self.GetTxtByID('txtVolume').SetText('Volume: {}%'.format(self.music.volume))

    def engineToggle(self, btnID):
        #Autogenerated Method Stub
        print('engineToggle - {}'.format(btnID))
        self.arduino_write_int(2)

    def windowChange(self, btnID):
        #Autogenerated Method Stub
        print('windowChange - {}'.format(btnID))
        self.arduino_write_int(3)

    def windowAutoToggle(self, btnID):
        #Autogenerated Method Stub
        print('windowAutoToggle - {}'.format(btnID))
        self.arduino_write_int(4)

    def lightsChange(self, btnID):
        #Autogenerated Method Stub
        print('lightsChange - {}'.format(btnID))
        self.write = not self.write

    def lightsAutoToggle(self, btnID):
        #Autogenerated Method Stub
        print('lightsAutoToggle - {}'.format(btnID))

    def updateVersion(self, btnID):
        #Autogenerated Method Stub
        print('updateVersion - {}'.format(btnID))

    
    def update_music_title(self):
        '''Updates the title text for the current song'''
        self.GetTxtByID('txtMusicTitle').SetText(self.music.get_pretty_name())
        if self.music.playing:
            self.GetButtonByID('btnMusicPlay').set_text('||')
        else:
            self.GetButtonByID('btnMusicPlay').set_text('>')