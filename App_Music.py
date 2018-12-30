from app import App
import utils
from utils import COLORS

import pygame, sys, os, time
from pygame.locals import *
from pygame import mixer
import random

from App_FileBrowser import App_FileBrowser
import filebrowser_helper

class App_Music(App):
  musicDir = '/home/pi/Music'
  fileBrowser = App_FileBrowser(musicDir)
  browserOpen = False
  runBrowserFirst = False

  def __init__(self):
    super(App_Music, self).__init__()
    self.MusicPlaylist = []
    self.ShuffledPlaylist = []
    self.Shuffle = False
    self.Repeat = False
    self.CurrentIndex = -1
    self.Playing = False
    mixer.init()
    self.Buttons, self.Texts = utils.load(self, 'App_Music.json')
    self.LoadConfig()
    self.dirty = False

  def FirstDraw(self, screen):
    #Draw the background
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    
    
    super(App_Music, self).FirstDraw(screen)
    
    #self.LoadMusicLibrary()

  def Draw(self, screen):
    super(App_Music, self).Draw(screen)
    
    if (self.browserOpen):
      if (self.runBrowserFirst):
        self.fileBrowser.FirstDraw(screen)
        self.runBrowserFirst = False
      self.fileBrowser.Draw(screen)
      return
    
    if self.dirty:
      self.dirty = False
      background = pygame.Surface(screen.get_size())
      background.fill((0, 0, 0))
      screen.blit(background, (0, 0))
      
      for btn in self.Buttons:
        btn.Draw(screen)
      for txt in self.Texts:
        txt.Draw(screen)
      return True
  
  def EventLoop(self, events):
    if (self.browserOpen):
      self.fileBrowser.EventLoop(events)
      if (filebrowser_helper.GetCompleted()):
        self.musicDir = filebrowser_helper.GetPath()
        self.browserOpen = False
        self.dirty = True
        self.CurrentIndex = 0
        self.LoadMusicLibrary()
      if (self.fileBrowser.GetButtonByID('btnCancel') and self.fileBrowser.GetButtonByID('btnCancel').Clicked_Self()):
        self.browserOpen = False
        self.dirty = True
      return
    self.CheckPlaying()
    super(App_Music, self).EventLoop(events)
  
  def BackgroundEventLoop(self, events):
    super(App_Music, self).BackgroundEventLoop(events)
    self.CheckPlaying()
    
  def OnClosed(self):
    super(App_Music, self).OnClosed()
    return self.Playing or mixer.music.get_busy()# we want to keep this running if we're playing (or paused)
    
  def WriteConfig(self):
    if not os.path.exists('data/App_Music'):
      os.mkdir('data/App_Music')
    with open('data/App_Music/App_Music.cfg', 'w') as cfg:
      cfg.write(self.musicDir+'\n')
      cfg.write(str(self.CurrentIndex)+'\n')
      cfg.write(str(self.Shuffle)+'\n')
      cfg.write('Playlist:'+str(len(self.MusicPlaylist))+'\n') #write out the whole playlist
      for song in self.MusicPlaylist:
        cfg.write(song+'\n')
      if self.Shuffle: #write out the original playlist
        cfg.write('NonShuffled:'+str(len(self.OriginalPlaylist))+'\n')
        for song in self.OriginalPlaylist:
          cfg.write(song+'\n')

  def LoadConfig(self):
    if (os.path.isfile('data/App_Music/App_Music.cfg')):
      with open('data/App_Music/App_Music.cfg', 'r') as cfg:
        self.musicDir = cfg.readline().strip()
        self.CurrentIndex = int(cfg.readline().strip())
        self.Shuffle = (cfg.readline().strip() == "True")
        nextLine = cfg.readline().strip()
        if nextLine is not None and 'Playlist' in nextLine:
          playCount = int(nextLine.split(':')[1])
          self.MusicPlaylist = []
          for i in range(playCount):
            self.MusicPlaylist.append(cfg.readline().strip())
        nextLine = cfg.readline().strip()
        if nextLine is not None and 'NonShuffled' in nextLine:
          playCount = int(nextLine.split(':')[1])
          self.OriginalPlaylist = []
          for i in range(playCount):
            self.OriginalPlaylist.append(cfg.readline().strip())
        if (len(self.MusicPlaylist) > 0):
          self.SetCurrent(max(0, self.CurrentIndex))
          
        #print("Loaded shuffle as: "+str(self.Shuffle))
    if self.Shuffle:
      self.GetButtonByID('btnShuffle').COLOR = COLORS.YELLOW
    else:
      self.GetButtonByID('btnShuffle').COLOR = COLORS.RED
      
  
  def CheckPlaying(self):
    if (not mixer.music.get_busy() and self.Playing): #song ended
      self.Play(self.CurrentIndex + 1)
  
  def browse(self, btnID):
    self.browserOpen = True
    self.fileBrowser = App_FileBrowser(self.musicDir)
    self.runBrowserFirst = True
    
    #self.LoadMusicLibrary()

  def music_back(self, btnID):
    if (self.Playing and mixer.music.get_pos() > 5000):
      mixer.music.rewind()
    else:
      self.Play(self.CurrentIndex - 1)
    return

  def music_stop(self, btnID):
    mixer.music.stop()
    self.Playing = False
    self.GetButtonByID('btnPlay').TXT = '>'
    self.dirty = True
    return

  def music_play(self, btnID):
    if (len(self.MusicPlaylist) == 0): 
      return
    if (self.Playing and mixer.music.get_busy()): #playing
      mixer.music.pause()
      self.Playing = False
      self.GetButtonByID('btnPlay').TXT = '>'
    else:
      self.Play(self.CurrentIndex)
    self.dirty = True
    return

  def Play(self, index):
