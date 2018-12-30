import pygame

PyClock = pygame.time.Clock()
defaultFPSOn = 10
defaultFPSOff = 1
FPS = defaultFPSOn
FPSOff = defaultFPSOff


def SetFPS(fps):
  global FPS
  FPS = fps

def SetOffFPS(fps):
  global FPSOff
  FPSOff = fps

def GetFPS():
  if True:#backlight_control.IsOn():
    return FPS
  else:
    return FPSOff
  
def GetActualFPS():
  return PyClock.get_fps()
  
def Default():
  global FPS
  global FPSOff
  FPS = defaultFPSOn
  FPSOff = defaultFPSOff
  
def FPS_Wait():
  PyClock.tick(GetFPS())
