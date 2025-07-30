from framer import Framer
import msvcrt

x = Framer()
x.initwin(color="a")
x.addObj(20, 12, "*")
x.addObj(32*4, 36, "*")
x.renderFrame()
msvcrt.getch()