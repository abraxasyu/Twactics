# twitch connect
import socket, select

port = 6667
nickname = 'twacticsbot'
identifier = 'twactics'
realname = 'twactics'
server = 'irc.chat.twitch.tv'
channel = '#twactics'
# password is "oauth:<oath token>"
password = 'oauth:rrzj32t2mfmy67t5toxrlbkx6pupww'
readbuffer = ''
print("Connecting...")
twitchirc = socket.socket()
twitchirc.connect((server, port))
print("Connected, logging in...")
twitchirc.send(bytes("PASS %s\r\n" % password, 'UTF-8'))
twitchirc.send(bytes("NICK %s\r\n" % nickname, 'UTF-8'))
twitchirc.send(bytes("USER %s %s BOT :%s\r\n" % (identifier, server, realname), 'UTF-8'))
print("Logged in, joining channel...")
twitchirc.send(bytes("JOIN %s\r\n" % channel, 'UTF-8'))
print("Joined!")

twitchirc.send(bytes('PRIVMSG #twactics :CHANNEL IS NOW ONLINE\r\n', 'UTF-8'))

cols = []
for i in range(1, 6):
    for j in range(1, 4):
        for k in range(1, 6):
            if i != j != k: #and i+j+k<=550:
                cols.append((50 * i, 50 * j, 50 * k))
import random

random.shuffle(cols)
import Team

teams = {}
commands = []


def userteam(user):
    retteam = None
    for team in teams:
        if user in teams[team].users:
            retteam = team
    return (retteam)


def gettime():
    hour = str(time.localtime().tm_hour)
    if int(hour) < 10:
        hour = '0' + hour
    min = str(time.localtime().tm_min)
    if int(min) < 10:
        min = '0' + min
    return (hour + ':' + min + ' ')


def parseloop():
    ready = select.select([twitchirc], [], [], 0)
    if ready[0]:
        readbuffer_src = str(twitchirc.recv(1024), 'UTF-8')
        # print(readbuffer_src)# = :abraxasone!abraxasone@abraxasone.tmi.twitch.tv PRIVMSG #twactics :hoho
        readbuffer = readbuffer_src.splitlines()
        for line in readbuffer:
            if line.find('PRIVMSG') > -1:
                user = line.split(':')[1].split('!')[0]
                msg = line.split('PRIVMSG ', 1)[1].split('#twactics :', 1)[1]
                uteam = userteam(user)
                # print('RAW------'+user+': '+msg)
                if msg.find('!join ') > -1:
                    curteam = msg.split('!join ', 1)[1]
                    if 0 < len(curteam) <= 16:
                        newcol = cols.pop(0)
                        cols.append(newcol)
                        if uteam is not None:  # check if user already exists in team
                            teams[uteam].users.remove(user)
                        if curteam in teams:  # if team already exists
                            teams[curteam].users.append(user)
                            commands.insert(0, [teams[curteam].col, gettime() + 'user <' + user + '> joined team <' + curteam + '>'])
                            # print('user <'+user+'> joined team <'+curteam+'>')
                        else:  # if team doesn't exist
                            teams[curteam] = (Team.Team(curteam, newcol, user, tilelist))
                            commands.insert(0, [teams[curteam].col, gettime() + 'user <' + user + '> created team <' + curteam + '>'])
                            # print('user <'+user+'> created team <'+curteam+'>')
                elif msg.find('!') > -1:
                    if uteam is None:
                        commands.insert(0, [(0,0,0), gettime() + 'user <' + user + '> needs to join team before attacking'])
                        # print('user <'+user+'> needs to join team before attacking')
                    else:
                        temptile = msg.split('!')[1]
                        #print(teams[uteam].attackable)
                        if (temptile in tilelist) and voting and (temptile in teams[uteam].attackable):  # valid attack command
                            tilelist[temptile].addvote(uteam, teams)
                            for updatetile in tilelist:
                                if len(tilelist[updatetile].votes) > 0:
                                    tilelist[updatetile].updatevote(teams)
                            commands.insert(0, [teams[userteam(user)].col, gettime() + 'user <' + user + '> attacked tile <' + temptile + '>'])
                            # print('user <'+user+'> attacks tile <'+temptile+'>')


