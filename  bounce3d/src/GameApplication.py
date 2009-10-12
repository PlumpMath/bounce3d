
# taskMgr
from direct.showbase.DirectObject import DirectObject

# plotting text
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode

from KeyboardControl import KeyboardControl
from GameModel import GameModel
from GameControl import GameControl

class GameApplication(DirectObject):
	
	def __init__(self):
		model = GameModel()
		loop = GameControl( 60.0, model )
		keys = KeyboardControl( model )
		
		# http://www.panda3d.org/wiki/index.php/Tasks
		# http://www.panda3d.org/apiref.php?page=TaskManager#doMethodLater
		taskMgr.doMethodLater(delayTime = 0.2,
			funcOrTask = loop.simulationTask,
			name = "Physics Simulation")
			
		self.createHUD()
		
	def createHUD(self):
		'''
		PRE: call once
		POST: a stylished text is placed on the screen.
		'''
		# Add a text on the screen.
		helpText = OnscreenText(
			text = "Turn gravity [SPACE], moving [ARROWS]",
			style = 1,
			fg = (1,1,1,1),
			pos = (-1.25,0.85),
			align = TextNode.ALeft,
			scale = 0.07
		)
		helpText.show()
	
	def run(self):
		base.run()