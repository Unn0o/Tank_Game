import pygame
import pygame_menu
import sys
import subprocess
import pyfirmata2
from pyfirmata2 import Arduino, util

#Arduino config
board = Arduino('com22')#The port where the Arduino is connected
it = util.Iterator(board)
it.start()

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
size = width,height = 600,400
screen = pygame.display.set_mode(size)
pygame.init()
pygame.display.set_caption('Tankkipeli')
menu = pygame_menu.Menu("Tankkipeli", 600, 400, theme=pygame_menu.themes.THEME_GREEN)

#Starts the game
def tankkipeli():
    subprocess.Popen(["python", "tes.py"])
    pygame.quit()
    sys.exit()
    
#Closes the menu window
def lopeta():
    pygame.quit()
    sys.exit()
 
#Creates the menu buttons
menu.add.button("Pelaa", tankkipeli)
menu.add.button("Lopeta", lopeta)
 
myfont = pygame.font.SysFont("ubuntu", 25)
label = myfont.render("Made by: @Unn0o & @Cefucr", 1, (0,0,0))

while True:
    events = pygame.event.get()
    menu.update(events)
    menu.draw(screen)
    screen.blit(label, (10, 360))
    
    #If you press the blue button it starts the game and if your press the red one it closes it.
    if(tankki1nappi.read() == True or tankki2nappi.read() == True):
        tankkipeli()
    elif(tankki4nappi.read() == True or tankki3nappi.read() == True):
        lopeta()
        
    pygame.display.update()
 