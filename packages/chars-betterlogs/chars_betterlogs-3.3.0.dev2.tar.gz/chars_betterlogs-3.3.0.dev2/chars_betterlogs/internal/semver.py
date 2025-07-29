from __future__ import annotations

def fromString(version:str)->SemVer: return SemVer.fromString(version)

class SemVer:
    r'''Modified version of the Semantic Versioning system that allows for an additional string identifier.
    
    E.G: `1.3.2h`'''
    
    major:int; minor:int; patch:int; identifier:(str | None)

    def __init__(self, major:int= 0, minor:int = 1, patch:int = 0, identifier:(str |  None) = None) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.identifier = identifier

    def __str__(self):
        return self.toString(4)
    
    def __repr__(self):
        fString = f'{self.major}, {self.minor}, {self.patch}'
        if self.identifier != None: fString += ', ' + f"'{self.identifier}'"

        return f'SemVer({fString})'

    def toString(self, places:int = 3, includeIdentifier:bool = False)->str:
        r'''Returns the full version string as `major.minor.patch<Identifier>`
        
        `places : int` | How far to include the version string | 1+ = major, 2+ = major.minor 3+ = major.minor.patch'''
        if places <= 0:  print('use a value higher than 0 idiot!'); return str(self.major)
        ver = ''
        if places >= 1: ver += str(self.major)
        if places >= 2: ver += f'.{str(self.minor)}'
        if places >= 3: ver += f'.{str(self.patch)}'
        if self.identifier != None and (places >= 4 or includeIdentifier): ver += self.identifier

        return ver
    
    def fromString(s:str) -> SemVer:
        verArray = s.split('.')
        
        ver = SemVer(0, 0, 0)
        if verArray.__len__() >= 1:
            v = SemVer._checkForIdentifier(verArray[0])
            if isinstance(v, int): ver.major = v
            else: ver.major = v[0]
        if verArray.__len__() >= 2:
            v = SemVer._checkForIdentifier(verArray[1])
            if isinstance(v, int): ver.minor = v
            else: ver.minor = v[0]
        if verArray.__len__() >= 3:
            v = SemVer._checkForIdentifier(verArray[2])
            if isinstance(v, int): ver.patch = v
            else: ver.patch = v[0]; ver.identifier = v[1]
        return ver
    
    def _checkForIdentifier(intstr:str)->(int | list[(int | str)]):
        finalResult:(int|list[int|str])
        try: finalResult = int(intstr)
        except:
            verStringSplit = list(intstr)
            verNum = int(verStringSplit[0])
            verStringSplit.pop(0)

            finalString = ''
            for char in verStringSplit: finalString += char
            finalResult = [verNum, finalString]

        return finalResult
    
    def greaterThan(self, version:(SemVer|str)) -> bool:
        r'Checks if another SemVer is greater than this SemVer (Ignores Identifier.)'

        v:SemVer
        if isinstance(version, str): v = fromString(version)
        else: v = version

        if self.major > v.major: return True
        if self.major == v.major and self.minor > v.minor: return True
        if self.major== v.major and self.minor == v.minor and self.patch > v.patch: return True
        return False
    
    def greaterThanOrEqual(self, version:(SemVer|str)) -> bool:
        r'Checks if another SemVer is greater than or equal to this SemVer (Ignores Identifier.)'

        v:SemVer
        if isinstance(version, str): v = fromString(version)
        else: v = version

        if (self.greaterThan(version)): return True
        if self.major== v.major and self.minor == v.minor and self.patch == v.patch: return True
        return False

    def lessThan(self, version:(SemVer | str)) -> bool:
        r'Checks if another SemVer is less than this SemVer (Ignores Identifier.)'

        v:SemVer
        if isinstance(version, str): v = fromString(version)
        else: v = version

        if self.major < v.major: return True
        if self.major == v.major and self.minor < v.minor: return True
        if self.major== v.major and self.minor == v.minor and self.patch < v.patch: return True
        return False
    
    def lessThanOrEqual(self, version:(SemVer | str))->bool:
        r'Checks if another SemVer is less than or equal to this SemVer (Ignores Identifier.)'

        v:SemVer
        if isinstance(version, str): v = fromString(version)
        else: v = version

        if (self.lessThan(version)): return True
        if self.major == v.major and self.minor == v.minor and self.patch == v.patch: return True
        return False
    
    def isEqual(self, version:(SemVer | str))->bool:

        v:SemVer
        if isinstance(version, str): v = fromString(version)
        else: v = version
        
        return (self.major == v.major and self.minor == v.minor and self.patch == v.patch)

    def copy(self)->SemVer: return self