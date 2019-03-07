# https://www.pygame.org/docs/
# https://www.red3d.com/cwr/boids/

import sys
import pygame
import math
from tkinter import *
import random
from pygame import mixer  # Load the required library

boids = []

obstacles = []

neighborhoodRadius = 25

speedMagnitude = 1

seperationModifier = 0.0001

alignmentModifier = 0.1

cohesionModifier = 0.001

obstacleAvoidanceRadius = 20

obstacleAvoidanceRadians = math.pi/6


class Boid:
    def __init__(self, speed, position):
        self.speed = speed
        self.position = position

    def move(self):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]

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

    def obstacleAvoidanceSteer(self):
        changeSpeed = [0, 0]
        w = 20
        for neighborObstacle in obstacles:
            if neighborhood(self, neighborObstacle, angle=obstacleAvoidanceRadians, radius=obstacleAvoidanceRadius):
                rightDist = dist(neighborObstacle, [self.position[0]+(w/2)*math.cos(
                    self.getAngle()+90), self.position[1]+(w/2)*math.sin(self.getAngle()+90)])
                leftDist = dist(neighborObstacle, [self.position[0]+(w/2)*math.cos(
                    self.getAngle()-90), self.position[1]+(w/2)*math.sin(self.getAngle()-90)])
                g = max(leftDist, rightDist)
                l = min(leftDist, rightDist)
                a = math.atan(l/w)
                b = math.acos((l**2+g**2)/(2*g*math.sqrt(w**2+l**2)))
                degreeChange = 90 - a - b
                self.setAngle(self.getAngle(
                )-degreeChange) if leftDist > rightDist else self.setAngle(self.getAngle()+degreeChange)

    def getAngle(self):
        angle = math.acos(self.speed[0]/getVectorMagnitude(self.speed))
        if boid.speed[1] < 0:
            angle = math.acos(-self.speed[0] /
                              getVectorMagnitude(self.speed)) + math.pi
        return angle

    def setAngle(self, angle):
        self.speed[0] = speedMagnitude*math.cos(angle)
        self.speed[1] = speedMagnitude*math.sin(angle)


def neighborhood(boid1, boid2Position, angle=math.pi*5/6, radius=neighborhoodRadius):
    vector1 = [boid1.speed[0], boid1.speed[1]]
    vector2 = [boid2Position[0]-boid1.position[0],
               boid2Position[1]-boid1.position[1]]
    withinRadius = dist(boid1.position, boid2Position) <= radius
    magnitudesMultiplied = getVectorMagnitude(
        vector1)*getVectorMagnitude(vector2)
    if magnitudesMultiplied == 0:
        return withinRadius
    x = (vector1[0]*vector2[0] + vector1[1]*vector2[1]) / magnitudesMultiplied
    if x < -1:
        x = -1
    if x > 1:
        x = 1
    if withinRadius and math.acos(x) <= angle:
        return True
    return False


def dist(p1, p2):
    return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))


def getVectorMagnitude(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


def getBoidTriangleCoordinates(boid):
    coordinates = []
    speedMagnitude = getVectorMagnitude(boid.speed)
    speedUnitVector = [boid.speed[0] /
                       speedMagnitude, boid.speed[1]/speedMagnitude]
    coordinates.append((boid.position[0]+speedUnitVector[0]*10,
                        boid.position[1]+speedUnitVector[1]*10))
    angle = boid.getAngle()
    coordinates.append((boid.position[0]+math.cos(angle + math.pi * 5/6)*5,
                        boid.position[1]+math.sin(angle + math.pi * 5/6)*5))
    coordinates.append((boid.position[0]+math.cos(angle - math.pi * 5/6)*5,
                        boid.position[1]+math.sin(angle - math.pi * 5/6)*5))
    return coordinates


def intResponse(response):
    try:
        return int(response)
    except:
        return intResponse(input('Please enter a number: '))


# MAIN
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [200, 200]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [250, 200]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [300, 200]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [200, 250]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [250, 250]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [300, 250]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [200, 300]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [250, 300]))
boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                   math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [300, 300]))

