import os

selectedPath = ''
showHidden = False
showFiles = False
completed = False
cancelled = False

def SetPath(path, complete = True):
  global selectedPath
  selectedPath = path
  if (complete):
    global completed
    completed = True
  
def SetCancelled():
  global completed
  global cancelled
  completed = True
  cancelled = True

def GetPath():
  return selectedPath
  
def ShowHidden(show=True):
  global showHidden
  showHidden = show

def ViewHidden():
  return showHidden
  
def ShowFiles(show=True):
  global showFiles
  showFiles = show

def ViewFiles():
  return showFiles
  
def GetCompleted(reset = True):
  global completed
  global cancelled
  result = completed
  cancel = cancelled
  if (completed and reset):
    completed = False
    cancelled = False
  return result, cancel
    
  
def ListDirectoryFull(path, files=False, hidden=False):
  items = []
  for i in os.listdir(path):
    if (not hidden and i.startswith('.')): continue
    if (not files and os.path.isfile(path+'/'+i)): continue
    items.append(i)
  return sorted(items)
  
def ListDirectory(path):
  return ListDirectoryFull(path, showFiles, showHidden)
