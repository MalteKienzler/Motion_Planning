from turtle import pos
import numpy as np
from PIL import Image, ImageTk, ImageColor
from io import BytesIO
from tkinter import ttk, Canvas, NW
import os
from configspace import Configspace
from utils import  isPixelWhite


class Workspace:
    def __init__(self, robotImagePath, envImagePath, root):
        
        self.root = root
        self.envImage = Image.open(envImagePath)
        self.envArray = np.array(self.envImage)
        self.envPhoto = ImageTk.PhotoImage(self.envImage)

        self.robotImage = Image.open(robotImagePath)
        self.robotArray = np.array(self.robotImage)
        self.robotPhoto = ImageTk.PhotoImage(self.robotImage)
        self.robotContourMap = self.__calcContour()

        self.label = ttk.Label(root, image = self.envPhoto)

        self.currentPos = (0,0)
        self.isInitialize = False

    def drawAll (self,xCurrent,yCurrent,xInit=-1,yInit=-1,xGoal=-1,yGoal=-1):
        self.currentPos=xCurrent,yCurrent
        self.imageToDraw = self.envImage.copy()
        if xInit>-1: self.imageToDraw.paste(self.robotImage.copy(),(xInit,yInit))
        if xGoal>-1: self.imageToDraw.paste(self.robotImage.copy(),(xGoal,yGoal))
        self.imageToDraw.paste(self.robotImage.copy(),(self.currentPos[0],self.currentPos[1]))
        self.photoToDraw = ImageTk.PhotoImage(self.imageToDraw)
        self.label.configure(image=self.photoToDraw)
        self.label.image = self.photoToDraw
        self.label.pack(side = "bottom", fill = "both", expand = "yes")

    def __calcContour(self):
        contourMap = []
        height,width, _ = self.robotArray.shape
        for i in range(height):
            for j in range(width):
                hasWhiteNeigbor = False
                if not isPixelWhite(self.robotArray[i][j]):
                    if i==0 or j==0 or i==height-1 or j==width-1:
                        contourMap.append([i,j])
                    if i > 0 and i < height-1:
                        if j > 0 and j < width-1:
                            ytemp = i-1
                            xtemp = j-1
                            for a in range(3):
                                for b in range(3):
                                    if isPixelWhite(self.robotArray[ytemp+a][xtemp+b]):
                                        hasWhiteNeigbor = True
                                        contourMap.append([i,j])
                                        break
                                if hasWhiteNeigbor:
                                    break                                     
        return contourMap 
               
    def isInCollisionFast(self,x,y):
        height, width, _ = self.envArray.shape
        for contourPoint in self.robotContourMap:
            posX = x+contourPoint[1]
            posY = y+contourPoint[0]
            if posX >= 0 and posX < width:
                if posY >=0 and posY < height:
                    if not isPixelWhite(self.envArray[posY][posX]):
                        return True
        return False
   
    def isInCollision(self,x,y):
        robotHeight = len(self.robotArray)
        robotWidth = len(self.robotArray[0])
        # iterate over Height and Width of the Robot
        for i in range(robotHeight):
            for j in range(robotWidth):
                posx = x+j 
                posy = y+i
                # check if Pixel of Robot is a Black Pixel
                if not isPixelWhite(self.robotArray[j][i]):
                    # check if Position is in the Env.
                    if posx >= 0 and posx < len(self.envArray[0]):
                        if posy >=0 and posy < len(self.envArray):
                            # check if Pixel of Env. is a Black Pixel
                            if not isPixelWhite(self.envArray[posy][posx]):
                                return True        
        return False


        
    
