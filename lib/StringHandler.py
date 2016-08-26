import re


## class to strip a string of each occurance of the supplied regular expression
# provides methods to replace the Stripped sections and index each occurance 
# individually
class StripRegex(object):

    def __init__(self, RegexString, flags=0):
        self.__reset__(All=True)
        self.__RegexFlags = flags
        self.Regex = RegexString

    def __reset__(self, All=False):
        if All:
            self.__Regex = ''
            self.__InputString = ''
        
        self.__AllStrippedString = ''
        self.__StrippedString = ''
        self.__offGroups = []
        self.__groups = []
        self.__InsertLocations = []
        self.__BoolGroupInclude = []
        self.__IncludeGroups = []
        self.__NumGroups = 0
        self.__RegexFlags = 0
    
    def __setRegexp__(self, RegexString):
        self.__RegexObj = re.compile(RegexString, flags=self.__RegexFlags)            
        self.Strip(self.InputString)
    
    @property
    def NumGroups(self):                        # allow getting of private attribute
        return self.__NumGroups
    
    @property
    def Regex(self):                            # allow getting of private attribute
        return self.__Regex
    
    @Regex.setter
    def Regex(self, RegexString):                # method to set the private attribute 
        self.__Regex = RegexString
        self.__setRegexp__(RegexString)
        self.__GeneralSetRoutine__()
    
    @property
    def InputString(self):                      # allow getting of private attribute
        return self.__InputString
    
    @InputString.setter
    def InputString(self, InString):             # method to set the private attribute 
        self.__InputString = InString
        self.__GeneralSetRoutine__()
    
    @property
    def IncludeGroups(self):                  # allow getting of private attribute
        return self.__IncludeGroups
    
    @IncludeGroups.setter
    def IncludeGroups(self, IncludeGroups):      # method to set the private attribute
        self.__IncludeGroups = IncludeGroups
        self.__setBoolGroupInclude__()
        _ = self.genNewStrippedString()
    
    def __setBoolGroupInclude__(self):
        self.__BoolGroupInclude = [False for i in range(self.__NumGroups)]
        for v in self.__IncludeGroups:
            if v < self.__NumGroups:
                self.__BoolGroupInclude[v] = True
            else:
                err = "Cannot include group: '" + str(v) + "', there are only " + str(self.__NumGroups) + " groups"
                raise Exception(err)
    
    @property                                   # create a dummy attribute
    def AllStrippedString(self):
        return self.__AllStrippedString
    
    @property                                   # create a dummy attribute
    def StrippedString(self):
        return self.__StrippedString
    
    @property                                   # create a dummy attribute
    def groups(self):
        return self.__groups
    
    @property                                   # create a dummy attribute
    def InsertLocations(self):
        return self.__InsertLocations
    
    def __GeneralSetRoutine__(self):
        self.Strip()
    
    def Strip(self, string=None):
        self.__reset__()
        if string is not None:
            self.__InputString = string
        
        MatchIterator = self.__RegexObj.finditer(self.__InputString)
        Spans = []
        for m in MatchIterator:
            self.__groups.append(m.group())
            Spans.append(m.span())
        self.__NumGroups = len(self.__groups)
        
        # this code ensures that that there are always one more offGroups as groups
        # there will be an offGroup both before and after any groupd even if they are empty
        Spans.append((None, None))  # extra span for after last group
        Start = 0
        for Span in Spans:
            End = Span[0]
            offgroup = self.__InputString[Start:End]
            self.__offGroups.append(offgroup)
            Start = Span[1]
        # ----
        
        self.__IncludeGroups = []
        self.__setBoolGroupInclude__()
        self.__InsertLocations = [None for i in range(self.__NumGroups)]
        
        self.__AllStrippedString = self.genNewStrippedString()

    def genNewStrippedString(self, IncludeGroups=None):
        if IncludeGroups is not None:
            self.IncludeGroups = IncludeGroups
        
        self.__StrippedString = ''
        for i, oG in enumerate(self.__offGroups):
            self.__StrippedString = self.__StrippedString + oG
            if i < self.__NumGroups:  # need this extra check because there is one more offgroups than groups
                if self.__BoolGroupInclude[i]:
                    self.__StrippedString = self.__StrippedString + self.__groups[i]
                    self.__InsertLocations[i] = None
                else:
                    self.__InsertLocations[i] = len(self.__StrippedString)
        
        return self.__StrippedString        

## test and devolpement code            
if __name__ == "__main__":
    SR1 = StripRegex('\d+')
    SR1.Strip('12ab34cd56ef')
    SR2 = StripRegex('\d+')
    SR2.Strip('12ab0000034cd56ef')
