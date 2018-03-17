import socket
import sys
import time
import math

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

    #parses output from STATUS and SCAN call to server
    #output should be of form:
    #[X, Y, DX, DY, MINES[OWNER X Y], PLAYERS[X Y DX DY], BOMBS[X Y]
    # WORMHOLES[X Y RADIUS OUT_X OUT_Y]]
    def parseStatus(trash, line):
         inputs = line.split()
         returnlst = []
         curr = 1
         

         for curr in range(1,5):
            returnlst.append(inputs[curr])
            #print(inputs[curr])

         curr = 7
         #mines[OWNER X Y]
         tempList1 = []
         if int(inputs[6]) is not 0:
             for i in range(int(inputs[6])):
                for j in range(curr, curr+3):
                    #print(input[j])
                    tempList1.append(inputs[j])
                returnlst.append(tempList1)
                curr += 3
                #del tempList[:]
         else:
             returnlst.append(1)

         #players[X Y DW DY]
         tempList2 = []
         nextStart = curr + 1
         curr += 2
         if int(inputs[nextStart]) is not 0:
             for i in range(int(inputs[nextStart])):
                 for j in range(curr, curr+4):
                     #print(input[j])
                     tempList2.append(inputs[j])
                 returnlst.append(tempList2)
                 curr+=4
                 #del tempList[:]
         else:
             returnlst.append(-1)

         #bombs[X Y]
         tempList3 = []
         nextStart = curr+1
         curr +=2
         if int(inputs[nextStart]) is not 0:
             for i in range(int(inputs[nextStart])):
                 for j in range(curr, curr+2):
                     #print(input[j])
                     tempList3.append(inputs[j])
                 returnlst.append(tempList3)
                 curr+=2
                 #del tempList[:]
         else:
             returnlst.append(-1)

         #wormholes[X Y RADIUS OUT_X OUT_Y]
         tempList4 = []
         nextStart = curr+1
         curr +=2
         if int(inputs[nextStart]) is not 0:
             for i in range(int(inputs[nextStart])):
                for j in range(curr, curr+5):
                    #print(input[j])
                    tempList4.append(inputs[j])
                returnlst[7].append(tempList4)
                curr+=5
                #del tempList[:]
         else:
             returnlst.append(-1)

         return returnlst
    
    #parses output from CONFIGURATION call to server
    #output should be of form:
    #[MapWidth, MapHeight, CaptureRadius, VISIONRADIUS, FRICTION
    #   BRAKEFRICTION, BOMBPLACERADIUS, BOMBEFFECTRADIUS,
    #   BOMBDELAY, BOMBPOWER, SCANRADIUS, SCANDELAY ]
    def parseConfig(trash, line):  
        lst = line.split()
        returnlst = []

        returnlst.append(lst[2])
        returnlst.append(lst[4])
        returnlst.append(lst[6])
        returnlst.append(lst[8])
        returnlst.append(lst[10])
        returnlst.append(lst[12])
        returnlst.append(lst[14])
        returnlst.append(lst[16])
        returnlst.append(lst[18])
        returnlst.append(lst[20])
        returnlst.append(lst[22])
        returnlst.append(lst[24])

        return returnlst