# https://stackoverflow.com/questions/28665491/getting-a-bounded-polygon-coordinates-from-voronoi-cells/33602171#33602171
import matplotlib.pyplot as pl
import numpy as np
import scipy as sp
import scipy.spatial
import sys
import math

iternum = 15
n_towers = 100
xfuldim = 1.28
xdim = 1.00
ydim = 0.72
scale = 1000

eps = sys.float_info.epsilon
towers = np.random.rand(n_towers, 2)
towers[:, 0] *= xdim
towers[:, 1] *= ydim
bounding_box = np.array([0., xdim, 0., ydim])  # [x_min, x_max, y_min, y_max]


def inbox(pt):
    return (0 <= pt[0] <= xdim * scale and 0 <= pt[1] <= ydim * scale)


def in_box(towers, bounding_box):
    return np.logical_and(np.logical_and(bounding_box[0] <= towers[:, 0],
                                         towers[:, 0] <= bounding_box[1]),
                          np.logical_and(bounding_box[2] <= towers[:, 1],
                                         towers[:, 1] <= bounding_box[3]))


def voronoi(towers, bounding_box):
    # Select towers inside the bounding box
    i = in_box(towers, bounding_box)
    # Mirror points
    points_center = towers[i, :]
    points_left = np.copy(points_center)
    points_left[:, 0] = bounding_box[0] - (points_left[:, 0] - bounding_box[0])
    points_right = np.copy(points_center)
    points_right[:, 0] = bounding_box[1] + (bounding_box[1] - points_right[:, 0])
    points_down = np.copy(points_center)
    points_down[:, 1] = bounding_box[2] - (points_down[:, 1] - bounding_box[2])
    points_up = np.copy(points_center)
    points_up[:, 1] = bounding_box[3] + (bounding_box[3] - points_up[:, 1])
    points = np.append(points_center,
                       np.append(np.append(points_left,
                                           points_right,
                                           axis=0),
                                 np.append(points_down,
                                           points_up,
                                           axis=0),
                                 axis=0),
                       axis=0)
    # Compute Voronoi
    vor = sp.spatial.Voronoi(points)
    # Filter regions
    regions = []
    for region in vor.regions:
        flag = True
        for index in region:
            if index == -1:
                flag = False
                break
            else:
                x = vor.vertices[index, 0]
                y = vor.vertices[index, 1]
                if not (bounding_box[0] - eps <= x and x <= bounding_box[1] + eps and
                                    bounding_box[2] - eps <= y and y <= bounding_box[3] + eps):
                    flag = False
                    break
        if region != [] and flag:
            regions.append(region)
    vor.filtered_points = points_center
    vor.filtered_regions = regions
    return vor


def centroid_region(vertices):
    # Polygon's signed area
    A = 0
    # Centroid's x
    C_x = 0
    # Centroid's y
    C_y = 0
    for i in range(0, len(vertices) - 1):
        s = (vertices[i, 0] * vertices[i + 1, 1] - vertices[i + 1, 0] * vertices[i, 1])
        A = A + s
        C_x = C_x + (vertices[i, 0] + vertices[i + 1, 0]) * s
        C_y = C_y + (vertices[i, 1] + vertices[i + 1, 1]) * s
    A = 0.5 * A
    C_x = (1.0 / (6.0 * A)) * C_x
    C_y = (1.0 / (6.0 * A)) * C_y
    return np.array([[C_x, C_y]])


for i in range(0, iternum):
    vor = voronoi(towers, bounding_box)
    # Compute and plot centroids
    centroids = []
    for region in vor.filtered_regions:
        vertices = vor.vertices[region + [region[0]], :]
        centroid = centroid_region(vertices)
        centroids.append(list(centroid[0, :]))
    towers = np.array(centroids)

vor.points *= scale
vor.vertices *= scale
edgeprop = 0.80
lakecenter = ((np.random.rand() - 0.5) * xdim * scale / 2 * 0.8 + xdim * scale / 2,
              (np.random.rand() - 0.5) * ydim * scale / 2 * 0.8 + ydim * scale / 2)
lakeradius = (np.random.rand() / 2 + 1) * ydim * scale / 2 / 5
data = {}
index = 0
for i in range(0, len(vor.points)):
    if (inbox(vor.points[i])):  # in box
        curnode = (vor.points[i][0], vor.points[i][1])
        curvertices = []
        for vertindex in vor.regions[vor.point_region[i]]:
            curvertices.append((vor.vertices[vertindex][0], vor.vertices[vertindex][1]))
        curneighbors = []
        for neighbor in vor.ridge_points:
            if (neighbor[0] == i and inbox(vor.points[neighbor[1]]) and (
            vor.points[neighbor[1]][0], vor.points[neighbor[1]][1]) not in curneighbors):
                curneighbors.append((vor.points[neighbor[1]][0], vor.points[neighbor[1]][1]))
            if (neighbor[1] == i and inbox(vor.points[neighbor[0]]) and (
            vor.points[neighbor[0]][0], vor.points[neighbor[0]][1]) not in curneighbors):
                curneighbors.append((vor.points[neighbor[0]][0], vor.points[neighbor[0]][1]))
        type = False
        if (math.sqrt(math.pow((curnode[0] - xdim * scale / 2) / xdim, 2) + math.pow(
                    (curnode[1] - ydim * scale / 2) / ydim, 2)) <= scale / 2 * edgeprop):
            type = True
        if (math.sqrt(pow(lakecenter[0] - curnode[0], 2) + pow(lakecenter[1] - curnode[1], 2)) <= lakeradius):
            type = False
        if (type):
            data[curnode] = {'position': curnode, 'vertices': curvertices, 'neighbors': curneighbors, 'type': type,
                             'name': str(index)}
            index = index + 1
        else:
            data[curnode] = {'position': curnode, 'vertices': curvertices, 'neighbors': curneighbors, 'type': type}
# assign name
# assign type (ocean, lake)
# ignore irrelevant links (node-to-water) and consolidate valid links
# squiggly line for realism\

import Tile

tilelist = {}
for tile in data:
    if 'name' in data[tile]:
        tempnode = data[tile]
        tempneighbors = []
        for neighbor in tempnode['neighbors']:
            if 'name' in data[neighbor]:
                tempneighbors.append(data[neighbor]['name'])
        tilelist[tempnode['name']] = Tile.Tile(tempnode['name'], tempnode['position'], tempnode['vertices'],
                                               tempneighbors)  # name,position,vertices,neighbors

col_water = (150, 200, 225)  # (163,200,245)
col_dirt = (255, 255, 255)  # (245,200,163)
col_UI = (0, 0, 0)
col_softUI = (155, 155, 155)
col_panel = (255, 255, 255)

import pygame
from pygame import gfxdraw
from math import pi

pygame.display.init()
size = width, height = int(xfuldim * scale), int(ydim * scale)
screen = pygame.display.set_mode(size)
PARSELOOP = pygame.USEREVENT + 1
pygame.time.set_timer(PARSELOOP, 1000)
arcr = 30
arct = 10


def intify(tuplein):
    return (int(tuplein[0]), int(tuplein[1]))


