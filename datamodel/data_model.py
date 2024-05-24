from enum import Enum

class EnumUser(Enum):    
    NAME=1
    
class ConState:
    def __init__(self):
        self.profile = EnumUser.NAME
    @property
    def CurrentPos(self):
        return self.profile
    @CurrentPos.setter
    def EnumUser(self,current:EnumUser):
        self.profile = current

class UserProfile:
    def __init__(self):
        self.name = ""

    @property
    def Name(self):
        return self.name
    @Name.setter
    def Name(self,name:str):
        self.name = name
    
    