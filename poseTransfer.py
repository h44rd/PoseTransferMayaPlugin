import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

from multiprocessing.connection import Client

kPluginCmdName = "poseTransfer"

# Command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.address = ('localhost', 6000)
        self.conn = Client(self.address, authkey='secret password')
        self.ifSpheresConstructed = False
        self.timeFrame = 1
        self.timeFrameIncrement = 4
        self.surfaceObjects = []
        # self.conn.send('Connected!')

    # Invoked when the command is run.

    def doIt(self,argList):
        print "In doIt"
        while True:
            msg = self.conn.recv()
            print "Received message: ", msg
            print "Number of spheres", len(msg[0][0])

            if not self.ifSpheresConstructed: # To construct the sphere after the first message is received
                for i in range(len(msg[0][0])):
                    print "Creating ", 'sphere' + str(i) 
                    name = cmds.sphere(r = 100)
                    print name
                    self.surfaceObjects.append(name[0])
                self.ifSpheresConstructed = True
            
            for i in range(len(msg[0][0])):
                sphereName = self.surfaceObjects[i]

                x = msg[0][0][i]
                y = msg[0][1][i]
                z = msg[0][2][i]
                
                cmds.move(x, y, z, sphereName, absolute=True)
                cmds.setKeyframe(sphereName, time = self.timeFrame)
            
            self.timeFrame = self.timeFrame + self.timeFrameIncrement

                

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( scriptedCommand() )
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )