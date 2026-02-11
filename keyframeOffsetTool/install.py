import os
import maya.mel as mel
import maya.cmds as cmds

def onMayaDroppedPythonFile(*args):
    Install()

class Install(object):
    def __init__(self, modVersion = 1.0, scripts = True):
        self.mayaPath = None 
        self.currDirPath = None
        self.modulesPath = None
        self.modName = None
        self.modVersion = modVersion
        self.scripts = scripts

        self.getMayaRootPath()
        self.getCurrentDirectoryPath()
        self.createModulesFolder()
        self.writeModuleFile()
        self.createShelfButton()

    def writeModuleFile(self):
        currDirPathInvertSlash = self.currDirPath.replace("\\", "/")

        modString = "+ {} {} {}".format(self.modName, self.modVersion, currDirPathInvertSlash)
        
        if self.scripts:
            modString = "{}\nscripts: {}".format(modString, currDirPathInvertSlash)

        filePath = os.path.join(self.modulesPath, "{}.mod".format(self.modName))
        with open(filePath, "w") as f:
            f.write(modString)

        print(filePath)

    def createModulesFolder(self):
        self.modulesPath = os.path.join(self.mayaPath, "modules")
        if os.path.exists(self.modulesPath):
            print("Modules folder exists.")
            return

        print("Creating Modules folder")
        os.makedirs(self.modulesPath)

    def getMayaRootPath(self):
        paths = mel.eval("getenv MAYA_APP_DIR;").split("/")
        self.mayaPath = os.path.join(paths[0], os.sep, *paths[1:])

    def getCurrentDirectoryPath(self):
        paths = os.path.dirname(os.path.realpath(__file__)).split("\\")
        self.modName = paths[-1]
        self.currDirPath = os.path.join(paths[0], os.sep, *paths[1:])

    def createShelfButton(self):
        try:
            # Get the current top shelf
            topShelf = mel.eval('$tmpVar=$gShelfTopLevel')
            currentShelf = cmds.tabLayout(topShelf, query=True, selectTab=True)
            print("Current shelf: {}".format(currentShelf))
            
            # Icon path
            iconPath = os.path.join(self.currDirPath, "offsetCurve.png").replace("\\", "/")
            print("Icon path: {}".format(iconPath))
            print("Icon exists: {}".format(os.path.exists(iconPath)))
            
            # Check if button already exists and remove it
            shelfButtons = cmds.shelfLayout(currentShelf, query=True, childArray=True) or []
            for btn in shelfButtons:
                if cmds.shelfButton(btn, query=True, exists=True):
                    if cmds.shelfButton(btn, query=True, label=True) == "Kot":
                        cmds.deleteUI(btn)
                        print("Removed existing Kot button")
            
            # Create the shelf button
            cmds.shelfButton(
                parent=currentShelf,
                imageOverlayLabel="Kot",
                annotation="Keyframe offset tool",
                image1=iconPath,  # Changed from image to image1
                command="import keyframeOffsetTool.ui\nfrom keyframeOffsetTool.ui import KeyframeOffsetUI\nKeyframeOffsetUI.run()",
                sourceType="python"
            )
            
            # Force shelf save
            cmds.saveAllShelves(topShelf)
            
            print("Shelf button 'Kot' created successfully.")
            
        except Exception as e:
            print("Error creating shelf button: {}".format(e))
            import traceback
            traceback.print_exc()