def drawvoro():
    for tileid in tilelist:
        curtile = tilelist[tileid]

        # regions
        if curtile.team is not None:
            pygame.gfxdraw.filled_polygon(screen, curtile.vertices, teams[curtile.team].col)
        else:
            pygame.gfxdraw.filled_polygon(screen, curtile.vertices, col_dirt)
        # borders (vertices)
        #    pygame.gfxdraw.aapolygon(screen,curtile.vertices,teams[curtile.team].col)
        # pygame.draw.polygon(screen,color,data[node]['vertices'],5)
        pygame.draw.aalines(screen, col_UI, True, curtile.vertices, True)

        # neighbors
        for neighbor in curtile.neighbors:
            pygame.draw.aaline(screen, col_softUI, curtile.position, tilelist[neighbor].position, True)

        # center
        #tempsize = pyfont.size(str(curtile.name))
        #screen.blit(pyfont.render(str(curtile.name), True, (0, 0, 0)),(curtile.position[0] - tempsize[0] / 2, curtile.position[1] - tempsize[1] / 2))
        # pygame.gfxdraw.aacircle(screen,int(curtile.position[0]),int(curtile.position[1]),5,col_UI)
        # pygame.gfxdraw.filled_circle(screen,int(curtile.position[0]),int(curtile.position[1]),5,col_UI)

        # pie chart
        if len(curtile.arcvotes) > 0:
            for i in range(0, len(curtile.arcvotes)):
                temparc = curtile.arcvotes[i]
                pygame.draw.arc(screen, temparc['col'],
                                [curtile.position[0] - arcr, curtile.position[1] - arcr, arcr * 2, arcr * 2],
                                temparc['start'], temparc['end'], arct)
            for i in range(0, len(curtile.arcvotes)):
                temparc = curtile.arcvotes[i]
                if len(curtile.arcvotes) > 1:
                    pygame.draw.aaline(screen, (0, 0, 0), (
                    (arcr - arct + 1) * math.cos(2 * pi - temparc['start']) + curtile.position[0],
                    (arcr - arct + 1) * math.sin(2 * pi - temparc['start']) + curtile.position[1]), (
                                       (arcr - 1) * math.cos(2 * pi - temparc['start']) + curtile.position[0],
                                       (arcr - 1) * math.sin(2 * pi - temparc['start']) + curtile.position[1]), 0)
            pygame.gfxdraw.aacircle(screen, int(curtile.position[0]), int(curtile.position[1]), arcr, (0, 0, 0))
            pygame.gfxdraw.aacircle(screen, int(curtile.position[0]), int(curtile.position[1]), arcr - arct, (0, 0, 0))


pyclock = pygame.time.Clock()
pygame.font.init()
pyfont = pygame.font.SysFont("sans", 24)
desfont = pygame.font.SysFont("sans", 20)
commfont = pygame.font.SysFont("sans", 12)
# gameloop
import time

