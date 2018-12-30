from app import App
import utils
from utils import COLORS
import pygame
import os

import filebrowser_helper

class App_FileBrowser(App):
  def __init__(self):
    super(App_FileBrowser, self).__init__()
    self.dir = '/home/pi'
    self.dirty = False
    filebrowser_helper.ShowHidden(False)
    filebrowser_helper.ShowFiles(False)
    self.page = 0
    self.Buttons, self.Texts = utils.load(self, 'App_FileBrowser.json')
    
  def __init__(self, path):
    super(App_FileBrowser, self).__init__()
    self.dir = path
    self.dirty = False
    filebrowser_helper.ShowHidden(False)
    filebrowser_helper.ShowFiles(False)
    self.page = 0
    self.Buttons, self.Texts = utils.load(self, 'App_FileBrowser.json')

  def FirstDraw(self, screen):
    #Add buttons
    self.DrawDefaultButtons(screen)

    #Add texts
    self.GetTxtByID('txtPath').SetText(self.dir)

    #Draw the background
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    super(App_FileBrowser, self).FirstDraw(screen)
    self.dirty = True

  def Select(self, btnID):
    filebrowser_helper.SetPath(self.dir)
    print('Selected '+self.dir)
    return

  def GoUp(self, btnID):
    if (self.dir != '/'):
      self.dir = self.dir.rsplit('/', 1)[0]
      self.dirty = True
      if (self.dir == ''):
        self.dir = '/'
      self.page = 0

  def ToggleHidden(self, btnID):
    filebrowser_helper.ShowHidden(not filebrowser_helper.ViewHidden())
    self.dirty = True
    self.page = 0
    
  def ToggleFiles(self, btnID):
    filebrowser_helper.ShowFiles(not filebrowser_helper.ViewFiles())
    self.dirty = True
    self.page = 0
  
  def PageChange(self, btnID):
    self.dirty = True
    if (btnID == "btnPPlus"):
      self.page += 1
    elif (btnID == "btnPMinus"):
      self.page -= 1
      if (self.page < 0): self.page = 0

  def Draw(self, screen):
    super(App_FileBrowser, self).Draw(screen)
    if self.dirty:
      self.dirty = False
      size = screen.get_size()
      background = pygame.Surface(size)
      background.fill((0, 0, 0))
      screen.blit(background, (0, 0))

      txt = self.dir
      if len(txt) > 60:
        txt = txt[-60:]
        txt = '...'+txt
      self.GetTxtByID('txtPath').SetText(txt)
      
      column = 0
      maxColumn = 2
      row = 0
      maxRow = 8
      self.DrawDefaultButtons(screen)
      #for d in os.listdir(self.dir):
        #if (not d.startswith('.') and os.path.isdir(self.dir+'/'+d )):
      if (os.path.isdir(self.dir)):
        dirs = filebrowser_helper.ListDirectory(self.dir)
        self.GetButtonByID('btnPPlus').SetVisible(len(dirs) > maxRow*maxColumn*(self.page+1))
        for i in range(self.page*maxRow*maxColumn, min(len(dirs), maxRow*maxColumn*(self.page+1))):
        #for d in filebrowser_helper.ListDirectory(self.dir):
          d = dirs[i]
          color = COLORS.WHITE
          isFile = False
          if (not os.path.isdir(self.dir+'/'+d)): 
            isFile = True
            color = COLORS.YELLOW
          if (d.startswith('.')):
            color = COLORS.BLUE
            if isFile: color = COLORS.CYAN
          self.Buttons.append(utils.Button(d, (column*((size[0]-100)/maxColumn)+50, row*38+76), ((size[0]-100)/maxColumn, 38), None, ((d[:25] + '..') if len(d) > 27 else d), color, self.PathButtonSelected, 38))
          row += 1
          if (row % maxRow == 0):
            row = 0
            column += 1
          if column > maxColumn: break
            
      for btn in self.Buttons:
        btn.Draw(screen)
      for txt in self.Texts:
        txt.Draw(screen)
          
  def DrawDefaultButtons(self, screen):
    self.Buttons, _ = utils.load(self, 'App_FileBrowser.json')
    self.GetButtonByID('btnHidden').TXTCOLOR = (COLORS.WHITE if filebrowser_helper.ViewHidden() else COLORS.BLACK)
    self.GetButtonByID('btnFiles').TXTCOLOR = (COLORS.CYAN if filebrowser_helper.ViewFiles() else COLORS.BLACK)
    self.GetButtonByID('btnPMinus').SetVisible(self.page > 0)
    
  def PathButtonSelected(self, btnID):
    #if (not os.path.isdir(self.dir + '/' + btnID)):
     # return
    if (self.dir != '/'):
      self.dir += '/'
    self.dir += btnID
    self.dirty = True
    self.page = 0
  
  def EventLoop(self, events):
    super(App_FileBrowser, self).EventLoop(events)

if __name__=="__main__":
  #os.environ["SDL_FBDEV"] = "/dev/fb1"
  #os.environ["SDL_MOUSEDRV"] = "TSLIB"
  #os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
  #os.environ["SDL_VIDEODRIVER"] = "fbcon"

  pygame.init()
  screen = pygame.display.set_mode((800, 480), 0, 32)
  app_fb = App_FileBrowser('/home/')
  app_fb.FirstDraw(screen)
  PyClock = pygame.time.Clock()
  while True:
    app_fb.EventLoop(pygame.event.get())
    app_fb.Draw(screen)
    pygame.display.update()
    PyClock.tick(5)
