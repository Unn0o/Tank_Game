import math
import pygame
import pyfirmata2
import time
import subprocess
import sys
from pyfirmata2 import Arduino, util
from win32api import GetSystemMetrics

#Arduino config
board = Arduino('com22')#Port where the arduino is connected
it = util.Iterator(board)
it.start()
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()
board.analog[2].enable_reporting()
board.analog[3].enable_reporting()
board.analog[4].enable_reporting()
board.analog[5].enable_reporting()
 
button1 = board.digital[4]
button1.mode = pyfirmata2.INPUT
tankki1nappi = button1
 
button2 = board.digital[2]
button2.mode = pyfirmata2.INPUT
tankki2nappi = button2
 
button3 = board.digital[8]
button3.mode = pyfirmata2.INPUT
tankki3nappi = button3
 
button4 = board.digital[12]
button4.mode = pyfirmata2.INPUT
tankki4nappi = button4
 
#pygame config
pygame.init()
size = width,height = GetSystemMetrics(0),GetSystemMetrics(1) #Finds screen resolution
print(width)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.mixer.init()
 
#Images
scale = (width+height)/2
tankki1 = pygame.image.load('tankki.png')
tankki1 = pygame.transform.scale(tankki1,(0.077*scale,0.1*scale))
 
tankki2 = pygame.image.load('tankki2.png')
tankki2 = pygame.transform.scale(tankki2,(0.077*scale,0.1*scale))
 
