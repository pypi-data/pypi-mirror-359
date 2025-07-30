## -- medialib v3.1
import pygame
from math import sqrt

def initialize():
    global __medialibGlobal
    __medialibGlobal = {
        "imgs": {},
        "backgroundColor": (0,0,0)
    }

    pygame.init()

    __medialibGlobal["screen"] = pygame.display.set_mode((800,600),pygame.DOUBLEBUF)
    pygame.display.set_caption("medialib")
    pygame.mixer.init()
    __medialibGlobal["font_name"] = pygame.font.get_default_font()
    __medialibGlobal["screen"].fill([0, 0, 0])# fix for macOS by LuMin: fix the bug of text() that renders a solid rect when used in macOS 3/2022

    #print("!")
    #print(__medialibGlobal)


def clear(r=None,g=None,b=None):
    """Clears the drawing window. The default background color is black. 

    If a color is specified (in RGB format), as in:
        clear(0,255,0) ## color is red
    the background color is changed. 
    Each successive clear() calls uses the newly set background color.
    """
    if r!=None and g!=None and b!=None:
        color = [r,g,b]
        __medialibGlobal["backgroundColor"] = color
    else:
        color = __medialibGlobal["backgroundColor"]
    __medialibGlobal["screen"].fill( color )
    pygame.display.update()
    
#def wait(secs):
#    """This blocking command pauses the program for a certain number of seconds. 
#
#    Real numbers can be used for the seconds.
#    Example: wait(1.5) ## pause the program for 1.5 seconds    
#    """
#    pygame.time.delay(int(secs*1000))

## 2021 Sept - a "less bloking" wait that does not freeze the main window!
def wait(secs):
    """This blocking command pauses the program for a certain number of seconds. 

    Real numbers can be used for the seconds.
    Example: wait(1.5) ## pause the program for 1.5 seconds    
    """
    current_time = pygame.time.get_ticks()
    exit_time = current_time + int(secs*1000)
    loop = True
    while loop:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            pass ## read and skip all events

        if current_time >= exit_time:
            loop = False

def wait_key_press():
#    modified by Jingyun at 3/2022
#  in Windows 10 and Mac ESC=27, 0~9=48~57, a~z=97-122
#  but the rest of the keys(F1-F12,Numlock,CapsLock,etc) are represented by a unicode
#  which vary by system and application,
#  for example arrow ->=1073741903, <-=1073741904, use chr will cause a bug when input keys such as arrow
#  need to check Mac
    """Pauses the program until a key is pressed (any key). 
    If ESC or numbers or a character is press, the key that was pressed is then returned as a character.
    otherwise will return a code.
    Example:
       k = wait_key_press()
       if k=="a":
          print("you pressed -a-")	
    """    
    key = None
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key < 256:
                    if 96 < event.key < 123:
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_LSHIFT or mods & pygame.KMOD_CAPS:
                            key = chr(event.key).upper()
                        else:
                            key = chr(event.key)
                else:
                    key = str(event.key)
                loop = False
    return key

# it works, but no key repetition
def is_key_press(keyName):
    """This function does not block the program. 
    It checks whether the key  keyName  was pressed just before the function was called; 
    if so, the functions returns True, otherwise it returns False.

    Example:
       if is_key_press("a"):
          print("you pressed -a-")
    """
    pygame.event.pump()  # Allow pygame to handle internal actions.
    events = pygame.event.get()
    for event in events:
        if event.type==pygame.KEYDOWN:
            if event.key==ord(keyName):
                return True
        pygame.event.post(event) # put it back
    return False

def is_mouse_leftclick(): ##changed by Adam Wynn on 10/12/22 in the previous version named is_mouse_press()
    pygame.event.pump()  # Allow pygame to handle internal actions.
    return pygame.mouse.get_pressed()[0] # left button pressed

def wait_mouse_leftclick(): ##changed by Jingyun Wang at 2021/10/6 in the previous version named wait_mouse_press()
    """Pauses the program until the mouse's left button is pressed"""
    pygame.event.clear()
    wait(0.1)
    while not is_mouse_leftclick():
        pygame.event.pump()  # Allow pygame to handle internal actions.
        wait(0.1)

def get_mouse_pos():
    pygame.event.pump()  # Allow pygame to handle internal actions.
    return pygame.mouse.get_pos()

def rect(x,y,w,h,r=None,g=None,b=None):
    color = [255,255,255]
    if r!=None and g!=None and b!=None:
        color = [r,g,b]
    pygame.draw.rect(__medialibGlobal["screen"],color,(x,y,w,h))
    pygame.display.update( pygame.Rect(x,y,w,h) ) ## faster refresh
    
