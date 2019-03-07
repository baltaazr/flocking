# https://www.intmath.com/vectors/7-vectors-in-3d-space.php

import pygame
from pygame.locals import *
import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *

boids = []

obstacles = []

neighborhoodRadius = 25

speedMagnitude = 1

seperationModifier = 0.0001

alignmentModifier = 0.1

cohesionModifier = 0.001


class Boid:
    def __init__(self, speed, position):
        self.speed = speed
        self.position = position

    def move(self):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        self.position[2] += self.speed[2]

    def seperationSteer(self):
        changeSpeed = [0, 0]
        for neighborBoid in boids:
            if neighborhood(self, neighborBoid.position) and neighborBoid is not self:
                changeX = self.position[0] - neighborBoid.position[0]
                changeY = self.position[1] - neighborBoid.position[1]
                if changeX > 0:
                    changeX = neighborhoodRadius - changeX
                elif changeX < 0:
                    changeX = -neighborhoodRadius - changeX
                else:
                    changeX = 0
                if changeY > 0:
                    changeY = neighborhoodRadius - changeY
                elif changeY < 0:
                    changeY = -neighborhoodRadius - changeY
                else:
                    changeY = 0
                changeSpeed[0] += changeX
                changeSpeed[1] += changeY
        self.speed[0] += changeSpeed[0] * seperationModifier
        self.speed[1] += changeSpeed[1] * seperationModifier
        self.speed[0] = self.speed[0] / \
            getVectorMagnitude(self.speed) * speedMagnitude
        self.speed[1] = self.speed[1] / \
            getVectorMagnitude(self.speed) * speedMagnitude

    def alignmentSteer(self):
        changeSpeed = [0, 0]
        sumUpSpeed = [0, 0]
        totalNeighborBoids = 0
        for neighborBoid in boids:
            if neighborhood(self, neighborBoid.position) and neighborBoid is not self:
                totalNeighborBoids += 1
                sumUpSpeed[0] += neighborBoid.speed[0]
                sumUpSpeed[1] += neighborBoid.speed[1]
        if totalNeighborBoids > 0:
            changeSpeed[0] = sumUpSpeed[0]/totalNeighborBoids
            changeSpeed[1] = sumUpSpeed[1]/totalNeighborBoids
        self.speed[0] += changeSpeed[0] * alignmentModifier
        self.speed[1] += changeSpeed[1] * alignmentModifier
        self.speed[0] = self.speed[0] / \
            getVectorMagnitude(self.speed) * speedMagnitude
        self.speed[1] = self.speed[1] / \
            getVectorMagnitude(self.speed) * speedMagnitude

    def cohesionSteer(self):
        changeSpeed = [0, 0]
        sumUpPosition = [0, 0]
        averagePosition = [0, 0]
        totalNeighborBoids = 0
        for neighborBoid in boids:
            if neighborhood(self, neighborBoid.position) and neighborBoid is not self:
                totalNeighborBoids += 1
                sumUpPosition[0] += neighborBoid.position[0]
                sumUpPosition[1] += neighborBoid.position[1]
        if totalNeighborBoids > 0:
            averagePosition[0] = sumUpPosition[0]/totalNeighborBoids
            averagePosition[1] = sumUpPosition[1]/totalNeighborBoids
            changeSpeed[0] = averagePosition[0] - self.position[0]
            changeSpeed[1] = averagePosition[1] - self.position[1]
        self.speed[0] += changeSpeed[0] * cohesionModifier
        self.speed[1] += changeSpeed[1] * cohesionModifier
        self.speed[0] = self.speed[0] / \
            getVectorMagnitude(self.speed) * speedMagnitude
        self.speed[1] = self.speed[1] / \
            getVectorMagnitude(self.speed) * speedMagnitude

    def getAngle(self):
        angle1 = math.acos(self.speed[0]/getVectorMagnitude(self.speed))
        if boid.speed[1] < 0:
            angle1 = math.acos(-self.speed[0] /
                              getVectorMagnitude(self.speed)) + math.pi
        angle2 = math.acos(math.sqrt(self.speed[0]**2+self.speed[1]**2)/getVectorMagnitude(self.speed))
        if self.speed[2] < 0:
            angle = math.acos(-math.sqrt(self.speed[0]**2+self.speed[1]**2)/getVectorMagnitude(self.speed)) + math.pi
        return (angle1,angle2)

    def setAngle(self, angle):
        self.speed[0] = speedMagnitude*math.cos(angle)
        self.speed[1] = speedMagnitude*math.sin(angle)

def dist(p1, p2):
    return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)+((p1[2]-p2[2])**2))


def getVectorMagnitude(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


def drawPyramid(boid):
    glBegin(GL_LINE_LOOP)

    glVertex3f(0.5, -0.5, 0.0)
    glVertex3f(0.5, 0.5, 0.0)
    glVertex3f(-0.5, 0.5, 0.0)
    glVertex3f(-0.5, -0.5, 0.0)
    glEnd()
    # draw the nose
    glBegin(GL_LINES)

    glVertex3f(0.5, -0.5, 0.0)
    # glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1)

    # glColor3f(1.0, 1.0, 1.0)
    glVertex3f(0.5, 0.5, 0.0)
    # glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1)

    # glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-0.5, 0.5, 0.0)
    # glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1)

    # glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-0.5, -0.5, 0.0)
    #  glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1)
    glEnd()


def main():
    boids.append(Boid([0, 0, 0], [0, 0, 0]))
    pygame.init()

    size = width, height = 500, 500
    black = 0, 0, 0
    blue = 66, 134, 244

    pygame.display.set_mode(size, DOUBLEBUF | OPENGL)

    gluPerspective(45, (size[0]/size[1]), 0.1, 50.0)

    glTranslatef(0.0, 0.0, -5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for boid in boids:
            # boid.seperationSteer()
            # boid.alignmentSteer()
            # boid.cohesionSteer()
            boid.move()
            if boid.position[0] < 0:
                boid.position[0] += 500
            if boid.position[1] < 0:
                boid.position[1] += 500
            if boid.position[2] < 0:
                boid.position[2] += 500
            if boid.position[0] > 500:
                boid.position[0] -= 500
            if boid.position[1] > 500:
                boid.position[1] -= 500
            if boid.position[2] > 500:
                boid.position[2] -= 500
            drawPyramid(boid)
        pygame.display.flip()
        pygame.time.wait(10)


main()
