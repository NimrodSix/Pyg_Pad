#!/usr/bin/env python3

import pygame

__author__ = "NimrodSix"
__email__ = "NimrodTH6 at gmail dot com"
__version__ = "0.1"


class PygPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def put(self, screen, text_string):
        text_bitmap = self.font.render(text_string, True, pygame.Color('white'))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10 

class FIFO:
    def __init__(self):
        self.size = 10
        self.stack = []
        self.stack.append(0)
        
    def push(self, item):
        if self.stack[-1] == item: # Never push the same item
            return
        if len(self.stack) > self.size:
            self.stack.pop(0)
        self.stack.append(item)
        
    def __str__(self):
        return str(self.stack)
    
class PygPad:
    """
    Treats cross & buttons twin stick  shooter style
    polar: Returns a 2 tuple (cross and buttons) with  0-8 as a direction

    Axis 0(X) value: (Left)-0.992157 (No press)0.003906 (Right).999969
    Axis 1 same as 0
    Button 0-9: 0 or 1
    """
    DEAD = 0
    UP = 1
    UPRIGHT = 2
    RIGHT = 3
    DOWNRIGHT = 4
    DOWN = 5
    DOWNLEFT = 6
    LEFT = 7
    UPLEFT = 8
    
    DIR = {0:'CENTER', 1:'UP', 2:'UP RIGHT', 3:'RIGHT', 4:'DOWN RIGHT', 5:'DOWN', 6:'DOWN LEFT', 7:'LEFT', 8:'UP LEFT'}
    
    # TODO: Time based stuff
    
    def __init__(self):
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        # print(dir(self.joystick))
        self.num_axes = self.joystick.get_numaxes()
        print('PygStick.axes: {}'.format(self.num_axes))
        self.num_buttons = self.joystick.get_numbuttons()
        print('PygStick.buttons: {}'.format(self.num_buttons))

        self.cross = PygPad.DEAD
        self.buttons = PygPad.DEAD
        
        self.fifo = FIFO()

    def __str__(self):
        return "Cross: {} Buttons: {}".format(PygPad.DIR[self.cross], PygPad.DIR[self.buttons])

    def solid(self, float_var: float) -> int:
        if float_var < -.5: return -1            # Solidify output
        elif float_var > .5: return 1
        else: return 0
    
    def direction(self, x, y):
        if x == -1 and y == -1:       # Yuck, if... else
            return PygPad.UPLEFT
        elif x == 1 and y == -1:
            return PygPad.UPRIGHT
        elif x == -1 and y == 1:
            return PygPad.DOWNLEFT
        elif x and y:
            return PygPad.DOWNRIGHT
        elif x == -1:
            return PygPad.LEFT
        elif y == -1:
            return PygPad.UP
        elif x:
            return PygPad.RIGHT
        elif y:
            return PygPad.DOWN
        else:
            return PygPad.DEAD    # Bad form...        
        
    def get_pad_cartesian(self):
        """     cartesian: returns axis as 2 tuple (0,0) (-1,1) """
        return (self.solid(self.joystick.get_axis(0)), self.solid(self.joystick.get_axis(1)))
    
    def get_polar(self):
        gx = self.solid(self.joystick.get_axis(0))  # 0.003906
        gy = self.solid(self.joystick.get_axis(1))  # Solidify output to 0
        
        self.cross = self.direction(gx, gy)
            
        bl = self.joystick.get_button(0) # LEFT
        bd = self.joystick.get_button(1) # DOWN
        br = self.joystick.get_button(2) # RIGHT
        bu = self.joystick.get_button(3) # UP
        
        if bl and bd:
            self.buttons = PygPad.DOWNLEFT
        elif bl and bu:
            self.buttons = PygPad.UPLEFT
        elif br and bu:
            self.buttons = PygPad.UPRIGHT
        elif br and bd:
            self.buttons = PygPad.DOWNRIGHT
        elif br:
            self.buttons = PygPad.RIGHT
        elif bd:
            self.buttons = PygPad.DOWN
        elif bl:
            self.buttons = PygPad.LEFT
        elif bu:
            self.buttons = PygPad.UP
        else:
            self.buttons = PygPad.DEAD

        if self.cross:
            self.fifo.push(self.cross)
            
        return (self.cross, self.buttons)