#Creates the Tank class
class Tank:  
    def __init__(self,tankki,ohjain1,ohjain2,ohjain3,tankkiX,tankkiY,tankBtn,tank2Btn):
        #Picture of the bullet
        self.panos = pygame.image.load('panos.png')
        self.panos = pygame.transform.scale(self.panos,(0.01875*scale,0.0375*scale))
        
        #Picture of the cannon
        self.tykki = pygame.image.load('tykki.png')
        self.tykki = pygame.transform.scale(self.tykki,(0.035*scale,0.12*scale))
        self.tykki1 = self.tykki
        
        #Picture of the mine
        self.mine = pygame.image.load('mine.png')
        self.mine = pygame.transform.scale(self.mine,(0.0625*scale,0.0625*scale))
 
        #Picture of tank
        self.tankki1 = tankki
        
        #Buttons and pins
        self.Btn = tankBtn
        self.Btn2 = tank2Btn
 
        self.pin1 = ohjain1
        self.pin2 = ohjain2
        self.pin3 = ohjain3
       
        #Tanks positon
        self.x = tankkiX
        self.y = tankkiY

        #Default values
        self.kaantyminen = 90
        self.kaantyminen2 = 90
        self.pauseliikkuminen = 0
        self.pausekaantyminen = 0
        self.liikkuminen = 0
        self.oldX = 0
        self.oldY = 0
        self.oldkaantyminen = 0
        self.oldkaantyminen2 = 0
        self.bullets = []
        self.mines = []
        self.points = 0
        self.ammuttu = 0
        self.miinattu = 0
        self.is_moving = 0
        self.hitbox = []
        self.osumat = 0
    
    #Calculates the position of the hitboxes
    def draw_rect_angle(self, surf, rect, pivot, angle):
        quarterxL_Top = rect.left + rect.width // 4
        quarterxR_Top = rect.right - rect.width // 4
        quarterxL_Bottom = rect.left + rect.width // 4
        quarterxR_Bottom = rect.right - rect.width // 4
        quarteryL_Top = (rect.topleft[0] + 5,rect.topleft[1] + 25)
        quarteryR_Top = (rect.topright[0] - 5,rect.topright[1] + 25)
        quarteryL_Bottom = (rect.topleft[0] + 5,rect.topleft[1] + 75)
        quarteryR_Bottom = (rect.topright[0] - 5,rect.topright[1] + 75)
 
        self.pts = [(rect.topleft[0] + 5,rect.topleft[1] + 5),(rect.midtop[0],rect.midtop[1] + 5),
                    (rect.midbottom[0],rect.midbottom[1] - 5),(rect.midright[0] - 5,rect.midright[1]),
                    (rect.midleft[0] + 5,rect.midleft[1]),(rect.topright[0] - 5,rect.topright[1] + 5), 
                    (rect.bottomright[0] - 5,rect.bottomright[1] - 5),(rect.bottomleft[0] + 5,rect.bottomleft[1] - 5),
                    (quarterxR_Top, rect.midtop[1] + 5), (quarterxL_Top, rect.midtop[1] + 5),
                    (quarterxR_Bottom, rect.midbottom[1] - 5), (quarterxL_Bottom, rect.midbottom[1] - 5),
                    (quarteryR_Top),(quarteryR_Bottom),(quarteryL_Top),(quarteryL_Bottom)
                    ]
       
        self.pts = [(pygame.math.Vector2(p) - pivot).rotate(-angle) + pivot for p in self.pts]
        for i in range(len(self.pts)):
            self.hitbox.append(self.pts[i])

    #Here is the code for the game
    def play(self):
        if(self.ammuttu > 0):
            self.ammuttu += 1
        if(self.ammuttu > 90):
            self.ammuttu = 0
        if(self.miinattu > 0):
            self.miinattu += 1
        if(self.miinattu > 600):
            self.miinattu = 0
 
        #Reads pins
        self.kulma = board.analog[self.pin1].read()
        self.kulma2 = board.analog[self.pin2].read()
        self.tykki = board.analog[self.pin3].read()
        
        #Reads button
        self.tankkiBtn = self.Btn.read()
        self.tankki2Btn = self.Btn2.read()
       
        #Counts where to move and how much
        if((self.kulma >0.45 and self.kulma < 0.55)) and (self.kulma2 >0.45 and self.kulma2 < 0.55):
            self.x += 0
            self.y += 0
            self.kaantyminen += 0
            self.kaantyminen2 += 0
            self.liikkuminen = self.kaantyminen2 - self.kaantyminen
        else:
            self.kaantyminen += (int(self.kulma * 180) - 90) *(0.000021*((width+height)/2))
            self.kaantyminen2 += (int(self.kulma2 * 180) - 90) * (0.000021*((width+height)/2))
            self.liikkuminen = self.kaantyminen2 - self.kaantyminen
            if(self.kulma + self.kulma2 < 1):
                self.x += (math.cos(math.radians(self.liikkuminen+90)))*(-0.0011*((width+height)/2))
                self.y -= math.sin(math.radians(self.liikkuminen+90))*(-0.0011*((width+height)/2))
            else:
                self.x += (math.cos(math.radians(self.liikkuminen+90)))*(0.0011*((width+height)/2))
                self.y -= math.sin(math.radians(self.liikkuminen+90))*(0.0011*((width+height)/2))
            self.is_moving += 1

        if(self.kaantyminen <= 0):
            self.kaantyminen += 360
        elif(self.kaantyminen >= 360):
            self.kaantyminen -= 360
            
        #Plays a sound when a mine is detonated
        for miina in self.mines:
            if(self.miinattu == 0):
                pygame.mixer.Channel(1).play(pygame.mixer.Sound("pum.mp3"))
 
                self.mines.clear()
            screen.blit(self.mine, (miina[0],miina[1]))
        
        if(self.tankki2Btn == True and self.miinattu ==  0):
            self.miinattu += 1
            self.mines.append([self.x,self.y])  

        #Rotates the tank
        rotated_tankki1 = pygame.transform.rotate(self.tankki1, self.liikkuminen)
        new_tankki1 = rotated_tankki1.get_rect(center = tankki1.get_rect(center = (self.x,self.y)).center)
       
        #Rotates the cannon
        rotated_tykki1 = pygame.transform.rotate(self.tykki1, self.liikkuminen + self.tykki*100-45)
        new_tykki1 = rotated_tykki1.get_rect(center = tankki1.get_rect(center = (self.x,self.y)).center)
 
        #Renders the tank onto the canvas
        screen.blit(rotated_tankki1, new_tankki1)
       
        #Shoots the bullet
        for b in range(len(self.bullets)):
            self.bullets[b][0] += math.cos(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*12
            self.bullets[b][1] -= math.sin(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*12
             
        if len(self.bullets) < 1:
            if(self.tankkiBtn != False and self.ammuttu == 0):
                self.ammuttu += 1
                self.pauseliikkuminen = self.liikkuminen
                self.pausekaantyminen = self.tykki*100-45
                self.bullets.append([self.x+math.cos(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*70,self.y-math.sin(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*70])
                pygame.mixer.Channel(1).play(pygame.mixer.Sound("pum.mp3"))

        for bullet in self.bullets:
            rotated_panos = pygame.transform.rotate(self.panos,self.pauseliikkuminen + self.pausekaantyminen)
            self.panos_rect = rotated_panos.get_rect(center = self.tykki1.get_rect(center = (bullet[0],bullet[1])).center)
            screen.blit(rotated_panos, self.panos_rect)
       
        recti = tankki1.get_rect(center = (self.x,self.y))
        self.draw_rect_angle(screen, recti, (self.x,self.y), self.liikkuminen)

        #Renders the cannon
        screen.blit(rotated_tykki1, new_tykki1)    
taso = []
 
#Function that renders the stage
def draw(blockX,blockY,blockW,blockH):
    colors = pygame.Color("black")
    block = pygame.Rect(blockX,blockY,blockW,blockH)
    screen.fill(colors, block)
    taso.append(block)        

tank1_posX = 0.8333*width
tank1_posY = 0.2222*height
tank2_posX = 0.1667*width
tank2_posY = 0.2222*height
 
#Assign classes
tank1 = Tank(tankki1,0,1,2,tank1_posX,tank1_posY,tankki1nappi,tankki3nappi)
tank2 = Tank(tankki2,3,4,5,tank2_posX,tank2_posY,tankki2nappi,tankki4nappi)
lapi  = 1

#Upon one tank scoring tanks get respawned to spawn locations
def restart():
    tank1.bullets.clear()
    tank2.bullets.clear()
    tank1.mines.clear()
    tank2.mines.clear()
    tank1.osumat = 0
    tank2.osumat = 0
    tank1.x = 0.8333*width
    tank1.y = 0.2222*height
    tank2.x = 0.1667*width
    tank2.y = 0.2222*height
 
while True:

    #Fills the canvas with light yellow RGB values
    screen.fill((244, 255, 176))
    
    #Scoreboard
    font = pygame.font.SysFont("ubuntu", int(0.02083*width))
    score = font.render("Score", 1, (255,255,255))
    scorepoint = font.render("Tank 2: " + str(tank2.points) + "  ||  Tank 1: " + str(tank1.points), 1, (255,255,255))
    draw(0.4166*width,0,0.1875*width,0.0833*height)
 
    #Plays the game
    tank2.play()
    tank1.play()
    tank1_rect = tank1.tankki1.get_rect(center=(tank1.x, tank1.y))
    tank2_rect = tank2.tankki1.get_rect(center=(tank2.x, tank2.y))

    #Plays a sound when the tank is moving
    if(tank1.is_moving == 20):
        pygame.mixer.Sound("brr.mp3").play()
        tank1.is_moving = 0
        tank2.is_moving = 0
    elif(tank2.is_moving == 20):
            pygame.mixer.Sound("brr.mp3").play()
            tank1.is_moving = 0
            tank2.is_moving = 0

    #Define what kind of blocks to draw
    taso.clear()

    draw(0,0,width*1.1,0.02222*height),
    draw(0,0.99*height,width*1.1,0.02222*height),
    draw(0,0,0.01667*width,1.117*height),
    draw(width*0.99,0,0.01667*width,1.117*height),
    draw(0.3333*width,0,0.01667*width,0.6667*height),
    draw(0.5*width,0.7833*height,0.01667*width,0.3333*height),
    draw(0.6666*width,0,0.01667*width,0.6667*height),
    draw(0,0.5*height,0.1667*width,0.02222*height)
    draw(width*0.884,0.5*height,0.1667*width,0.02222*height)


    screen.blit(score, (0.4875*width, 0.0107*height))
    screen.blit(scorepoint, (0.4292*width, 0.0444*height))

    #Checks who won
    if(tank1.points == 3):
        draw(0.435*width,0.222*height,300,200)
        font = pygame.font.SysFont("ubuntu", 25)
        tan1 = font.render("Tank 1 WON!!", 1, (255,255,255))
        screen.blit(tan1, (0.4775*width, 0.3056*height))
        pygame.display.flip()

        #FPS limit
        clock.tick(60)
        time.sleep(5)
        subprocess.Popen(["python", "menu.py"])
        pygame.quit()
        sys.exit()
       
    elif(tank2.points == 3):
        draw(0.435*width,0.2222*height,300,200)
        font = pygame.font.SysFont("ubuntu", 25)
        tan1 = font.render("Tank 2 WON!!", 1, (255,255,255))
        screen.blit(tan1, (0.4775*width, 0.3056*height))
        pygame.display.flip()

        #FPS limit
        clock.tick(60)
        time.sleep(5)
        subprocess.Popen(["python", "menu.py"])
        pygame.quit()
        sys.exit()
       
    #Tells which tank is which  
    if(lapi == 1):

        lapi += 1
        font = pygame.font.SysFont("ubuntu", 25)
        tan1 = font.render("Tank 2", 1, (128,128,128))
        screen.blit(tan1, (0.1555*width, 0.1111*height))
        font = pygame.font.SysFont("ubuntu", 25)
        tan2 = font.render("Tank 1", 1, (128,128,128))
        screen.blit(tan2, (0.82*width, 0.1111*height))
        pygame.display.flip()
        #FPS limit
        clock.tick(60)
        time.sleep(2.5)

    
    #Checks if the tanks hit the walls
    for a in range(len(tank1.hitbox)):
        tank1.hitboxrect = pygame.Rect(tank1.hitbox[a].x,tank1.hitbox[a].y, 11, 11)
        if a+1 == len(tank1.hitbox):
            tank1.hitbox.clear()
        for i in range(len(taso)):
            if tank1.hitboxrect.colliderect(taso[i]):
                tank1.x = tank1.oldX
                tank1.y = tank1.oldY
                tank1.kaantyminen = tank1.oldkaantyminen
                tank1.kaantyminen2 = tank1.oldkaantyminen2
               
    for a in range(len(tank2.hitbox)):
        tank2.hitboxrect = pygame.Rect(tank2.hitbox[a].x,tank2.hitbox[a].y, 1, 1)
        if a+1 == len(tank2.hitbox):
            tank2.hitbox.clear()
        for i in range(len(taso)):
            if tank2.hitboxrect.colliderect(taso[i]):
                tank2.x = tank2.oldX
                tank2.y = tank2.oldY
                tank2.kaantyminen = tank2.oldkaantyminen
                tank2.kaantyminen2 = tank2.oldkaantyminen2
             
                
 
    #Checks if tanks hit eachother and makes them stop
    if tank1_rect.colliderect(tank2_rect):
        tank1.x = tank1.oldX
        tank1.y = tank1.oldY
        tank2.x = tank2.oldX
        tank2.y = tank2.oldY
 
    #Check if bullets hit the other tank or the wall  
    for bullet in tank1.bullets:
        panos_rect = tank1.panos.get_rect(center=(bullet[0], bullet[1]))
        if tank2_rect.colliderect(panos_rect):
            tank1.osumat += 1
            tank1.bullets.clear()
            if tank1.osumat > 2:
                tank1.points += 1
                restart()
                lapi = 1
                break
            
        for i in range(len(taso)):
            if panos_rect.colliderect(taso[i]):
                tank1.bullets.clear()
 
    for bullet in tank2.bullets:
        panos_rect = tank2.panos.get_rect(center=(bullet[0], bullet[1]))
        if tank1_rect.colliderect(panos_rect):
            tank2.osumat += 1
            tank2.bullets.clear()
            if tank2.osumat > 2:
                tank2.points += 1
                restart()
                lapi = 1
                break
            
        for i in range(len(taso)):
            if panos_rect.colliderect(taso[i]):
                tank2.bullets.clear()
                
   #Checks if tanks hit eachothers mines
    for miina in tank1.mines:
        mine_rect = tank1.mine.get_rect(center=(miina[0],miina[1]))
        if(tank2_rect.colliderect(mine_rect)):
            tank1.points += 1
            pygame.mixer.Channel(1).play(pygame.mixer.Sound("pum.mp3"))
            restart()
            lapi = 1
           
    for miina in tank2.mines:
        mine_rect = tank2.mine.get_rect(center=(miina[0],miina[1]))
        if(tank1_rect.colliderect(mine_rect)):
            tank2.points += 1
            pygame.mixer.Channel(1).play(pygame.mixer.Sound("pum.mp3"))
            restart()
            lapi = 1
    
    #Defines the current position as the last position 
    tank1.oldX = tank1.x
    tank1.oldY = tank1.y
    tank2.oldX = tank2.x
    tank2.oldY = tank2.y
    tank2.oldkaantyminen = tank2.kaantyminen
    tank2.oldkaantyminen2 = tank2.kaantyminen2
    tank1.oldkaantyminen = tank1.kaantyminen
    tank1.oldkaantyminen2 = tank1.kaantyminen2

    #if player presses ESC key game goes back to menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            subprocess.Popen(["python", "menu.py"])
            pygame.quit()
            sys.exit()
           
    pygame.display.flip()
    #FPS limit
    clock.tick(60)