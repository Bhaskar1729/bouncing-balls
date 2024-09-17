from tkinter import *
import random
import time
import math


HEIGHT = 800
WIDTH = 600

tk = Tk()
canvas = Canvas(tk, width = WIDTH, height = HEIGHT)
tk.title("Bouncing balls")
canvas.pack()
balls = []
dt = 0.1

class Ball:
    def __init__(self, color, size, xspeed, yspeed, x, y):
        self.shape = canvas.create_oval(x-size, y-size, x+size, y+size, fill=color)
        self.size = size
        self.color = color
        self.xspeed = xspeed
        self.yspeed = yspeed
        self.mass = 10
        self.x = x
        self.y = y
        self.newxspeed = xspeed
        self.newyspeed = yspeed
        

    def move(self):
        self.x += self.xspeed*dt
        self.y += self.yspeed*dt
    
        if self.x-self.size <= 0:
            self.xspeed = abs(self.xspeed)
            
        if self.x + self.size >= WIDTH:
            self.xspeed = -abs(self.xspeed)
            
        if self.y-self.size <= 0:
            self.yspeed = abs(self.yspeed)
            
        if self.y + self.size >= HEIGHT:
            self.yspeed = -abs(self.yspeed)
        
        self.newxspeed = self.xspeed
        self.newyspeed = self.yspeed

    def collide(self, other):
        c1 = self.center()
        c1[0] += self.xspeed*dt
        c1[1] += self.yspeed*dt
        
        c2 = other.center()
        c2[0] += other.xspeed*dt
        c2[1] += other.yspeed*dt
    
        return (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 <= (self.size + other.size)**2
    
    def center(self):
        return [self.x, self.y]
    
    def updateSpeed(self):
        self.xspeed = self.newxspeed
        self.yspeed = self.newyspeed

class Point:
    def __init__(self, ball: Ball):
        c = ball.center()
        self.x = c[0]
        self.y = c[1]
        self.obj = ball

class Range:
    def __init__(self, point, epsilon = 0):
        self.x_min = point.x - epsilon
        self.x_max = point.x + epsilon
        self.y_min = point.y - epsilon
        self.y_max = point.y + epsilon

class QuadTree:
    def __init__(self, x_min, y_min, x_max, y_max, capacity):
        self.isDivided = False
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.capacity = capacity
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None
        self.elements = []
    
    def insert(self, point):
        if not self.overlap(Range(point)):
            return False
        
        if not self.isDivided:
            self.elements.append(point)
            if len(self.elements) > self.capacity:
                self.subDivide()
        else:
            if self.nw.insert(point):
                return True
            if self.ne.insert(point):
                return True
            if self.sw.insert(point):
                return True
            if self.se.insert(point):
                return True
            
    def subDivide(self):
        self.nw = QuadTree(self.x_min, self.y_min, (self.x_max + self.x_min)/2, (self.y_max + self.y_min)/2, self.capacity)
        self.ne = QuadTree((self.x_max + self.x_min)/2, self.y_min, self.x_max, (self.y_max + self.y_min)/2, self.capacity)
        self.sw = QuadTree(self.x_min, (self.y_max + self.y_min)/2, (self.x_max + self.x_min)/2, self.y_max, self.capacity)
        self.se = QuadTree((self.x_max + self.x_min)/2, (self.y_max + self.y_min)/2, self.x_max, self.y_max, self.capacity)
        
        for point in self.elements:
            if self.nw.insert(point):
                continue
            if self.ne.insert(point):
                continue
            if self.sw.insert(point):
                continue
            if self.se.insert(point):
                continue
        
        self.isDivided = True
        
        
    def overlap(self, range):
        return not (self.x_max < range.x_min or self.x_min > range.x_max or self.y_max < range.y_min or self.y_min > range.y_max)
    
    def query(self, range, found = None) -> list[Point]:
        if found == None:
            found = []
        
        if not self.overlap(range):
            return found
        
        if not self.isDivided:
            for point in self.elements:
                if self.overlap(Range(point)):
                    found.append(point)
            return found
        
        self.ne.query(range, found)
        self.nw.query(range, found)
        self.se.query(range, found)
        self.sw.query(range, found)
        
        return found
        
colors = ["yellow", "blue", "red", "green"]

numberOfBalls = 1000
radius = 3

for i in range(numberOfBalls):
    balls.append(Ball(random.choice(colors), radius, random.randint(-20, 20), random.randint(-20, 20), random.randrange(0, WIDTH-20), random.randrange(0, HEIGHT-20)))
    
while True:
    qt = QuadTree(0, 0, WIDTH, HEIGHT, 10)

    for i in range(len(balls)):
        qt.insert(Point(balls[i]))
        
    processed = set()
        
    for i in range(len(balls)):
        points = qt.query(Range(Point(balls[i]), 5*radius))
        for point in points:
            ball = point.obj
    
            if ball in processed or ball == balls[i]:
                continue
            
            if (not balls[i].collide(ball)):
                continue
            
            v1 = balls[i].xspeed**2 + balls[i].yspeed**2
            v1 = v1**0.5
            theta1 = math.atan2(balls[i].yspeed, balls[i].xspeed)
            c1 = [balls[i].x, balls[i].y]

            v2 = ball.xspeed**2 + ball.yspeed**2
            v2 = v2**0.5
            theta2 = math.atan2(ball.yspeed, ball.xspeed)
            c2 = [ball.x, ball.y]

            phi = math.atan2(c2[1]-c1[1], c2[0]-c1[0])
                        
            balls[i].newxspeed = (v1*math.cos(theta1-phi)*(balls[i].mass - ball.mass) + 2*ball.mass*v2*math.cos(theta2-phi))/(balls[i].mass + ball.mass) * math.cos(phi) + v1*math.sin(theta1-phi)*math.cos(phi + math.pi/2)
            balls[i].newyspeed = (v1*math.cos(theta1-phi)*(balls[i].mass - ball.mass) + 2*ball.mass*v2*math.cos(theta2-phi))/(balls[i].mass + ball.mass) * math.sin(phi) + v1*math.sin(theta1-phi)*math.sin(phi + math.pi/2)

            ball.newxspeed = (v2*math.cos(theta2-phi)*(ball.mass - balls[i].mass) + 2*balls[i].mass*v1*math.cos(theta1-phi))/(ball.mass + balls[i].mass) * math.cos(phi) + v2*math.sin(theta2-phi)*math.cos(phi + math.pi/2)
            ball.newyspeed = (v2*math.cos(theta2-phi)*(ball.mass - balls[i].mass) + 2*balls[i].mass*v1*math.cos(theta1-phi))/(ball.mass + balls[i].mass) * math.sin(phi) + v2*math.sin(theta2-phi)*math.sin(phi + math.pi/2)
            
            processed.add(balls[i])
                
    energy = 0
    mx = 0
    my = 0
    canvas.delete("all")
    for i in range(len(balls)):
        balls[i].updateSpeed()
        balls[i].move()
        balls[i].shape = canvas.create_oval(balls[i].x-balls[i].size, balls[i].y-balls[i].size, balls[i].x+balls[i].size, balls[i].y+balls[i].size, fill = balls[i].color)
        
        energy += balls[i].xspeed**2 + balls[i].yspeed**2
        mx += balls[i].xspeed
        my += balls[i].yspeed
            
    tk.update()
    