class Dot:
    def __init__(self, screen):
        self.screen = screen
        self.x = 320
        self.y = 240
    
    def draw(self):
        pygame.draw.circle(self.screen, pygame.Color('blue'), (self.x, self.y), 20)


def combo_tester(combo_list, move_list): 
    n = len(combo_list)
    return any(combo_list == move_list[i:i + n] for i in range(len(move_list)-n + 1)) 

if __name__ == '__main__':
    # Setup pygame/window ---------------------------------------- #
    mainClock = pygame.time.Clock()
    from pygame.locals import *
    pygame.init()
    pygame.display.set_caption('Pyg Pad')
    #set_mode(size=(0, 0), flags=0, depth=0, display=0, vsync=0)
    screen = pygame.display.set_mode((640, 480), 0, 32)

    # Setup globals ---------------------------------------- #
    pygpad = PygPad()
    pyg_text = PygPrint()
    dot = Dot(screen)

    
    # Loop ------------------------------------------------------- #
    while True:
    
        # Background --------------------------------------------- #
        #screen.fill(pygame.Color('black'))
        screen.fill(0)
        # mx, my = pygame.mouse.get_pos()
        pad = pygpad.get_polar()
        
        pyg_text.put(screen, 'Cross: {}'.format(PygPad.DIR[pad[0]]))
        pyg_text.put(screen, 'Buttons: {}'.format(PygPad.DIR[pad[1]]))
        pyg_text.put(screen, 'FIFO: {}'.format(pygpad.fifo))
        
        combo = [1,2,3,4,5,6,7,8]   # Circle
        combo2 = [7,6,5,4,3]    # Left to right bottom arc
        
        # If combo is in there in ANY arrangement... thihs works
        #if all(item in combo for item in pygpad.fifo.stack):
        #    pyg_text.put(screen, 'COMBO!!!!')

        # Need true only if combo is in there in EXACT order
        result = combo_tester(combo, pygpad.fifo.stack)
        if result:
            pyg_text.put(screen, 'Circle COMBO!!!')

        result = combo_tester(combo2, pygpad.fifo.stack)
        if result:
            pyg_text.put(screen, 'Arc COMBO!!!')

        pyg_text.reset()

        #    DEAD = 0
        #    UP = 1
        #    UPRIGHT = 2
        #    RIGHT = 3
        #    DOWNRIGHT = 4
        #    DOWN = 5
        #    DOWNLEFT = 6
        #    LEFT = 7
        #    UPLEFT = 8
    
        speed = 5
        
#        xlate = {8: (-1, -1), 7: (-1, 0), 6: (-1, 1), 5: (0, 1), 4:(1, 1), 3: (1, 0), 2: (1, -1), 1:(0, -1), 0: (0, 0)}
        
#        x, y = xlate[pad[0]]
        
#        dot.x += x * speed
#        dot.y += y * speed

        x, y = pygpad.get_pad_cartesian()

        dot.x += x * speed
        dot.y += y * speed
        
        """
        # Move a dot around
        if pad[0] == 8:
            dot.x -= speed
            dot.y -= speed
        elif pad[0] == 6:
            dot.x -= speed
            dot.y += speed
        elif pad[0] == 4:
            dot.x += speed
            dot.y += speed
        elif pad[0] == 2:
            dot.x += speed
            dot.y -= speed
        elif pad[0] == 7:
            dot.x -= speed
        elif pad[0] == 5:
            dot.y += speed
        elif pad[0] == 3:
            dot.x += speed
        elif pad[0] == 1:
            dot.y -= speed
        else:
            pass
        """
        
        dot.draw()
        
        # Buttons ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()

        # Update ------------------------------------------------- #
        pygame.display.update()
        mainClock.tick(30)
