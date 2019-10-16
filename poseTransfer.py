import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

from multiprocessing.connection import Client

kPluginCmdName = "poseTransfer"

# Command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.address = ('localhost', 6000)
        self.conn = Client(self.address, authkey='secret password')        
        # self.conn.send('Connected!')
    # Invoked when the command is run.

    def doIt(self,argList):
        print "Hello World!"
        while True:
            msg = self.conn.recv()
            print "Received message: ", msg

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