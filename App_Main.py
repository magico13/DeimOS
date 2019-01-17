from app import App
import utils
from utils import COLORS

class App_Main(App):
	def __init__(self):
		super(App_Main, self).__init__()
		self.Buttons, self.Texts = utils.load(self, 'App_Main.json')

	def FirstDraw(self, screen):
		#Draw the background
		self.DrawBackground(screen, (0, 0, 0))

		super(App_Main, self).FirstDraw(screen)

	def musicPanel(self, btnID):
		#Autogenerated Method Stub
		print('musicPanel - {}'.format(btnID))

	def systemsPanel(self, btnID):
		#Autogenerated Method Stub
		print('systemsPanel - {}'.format(btnID))

	def settingsPanel(self, btnID):
		#Autogenerated Method Stub
		print('settingsPanel - {}'.format(btnID))

	def musicPause(self, btnID):
		#Autogenerated Method Stub
		print('musicPause - {}'.format(btnID))

	def musicSkip(self, btnID):
		#Autogenerated Method Stub
		print('musicSkip - {}'.format(btnID))

	def volumeAdjust(self, btnID):
		#Autogenerated Method Stub
		print('volumeAdjust - {}'.format(btnID))

	def engineToggle(self, btnID):
		#Autogenerated Method Stub
		print('engineToggle - {}'.format(btnID))

	def windowChange(self, btnID):
		#Autogenerated Method Stub
		print('windowChange - {}'.format(btnID))

	def windowAutoToggle(self, btnID):
		#Autogenerated Method Stub
		print('windowAutoToggle - {}'.format(btnID))

	def lightsChange(self, btnID):
		#Autogenerated Method Stub
		print('lightsChange - {}'.format(btnID))

	def lightsAutoToggle(self, btnID):
		#Autogenerated Method Stub
		print('lightsAuto Toggle - {}'.format(btnID))
