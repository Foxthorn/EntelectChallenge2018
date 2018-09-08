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


class BoardState(Enum):
    PLAYER_FAVOURED = 1
    OPPONENT_FAVOURED = 2
    EVEN = 3
    IRON_CURTAIN = 4


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
                           'constructionScore']},
            "TESLA": {"health": self.game_state['gameDetails']['buildingsStats']['TESLA']['health'],
                      "constructionTime": self.game_state['gameDetails']['buildingsStats']['TESLA'][
                          'constructionTime'],
                      "price": self.game_state['gameDetails']['buildingsStats']['TESLA']['price'],
                      "weaponDamage": self.game_state['gameDetails']['buildingsStats']['TESLA']['weaponDamage'],
                      "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['TESLA']['weaponSpeed'],
                      "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['TESLA'][
                          'weaponCooldownPeriod'],
                      "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['TESLA'][
                          'destroyMultiplier'],
                      "constructionScore": self.game_state['gameDetails']['buildingsStats']['TESLA'][
                          'constructionScore']}}
        self.max_defence = 0
        self.board_state = BoardState.EVEN
        self.move_made = False
        return None

    def loadState(self, state_location):
        """
        Gets the current Game State json file.
        """
        return json.load(open(state_location, 'r'))

    def getPlayerInfo(self, playerType):
        """
        Gets the player information of specified player type
        """
        for i in range(len(self.game_state['players'])):
            if self.game_state['players'][i]['playerType'] == playerType:
                return self.game_state['players'][i]
            else:
                continue
        return None

    def getOpponentBuildings(self):
        """
        Looks for all buildings, regardless if completed or not.
        0 - Nothing
        1 - Attack Unit
        2 - Defense Unit
        3 - Energy Unit
        """
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
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'TESLA':
                    buildings.append(4)
                else:
                    buildings.append(0)

            opponent_buildings.append(buildings)

        return opponent_buildings

    def getPlayerBuildings(self):
        """
        Looks for all buildings, regardless if completed or not.
        0 - Nothing
        1 - Attack Unit
        2 - Defense Unit
        3 - Energy Unit
        """
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
                elif self.full_map[row][col]['buildings'][0]['buildingType'] == 'TESLA':
                    buildings.append(4)
                else:
                    buildings.append(0)

            player_buildings.append(buildings)

        return player_buildings

    def getProjectiles(self):
        """
        Find all projectiles on the map.
        0 - Nothing there
        1 - Projectile belongs to player
        2 - Projectile belongs to opponent
        """
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
        """
        Checks a lane.
        Returns True if lane contains defense unit.
        """

        lane = list(self.opponent_buildings[lane_number])
        if lane.count(2) > 0:
            return True
        else:
            return False

    def checkEnergy(self, lane_number):
        lane = list(self.opponent_buildings[lane_number])
        if lane.count(3) > 0:
            return True
        else:
            return False

    def checkMyEnergy(self, lane_number):
        lane = list(self.player_buildings[lane_number])
        if lane.count(3) > 0:
            return True
        else:
            return False

    def checkMyDefense(self, lane_number):

        """
        Checks a lane.
        Returns True if lane contains defense unit.
        """

        lane = list(self.player_buildings[lane_number])
        if lane.count(2) > 0:
            return True
        else:
            return False

    def checkMyAttack(self, lane_number):
        lane = list(self.player_buildings[lane_number])
        if lane.count(1) > 0:
            return True
        else:
            return False

    def checkAttack(self, lane_number):

        """
        Checks a lane.
        Returns True if lane contains attack unit.
        """

        lane = list(self.opponent_buildings[lane_number])
        if lane.count(1) > 0:
            return True
        else:
            return False

    def getUnOccupiedDefence(self):
        """
        Returns index of all unoccupied cells in a lane
        """
        indexes = []
        for i, lane in enumerate(self.opponent_buildings):
            if 2 in lane:
                indexes.append(i)

        return indexes

    def getUnOccupied(self, lane):
        """
        Returns index of all unoccupied cells in a lane
        """
        indexes = []
        for i, place in enumerate(lane):
            if place == 0:
                indexes.append(i)

        return indexes

    def getNumEmptySpace(self, lane):
        count = 0
        for place in lane:
            if place == 0:
                count += 1
        return count

    def getEmptyLaneNumber(self):
        for i, lane in enumerate(self.player_buildings):
            if len(self.getUnOccupied(lane)) == self.columns / 2:
                return i
        return -1

    def numBuildingsInRowEnemy(self, lane_num, building):
        lane = list(self.opponent_buildings[lane_num])
        return lane.count(building)

    def numBuildingsInRowPlayer(self, lane_num, building):
        lane = list(self.player_buildings[lane_num])
        return lane.count(building)

    def getMaxDefence(self, lane_num):
        max_def = 0
        num_attack = self.numBuildingsInRowEnemy(lane_num, 1)
        if num_attack > 0:
            max_def = 1
        if num_attack > 3:
            max_def += round(num_attack / 3)
        return max_def

    def getXValueBehindDefence(self, lane):
        behind = []
        x_defence = 0
        for i, place in enumerate(lane):
            if place == 2:
                x_defence = i
        x_list = self.getUnOccupied(lane)
        for i, place in enumerate(x_list):
            if place < x_defence:
                behind.append(place)
        return behind

    def buildDefense(self, x_list, y):
        x = max(x_list)
        self.move_made = True
        self.writeCommand(x, y, 0)

    def buildAttack(self, x_list, y):
        x = max(x_list)
        self.move_made = True
        self.writeCommand(x, y, 1)

    def buildMinAttack(self, x_list, y):
        x = min(x_list)
        self.move_made = True
        self.writeCommand(x, y, 1)

    def buildEnergy(self, x_list, y):
        x = min(x_list)
        self.move_made = True
        self.writeCommand(x, y, 2)

    def buildTesla(self, x_list, y):
        x = max(x_list)
        self.move_made = True
        self.writeCommand(x, y, 4)

    def buildIronCurtain(self):
        self.writeCommand(0, 0, 5)

    def getLaneWithFewestBuildings(self, building):
        lanes = []
        low = self.columns / 2
        for i, lane in enumerate(self.player_buildings):
            if self.numBuildingsInRowPlayer(i, building) < low and 0 in lane:
                lanes.clear()
                low = self.numBuildingsInRowPlayer(i, building)
                lanes.append(i)
            elif self.numBuildingsInRowPlayer(i, building) == low and 0 in lane:
                lanes.append(i)
        return lanes

    def getLaneWithFewestBuildingsOpponent(self, building):
        lanes = []
        low = self.columns / 2
        for i, lane in enumerate(self.opponent_buildings):
            if self.numBuildingsInRowEnemy(i, building) < low and 0 in lane:
                lanes.clear()
                low = self.numBuildingsInRowEnemy(i, building)
                lanes.append(i)
            elif self.numBuildingsInRowEnemy(i, building) == low and 0 in lane:
                lanes.append(i)
        return lanes

    def getLaneWithMostBuildings(self, building):
        lanes = []
        max_num = 0
        for i, lane in enumerate(self.player_buildings):
            if self.numBuildingsInRowPlayer(i, building) > max_num and 0 in lane:
                lanes.clear()
                max_num = self.numBuildingsInRowPlayer(i, building)
                lanes.append(i)
            elif self.numBuildingsInRowPlayer(i, building) == max_num and 0 in lane:
                lanes.append(i)
        return lanes

    def getLaneWithMostBuildingsOpponent(self, building):
        lanes = []
        max_num = 0
        for i, lane in enumerate(self.opponent_buildings):
            if self.numBuildingsInRowEnemy(i, building) > max_num and 0 in lane:
                lanes.clear()
                max_num = self.numBuildingsInRowEnemy(i, building)
                lanes.append(i)
            elif self.numBuildingsInRowEnemy(i, building) == max_num and 0 in lane:
                lanes.append(i)
        return lanes

    def checkAllLanesForDefence(self):
        for i, lane in enumerate(self.player_buildings):
            if self.numBuildingsInRowPlayer(i, 2) != self.getMaxDefence(i):
                return False
        return True

    def checkAllLanesForBuilding(self, building):
        for lane in self.player_buildings:
            if building not in lane:
                return False
        return True

    def getTotalNumBuildingsOpponent(self, building):
        num = 0
        for lane in self.opponent_buildings:
            b_list = list(lane)
            num += b_list.count(building)
        return num

    def getTotalNumBuildings(self, building):
        num = 0
        for lane in self.player_buildings:
            b_list = list(lane)
            num += b_list.count(building)
        return num

    def getNumBuildingsInLane(self, lane):
        b_list = list(lane)
        num = (self.columns / 2) - b_list.count(0)
        return num

    def getOpponentBiggestLane(self):
        highest = 0
        b_list = []
        for i, lane in enumerate(self.opponent_buildings):
            num = self.getNumBuildingsInLane(lane)
            if num > highest:
                b_list.clear()
                highest = num
                b_list.append(i)
            if num == highest:
                b_list.append(i)
        return b_list

    def checkIfBoardIsFull(self):
        for lane in self.player_buildings:
            b_list = list(lane)
            if b_list.count(0) > 0:
                return False
        return True

    def getBoardState(self):
        player_value = 0
        opponent_value = 0
        if self.player_info['isIronCurtainActive'] is True:
            self.board_state = BoardState.IRON_CURTAIN
            return
        for i, lane in enumerate(self.player_buildings):
            player_value += self.numBuildingsInRowPlayer(i, 1) * self.buildings_stats['ATTACK']['health']
            opponent_value += self.numBuildingsInRowEnemy(i, 1) * self.buildings_stats['ATTACK']['health']
            if self.checkAttack(i):
                opponent_value += self.numBuildingsInRowEnemy(i, 2) * self.buildings_stats['DEFENSE']['health']
            if self.checkMyAttack(i):
                player_value += self.numBuildingsInRowPlayer(i, 2) * self.buildings_stats['DEFENSE']['health']
        print(player_value)
        print(opponent_value)
        if opponent_value > player_value:
            self.board_state = BoardState.OPPONENT_FAVOURED
        elif opponent_value < player_value:
            self.board_state = BoardState.PLAYER_FAVOURED
        elif opponent_value == player_value:
            self.board_state = BoardState.EVEN

    def getLaneWithNoAttack(self):
        lanes = []
        for i, lane in enumerate(self.player_buildings):
            if self.checkAttack(i) is False and 0 in lane:
                lanes.append(i)
        return lanes

    def teslaLogic(self):
        lanes = self.getLaneWithMostBuildingsOpponent(1)
        if len(lanes) != 0:
            i = random.choice(lanes)
            if i == self.rows - 1:
                x_list = self.getUnOccupied(self.player_buildings[i])
                self.buildTesla(x_list, i)
                return
            else:
                x_list = self.getUnOccupied(self.player_buildings[i + 1])
                self.buildTesla(x_list, i + 1)
                return
        self.player_favoured_attack()


    def energyLogic(self):
        lanes = self.getLaneWithNoAttack()
        lane_numbers = self.getLaneWithFewestBuildings(3)
        if len(lanes) != 0:
            i = random.choice(lanes)
            if i not in lane_numbers:
                for j in lanes:
                    i = j
                    if i in lane_numbers:
                        break
                if i not in lane_numbers:
                    i = random.choice(lanes)
        else:
            i = random.choice(self.getLaneWithFewestBuildingsOpponent(1))
        x_list = self.getUnOccupied(self.player_buildings[i])
        self.buildEnergy(x_list, i)
        return

    def player_favoured_attack(self):
        lanes = self.getLaneWithMostBuildingsOpponent(3)
        for i in lanes:
            x_list = self.getUnOccupied(self.player_buildings[i])
            if len(x_list) > 0:
                if self.numBuildingsInRowPlayer(i, 1) <= self.numBuildingsInRowEnemy(i, 3):
                    self.buildAttack(x_list, i)
                    return
        lanes = self.getLaneWithFewestBuildings(3)
        for i in lanes:
            x_list = self.getUnOccupied(self.player_buildings[i])
            if len(x_list) > 0:
                self.buildAttack(x_list, i)
                return
        self.opponent_favoured_attack()

    def opponent_favoured_attack(self):
        lanes = self.getLaneWithMostBuildingsOpponent(1)
        for i in lanes:
            x_list = self.getUnOccupied(self.player_buildings[i])
            if len(x_list) > 0:
                self.buildMinAttack(x_list, i)
                return
        for i, lane in self.player_buildings:
            x_list = self.getUnOccupied(lane)
            if self.checkMyDefense(i) and self.checkMyAttack(i) is False:
                if len(x_list) > 0:
                    if self.numBuildingsInRowPlayer(i, 1) <= self.numBuildingsInRowEnemy(i, 1):
                        self.buildAttack(x_list, i)
                        return
        self.defence_logic()

    def defence_logic(self):
        lanes = self.getLaneWithMostBuildingsOpponent(1)
        for i in lanes:
            x_list = self.getUnOccupied(self.player_buildings[i])
            if len(x_list) > 0:
                self.buildDefense(x_list, i)
                return
        for i, lane in enumerate(self.player_buildings):
            x_list = self.getUnOccupied(lane)
            if self.checkAttack(i) and self.numBuildingsInRowPlayer(i, 2) < self.getMaxDefence(i):
                if len(x_list) > 0:
                    self.buildDefense(x_list, i)
                    return

    def generateAction(self):
        if self.checkIfBoardIsFull():
            self.writeDoNothing()
            return
        self.getBoardState()
        print(self.player_info)
        if self.player_info['energy'] >= 100 and self.player_info['ironCurtainAvailable'] is True:
            self.buildIronCurtain()
            return
        if self.player_info['isIronCurtainActive'] is True:
            if self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                self.player_favoured_attack()
        if self.board_state == BoardState.EVEN:
            if self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                self.player_favoured_attack()
            elif self.player_info['energy'] >= self.buildings_stats['ENERGY']['price']:
                self.energyLogic()
        if self.board_state == BoardState.PLAYER_FAVOURED:
            if self.player_info['energy'] >= self.buildings_stats['TESLA']['price']:
                self.teslaLogic()
            elif self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                self.player_favoured_attack()
            elif self.player_info['energy'] >= self.buildings_stats['ENERGY']['price']:
                self.energyLogic()
        if self.board_state == BoardState.OPPONENT_FAVOURED:
            if self.player_info['energy'] >= self.buildings_stats['ATTACK']['price']:
                self.opponent_favoured_attack()
            elif self.player_info['energy'] >= self.buildings_stats['ENERGY']['price']:
                self.energyLogic()
        if not self.move_made:
            self.writeDoNothing()

    def writeCommand(self, x, y, building):
        """
        command in form : x,y,building_type
        """
        outfl = open('command.txt', 'w+')
        outfl.write(','.join([str(x), str(y), str(building)]))
        outfl.close()
        return None

    def writeDoNothing(self):
        """
        command in form : x,y,building_type
        """
        outfl = open('command.txt', 'w+')
        outfl.write("")
        outfl.close()
        return None


if __name__ == '__main__':
    s = StarterBot('state.json')
    s.generateAction()
