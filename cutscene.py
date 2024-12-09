import pygame
import cv2
import GameData as state

import menufuncs

class cutscenePlayer:
    def __init__(self,name):
        path = "Assets\\cutscene\\" + name + ".mp4"
        self.video = cv2.VideoCapture(path)
        self.frame = pygame.Surface((state.screensize[0],state.screensize[1]))
        self.currenttime = 0
        self.framerate = self.video.get(cv2.CAP_PROP_FPS)
        state.objects.append(self)
        self.func = state.cutscenesource[name][0]
        self.funcargs = state.cutscenesource[name][1]
        #load cutscene audio. Sadly must be stored separately
        pygame.mixer.music.load(f"Assets\\cutscene\\{name}.wav")
    def update(self):
        #update the timer
        self.currenttime += state.deltatime
        usetime = int(self.currenttime*(self.framerate/state.fpsTarget))
        #print(self.currenttime,usetime)
        #get the current frame of video as a cv2 image
        self.video.set(cv2.CAP_PROP_POS_FRAMES,usetime)
        returnval, rawimage = self.video.read()
        self.frame.fill((0,0,0))
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        if returnval == True and (True not in state.keys):
            #convert to a pygame image
            self.frame.blit(pygame.transform.scale(pygame.image.frombuffer(rawimage.tostring(),rawimage.shape[1::-1],"BGR"),[state.screensize[0]*state.scaleamt,state.screensize[1]*state.scaleamt]),(0,0))
            #draw to screen
            state.display.blit(self.frame,(0,0))
        else:
            #leave
            getattr(menufuncs,self.func)(self.funcargs[0])
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
