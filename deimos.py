import FPS_control

from app import App
from App_WiFi import App_WiFi
from App_Music import App_Music

import utils
from utils import COLORS

import pygame, sys, os, time
from pygame.locals import *
from datetime import datetime

class CORE:
    ActiveApp = None
    BackgroundApps = {}
    BarColor = COLORS.WHITE
    BarHeight = 40
    BarTextSize = 36
    Width = 800
    Height = 480
    def __init__(self):
        self.screen = pygame.display.set_mode((self.Width, self.Height), 0, 32)
        self.homeBtn = utils.Button("btnHome", (0, self.Height - self.BarHeight), (100, self.BarHeight), COLORS.RED, "HOME", COLORS.WHITE, self.HOME, self.BarTextSize)
        self.CREATE_DATA_DIR()
        
    def CREATE_DATA_DIR(self):
        try:
            os.mkdir('data')
        finally:
            return
          
    
    def SET_APP(self, name, newAPP):
        if self.ActiveApp is not None:
            keep = self.ActiveApp.OnClosed()
            coreID = self.ActiveApp.CORE_ID
            print("Keep {} open? {}".format(coreID, keep))
            if keep:
                self.BackgroundApps[coreID] = self.ActiveApp
        if name in self.BackgroundApps:
            print("Loading existing {}".format(name))
            self.ActiveApp = self.BackgroundApps[name]
            del self.BackgroundApps[name]
        else:
            print("Creating new {}".format(name))
            self.ActiveApp = newAPP()
            self.ActiveApp.CORE_ID = name
        self.ActiveApp.FirstDraw(self.screen)
        
    
    def DRAW(self):
        #start_time = time.time()
        self.ActiveApp.Draw(self.screen)
        self.DrawStatusBar()
        pygame.display.update()
        FPS_control.FPS_Wait()
        #end_time = time.time()
        #print('DRAW: {}'.format(end_time - start_time))
          
    
    def DrawStatusBar(self):
        #Draws a bar along the bottom border
        #Clicking the left side returns home
        #The clock is on the right
        #Notifications (music control?) in the center
        StatusBarSurf = pygame.Surface((self.Width, self.BarHeight))
        StatusBarSurf.fill(self.BarColor)

        #Draw the time on the right
        clockTxt = utils.Text("txtClock", datetime.now().strftime("%H:%M"), (self.Width - 75, 0), self.BarTextSize)
        clockTxt.Center((0, self.BarHeight/2), vertical=True, horizontal=False)
        clockTxt.Draw(StatusBarSurf)

        fps = FPS_control.GetActualFPS()
        fpsTxt = utils.Text("txtFPS", "{0:.1f}".format(fps), (110, 0), self.BarTextSize)
        fpsTxt.Center((0, self.BarHeight/2), vertical=True, horizontal=False)
        fpsTxt.Draw(StatusBarSurf)
        
        self.screen.blit(StatusBarSurf, (0, self.Height - self.BarHeight))
        
        self.homeBtn.Draw(self.screen)

    
    def HOME(self, btnID):
        print("Returning to home screen")
        self.SET_APP("home", App_Launcher)
    
    def EVENTLOOP(self):
        #start_time = time.time()
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  
                self.homeBtn.Check(pygame.mouse.get_pos())
                #self.ActiveApp.MouseClick(pygame.mouse.get_pos())
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
                
        self.ActiveApp.EventLoop(events)
        for appname, app in self.BackgroundApps.items():
            app.BackgroundEventLoop(events)
        #end_time = time.time()
        #print('EVENTLOOP: {}'.format(end_time - start_time))
        
        
class App_Launcher(App):
    ROWS = 2
    COLS = 3
    def __init__(self):
        super(App_Launcher, self).__init__()
        FPS_control.Default()
        self.Apps = []
        self.Apps.append(AppIcon("Music", App_Music, COLORS.RED))
        self.Apps.append(AppIcon("WiFi", App_WiFi, COLORS.BLUE))
                
    def FirstDraw(self, screen):
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill(COLORS.BLACK)
        screen.blit(background, (0,0))
        
        i=0
        W = CORE.Width/(2*self.COLS+1)
        H = CORE.Height/(2*self.ROWS+1)
        for app in self.Apps:
            app.Draw(screen, (2*W*(i%self.COLS)+W, 2*H*(i/self.COLS)+H))
            i += 1
        
        super(App_Launcher, self).FirstDraw(screen)
        
    def MouseClick(self, mousePos):
        super(App_Launcher, self).MouseClick(mousePos)
        for app in self.Apps:
            app.BTN.Check(mousePos)

class AppIcon():
    def __init__(self, name, appClass, color):
        self.NAME = name
        self.APP = appClass
        self.COLOR = color
        self.BTN = utils.Button("btn"+name, (0, 0), (128, 96), self.COLOR, self.NAME, COLORS.WHITE, self.Activate)
        self.BTN.TXTSIZE = 36
    
    def Draw(self, screen, pos):
        self.BTN.POS = pos
        #btn = utils.Button(pos, (64, 48), self.COLOR, self.NAME, COLORS.WHITE, self.Activate)
        self.BTN.Draw(screen)
        
    def Activate(self, btnID):
        global Core
        print("Activating "+self.NAME)
        Core.SET_APP(self.NAME, self.APP)


##main

if __name__ == "__main__":
#    os.environ["SDL_FBDEV"] = "/dev/fb1"
#    os.environ["SDL_MOUSEDRV"] = "TSLIB"
#    os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
#    os.environ["SDL_VIDEODRIVER"] = "fbcon"

    pygame.init()
    
    pygame.mouse.set_visible(True)
    
    Core = CORE()
    Core.SET_APP("home", App_Launcher)
    while True:
        Core.EVENTLOOP()
        Core.DRAW()
        
