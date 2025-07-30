import os
from Blockporn.scripts import Scripted
#====================================================================

class LoadeR:

    def loadfile(flocation):
        with open(flocation, 'r') as floaded:
            return floaded.read().splitlines()

#====================================================================

    def readfile():
        osem_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(osem_path, Scripted.DATA03)
        with open(file_path, 'r') as filed:
            listed = filed.read().splitlines()
            return listed

#====================================================================

class Blocker:

    def __init__(self, block=None):
        self.addlk = block
        self.block = self.readblock()
        self.cusom = block if block else []

#====================================================================

    def cloenlink(self, cleaned):
        emoonsond = cleaned.split("/")
        ouenoined = emoonsond[0]
        return ouenoined

#====================================================================
    
    def blocked(self, incoming):
        coxonos = str(incoming)
        cleaned = self.cleanlink(coxonos)
        matterd = self.cloenlink(cleaned)
        for blockers in self.cusom:
            if matterd == blockers:
                return True
        else:
            return False
    
#====================================================================

    def blocker(self, incoming):
        coxonos = str(incoming)
        cleaned = self.cleanlink(coxonos)
        matterd = self.cloenlink(cleaned)
        for blockers in self.block:
            if matterd == blockers:
                return True
        else:
            return False

#====================================================================
    
    def cleanlink(self, incoming):
        if incoming.startswith(Scripted.DATA01):
             return incoming.replace(Scripted.DATA01, "", 1)
        elif incoming.startswith(Scripted.DATA02):
             return incoming.replace(Scripted.DATA02, "", 1)
        else:
             return incoming

#====================================================================
    
    def readblock(self):
        osem_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(osem_path, Scripted.DATA03)
        with open(file_path, 'r') as filed:
            listed = filed.read().splitlines()
            listed.extend(self.addlk) if self.addlk else listed
            return listed

#====================================================================
