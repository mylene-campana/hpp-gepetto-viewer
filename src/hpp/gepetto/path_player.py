# Copyright (c) 2013, 2014 CNRS
# Author: Florent Lamiraux
#
# This file is part of hpp-gepetto-viewer.
# hpp-gepetto-viewer is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# hpp-gepetto-viewer is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Lesser Public License for more details.  You should have
# received a copy of the GNU Lesser General Public License along with
# hpp-gepetto-viewer.  If not, see
# <http://www.gnu.org/licenses/>.

import time
import numpy as np
import pickle as pk

## displays a path by sampling configurations along the path.
#
class PathPlayer (object):
    def __init__ (self, client, publisher, dt = 0.01, speed = 1) :
        self.client = client
        self.publisher = publisher
        self.dt = dt
        self.speed = speed
        self.start = 0.
        self.end = 1.

    def setDt(self,dt):
      self.dt = dt

    def setSpeed(self,speed) :
      self.speed = speed

    def __call__ (self, pathId) :
        length = self.end*self.client.problem.pathLength (pathId)
        t = self.start*self.client.problem.pathLength (pathId)
        while t < length :
            start = time.time()
            q = self.client.problem.configAtParam (pathId, t)
            self.publisher.robotConfig = q
            self.publisher.publishRobots ()
            t += (self.dt * self.speed)
            elapsed = time.time() - start
            if elapsed < self.dt :
              time.sleep(self.dt-elapsed)

    def displayPath(self,pathId,color=[0.85,0.75,0.15,0.9],jointName=0) :
      if jointName == 0 :
        if self.publisher.robot.rootJointType == 'planar' :
          jointName = self.publisher.robot.tf_root+'_joint'
      pathPos=[]
      length = self.end*self.client.problem.pathLength (pathId)
      t = self.start*self.client.problem.pathLength (pathId)
      while t < length :
        q = self.client.problem.configAtParam (pathId, t)
        if jointName != 0 : 
          self.publisher.robot.setCurrentConfig(q)
          q = self.publisher.robot.getLinkPosition(jointName)
        pathPos = pathPos + [q[:3]]
        t += self.dt
      if jointName == 0 :
        jointName = "root"
      nameCurve = "path_"+str(pathId)+"_"+jointName
      self.publisher.client.gui.addCurve(nameCurve,pathPos,color)
      self.publisher.client.gui.addToGroup(nameCurve,self.publisher.sceneName)
      self.publisher.client.gui.refresh()



    def toFile(self, pathId, fname):
        length = self.client.problem.pathLength (pathId)
        t = 0
        tau = []
        while t < length :
            q = self.client.problem.configAtParam (pathId, t)
            tau.append(q)
            t += (self.dt * self.speed)
        fh = open(fname,"wb")
        pk.dump(tau,fh)
        fh.close()

    def toFileAppend(self, pathId, fname):
        length = self.client.problem.pathLength (pathId)
        t = 0
        tau = []
        while t < length :
            q = self.client.problem.configAtParam (pathId, t)
            tau.append(q)
            t += self.dt
        fh = open(fname,"a")
        pk.dump(tau,fh)
        fh.close()

    def getTrajFromFile(self, fname):
        fh = open(fname,"rb")
        tau = []
        while 1:
            try:
                tau.append(pk.load(fh))
            except EOFError:
                break
        fh.close()
        return tau

    def fromFile(self, fname):
        self.tau = self.getTrajFromFile(fname)
        for tauK in self.tau:
            for q in tauK:
                start = time.time()
                self.publisher.robotConfig = q
                self.publisher.publishRobots ()
                elapsed = time.time() - start
                if elapsed < self.dt :
                  time.sleep(self.dt-elapsed)

    # to use this function, create a sphere of name "comName"
    def plotRobotTrajectoryWithCOM (self, pathId, comName):
        length = self.end*self.client.problem.pathLength (pathId)
        t = self.start*self.client.problem.pathLength (pathId)
        comQ = [0,0,0,1,0,0,0]
        while t < length :
            start = time.time()
            q = self.client.problem.configAtParam (pathId, t)
            self.publisher.robotConfig = q
            self.publisher.publishRobots ()
            comQ [0:3] = self.client.robot.getCenterOfMass ()
            self.publisher.client.gui.applyConfiguration (comName, comQ)
            self.publisher.client.gui.addToGroup (comName, self.publisher.sceneName)
            t += (self.dt * self.speed)
            elapsed = time.time() - start
            if elapsed < self.dt :
              time.sleep(self.dt-elapsed)