testBoid = Boid([1, 1], [250, 250])

interval = intResponse(input('Degree Interval between circles: '))

if interval < 361:
    radius = intResponse(input('Radius of the circle: '))

    for degrees in range(0, 360, interval):
        radians = degrees * math.pi / 180
        obstacles.append(
            [250+radius*math.cos(radians), 250+radius*math.sin(radians)])

pygame.init()
mixer.init()
mixer.music.load(
    './tangerineDream.mp3')
mixer.music.play()

size = width, height = 500, 500
black = 0, 0, 0

screen = pygame.display.set_mode(size)

master = Tk()

speedSlider = Scale(master, from_=1, to=10,
                    orient=HORIZONTAL, label='Speed')
speedSlider.pack()
speedSlider.set(5)

seperationSlider = Scale(master, from_=0, to=10,
                         orient=HORIZONTAL, label='Seperation')
seperationSlider.pack()
seperationSlider.set(5)

alignmentSlider = Scale(master, from_=0, to=10,
                        orient=HORIZONTAL, label='Alignment')
alignmentSlider.pack()
alignmentSlider.set(5)

cohesionSlider = Scale(master, from_=0, to=10,
                       orient=HORIZONTAL, label='Cohesion')
cohesionSlider.pack()
cohesionSlider.set(5)

neighborhoodRadiusSlider = Scale(
    master, from_=0, to=250, orient=HORIZONTAL, label='Neighborhood Radius')
neighborhoodRadiusSlider.pack()
neighborhoodRadiusSlider.set(50)

oaSlider = Scale(
    master, from_=1, to=10, orient=HORIZONTAL, label='Obstacle Avoidance')
oaSlider.pack()
oaSlider.set(5)

oarSlider = Scale(
    master, from_=0, to=10, orient=HORIZONTAL, label='Obstacle Avoidance Radius')
oarSlider.pack()
oarSlider.set(5)

while True:
    master.update()
    speedMagnitude = speedSlider.get()/5
    seperationModifier = seperationSlider.get()/5000
    alignmentModifier = alignmentSlider.get()/50
    cohesionModifier = cohesionSlider.get()/500
    neighborhoodRadius = neighborhoodRadiusSlider.get()
    obstacleAvoidanceRadians = oaSlider.get()/5*math.pi/6
    obstacleAvoidanceRadius = oarSlider.get()*4

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if pygame.mouse.get_pressed()[0]:
            boids.append(Boid([math.cos(random.randint(0, 360)*math.pi/180) * speedMagnitude,
                               math.sin(random.randint(0, 360)*math.pi/180) * speedMagnitude], [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]))

        if pygame.mouse.get_pressed()[2]:
            obstacles.append([pygame.mouse.get_pos()[0],
                              pygame.mouse.get_pos()[1]])

    screen.fill(black)

    # pygame.draw.polygon(screen, blue, getBoidTriangleCoordinates(testBoid))

    # for x in range(0, 500):
    #     for y in range(0, 500):
    #         if neighborhood(testBoid, Boid([0, 0], [x, y])):
    #             pygame.draw.circle(screen, (255, 255, 255), [x, y], 1)

    for obstacle in obstacles:
        pygame.draw.circle(screen, (255, 0, 0), [
            int(obstacle[0]), int(obstacle[1])], 5)

    for boid in boids:
        boid.seperationSteer()
        boid.alignmentSteer()
        boid.cohesionSteer()
        boid.obstacleAvoidanceSteer()
        boid.move()
        if boid.position[0] < 0:
            boid.position[0] += 500
        if boid.position[1] < 0:
            boid.position[1] += 500
        if boid.position[0] > 500:
            boid.position[0] -= 500
        if boid.position[1] > 500:
            boid.position[1] -= 500
        pygame.draw.polygon(screen, (abs(255*math.cos(boid.getAngle())), 125,
                                     abs(255*math.cos(boid.getAngle()))), getBoidTriangleCoordinates(boid))
    pygame.display.flip()
