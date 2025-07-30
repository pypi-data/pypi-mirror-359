import msvcrt
import os
import time
import sys
class Framer:

    def __init__(self):
        pass

    def initwin(self, lines=None, cols=None, color=None, ar="32:9", scale=4, fps=None):
        if cols is None and lines is None:
            cols = int(ar.split(":")[0])*scale
            lines = int(ar.split(":")[1])*scale
            os.system(f"mode con: cols={cols} lines={lines}")
        else:
            os.system(f"mode con: cols={cols} lines={lines}")
        if color is not None:
            os.system(f"color {color}")
        self.cols = cols
        self.lines = lines
        self.pixels = cols*lines
        self.color = color
        self.frame = []
        self.fps = fps

    def addObj(self, x, y, char=" "):
        if x > self.cols or x < 0:
            raise Exception("x Coordinate out of Display or Negative")
        elif y > self.lines or y < 0:
            raise Exception("y Coordinate out of Display or Negative")
        else:
            self.frame.append([x, y, char])
        self.frame.append([x, y, char])


    def renderFrame(self):
        self.frame.sort(key=(lambda array : array[1]))
        y = 0
        x = 0
        spacer = 0
        for obj in self.frame:
            if self.frame.index(obj) == 0:
                spacer = obj[1]*self.cols + obj[0] - 1
                final = " " * spacer + obj[2]
                if obj == self.frame[-1] :
                    y = self.lines - obj[1]
                    x = self.cols - obj[0]
                final += " " * (y * self.cols + x)
                sys.stdout.write(final)
            else :
                co = self.frame.index(obj)
                po = self.frame[co - 1]
                y = obj[1]  - po[1] - 1
                x = self.cols - po[0] + obj[0] - 1
                final = " "*(y * self.cols + x) + obj[2]
                if obj == self.frame[-1] :
                    y = self.lines - obj[1]
                    x = self.cols - obj[0]
                    final += " " * (y * self.cols + x)
                sys.stdout.write(final)
            sys.stdout.flush()


        if self.fps != None:
            time.sleep(1/self.fps)
        if msvcrt.kbhit() != 0:
            return msvcrt.getch().decode()
        self.frame = []


"""    def renderFrame(self):
        # os.system("cls")
        self.frame.sort(key=self.sortf)
        # print(self.frame)
        y = 0
        x = 0
        spacer = 0
        for obj in self.frame:
            # print(obj[1])
            if self.frame.index(obj) == 0:
                spacer = obj[1]*self.cols + obj[0] - 1
                # print(" " * spacer + obj[2], end="", flush=True)
                #print(self.frame.index(obj))
                final = " " * spacer + obj[2]
                if obj == self.frame[-1] :
                    y = self.lines - obj[1]
                    x = self.cols - obj[0]
                    # print(" " * (y * self.cols + x), end="", flush=True)
                final += " " * (y * self.cols + x)
                # print(final, end="", flush=True)
                sys.stdout.write(final)
            else :
                co = self.frame.index(obj)
                po = self.frame[co - 1]
                y = obj[1]  - po[1] - 1
                x = self.cols - po[0] + obj[0] - 1
                # print(" "*(y * self.cols + x) + obj[2], end="", flush=True)
                final = " "*(y * self.cols + x) + obj[2]
                if obj == self.frame[-1] :
                    y = self.lines - obj[1]
                    x = self.cols - obj[0]
                    # print(" " * (y * self.cols + x), end="", flush=True)
                    final += " " * (y * self.cols + x)
                # print(final, end="", flush=True)
                sys.stdout.write(final)
            sys.stdout.flush()

        # print(self.frame[-1])
        # try:
        #spacer = self.pixels - (self.frame[-1][1]*self.cols + self.frame[-1][0]) Last element
        # except:
        #     spacer = self.pixels
        #print(" "*spacer, end="", flush=True)
        self.frame = []
        # for obj in self.frame:
        #     empties = obj

"""
"""
    def renderFrame(self):
        os.system("cls")
        pixel = 1
        while pixel <= self.pixels :
            x = (pixel % self.cols)
            if x == 0:
                x = self.cols
            y = pixel // self.cols
            present = False
            for coordinates in self.frame:
                if coordinates[0] == x and coordinates[1] == y :
                    print(coordinates[2], end="", flush=True)
                    # print("Iasdfadsdfsdfasdfasdfasdfasdfasdfasdfasdf", end="", flush=True)
                    self.frame.remove(coordinates)
                    present = True
                    break
                else:
                    present = False
            if not present:
                print(" ", end="", flush=True)
            pixel += 1
"""
