import pygame

from app import App
import utils
from utils import COLORS
from App_FileBrowser import App_FileBrowser
import filebrowser_helper

class Panel_Music(App):
	WIDTH = 268
	HEIGHT = 250
	LEFT = 0
	TOP = 480 - HEIGHT - 40
	should_close = False
	file_browser = None

	def __init__(self, musicController):
		super(Panel_Music, self).__init__()
		self.Buttons, self.Texts = utils.load(self, 'Panel_Music.json')
		self.music = musicController
		self.set_shuffled_button()
		print('Instantiated music panel')

	def FirstDraw(self, screen):
		#Draw the background
		print('First Drawing music panel')
		if self.file_browser:
			self.file_browser.FirstDraw(screen)
			return
		#draw the buttons onto a new surface
		area = pygame.Surface((self.WIDTH, self.HEIGHT))
		self.DrawBackground(area, COLORS.DARK_GRAY)
		super(Panel_Music, self).FirstDraw(area)
		screen.blit(area, (self.LEFT, self.TOP))

	def DrawBackground(self, screen, color = (0, 0, 0)):
		background = pygame.Surface((self.WIDTH, self.HEIGHT))
		background.fill(color)
		screen.blit(background, (0, 0))
	
	def Draw(self, screen):
		if self.file_browser:
			complete, cancel = filebrowser_helper.GetCompleted()
			if complete:
				if not cancel: self.music.load_library(filebrowser_helper.GetPath())
				self.file_browser.OnClosed()
				self.file_browser = None
				return True
			else:
				return self.file_browser.Draw(screen)

		worked = super(Panel_Music, self).Draw(screen)
		for button in self.Buttons:
			if worked: break
			worked |= button.updated
		for text in self.Texts:
			if worked: break
			worked |= text.updated
		return worked

	def EventLoop(self, events):
		if self.file_browser:
			self.file_browser.EventLoop(events)
			return
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				if not pygame.Rect(self.LEFT, self.TOP, self.WIDTH, self.HEIGHT).collidepoint(pos):
					self.should_close = True
				else:
					#adjust the mouse position to be relative to the top left of the panel
					newPos = (pos[0] - self.LEFT, pos[1] - self.TOP)
					self.MouseClick(newPos)

	def musicPrevious(self, btnID):
		print('musicPrevious - {}'.format(btnID))
		self.music.skip_backward()

	def musicShuffle(self, btnID):
		print('musicShuffle - {}'.format(btnID))
		self.music.toggle_shuffle()
		self.set_shuffled_button()

	def set_shuffled_button(self):
		btn = self.GetButtonByID('btnShuffle')
		shuffleText = 'Off'
		color = COLORS.GRAY
		if self.music.shuffled:
			shuffleText = 'On'
			color = COLORS.BLUE
		btn.set_text('Shuffle: {}'.format(shuffleText))
		btn.set_color(color)

	def musicFileSelect(self, btnID):
		print('musicFileSelect - {}'.format(btnID))
		self.file_browser = App_FileBrowser(self.music.music_directory)