def draw(imgFileName,x,y,width=None,height=None):
    ##print(imgFileName, "at", x,",",y)
    image = None
    w,h = 160,120 ## default size
    if imgFileName in __medialibGlobal["imgs"]:
        # cached
        image = __medialibGlobal["imgs"][imgFileName]
    else:
        try:
            image = pygame.image.load(imgFileName).convert() ##changed by Adam Wynn 17/10/22 - added convert() to load image faster
            __medialibGlobal["imgs"][imgFileName] = image
        except Exception:
            image = None

    if image==None:
        pygame.draw.rect(__medialibGlobal["screen"],(255,255,255),(x,y,w,h))
        print("Medialib: Image %s not found." % imgFileName)
    else:
        if width!=None and height!=None:
            w,h = width,height
            scaled_img = pygame.transform.scale( image, (w,h) )
            __medialibGlobal["screen"].blit(scaled_img, (x,y) )
        else:
            xx,yy,w,h = image.get_rect()
            __medialibGlobal["screen"].blit(image, (x,y) )
    pygame.display.update( pygame.Rect(x,y,w,h) ) ## faster refresh

## saveScreen("test123.png")
def save_screen(file_name,pos_x=None,pos_y=None,width=None,height=None):
    if pos_x!=None and pos_y!=None and width!=None and height!=None:
        ## save only the given rectangle
        temp_surface = pygame.Surface((width,height))
        temp_surface.blit(__medialibGlobal["screen"],(pos_x,pos_y,width,height))
        pygame.image.save(temp_surface, file_name)
    else:
        pygame.image.save(__medialibGlobal["screen"], file_name)

def play(soundFileName):
    notfound = False
    try:
        f = open(soundFileName)
        f.close()
    except FileNotFoundError:
        notfound = True
    
    if notfound:
        print("Medialib: Audio file %s not found." % soundFileName)
    else:
        pygame.mixer.music.load(soundFileName)
        pygame.mixer.music.stop()
        pygame.mixer.music.play(0) ## -1 play forever

## file_name should be the pathname to a  .ttf  file
def set_font(file_name):
    ## test if the font file exists
    try:
        font = pygame.font.Font(file_name, 16)
    except:
        ## default: if no file, use default font!
        file_name = pygame.font.get_default_font()
    __medialibGlobal["font_name"] = file_name

## Writes the message string in the drawing window, at the postion (x,y), 
## with the current font, and the characters will have the size font_size (measured in pixels).
def text(message,x,y,font_size, r=None,g=None,b=None):
    color = [255,255,255] ## default text color is white
    if r!=None and g!=None and b!=None:
        color = [r,g,b]

    font = pygame.font.Font(__medialibGlobal["font_name"], font_size)
    the_message = font.render(message, True, color)
    w,h = the_message.get_width(),the_message.get_height()
    __medialibGlobal["screen"].blit(the_message,(x,y))
    pygame.display.update( pygame.Rect(x,y,w,h) ) ## faster refresh

## Does not display the message on the drawing window,
## instead it calculates and returns 2 values: 
##      the width and height of the rectangle containing the text, measured in pixels.
def get_text_rect(message,x,y,font_size):
    font = pygame.font.Font(__medialibGlobal["font_name"], font_size)
    the_message = font.render(message, True, (0,0,0))
    w,h = the_message.get_width(),the_message.get_height()
    return (w,h)

## all_done() and force_all_done() updated by Adam Wynn on 2/7/25 due to freezing issues on macOS
## all_done() is the recommended way to end a program using MediaLib.
## force_all_done() is a temporary workaround if all_done() freezes the program but will exit all python processes.
import platform
import os

def all_done():
    if platform.system() == "Darwin":
        print("On macOS, MediaLib may freeze if all_done() is used. If this happens, use force_all_done() instead.")
    pygame.quit()

def force_all_done():
    print("Warning: Only use force_all_done() if MediaLib freezes when all_done() is used.")
    os._exit(0)  


############################################# utils 

def distance(x1,y1,x2,y2):
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

## tPercentage=  0 -> a
## tPercentage=100 -> b
## tPercentage= 50 -> a/2 + b/2
def a_to_b(a,b,tPercentage):
    t = tPercentage/100.0
    return (1-t)*a + t*b
    
def point_inside_rect(px,py,  pos_x,pos_y, width,height):
    if (px>=pos_x and px<=pos_x+width) and (py>=pos_y and py<=pos_y+height):
        return True
    return False

#############################################

if __name__ == "__main__":
    ### execute only if run as a script
    initialize()
    rect(10,10,150,250)
    rect(300,250,250,50)
    save_screen("testing1.png",0,0,600,400)
    save_screen("testing2.png",10,10,600,400)
    all_done()
