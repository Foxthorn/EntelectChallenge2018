# -*- coding: utf-8 -*-
'''
Entelect StarterBot for Python3
'''
import time
from enum import Enum

startTime = time.time()

import json
import os
from time import sleep
import random

class BoardSate(Enum):
    EMPTY = 1
    SAFE = 2
    CONTESTED = 3
    DANGER = 4
    FULL = 5

class StarterBot:

    def __init__(self, state_location):
        '''
        Initialize Bot.
        Load all game state information.
        '''
        try:
            self.game_state = self.loadState(state_location)
        except IOError:
            print("Cannot load Game State")

        self.full_map = self.game_state['gameMap']
        self.rows = self.game_state['gameDetails']['mapHeight']
        self.columns = self.game_state['gameDetails']['mapWidth']
        self.command = ''

        self.player_buildings = self.getPlayerBuildings()
        self.opponent_buildings = self.getOpponentBuildings()
        self.projectiles = self.getProjectiles()

        self.player_info = self.getPlayerInfo('A')
        self.opponent_info = self.getPlayerInfo('B')

        self.round = self.game_state['gameDetails']['round']

        self.buildings_stats = {
            "ATTACK": {"health": self.game_state['gameDetails']['buildingsStats']['ATTACK']['health'],
                       "constructionTime": self.game_state['gameDetails']['buildingsStats']['ATTACK'][
                           'constructionTime'],
                       "price": self.game_state['gameDetails']['buildingsStats']['ATTACK']['price'],
                       "weaponDamage": self.game_state['gameDetails']['buildingsStats']['ATTACK']['weaponDamage'],
                       "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['ATTACK']['weaponSpeed'],
                       "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['ATTACK'][
                           'weaponCooldownPeriod'],
                       "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['ATTACK'][
                           'energyGeneratedPerTurn'],
                       "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['ATTACK'][
                           'destroyMultiplier'],
                       "constructionScore": self.game_state['gameDetails']['buildingsStats']['ATTACK'][
                           'constructionScore']},
            "DEFENSE": {"health": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['health'],
                        "constructionTime": self.game_state['gameDetails']['buildingsStats']['DEFENSE'][
                            'constructionTime'],
                        "price": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['price'],
                        "weaponDamage": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['weaponDamage'],
                        "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['weaponSpeed'],
                        "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['DEFENSE'][
                            'weaponCooldownPeriod'],
                        "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['DEFENSE'][
                            'energyGeneratedPerTurn'],
                        "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['DEFENSE'][
                            'destroyMultiplier'],
                        "constructionScore": self.game_state['gameDetails']['buildingsStats']['DEFENSE'][
                            'constructionScore']},
            "ENERGY": {"health": self.game_state['gameDetails']['buildingsStats']['ENERGY']['health'],
                       "constructionTime": self.game_state['gameDetails']['buildingsStats']['ENERGY'][
                           'constructionTime'],
                       "price": self.game_state['gameDetails']['buildingsStats']['ENERGY']['price'],
                       "weaponDamage": self.game_state['gameDetails']['buildingsStats']['ENERGY']['weaponDamage'],
                       "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['ENERGY']['weaponSpeed'],
                       "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['ENERGY'][
                           'weaponCooldownPeriod'],
                       "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['ENERGY'][
                           'energyGeneratedPerTurn'],
                       "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['ENERGY'][
                           'destroyMultiplier'],
                       "constructionScore": self.game_state['gameDetails']['buildingsStats']['ENERGY'][
                           'constructionScore']}}
        self.board_state = BoardSate.EMPTY
        self.energy_full = False
        self.defence_full = False
        return None

    def loadState(self, state_location):
        '''
        Gets the current Game State json file.
        '''
        return json.load(open(state_location, 'r'))

    def getPlayerInfo(self, playerType):
        '''
        Gets the player information of specified player type
        '''
        for i in range(len(self.game_state['players'])):
            if self.game_state['players'][i]['playerType'] == playerType:
                return self.game_state['players'][i]
            else:
                continue
        return None

    def getOpponentBuildings(self):
        '''
        Looks for all buildings, regardless if completed or not.
        0 - Nothing
        1 - Attack Unit
        2 - Defense Unit
        3 - Energy Unit
        '''
        opponent_buildings = []

        for row in range(0, self.rows):
            buildings = []
            for col in range(int(self.columns / 2), self.columns):
                if len(self.full_map[row][col]['buildings']) == 0:
                    buildings.append(0)
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'ATTACK':
                    buildings.append(1)
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'DEFENSE':
                    buildings.append(2)
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'ENERGY':
                    buildings.append(3)
                else:
                    buildings.append(0)

            opponent_buildings.append(buildings)

        return opponent_buildings

    def getPlayerBuildings(self):
        '''
        Looks for all buildings, regardless if completed or not.
        0 - Nothing
        1 - Attack Unit
        2 - Defense Unit
        3 - Energy Unit
        '''
        player_buildings = []

        for row in range(0, self.rows):
            buildings = []
            for col in range(0, int(self.columns / 2)):
                if len(self.full_map[row][col]['buildings']) == 0:
                    buildings.append(0)
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'ATTACK':
                    buildings.append(1)
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'DEFENSE':
                    buildings.append(2)
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'ENERGY':
                    buildings.append(3)
                else:
                    buildings.append(0)

            player_buildings.append(buildings)

        return player_buildings

    def getProjectiles(self):
        '''
        Find all projectiles on the map.
        0 - Nothing there
        1 - Projectile belongs to player
        2 - Projectile belongs to opponent
        '''
        projectiles = []

        for row in range(0, self.rows):
            temp = []
            for col in range(0, self.columns):
                if len(self.full_map[row][col]['missiles']) == 0:
                    temp.append(0)
                elif self.full_map[row][col]['missiles'][0]['playerType'] == 'A':
                    temp.append(1)
                elif self.full_map[row][col]['missiles'][0]['playerType'] == 'B':
                    temp.append(2)

            projectiles.append(temp)

        return projectiles

    def checkDefense(self, lane_number):

        '''
        Checks a lane.
        Returns True if lane contains defense unit.
        '''

        lane = list(self.opponent_buildings[lane_number])
        if lane.count(2) > 0:
            return True
        else:
            return False

    def checkMyDefense(self, lane_number):

        '''
        Checks a lane.
        Returns True if lane contains defense unit.
        '''

        lane = list(self.player_buildings[lane_number])
        if lane.count(2) > 0:
            return True
        else:
            return False

    def CheckAttack(self, lane_number):

        '''
        Checks a lane.
        Returns True if lane contains attack unit.
        '''

        lane = list(self.opponent_buildings[lane_number])
        if lane.count(1) > 0:
            return True
        else:
            return False

    def getUnOccupied(self, lane):
        '''
        Returns index of all unoccupied cells in a lane
        '''
        indexes = []
        for i in range(len(lane)):
            if lane[i] == 0:
                indexes.append(i)

        return indexes

    def getBoardState(self):
        num_empty = 0
        num_attack = 0
        for line in self.opponent_buildings:
            for spot in line:
                if spot == 0:
                    num_empty += 1
                if spot == 2:
                    num_attack += 1
        if num_empty == self.rows * (self.columns / 2):
            self.board_state = BoardSate.EMPTY
        elif num_attack == 0:
            self.board_state = BoardSate.SAFE
        elif num_attack < self.rows:
            self.board_state = BoardSate.CONTESTED
        elif num_attack >= self.rows:
            self.board_state = BoardSate.DANGER

    def getUnOccupiedSpot(self, x_index, building):
        if x_index == self.columns / 2:
            self.board_state = BoardSate.FULL
            return 0, 0
        for y, line in enumerate(self.player_buildings):
            for x, spot in enumerate(line):
                if x != x_index:
                    continue
                else:
                    if spot == 0:
                        return x, y
                    else:
                        break
        if building == 2:
            self.energy_full = True
            return -1, -1
        if building == 0:
            self.defence_full = True
            return -1, -1
        return -1, -1

    def generateAction(self):
        self.getBoardState()
        if self.board_state == BoardSate.EMPTY:
            if self.player_info['energy'] >= self.buildings_stats['ENERGY']['price']:
                x, y, = self.getUnOccupiedSpot(0, 2)
                if x != -1 or y != -1:
                    self.writeCommand(x, y, 2)
                elif self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                    i = 0
                    while i < self.columns / 2 and x == -1 or y == -1:
                        x, y, = self.getUnOccupiedSpot(i, 1)
                        i += 1
                    if x != -1 or y != -1:
                        self.writeCommand(x, y, 1)
            else:
                self.writeDoNothing()
        if self.board_state == BoardSate.SAFE:
                if self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                    x, y, = self.getUnOccupiedSpot(0, 1)
                    if x != -1 or y != -1:
                        self.writeCommand(x, y, 1)
                    elif self.player_info['energy'] >= self.buildings_stats['ENERGY']['price']:
                        x, y, = self.getUnOccupiedSpot(1, 2)
                        self.writeCommand(x, y, 2)
                    else:
                        self.writeDoNothing()
        if self.board_state == BoardSate.CONTESTED:
                if self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                    x, y, = self.getUnOccupiedSpot(1, 1)
                    if x != -1 or y != -1:
                        self.writeCommand(x, y, 1)
                    elif self.player_info['energy'] >= self.buildings_stats['DEFENCE']['price']:
                        x, y, = self.getUnOccupiedSpot(self.columns - 1, 0)
                        self.writeCommand(x, y, 0)
                    else:
                        self.writeDoNothing()
        if self.board_state == BoardSate.DANGER:
            if self.player_info['energy'] >= self.buildings_stats['DEFENCE']['price']:
                x, y, = self.getUnOccupiedSpot(0, 0)
                if x != -1 or y != -1:
                    self.writeCommand(x, y, 0)
                else:
                    self.writeDoNothing()


    def writeCommand(self, x, y, building):
        '''
        command in form : x,y,building_type
        '''
        outfl = open('command.txt', 'w')
        outfl.write(','.join([str(x), str(y), str(building)]))
        outfl.close()
        return None

    def writeDoNothing(self):
        '''
        command in form : x,y,building_type
        '''
        outfl = open('command.txt', 'w')
        outfl.write("")
        outfl.close()
        return None


if __name__ == '__main__':
    s = StarterBot('state.json')
    s.generateAction()