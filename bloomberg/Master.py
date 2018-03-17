import socket
import sys
import time

def run(user, password, * commands):
    HOST, PORT = "codebb.cloudapp.net", 17429
    data = user + " " + password + "\n" + "\n".join(commands) + "\nCLOSE_CONNECTION\n"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, "utf-8"))
        sfile = sock.makefile()
        rline = sfile.readline()
        while rline:
            print(rline.strip())
            return rline
            rline = sfile.readline()

def subscribe(user, password):
    HOST, PORT = "codebb.cloudapp.net", 17429
    data = user + " " + password + "\nSUBSCRIBE\n"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, "utf-8"))
        sfile = sock.makefile()
        rline = sfile.readline()
        while rline:
            print(rline.strip())
            rline = sfile.readline()

#parser for parsing server output
class Parser:
    def __init__():

    #parses output from STATUS and SCAN call to server
    #output should be of form:
    #[X, Y, DX, DY, MINES[OWNER X Y], PLAYERS[X Y DX DY], BOMBS[X Y]
    # WORMHOLES[X Y RADIUS OUT_X OUT_Y]]
    def parseStatus(line): 
         inputs = line.split()
         returnlst = []
         curr = 1

         for curr in range(1,5):
            returnlst.append(inputs[curr])

         curr = 7

         #mines[OWNER X Y]
         tempList = []
         returnlst[4] = []
         for i in range(inputs[6]):
            for j in range(curr, curr+3):
                tempList.append(inputs[j])
            returnlst[4].append(tempList)
            curr += 3
            del tempList[:]

        #players[X Y DW DY]
        nextStart = curr + 1
        curr += 2
        for i in range(nextStart):
            for j in range(curr, curr+4):
                tempList.append(inputs[j])
            returnlst[5].append(tempList)
            curr+=4
            del tempList[:]

        #bombs[X Y]
        nextStart = curr+1
        curr +=2
        for i in range(nextStart):
            for j in range(curr, curr+2):
                tempList.append(inputs[j])
            returnlst[6].append(tempList)
            curr+=2
            del tempList[:]

        #wormholes[X Y RADIUS OUT_X OUT_Y]
        nextStart = curr+1
        curr +=2
        for i in range(nextStart):
            for j in range(curr, curr+5):
                tempList.append(inputs[j])
            returnlst[7].append(tempList)
            curr+=5
            del tempList[:]
    
    #parses output from CONFIGURATION call to server
    #output should be of form:
    #[MapWidth, MapHeight, CaptureRadius, VISIONRADIUS, FRICTION
    #   BRAKEFRICTION, BOMBPLACERADIUS, BOMBEFFECTRADIUS,
    #   BOMBDELAY, BOMBPOWER, SCANRADIUS, SCANDELAY ]
    def parseConfig(line):  
        lst = line.split()
        returnlst = []

        returnlst[0] = lst[2]
        returnlst[1] = lst[4]
        returnlst[2] = lst[6]
        returnlst[3] = lst[8]
        returnlst[4] = lst[10]
        returnlst[5] = lst[12]
        returnlst[6] = lst[14]
        returnlst[7] = lst[16]
        returnlst[8] = lst[18]
        returnlst[9] = lst[20]
        returnlst[10] = lst[22]
        returnlst[11] = lst[24]
        returnlst[12] = lst[26]

        return returnlst

#countdown timer
class Timer:
    startTime = -1
    amountTime = -1
    timesUp = True
    
    def __init__(self):

    def start(self, seconds):
        timesUp = False
        amountTime = seconds
        startTime = time.time()

    def isFinished(self):
        if ((timesUp == True) or (time.time()-startTime >= amountTime)):
            timesUp = True
            amountTime = -1
            startTime = -1
            return True
        else:
            return False


#class for all logic related stuff
class Logic:
    #-------------------------------------------------------------#
    #                     INITIALIZING VARIABLES                  #
    #-------------------------------------------------------------#

    #USER stuff
    user = 'a'
    password = 'a'

    #CONFIG stuff
    mapWidth = -1
    mapHeight = -1
    captureRadius = -1
    visionRadius = -1
    friction = -1
    brakeFriction = -1
    bombPlaceRadius = -1
    bombEffectRadius = -1
    bombDelay = -1
    bombPower = -1
    scanRadius = -1
    scanDelay = -1

    #COORDINATE related stuff
    selfCoords = []
    selfVelocities = []
    selfAccelerations = []
    
    otherPlayerCoords = []
    otherPlayerVelocities = []
    wormHoleCoords = set()  #contains tuples in form (x, y, radius)
    mineCoords = set()      #contains tuples in form (x, y)

    destinationCoords = []
    tempDestinationCoords = []
    destinationVelocity = []
    destinationAcceleration = []

    #ABILITIES
    canScan = True
    scanTimer = Timer()
    canBomb = True
    bombTimer = Timer()

    #-------------------------------------------------------------#
    #                          FUNCTIONS                          #
    #-------------------------------------------------------------#

    def __init__(self):
        

    #predict where the spaceship at x, y will be after t seconds have passed
    def prediction(self, x, y, dx, dy, a, angle, t):
        
    #outputs location of most suitable mine to go to [x,y]
    def findBestMine(self):

    #returns list of coordinates outlining path to desired coordinates
    #the first point in the list is the first destination
    def findPath(self, x, y):

    #Return acceleration and angle to reach destination
    def setCourse(self, x, y, destVx, destVy):
        

    #figure out where to bomb
    #bomb the place
    def findBombTarget(self):

    #figure out where to scan
    #scan the place and update information
    def findScanTarget(self):
        
    #enter the info list into self fields
    def enterStatusInfo(self, info):
        
    
    #update all whereabouts
    def updateStatus(self):
        

    def updateTimes(self):
        this.canScan = this.scanTimer.isFinished()
        this.canBomb = this.bombTimer.isFinished()
    
    def update(self): #main function 
        updateStatus()   #get updates
        tempDestinationCoords = findBestMine(self)
        updateTimers()   #update scan and bomb timer
            