def parseTest():
    parse = Parser()
    line = run('a', 'a', "STATUS")
    print(line.split())
    lst = parse.parseStatus(line)
    print(lst[:])

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
    parser = Parser()

    #Aribrary constants
    gridPartitionSize = 3.0/4
    radiusScaler = 1.3
    BOMB_ERROR = 1.0

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
    projectedNextCoords = []
    selfVelocities = []
    selfAccelerations = []
    path = []
    
    otherPlayerInfo = []    #contains arrays in form (x, y, dx, dy)
    wormholeCoords = set()  #contains tuples in form (x, y, radius)
    mineCoords = set()      #contains tuples in form (x, y)
    ownedMineCoords = set()

    destinationCoords = []
    tempDestinationCoords = []
    destinationVelocity = []
    destinationAcceleration = []

    #MAP stuff
    mapVisited = []
    numHPartitions = -1
    numVPartitions = -1

    #ABILITIES
    canScan = True
    scanTimer = Timer()
    canBomb = True
    bombTimer = Timer()

    #SITUATIONAL variables
    mineLocked = False
    destinationLocked = False #decided to go to a place but it isn't a mine

    #-------------------------------------------------------------#
    #                          FUNCTIONS                          #
    #-------------------------------------------------------------#

    def enterConfig(self, info):

    #separate map into grid with squares proportional to scanRadius by gridPartitionSize
    #the squares won't tile the map perfectly so the actual squares will be computed with size mapDimension/numPartitions
    def initMapVisited(self):
        #compute number of partitions
        self.numHPartitions = self.mapWidth/(self.scanRadius*2*self.gridPartitionSize)
        self.numVPartitions = self.mapHidth/(self.scanRadius*2*self.gridPartitionSize)
        
        #if there is enough extra space left over increase number of partitions by 1
        if (self.mapWidth - self.scanRadius*2*self.gridPartitionSize*self.numHPartitions > self.scanRadius*self.gridPartitionSize):
            self.numHPartitions += 1
        if (self.mapHeight - self.scanRadius*2*self.gridPartitionSize*self.numVPartitions > self.scanRadius*self.gridPartitionSize):
            self.numVPartitions += 1

        #create mapVisited
        for i in range(0, self.numVPartitions):
            self.mapVisited.append([])
            for (j in range(0, self.numHPartitions):
                self.mapVisited[i].append(False)

    def __init__(self):
        self.enterConfig(self.parseConfig(run(self.user, self.password, 'CONFIGURATION')))
        initMapVisited()
        self.projectedNextCoords = [0,0] #just to initialize it
        self.path = [0,0]
        

    #predict where the spaceship at x, y will be after t seconds have passed
    def prediction(self, x, y, dx, dy, a, angle, t):
        
    #outputs location of most suitable mine to go to [x,y]
    #SET MINELOCKED TO YES IF MINE IS FOUND
    def findBestMine(self):

    #returns list of coordinates outlining path to desired coordinates (x,y) from (x0, y0)
    #the first point in the list is the first destination
    def findPath(self, x0, y0, x, y):
        points = []
        m = (y-y0+0.0)/(x-x0)

        #check for and avoid wormhole intersections
        for i : wormholeCoords:
            if( abs(m*i(0)-i(1)+m*x0+y0+0.0)/math.sqrt(m**2+1) <= i(2)): #if shortest line from center of wormhole to line < wormhole radius
                 dist = ((i(0)-x0)*(x-x0)+(i(1)-y0)*(y-y0)+0.0)/((x-x0)**2+(y-y0)**2) #a dot b/|a|^2
                 tempX = x0 + (x-x0)*dist
                 tempY = y0 + (y-y0)*dist
                 newX = i(0) + i(2)*(tempX-i(0))/math.sqrt(tempX**2+i(0)**2)*radiusScaler
                 newY = i(1) + i(2)*(tempY-i(1))/math.sqrt(tempY**2+i(1)**2)*radiusScaler
                 temp1 = findPath(x0, y0, newX, newY)
                 temp2 = findPath(newX, newY, x, y)
                 for i in temp1:
                     points.append(i)
                 for i in temp2:
                     points.append(i)
                 return points
        return [[x,y]]
                 

    #Return acceleration and angle to reach destination
    def setCourse(self, x, y, destVx, destVy):
        

    #figure out where to bomb
    #bomb the place
    #targeting priority:
    #   1 - players heading for owned mines
    #   2 - players heading for unowned mines
    #   3 - random players in range
    def findBombTarget(self):
        #for every opponent visible find where they might be and see if they can be bombed
        for i : otherPlayerInfo:
            for t : range (1, bombDelay*20):
                 p = prediction(i(0), i(1), i(2), i(3), 0, 0, t*0.05) #opponent projected point
                 if (math.sqrt((self.selfCoords[0]-p(0))**2+(self.selfCoords[1]-p(1))**2) < (bombPlaceRadius+bombEffectRadius)): #opponent is in range
                     dist = sqrt((self.selfCoords[0]-p(0))**2+(self.selfCoords[1]-p(1))**2)
                     bombDist = max(bombPlaceRadius, dist)
                     bP = (self.selfCoords[0]+bombDist*(p(0)-self.selfCoords[0])/dist, self.selfCoords[1]+bombDist*(p(1)-self.selfCoords[1])/dist)
                     selfP = prediction(self.selfCoords[0], self.selfCoords[1], self.selfVelocities[0], self.selfVelocities[1], self.selfAccelerations[0], self.selfAccelerations[1], t*0.05)
                     #make sure won't bomb ourself
                     if (math.sqrt((bP(0)-selfP(0))**2+(bP(1)-selfP(1))**2) > (self.bombEffectRadius):
                         run(self.user, self.password, "BOMB "+bP(0)+" "+bP(1))
                         return
                
                 

    #figure out where to scan
    #scan the place and update information
    def findScanTarget(self):
        startX = round(self.selfCoords[0]/self.numHPartitions)
        startY = round(self.selfCoords[1]/self.numVPartitions)
        if (self.numHPartitions > self.numVPartitions):
            scanRange = self.numHPartitions
        else
            scanrange = self.numVPartitions

        #circular scan
        for r in range(1,scanRange):
            #top line
            for x in range(startX-scanRange, startX+scanRange+1):
                 if (startY-scanRange < 0):
                     break
                 if (x >= 0):
                     if (x < self.numHPartitions):
                         if (not mapVisited[startY-scanRange][x]):
                             run(self.user, self.password, "SCAN "+x+" "+(startY-scanRange))
                             self.scanTimer.start(self.scanDelay)
                             return
                     else:
                         break
            #bottom line
            for x in range(startX-scanRange, startX+scanRange+1):
                 if (startY+scanRange >= numVPartitions):
                     break
                 if (x >= 0):
                     if (x < self.numHPartitions):
                         if (not mapVisited[startY-scanRange][x]):
                             run(self.user, self.password, "SCAN "+x+" "+(startY-scanRange))
                             self.scanTimer.start(self.scanDelay)
                             return
                     else:
                         break
            #left line
            for y in range(startY-scanRange, startY+scanRange+1):
                 if (startX-scanRange < 0):
                     break
                 if (y >= 0):
                     if (y < self.numVPartitions):
                         if (not mapVisited[y][startX-scanRange]):
                             run(self.user, self.password, "SCAN "+(startX-scanRange)+" "+y)
                             self.scanTimer.start(self.scanDelay)
                             return
                     else:
                         break
            #right line
            for y in range(startY-scanRange, startY+scanRange+1):
                 if (startX+scanRange >= numHPartitions):
                     break
                 if (y >= 0):
                     if (y < self.numVPartitions):
                         if (not mapVisited[y][startX-scanRange]):
                             run(self.user, self.password, "SCAN "+(startX-scanRange)+" "+y)
                             self.scanTimer.start(self.scanDelay)
                             return
                     else:
                         break
                 
        
    #enter the info list into self fields
    def enterStatusInfo(self, info):
        
    
    #update all whereabouts
    def updateStatus(self):
        self.enterStatusInfo(parser.parseStatus(run(self.user,self.password,'STATUS')))

    def updateTimers(self):
        self.canScan = self.scanTimer.isFinished()
        self.canBomb = self.bombTimer.isFinished()
    
    def update(self): #main function 
        self.updateStatus()   #get updates
        mapVisited[round(self.selfCoords[1]/self.numVPartitions)][round(self.selfCoords[0]/self.numHPartitions)] = True #update map visited

        #compute next mine and path to next mine only if we don't have a mine locked in
        if (not mineLocked):
            self.destinationCoords = self.findBestMine(self)
            self.path = self.findPath(self.selfCoords[0], self.selfCoords[1], self.destinationCoords[0], self.destinationCoords[1])

        #calculate velocity we want when we reach final point
        dX = self.path[0][0] - self.selfCoords[0]
        dY = self.path[0][1] - self.selfCoords[1]
        if (len(path) > 1):
            dX = self.path[1][0] - self.selfCoords[0]
            dY = self.path[1][1] - self.selfCoords[1]
        self.setCourse(self.path[0][0], self.path[0][1], dX, dY)# take out dX and dY if not needed

        #if we reach a point in the path remove it
        if (math.sqrt((self.selfCoords[0]-self.path[0][0])**2+(self.selfCoords[1]-self.path[0][1])**2) < self.captureRadius):
            del self.path[0]

        #only unlock mine if we reach it or if we get bombed
        if (len(self.path) == 0):
            mineLocked = False
        #if the difference between our current coordinates and where we should be as predicted last tick differs by more than BOMB_ERROR,
        #assume we've been bombed
        if (math.sqrt((self.selfCoords[0]-projectedNextCoords[0])**2+(self.selfCoords[1]-projectedNextCoords[1])**2) > BOMB_ERROR):
            mineLocked = False
        
        self.updateTimers()   #update scan and bomb timer
        if (canBomb):
            findBombTarget()
        if (canScan):
            findScanTarget()


def main():
    logic = Logic()
    while(True):
        logic.update()

main()
        













