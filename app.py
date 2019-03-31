#Base class for apps for the 2.8" PiTFT and "ArmOS"
import utils
import pygame
class App(object):
  
  def __init__(self):
    self.Buttons = []
    self.Texts = []
    self.PopUps = []
  
  def FirstDraw(self, screen):
    for button in self.Buttons:
      button.Draw(screen)
    for text in self.Texts:
      text.Draw(screen)
    return
      
  def Draw(self, screen):
    worked = len(self.PopUps) > 0
    for popup in self.PopUps:
      if not popup.Tick(screen):
        self.PopUps.remove(popup)
    return worked
    
  def DrawBackground(self, screen, color = (0, 0, 0)):
    background = pygame.Surface(screen.get_size())
    background.fill(color)
    screen.blit(background, (0, 0))
    
  def MouseClick(self, mousePos):
    for button in self.Buttons:
      button.Check(mousePos)
    return
    
  def EventLoop(self, events, touches):
    if not touches or len(touches) == 0:
      for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
          self.MouseClick(pygame.mouse.get_pos())
    else:
      for touch in touches:
        self.MouseClick((touch.x, touch.y))
    return
    
  def BackgroundEventLoop(self, events):
    return
  
  def OnClosed(self):
    return False
    
  def GetButtonByID(self, btnID):
    for b in self.Buttons:
      if b.NAME == btnID:
        return b
    return None
  
  def GetTxtByID(self, txtID):
    for t in self.Texts:
      if t.NAME == txtID:
        return t
    return None
