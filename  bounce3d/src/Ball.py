
from pandac.PandaModules import (
	Quat,OdeBody, OdeMass, OdeSphereGeom, BitMask32)	
from pandac.PandaModules import OdePlane2dJoint

from direct.directbase.DirectStart import *

class Ball:
	
	NAME_DEFAULT = "UNNAMED"
	POS_DEFAULT = ( 0,0,5 )
	SCALE_DEFAULT = ( 1,1,1 )
	HPR_DEFAULT = ( 0,0,0 )
	MODEL_EGG_DEFAULT = "../egg/paahahmo.egg"
	
	BALL_BODY_MASS_WEIGHT = 1000
	BALL_BODY_MASS_RADIUS = 1
	FORCE = 90000
	TORQUE = 3000

	STATIC_JUMP = 0
	STATIC_JUMP_FORCE = 2800000
	JUMP_FORCE = 120000
	MAX_JUMP_REACH_TIME = 0.7
	COLLISION_THRESHOLD_TIME = 0.1

	def __init__(
	self, 
	world,
	space,
	name = NAME_DEFAULT, 
	modelEgg = MODEL_EGG_DEFAULT,
	pos = POS_DEFAULT, 
	scale = SCALE_DEFAULT, 
	hpr = HPR_DEFAULT,
	):
		self.name = name
		self.pos = pos
		self.hpr = hpr
		self.scale = scale
		self.world = world
		self.space = space
		self.jumping = False
		self.jumpStarted = 0.0
		self.jumpLastUpdate = 0.0
		self.lastCollisionTime = 0.0
		self.lastCollisionIsGround = True
		self.moveLeft = False
		self.moveRight = False
		self.modelNode = self.createModelNode( self.pos, self.hpr, self.scale, modelEgg )
		self.ballBody = self.createBallBody( self.modelNode, self.world )
		self.ballGeom = self.createBallGeom( self.modelNode, self.ballBody, self.space )
		self.modelNode.reparentTo( render )
	
	def createModelNode( self, pos, hpr, scale, modelEgg ):
		modelNode = loader.loadModel( modelEgg ) 
		modelNode.setPos( pos )
		modelNode.setHpr( hpr )
		modelNode.setScale( scale )
		return modelNode
		
	def createBallBody( self, modelNode, world ):
		ballBody = OdeBody( world )
		M = OdeMass()
		M.setSphere( Ball.BALL_BODY_MASS_WEIGHT, Ball.BALL_BODY_MASS_RADIUS )
		ballBody.setMass( M )
		ballBody.setPosition( modelNode.getPos( render ) )
		ballBody.setQuaternion( modelNode.getQuat( render ) )
		return ballBody
	
	def createBallGeom( self, modelNode, ballBody, space ):
		ballGeom = OdeSphereGeom( space, 1 )
		ballGeom.setCollideBits( BitMask32( 0x2 ) )
		ballGeom.setCategoryBits( BitMask32( 0x1 ) )
		ballGeom.setBody( ballBody )
		return ballGeom
	
	def startMoveLeft( self ):
		self.moveLeft = True
	def stopMoveLeft( self ):
		self.moveLeft = False
	def isMovingLeft( self ):
		return self.moveLeft
	
	def startMoveRight( self ):
		self.moveRight = True
	def stopMoveRight( self ):
		self.moveRight = False
	def isMovingRight( self ):
		return self.moveRight

	def jumpOn( self ):
		if self.isColliding() == True and self.lastCollisionIsGround:
			self.jumping = True
			self.jumpStarted = globalClock.getLongTime()
		return

	def jumpOff( self ):
		self.jumping = False
		self.jumpStarted = 0.0
		self.jumpLastUpdate = 0.0
		return

	def isColliding( self ):
		if self.lastCollisionTime == 0.0:
			return False

		now = globalClock.getLongTime()
		interval = now - self.lastCollisionTime
                
		if interval < Ball.COLLISION_THRESHOLD_TIME:
			return True
		else:
			return False
	
	def isGroundCollision( self, colPos ):
		body = self.ballBody
		pos = body.getPosition()
		if colPos[2] < pos[2]:
			return True
		return False

	def refreshCollisionTime( self, numCol, colPos ):
		self.lastCollisionTime = globalClock.getLongTime()
		if numCol == 1:
			self.lastCollisionIsGround = self.isGroundCollision(colPos)

	def updateModelNode(self):
		''' Update objects after one physics iteration '''

		''' Can move better when on (touching) something, moving in the air is harder '''
		divisor = 3.5
		if self.isColliding() and self.lastCollisionIsGround:
		   divisor = 1.0

		if self.moveLeft:
			self.ballBody.setForce( y = -Ball.FORCE/divisor, x = 0, z = 0 )
			self.ballBody.setTorque( y = -Ball.TORQUE/divisor, x = 0, z = 0 )	
		elif self.moveRight:
			self.ballBody.setForce( y = Ball.FORCE/divisor, x = 0, z = 0 )
			self.ballBody.setTorque( y = Ball.TORQUE/divisor, x = 0, z = 0 )		

		''' This is still really crappy, will revise later '''
		if self.jumping == True:
			if Ball.STATIC_JUMP:
				self.ballBody.setForce( y = 0, x = 0, z = Ball.STATIC_JUMP_FORCE)
				self.jumping = False
			else:
				now = globalClock.getLongTime()
				elapsed = now - self.jumpStarted

				if elapsed > 0.0 and elapsed < Ball.MAX_JUMP_REACH_TIME:
					self.ballBody.setForce( y = 0, x = 0, z = Ball.JUMP_FORCE)
				elif elapsed > Ball.MAX_JUMP_REACH_TIME:
					self.jumping = False 
					
		# Keep the body in 2d position
		self.alignBodyTo2d()
		
		# Set the new position
		self.modelNode.setPos( render, self.ballBody.getPosition() )
		self.modelNode.setQuat( render, Quat(self.ballBody.getQuaternion() ) )	

	def alignBodyTo2d( self ):
		body = self.ballBody
		
		# Constrain position of the body
		oldPos = body.getPosition()
		newPos = oldPos
		newPos[0] = 0
		newPos[1] = oldPos[1]
		newPos[2] = oldPos[2]
		
		# Constrain quaternion of the body
		oldQuat = body.getQuaternion()
		newQuat = oldQuat
		newQuat[0] = oldQuat[0]
		newQuat[1] = oldQuat[1]
		newQuat[2] = 0
		newQuat[3] = 0
		
		# Set new position and quaternion of the body
		body.setPosition(newPos)
		body.setQuaternion(Quat(newQuat))
	
	def getPosition( self ):
		return self.ballBody.getPosition()
		
	def getBody( self ):
		return self.ballBody

	def getModelNode( self ):
                return self.modelNode
	
