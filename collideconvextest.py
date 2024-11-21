import pygame
import time

pygame.init()
window = pygame.display.set_mode((800,800))
shapecolor1 = (255,0,0)
shapecolor2 = (0,255,0)
def main():
    while True:
        pygame.event.get()
        mouse = pygame.mouse.get_pos()
        shape1 = [
            [50,50],
            [50,600],
            [300,300],
            [300,50]]
        shape2 = [
            [0+mouse[0],0+mouse[1]],
            [0+mouse[0],50+mouse[1]],
            [50+mouse[0],50+mouse[1]],
            [50+mouse[0],0+mouse[1]]]
        window.fill((0,0,0))
        pointcolor = 50
        collide = shapecollide(shape2,shape1)
        #pygame.draw.rect(window,(pointcolor,pointcolor,pointcolor),(sourcelowest[0]-5,sourcelowest[1]-5,10,10))
        #pygame.draw.rect(window,(pointcolor,pointcolor,pointcolor),(sourcehighest[0]-5,sourcehighest[1]-5,10,10))
        #pygame.draw.rect(window,(pointcolor,pointcolor,pointcolor),(targetlowest[0]-5,targetlowest[1]-5,10,10))
        #pygame.draw.rect(window,(pointcolor,pointcolor,pointcolor),(targethighest[0]-5,targethighest[1]-5,10,10))
        pointcolor += 50
        #pygame.display.flip()
        #time.sleep(0.5)
        if collide == True:
            pygame.draw.polygon(window,shapecolor1,shape2)
        else:
            pygame.draw.polygon(window,shapecolor2,shape2)
        pygame.draw.polygon(window,shapecolor1,shape1)
        pygame.display.flip()

def shapecollide(shape1,shape2):
    collide = True
    for item in range(len(shape2)):
        try:
            slopetop = shape2[item][1]-shape2[item+1][1]
            slopebottom = shape2[item][0]-shape2[item+1][0]
            pygame.draw.line(window,(255,255,0),shape2[item],shape2[item+1])
        except IndexError:
            slopetop = shape2[item][1]-shape2[0][1]
            slopebottom = shape2[item][0]-shape2[0][0]
            pygame.draw.line(window,(255,255,0),shape2[item],shape2[0])
            
        targethighest = shape2[0]
        targetlowest = shape2[0]
        sourcehighest = shape1[0]
        sourcelowest = shape1[0]
        
        if slopebottom != 0:
            if slopetop != 0:
                offset = shape2[0][1]-(shape2[0][0]*slopetop/slopebottom)
                perpendicularx = offset/((-slopebottom/slopetop)-(slopetop/slopebottom))
                perpendiculary = (-slopebottom/slopetop)*perpendicularx
                pygame.draw.line(window,(255,255,255), (10,10*(-slopebottom/slopetop)-500),(1000,1000*(-slopebottom/slopetop)-500))
                for point in shape2:
                    scalar = (perpendicularx*point[0] + perpendiculary*point[1])/(perpendicularx*perpendicularx + perpendiculary*perpendiculary)
                    targety = point[1]*scalar#point[0]*(slopetop/slopebottom)+offset
                    if targety < targetlowest[1]:
                        targetlowest = point
                    elif targety > targethighest[1]:
                        targethighest = point
                for point in shape1:
                    scalar = (perpendicularx*point[0] + perpendiculary*point[1])/(perpendicularx*perpendicularx + perpendiculary*perpendiculary)
                    sourcey = point[1]*scalar#point[0]*(slopetop/slopebottom)+offset
                    if sourcey < sourcelowest[1]:
                        sourcelowest = point
                    elif sourcey > sourcehighest[1]:
                        sourcehighest = point
                if not (targetlowest[1]<=sourcelowest[1]<=targethighest[1] or targetlowest[1]>=sourcelowest[1]>=targethighest[1] or targetlowest[1]<=sourcehighest[1]<=targethighest[1] or targetlowest[1]>=sourcehighest[1]>=targethighest[1] or sourcelowest[1]<=targetlowest[1]<=sourcehighest[1] or sourcelowest[1]>=targetlowest[1]>=sourcehighest[1] or sourcelowest[1]<=targethighest[1]<=sourcehighest[1] or sourcelowest[1]>=targethighest[1]>=sourcehighest[1]):
                    collide = False
            else:
                for point in shape2:
                    if point[1] < targetlowest[1]:
                        targetlowest = point
                    elif point[1] > targethighest[1]:
                        targethighest = point
                for point in shape1:
                    if point[1] < sourcelowest[1]:
                        sourcelowest = point
                    elif point[1] > sourcehighest[1]:
                        sourcehighest = point
                if not (targetlowest[1]<=sourcelowest[1]<=targethighest[1] or targetlowest[1]>=sourcelowest[1]>=targethighest[1] or targetlowest[1]<=sourcehighest[1]<=targethighest[1] or targetlowest[1]>=sourcehighest[1]>=targethighest[1] or sourcelowest[1]<=targetlowest[1]<=sourcehighest[1] or sourcelowest[1]>=targetlowest[1]>=sourcehighest[1] or sourcelowest[1]<=targethighest[1]<=sourcehighest[1] or sourcelowest[1]>=targethighest[1]>=sourcehighest[1]):
                    collide = False
        else:
            for point in shape2:
                if point[0] < targetlowest[0]:
                    targetlowest = point
                elif point[0] > targethighest[0]:
                    targethighest = point
            for point in shape1:
                if point[0] < sourcelowest[0]:
                    sourcelowest = point
                elif point[0] > sourcehighest[0]:
                    sourcehighest = point
            if not (targetlowest[0]<=sourcelowest[0]<=targethighest[0] or targetlowest[0]>=sourcelowest[0]>=targethighest[0] or targetlowest[0]<=sourcehighest[0]<=targethighest[0] or targetlowest[0]>=sourcehighest[0]>=targethighest[0] or sourcelowest[0]<=targetlowest[0]<=sourcehighest[0] or sourcelowest[0]>=targetlowest[0]>=sourcehighest[0] or sourcelowest[0]<=targethighest[0]<=sourcehighest[0] or sourcelowest[0]>=targethighest[0]>=sourcehighest[0]):
                collide = False
    return collide
main()