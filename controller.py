from xmlrpc.client import Boolean
from scipy.spatial import KDTree
from dijkstar import Graph,find_path
import numpy as np



class Controller:
    def __init__(self, workspace, configspace):
        self.workspace = workspace
        self.configspace= configspace
        self.configspace.setDimensions(self.workspace.envArray.shape[1]-round(self.workspace.robotArray.shape[1]/2)
        ,self.workspace.envArray.shape[0]-round(self.workspace.robotArray.shape[0]/2))
        ## calculation of the Configspace
        #self.calcConfigspace()

    def calcConfigspace(self):
        for i in range(self.configspace.yExt):
            for j in range(self.configspace.xExt):
                print(str(i)+str(j))
                if self.workspace.isInCollisionFast(i+round(self.workspace.robotArray.shape[1]/2),j+round(self.workspace.robotArray.shape[0]/2)):
                    self.configspace.obsConfig.append([i,j]) 

    def setCurrentPosAsInit(self):
        self.configspace.initConfig=(self.workspace.currentPos[0],self.workspace.currentPos[1])
        self.configspace.drawSpace()

    def setCurrentPosAsGoal(self):
        self.configspace.goalConfig=(self.workspace.currentPos[0],self.workspace.currentPos[1])
        path = self.sPRM()
        self.configspace.setSolutionPath(path)
        #self.configspace.setIntialSolutionPath()
        self.configspace.isInitialize = True
        self.workspace.isInitialize = True
        self.configspace.drawSpace()

    def drawMouseOffSet(self,mouseX,mouseY):
        self.workspace.drawAll(mouseX-round(0.5*self.workspace.robotImage.width),mouseY-round(0.5*self.workspace.robotImage.height),
        self.configspace.initConfig[0],self.configspace.initConfig[1], 
        self.configspace.goalConfig[0],self.configspace.goalConfig[1])

    def drawCurrentPos(self):
        self.workspace.drawAll(self.workspace.currentPos[0],self.workspace.currentPos[1],
        self.configspace.initConfig[0],self.configspace.initConfig[1], 
        self.configspace.goalConfig[0],self.configspace.goalConfig[1])

    def isInCollision(self, x=None,y=None):
        if x is None: x= self.workspace.currentPos[0]
        if y is None: y= self.workspace.currentPos[1]
        return self.workspace.isInCollisionFast(x,y)
    
    def sPRM(self, distances=10):
        initP = self.configspace.getInitPos()
        goalP = self.configspace.getGoalPos()
        if self.isInCollision(initP[0],initP[1]) is True: return []
        if self.isInCollision(goalP[0],goalP[1]) is True: return []
        points,path = [],[]
        graph = Graph()
        points.append(initP)
        points.append(goalP)
        samplePoints = self.configspace.uniformSampling(2000)
        for point in samplePoints:
            if self.isInCollision(point[0],point[1]) is False:
                points.append(point)
        points = np.array(points)
        print('points')
        print(points)
        tree = KDTree(np.copy(points), leafsize=points.shape[0]+1)
        for p in range(len(points)):
            distanceToNeigbor,ndx = tree.query(points[p],k=11)
            print('indexNeig')
            print(ndx)
            for i in range(len(ndx)):
                if distanceToNeigbor[i]>0:
                    if self.testValidEdge(points,p,ndx[i],distanceToNeigbor[i]) is True:
                        graph.add_edge(p,ndx[i],distanceToNeigbor[i])
        #print('Graph:')
        #print(graph)
        indizes = find_path(graph, initP, goalP).nodes
        print('index0')
        print(indizes)
        for i in indizes:
            path.append(points[i])
        try:
            indizes = find_path(graph, initP, goalP).nodes
            print('index0')
            print(indizes)
            for i in indizes:
                path.append(points[i])
        except:
            return []
        print('path0')
        print(path)
        return path
    
    
    # nicht mehr benötigt  
    # def connected(self,initP,goalP,v,e):
    #     graph = np.copy(v)
    #     observedPoints = [initP]
    #     while len(observedPoints)!=0 :
    #         for point in observedPoints:
    #             if point==goalP:
    #                 return True
    #         for point in observedPoints:
    #             np.delete(observedPoints,point)
    #             for edge in graph:
    #                 if edge[0]==point:
    #                     np.append(observedPoints,edge[1])
    #                     np.delete(graph,edge)
    #                 elif edge[1]==point:
    #                     np.append(observedPoints,edge[0])
    #                     np.delete(graph,edge)
    #     return False
          
    def testValidEdge(self,points,s,g,distance,numberOfPoints=10):
        start = points[s]
        goal = points[g]
        resolution = max(abs(start[0]-goal[0]), abs(start[1]-goal[1]))
        #stepWidth = distance/(float) (numberOfPoints)
        #r = [goal[0]-start[0],goal[1]-start[1]]
        for i in range(resolution):
            deltaX = round(i*float(goal[0]-start[0])/float(resolution))
            deltaY = round(i*float(goal[1]-start[1])/float(resolution))
            newX = start[0] + deltaX
            newY = start[1] + deltaY
            if self.isInCollision(newX,newY) is True:#(int)(start[0]+i*stepWidth*r[0]),(int)(start[1]+i*stepWidth*r[1])
                return False
        return True
    
    def isAllInitialized(self):
        if self.configspace.isInitialize and self.workspace.isInitialize: return True
        return False
    
    def setSolutionPathOnCurrentPos(self, index):
        self.workspace.currentPos = self.configspace.solutionPath[index]