#    self.SetCurrent(index)
    self.GetButtonByID('btnPlay').TXT = '||'
    self.dirty = True
    if (not self.Playing and mixer.music.get_busy() and index == self.CurrentIndex): #paused
      mixer.music.unpause()
    else: #stopped
      self.SetCurrent(index)
      mixer.music.play()
      mixer.music.set_volume(1)
    self.Playing = True
    self.WriteConfig() #update config file
    
  def music_forward(self, btnID):
    self.Play(self.CurrentIndex + 1)
    return

  def shuffle_toggle(self, btnID):
    self.dirty = True
    self.Shuffle = not self.Shuffle
    if self.Shuffle:
      self.GetButtonByID('btnShuffle').COLOR = COLORS.YELLOW
    else:
      self.GetButtonByID('btnShuffle').COLOR = COLORS.RED
    self.DoShuffleTask()

  def DoShuffleTask(self):
    print("shuffle pressed")
    if len(self.MusicPlaylist) > 0:
      PlayingSongName = self.MusicPlaylist[self.CurrentIndex]
      if self.Shuffle: #We are activating shuffle
        self.OriginalPlaylist = self.MusicPlaylist[:]
        random.shuffle(self.MusicPlaylist)
      else: #We are going back to normal
        self.MusicPlaylist = self.OriginalPlaylist
      index = self.GetIndexByName(PlayingSongName)
      self.SetCurrent(index, False) #reset to the current song, don't reload it
    

  def GetIndexByName(self, name):
    for i in range(len(self.MusicPlaylist)):
      if self.MusicPlaylist[i] == name:
        return i
    return 0

  def repeat_toggle(self, btnID):
    self.dirty = True
    self.Repeat = not self.Repeat
    if self.Repeat:
      self.GetButtonByID('btnRepeat').COLOR = COLORS.YELLOW
    else:
      self.GetButtonByID('btnRepeat').COLOR = COLORS.RED

  def LoadMusicLibrary(self):
    #loads the music library into the list
    print('Loading music from '+self.musicDir)
    self.MusicPlaylist = []
    for rootName, dirNames, fileNames in os.walk(self.musicDir):
      print('Checking ' +  rootName)
      dirNames.sort()
      fileNames.sort()
      
      found = 0
      
      for f in fileNames:
        if f.endswith('.mp3'):
          self.MusicPlaylist.append(os.path.join(rootName, f))
          found += 1
          #print('Adding '+ os.path.join(rootName, f))
      print('Found {0} mp3 files.'.format(found))
    print('Found a total of {0} mp3 files.'.format(len(self.MusicPlaylist)))
    if (len(self.MusicPlaylist) > 0):
      #self.MusicPlaylist.sort()
      self.SetCurrent(max(0, self.CurrentIndex))
      if (self.Shuffle):
        self.DoShuffleTask()
        
  def GetPrettyName(self, index):
    name = os.path.basename(self.MusicPlaylist[index])[:-4] #remove the path and the '.mp3'
    if '- ' in name:
      name = name.rsplit('- ', 1)[1].strip() #turn "02 - filename" into "filename"
    return name
    
  def SetCurrent(self, index, load=True):
    if (index >= len(self.MusicPlaylist)):
      index = 0
    elif (index < 0):
      index = len(self.MusicPlaylist)-1
    self.CurrentIndex = index
    self.GetTxtByID('txtPlayingData').SetText(self.GetPrettyName(index))
    if load:
      mixer.music.load(self.MusicPlaylist[index])
    self.LoadNextList()
    self.dirty = True
    
  def LoadNextList(self):
    for i in range(5):
      self.GetTxtByID('txtMusicN'+str(i)).SetText(self.GetPrettyName((self.CurrentIndex+1+i)%len(self.MusicPlaylist)))
    self.dirty = True

if __name__=="__main__":
  #os.environ["SDL_FBDEV"] = "/dev/fb1"
  #os.environ["SDL_MOUSEDRV"] = "TSLIB"
  #os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
  #os.environ["SDL_VIDEODRIVER"] = "fbcon"

  pygame.init()
  screen = pygame.display.set_mode((800, 480), 0, 32)
  app_music = App_Music()
  app_music.FirstDraw(screen)
  PyClock = pygame.time.Clock()
  while True:
    app_music.EventLoop(pygame.event.get())
    app_music.Draw(screen)
    pygame.display.update()
    PyClock.tick(5)