blinktime = 0.5
curblinktime = time.time()
curtime = time.time()
voting = True
running = True
instwidth = 280
instheight = 200
rankheight = 245
mg = 10
gap = 20
votelength = 45
resolength = 15
teamranks = []  # text for display
resolvetiles={}#tile:col
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == PARSELOOP:
            parseloop()
    if voting and time.time() - curtime > votelength:  # voting to resolution
        voting = False
        curtime = time.time()
        commands.insert(0, [(0,0,0), gettime() + 'Resolving Turn'])
        resolvetiles={}
        for tile in tilelist:
            newteam=tilelist[tile].teamchange()
            if newteam!=None:
                resolvetiles[tile]=teams[newteam].col
    elif not voting and time.time() - curtime > resolength:  # resolution to voting
        voting = True
        curtime = time.time()
        scoredict = {}
        for team in teams:
            teams[team].votes = 0
            teams[team].numtiles=0
        for tile in tilelist:  # settle tiles
            tilelist[tile].resolvevote()
            winteam = tilelist[tile].team
            if winteam is not None:
                teams[winteam].numtiles+=1
                if winteam in scoredict:
                    scoredict[winteam] += 1
                else:
                    scoredict[winteam] = 1
        for team in teams: #calculate attackabletiles
            if team in scoredict:
                tempattackable=[]
                for tile in tilelist:
                    if team==tilelist[tile].team:
                        if tile not in tempattackable:
                            tempattackable.append(tile)
                        for neighbor in tilelist[tile].neighbors:
                            if neighbor not in tempattackable:
                                tempattackable.append(neighbor)
                teams[team].attackable=tempattackable
            else:
                teams[team].attackable=tilelist.keys()
        maxscore = 0
        prevmax = 0
        maxteam = None
        currank = 1
        teamranks=[]
        while len(scoredict) > 0: #calculate teamranks
            for team in scoredict:
                if scoredict[team] > maxscore:
                    maxteam = team
                    maxscore = scoredict[team]
            if maxscore < prevmax:
                currank += 1
            teamranks.append(
                [teams[maxteam].col, str(currank) + '. <' + maxteam + '> with ' + str(maxscore) + ' tile(s)'])
            prevmax = maxscore
            scoredict.pop(maxteam)
            maxscore = 0
            maxteam = None
        commands.insert(0, [(0,0,0), gettime() + 'Voting Started'])
    screen.fill(col_water)
    drawvoro()
    # pygame.draw.circle(screen,(0,0,0),(100,100),1)
    screen.blit(pyfont.render('FPS: ' + "{0:.2f}".format(pyclock.get_fps()), 1, (0, 0, 0)), (10, 10))
    if voting:
        screen.blit(pyfont.render('Voting: ' + str(votelength - round(time.time() - curtime-0.5)), 1, (0, 0, 0)),
                    (xdim * scale * 0.50, 10))
    else:
        screen.blit(pyfont.render('Resolving: ' + str(resolength - round(time.time() - curtime-0.5)), 1, (255, 0, 0)),
                    (xdim * scale * 0.50, 10))
        if time.time()-curblinktime>blinktime*2:
            curblinktime=time.time()
        elif time.time()-curblinktime>blinktime:
            for rtile in resolvetiles: #rtile = teamname, resolvetiles[rtile]=newcol
                pygame.gfxdraw.filled_circle(screen,int(tilelist[rtile].position[0]),int(tilelist[rtile].position[1]),15,resolvetiles[rtile])

    for tile in tilelist:
        curtile=tilelist[tile]
        tempsize = pyfont.size(str(curtile.name))
        screen.blit(pyfont.render(str(curtile.name), True, (0, 0, 0)),(curtile.position[0] - tempsize[0] / 2, curtile.position[1] - tempsize[1] / 2))

    # add instructions
    pygame.draw.rect(screen, col_panel, [1280 - instwidth - mg, mg, instwidth, instheight], 0)
    screen.blit(desfont.render('How to play:', 1, (0, 0, 0)), (1280 - instwidth + mg, mg + gap))
    screen.blit(desfont.render(' 1. Join a team by typing:', 1, (0, 0, 0)), (1280 - instwidth + mg, mg + gap * 2))
    screen.blit(desfont.render('      !join [teamname]', 1, (255, 0, 0)), (1280 - instwidth + mg, mg + gap * 3))
    screen.blit(desfont.render('      example: !join ABC', 1, (0, 0, 0)), (1280 - instwidth + mg, mg + gap * 4))
    screen.blit(desfont.render(' 2. Attack a tile by typing:', 1, (0, 0, 0)), (1280 - instwidth + mg, mg + gap * 5))
    screen.blit(desfont.render('      ![tilenumber]', 1, (255, 0, 0)), (1280 - instwidth + mg, mg + gap * 6))
    screen.blit(desfont.render('      example : !10', 1, (0, 0, 0)), (1280 - instwidth + mg, mg + gap * 7))
    screen.blit(desfont.render('More details in channel description', 1, (0, 0, 0)),
                (1280 - instwidth + mg, mg + gap * 8))

    # add scoreboard
    pygame.draw.rect(screen, col_panel, [1280 - instwidth - mg, instheight + mg * 2, instwidth, rankheight], 0)
    for i in range(0, min(11, len(teamranks) + 1)):
        if i == 0:
            screen.blit(desfont.render('Team Ranking:', 1, (0, 0, 0)),
                        (1280 - instwidth + mg, instheight + mg * 3 + i * 20))
        else:
            screen.blit(desfont.render(teamranks[i - 1][1], 1, teamranks[i - 1][0]),
                        (1280 - instwidth + mg, instheight + mg * 3 + i * 20))
    # add commands
    pygame.draw.rect(screen, col_panel, [1280 - instwidth - mg, mg * 3 + instheight + rankheight, instwidth,
                                               720 - (mg * 4 + instheight + rankheight)], 0)
    for i in range(0, min(14, len(commands))):
        screen.blit(commfont.render(commands[i][1], 1, commands[i][0]), (1280 - instwidth + mg, 720 - gap - mg * 1.5 * (i + 1)))
    # fps lock and flip
    pyclock.tick(30)
    pygame.display.flip()
pygame.quit()
sys.exit()
