from pynput import keyboard, mouse
from PIL import ImageGrab
from time import sleep, localtime
from os import mkdir, path
import sys
from pygame import mixer

class ChangeObserver:
    captureKeys = ['Key.ctrl', 'Key.ctrl_l', 'Key.ctrl_r']
    playSounds = True
    save = False
    soundPath = 'notification.wav'

    soundPlayer = None

    screenShotfolder = ''

    changesCount = 0
    prevScreen = None
    mousePos = mousePos1 = mousePos2 = [0, 0]
    mousePos1Captured = False
    klis = None
    mlis = None
        

    def _grabScreen(self, x1,y1,x2,y2):
        bbox = (x1,y1,x2,y2)
        im = ImageGrab.grab(bbox=bbox, include_layered_windows=False, all_screens=True)
        return im

    def _getCoord(self, x,y):
        global mousePos
        mousePos = [x,y]     

    def _onPress(self, key):
        key = str(key).strip("'")
        print(key)
        if key in self.captureKeys:
            if not self.mousePos1Captured:
                self.mousePos1 = mousePos
                self.mousePos1Captured = True
                print('PRESS "CTRL" TO CAPTURE MOUSE POSITION FOR SECOND AREA CORNER')
                return True
            else:
                self.mousePos2 = mousePos
                self.mlis.stop()
                self.klis.stop()  
                return False
            
    def captureCoords(self):
        self.mousePos1Captured = False
        print('PRESS "CTRL" TO CAPTURE MOUSE POSITION FOR FIRST AREA CORNER')
        with keyboard.Listener(on_press = self._onPress) as self.klis:
            with mouse.Listener(on_move = self._getCoord) as self.mlis:
                self.klis.join()
                self.mlis.join()
        
         # for observing one pixel
        if self.mousePos1 == self.mousePos2:
            self.mousePos2 = [self.mousePos2[0]+1,self.mousePos2[1]+1]

        # correction for reverse capture
        if self.mousePos1[0] > self.mousePos2[0]:
            self.mousePos1[0], self.mousePos2[0] = self.mousePos2[0], self.mousePos1[0]

        if self.mousePos1[1] > self.mousePos2[1]:
            self.mousePos1[1], self.mousePos2[1] = self.mousePos2[1], self.mousePos1[1]

        print()
        print(f"OK I'M OBSERVING CHANGES ON THE SCREEN BETWEEN POSITION [X:{self.mousePos1[0]} Y:{self.mousePos1[1]}] AND [X:{self.mousePos2[0]} Y:{self.mousePos2[1]}]...")
        
        self.prevScreen = self._grabScreen(self.mousePos1[0], self.mousePos1[1], self.mousePos2[0], self.mousePos2[1])

    def check(self):
        screen = self._grabScreen(self.mousePos1[0], self.mousePos1[1], self.mousePos2[0], self.mousePos2[1])
        if screen != self.prevScreen:
            self.changesCount += 1
            print(f"CHANGE {self.changesCount} DETECTED - {localtime().tm_hour}:{localtime().tm_min}:{localtime().tm_sec}")
            self.prevScreen = screen
            if self.save:
                screen.save(fr"{self.screenShotfolder}/screenshot{self.changesCount}.png", 'PNG')
            if self.playSounds:
                self.soundPlayer.play()
                

# for PyInstaller
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


if __name__ == '__main__':
    changeObserver = ChangeObserver()

    print("---CHANGE OBSERVER---")

    # check delay
    _in = input("CHECK DELAY (IN SECONDS): ")
    if _in:
        checkDelay = float(_in)
    else:
        checkDelay = 1
        
    # sounds
    _in = input("PLAY SOUNDS? (0 = no, 1 = yes): ")
    if _in == '0':
        changeObserver.playSounds = False

    if changeObserver.playSounds:
        mixer.init()
        try:
            changeObserver.soundPlayer = mixer.Sound(resource_path(changeObserver.soundPath))
        except FileNotFoundError:
            print(f"ERROR: FILE {changeObserver.soundPath} NOT FOUND!")
            changeObserver.playSounds = False

    # screenshots saving
    _in = input("SAVE CHANGE SCREENSHOTS? (0 = no, 1 = yes): ")

    if _in == '1':
        changeObserver.save = True
    del _in

    if changeObserver.save:
        changeObserver.screenShotfolder = input("SAVE TO FOLDER (FOLDER NAME): ")
        try:
            mkdir(changeObserver.screenShotfolder)
        except FileExistsError:
            pass

    changeObserver.captureCoords()

    
    while True:
        changeObserver.check()
        sleep(checkDelay)