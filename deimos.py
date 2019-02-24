import FPS_control

from app import App
from App_Main import App_Main

import utils
from utils import COLORS

import pygame, sys, os, time
from pygame.locals import *
from datetime import datetime

class CORE:
    Run = True
    ActiveApp = None
    BackgroundApps = {}
    BarColor = COLORS.WHITE
    BarHeight = 40
    BarTextSize = 36
    Width = 800
    Height = 480
    def __init__(self):
        pygame.display.set_caption('DeimOS')
        
        self.screen = pygame.display.set_mode((self.Width, self.Height), 0, 32)
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
        if self.ActiveApp.Draw(self.screen):
            pygame.display.update()
        FPS_control.FPS_Wait()
          
    def HOME(self, btnID):
        print("Returning to home screen")
        self.SET_APP("home", App_Main)
    
    def EVENTLOOP(self):
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.Run = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.Run = False
                
        self.ActiveApp.EventLoop(events)
        for appname, app in self.BackgroundApps.items():
            app.BackgroundEventLoop(events)
        
        
##main
if __name__ == "__main__":
#    os.environ["SDL_FBDEV"] = "/dev/fb1"
#    os.environ["SDL_MOUSEDRV"] = "TSLIB"
#    os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
#    os.environ["SDL_VIDEODRIVER"] = "fbcon"

    pygame.init()
    pygame.mixer.quit()
    
    pygame.mouse.set_visible(True)
    
    Core = CORE()
    Core.SET_APP("home", App_Main)
    while Core.Run:
        Core.EVENTLOOP()
        Core.DRAW()
    pygame.quit()
