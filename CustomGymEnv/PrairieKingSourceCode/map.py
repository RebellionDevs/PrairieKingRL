from settings import *
from random import random, choice

class Map():
    def __init__(self):
        
        self.displaySurf = pygame.display.get_surface()

        # sprite groups setup
        self.visibleSprites = pygame.sprite.Group()
        self.obstaclesSprites = pygame.sprite.Group()

    def getMap(self, wave):
        newMap = [[0 for _ in range(16)] for _ in range(16)]

        for i in range(16):
            for j in range(16):
                if (i == 0 or i == 15 or j == 0 or j == 15) and (i <= 6 or i >= 10) and (j <= 6 or j >= 10):
                    newMap[i][j] = 5
                elif i == 0 or i == 15 or j == 0 or j == 15:
                    newMap[i][j] = 1 if random() < 0.15 else 0
                elif i == 1 or i == 14 or j == 1 or j == 14:
                    newMap[i][j] = 2
                else:
                    newMap[i][j] = 4 if random() < 0.1 else 3

        if wave == -1:
            for i in range(16):
                for j in range(16):
                    if newMap[i][j] in [0, 1, 2, 5]:
                        newMap[i][j] = 3
            newMap[3][1] = 5; newMap[8][2] = 5; newMap[13][1] = 5
            newMap[5][0] = 0; newMap[10][2] = 2; newMap[15][2] = 1
            newMap[14][12] = 5; newMap[10][6] = 7

            for i in range(10, 15) : newMap[i][6] = 7
            for j in range(6, 14) : newMap[14][j] = 7

            for i in range(16):
                newMap[i][3] = 9 if i % 2 == 0 else 8
            newMap[3][3] = 10

            pointsTo2 = [(7,8), (8,8), (4,11), (11,12), (9,11), (3,9), (7,14), (6,14), (8,14), (7,13), (7,15)]
            for r, c in pointsTo2: 
                if 0 <= r < 16 and 0 <= c < 16: newMap[r][c] = 2
            for r, c in [(2,12), (8,13), (12,11)]: newMap[r][c] = 5

        elif wave == 1:
            for r, c in [(4,4), (4,5), (5,4), (12,4), (11,4), (12,5), (4,12), (5,12), (4,11), (12,12), (11,12), (12,11)]:
                 newMap[r][c] = 7
            
        elif wave == 2:
            for r, c in [(8,4), (12,8), (8,12), (4,8)]:  newMap[r][c] = 7
            for r, c in [(1,1), (14,1), (14,14), (1,14), (2,1), (13,1), (13,14), (2,14), (1,2), (14,2), (14,13), (1,13)]:
                 newMap[r][c] = 5

        elif wave == 3:
            for r in [5,6,7,9,10,11]: 
                 newMap[r][5] = 7
                 newMap[r][11] = 7
            for c in [6,7,9,10]:
                 newMap[5][c] = 7
                 newMap[11][c] = 7

        elif wave in [4, 8]:
            for i in range(16):
                for j in range(16):
                    if  newMap[i][j] == 5:
                         newMap[i][j] = choice([0, 1])
                newMap[i][8] = choice([8, 9])
            newMap[8][4] = 7;  newMap[8][12] = 7;  newMap[9][12] = 7;  newMap[7][12] = 7
            newMap[5][6] = 5;  newMap[10][6] = 5

        elif wave == 7:
            for i in range(16):
                newMap[i][5] = 9 if i % 2 == 0 else 8
                newMap[i][10] = 9 if i % 2 == 0 else 8
            for r in [4, 8, 12]:
                newMap[r][5] = 10
                newMap[r][10] = 10
            
        elif wave == 12:
            for i in range(16):
                for j in range(16):
                    if  newMap[i][j] in [0, 1]:  newMap[i][j] = 5
                newMap[i][0] = 9 if i % 2 == 0 else 8
                newMap[i][15] = 9 if i % 2 == 0 else 8
            for i in range(1, 15):
                newMap[i][1] = 10;  newMap[i][14] = 10
                newMap[1][i] = 10;  newMap[14][i] = 10
            for i in range(2, 14):
                newMap[i][2] = 2; newMap[i][13] = 2
                newMap[2][i] = 2; newMap[13][i] = 2

        else:
             newMap[4][4] = 5;  newMap[12][4] = 5;  newMap[4][12] = 5;  newMap[12][12] = 5

        return  newMap

    def run(self):
        pass