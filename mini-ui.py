# -*- coding: utf-8 -*-
import cv2
import numpy as np
import imageio
import os


class MiniUI(object):
    def __init__(self, size=(500, 500), window_name="MiniUI"):
        # Window
        
        self.window_size_x = size[0]
        self.window_size_y = size[1]
        self.bg = np.zeros((self.window_size_x, self.window_size_y, 3), dtype=np.uint8)
        self.ui = np.zeros_like(self.bg, dtype=np.uint8)
        self.window_name = window_name
        self.window = cv2.namedWindow(self.window_name)
        self.load_font()
        
        # Navigation
        self.nav_centered= False
        self.nav_font_scale = 4
        self.nav_spacing = 4
        self.last_selected = 0

        self.selected = [0, 0, 0, 0]  
        self.level = 0
        self.nav_items = []
        self.key = None
        self.close_selected = False
        if self.nav_centered:
            self.nav_origin = (50, self.window_size_y//2)
        else:
            self.nav_origin = (50, self.window_size_y//8)
            
            
        self.t = 0.0
            
        cv2.setMouseCallback(self.window_name, self.onMouse)
        
    def add(self, entry):
        '''
        Adds new entry to the menu
        
        Parameters
        ----------
        entry : ['Name', callback_function]
             or ['Name', [['name', cb], ['name', cb]]]

        '''
        
        # If second element is list, append back button
        if isinstance(entry[1], list):
            entry[1].append(['Back', self.back])
            
        self.nav_items.append(entry)

 
    def show(self, key):
        self.ui *= 0
        self.key = key

        self.handle_input()
        self.show_navigation()
        self.scroll()
        
        
        cv2.imshow(self.window_name, self.bg + self.ui)
        
        if self.close_selected:
            return 'exit'
        else:
            return 'running'

    def scroll(self):

        img_nav1 = np.zeros_like(self.ui)
        img_nav2 = np.zeros_like(self.ui)
        
        items1 = [i[0] for i in self.nav_items]
        items2 = []
        try:
            element = self.nav_items[self.selected[0]][1]
        except:
            element = []
        
        if isinstance(element, list): # item is list
            # get List Text elements
            items2 = [i[0] for i in element]
            
            
        # render level 1 nav
        for i, entry in enumerate(items1):
            col = 'g' if i == self.selected[0] else 'w'
            pos = (self.nav_origin[0] + i * (self.nav_font_scale * 8 + self.nav_spacing), self.nav_origin[1])
            self.put_text(img_nav1 , entry, pos, scale=self.nav_font_scale,
                          color = col, centered = self.nav_centered)
            
        # render level 2 nav
        for i, entry in enumerate(items2):
            col = 'g' if i == self.selected[1] else 'w'
            pos = (self.nav_origin[0] + i * (self.nav_font_scale * 8 + self.nav_spacing), self.nav_origin[1])
            self.put_text(img_nav2 , entry, pos, scale=self.nav_font_scale,
                          color = col, centered = self.nav_centered)
            
            
        img_plane = np.hstack((img_nav1, img_nav2))
        size_x = self.window_size_x 
        self.t += (self.level - 0.5) * 0.7
        self.t = max(min(self.t, 1), 0)
        val =  (1 + np.sin(((self.t) * np.pi) - np.pi/2))  * size_x / 2
        pos_x =  int(val) #int((1 + np.sin(self.t/10)) * size_x / 2)
        self.ui = img_plane[:,pos_x:pos_x+size_x,:]
        

    def back(self):
        self.level -= 1

    def show_navigation(self):
        items= []
        level = self.level
        
        if level == 0:
            items = [i[0] for i in self.nav_items]
            
        elif level >= 1:
            element = self.nav_items[self.selected[0]][1]
            if isinstance(element, list): # item is list
                # get List Text elements
                items = [i[0] for i in element]
           
                if level == 2:
                    element[self.selected[1]][1]() # call function
                    print("'{}' - function called".format(element[self.selected[1]][0]))
                    self.level -= 1
                
            else:
                 #item is function
                 print("'{}' - function called".format(self.nav_items[self.selected[0]][0]))
                 element() # call function
                 self.level -= 1

        self.level = max(0, min(self.level, 1))
        self.selected[self.level] = max(0, min(self.selected[self.level], len(items)-1))

        for i, entry in enumerate(items):
            col = 'g' if i == self.selected[self.level] else 'w'
            pos = (self.nav_origin[0] + i * (self.nav_font_scale * 8 + self.nav_spacing), self.nav_origin[1])
            self.put_text(self.ui, entry, pos, scale=self.nav_font_scale,
                          color = col, centered = self.nav_centered)


    def handle_input(self):
        n, l=0, 0
        if self.key == ord('w'):
            n=-1
        elif self.key == ord('s'):
            n=+1
        elif self.key == ord('d'):
            l=+ 1
        elif self.key == ord('a'):
            l=- 1

        self.level=self.level + l
        self.selected[self.level]=self.selected[self.level] + n


    def onMouse(self, event, x, y, flags, param):
        FONT_HIGHT=8
        self.selected[self.level]=(
            y - self.nav_origin[0]) // (FONT_HIGHT * self.nav_font_scale + self.nav_spacing)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.level += 1



    def close(self):
        self.close_selected = True

    def put_text(self,img, text, pos, scale = 3, centered=False, color="w"):

        for i, str_char in enumerate(text):
            order=ord(str_char.upper())
            if order >= 65 and order <= 90:
                index=ord(str_char.upper()) - 65
            elif order >= 48 and order <= 57:
                index=ord(str_char.upper()) - 22
            elif order == 32:
                index=37
            else:
                break

            char_resized=self.resize_char(self.font[index], self.nav_font_scale)
            height, width=char_resized.shape[0], char_resized.shape[1]
            if not centered:
                x, y=pos[0], pos[1] + i * (char_resized.shape[1] + scale)
            else:
                x, y=pos[0], int(pos[1] + i * (char_resized.shape[1] +
                                   scale) - len(text) * (char_resized.shape[1]+scale) / 2)
            try:
                if color == "b":
                    img[x: x+height, y:y+width, 0] += char_resized
                elif color == "g":
                    img[x: x+height, y:y+width, 1] += char_resized
                elif color == "r":
                    img[x: x+height, y:y+width, 2] += char_resized
                else:
                    img[x: x+height, y:y+width, 0] += char_resized
                    img[x: x+height, y:y+width, 1] += char_resized
                    img[x: x+height, y:y+width, 2] += char_resized
            except ValueError:
                pass

    def resize_char(self, char, factor):
        outp=np.zeros( (char.shape[0] * factor, char.shape[1] * factor) , dtype=np.uint8)
        for x, y in np.ndindex(char.shape):
            outp[factor*x:factor*x+factor, factor *
                 y:factor*y+factor] = char[x, y]
        return outp

    def load_font(self):
        self.font = np.array([[[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ]],
        
        [[1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 1 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ]],
        
        [[1 , 1 , 1 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 1 , 0 , 0 ],
        [1 , 1 , 0 , 0 , 0 ],
        [1 , 0 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ]],
        
        [[1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 1 , 0 ]],
        
        [[1 , 0 , 0 , 0 , 1 ],
        [1 , 1 , 0 , 1 , 1 ],
        [1 , 0 , 1 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ]],
        
        [[1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 0 , 1 , 0 ],
        [1 , 0 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 1 , 0 , 0 ],
        [0 , 1 , 0 , 1 , 0 ]],
        
        [[1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [0 , 1 , 1 , 0 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 1 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 1 , 0 , 0 ]],
        
        [[1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [0 , 1 , 0 , 1 , 0 ],
        [0 , 0 , 1 , 0 , 0 ]],
        
        [[1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 0 , 0 , 1 ],
        [1 , 0 , 1 , 0 , 1 ],
        [1 , 0 , 1 , 0 , 1 ],
        [0 , 1 , 0 , 1 , 0 ]],
        
        [[1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ]],
        
        [[1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 1 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 1 , 1 , 0 ],
        [1 , 1 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 1 , 0 , 0 , 0 ],
        [1 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 1 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 0 , 1 , 1 , 0 ],
        [0 , 1 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 1 , 1 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 0 , 1 , 1 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 0 , 0 , 0 , 0 ],
        [1 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[1 , 1 , 1 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 1 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ],
        [0 , 1 , 0 , 0 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 1 , 1 , 0 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [0 , 0 , 0 , 1 , 0 ],
        [1 , 0 , 0 , 1 , 0 ],
        [0 , 1 , 1 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]],
        
        [[0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ],
        [0 , 0 , 0 , 0 , 0 ]]]).astype(np.uint8) * 255
        
       

import time
def demo1():
    t1 = time.time()
    for x,y in np.ndindex(100,10):
        print(f'{x = }  {y = }')
    t2  = time.time()    
    print(f'{1000} ops - Processing Time:{(t2 - t1)*1000}ms')

def demo3():
    t1 = time.time()
    for x,y in np.ndindex(100,100):
        #print(f'{x = }  {y = }')
        d = x+y
    t2  = time.time()    
    print(f'{100*100} ops - Processing Time:{(t2 - t1)*1000}ms ' )

def demo2():
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), "error.png"))
    source = imageio.imread(path)
    cv2.imshow(f"Image{np.random.randint(1000)}", source)
    
def main():
    ui = MiniUI()
    ui.add(['Demo 1', demo1])
    ui.add(['More', [['Demo 2', demo2], ['Demo 3', demo3]]])
    ui.add(['Settings', [['General', demo2], ['Graphics', demo2], ['Controlls', demo2], ['Audio', demo2]]])
    ui.add(['Exit', ui.close])
    
    
    
    key = None
    while (key != ord('x')):
        key = cv2.waitKey(30)
        
        ret = ui.show(key)
  
        if ret == 'exit':
            break
        
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
