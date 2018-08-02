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
        self.max_defence = 0
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
        self.writeCommand(x, y, 0)

    def buildAttack(self, x_list, y):
        x = max(x_list)
        self.writeCommand(x, y, 1)

    def buildMinAttack(self, x_list, y):
        x = min(x_list)
        self.writeCommand(x, y, 1)

    def buildEnergy(self, x_list, y):
        x = min(x_list)
        self.writeCommand(x, y, 2)

    def buildTesla(self, x_list, y):
        x = max(x_list)
        self.writeCommand(x, y, 4)

    def getLaneWithFewestBuildings(self, building):
        lanes = []
        low = self.columns/2
        for i, lane in enumerate(self.player_buildings):
            if self.numBuildingsInRowPlayer(i, building) < low:
                lanes.clear()
                low = self.numBuildingsInRowPlayer(i, building)
                lanes.append(i)
            elif self.numBuildingsInRowPlayer(i, building) == low:
                lanes.append(i)
        return lanes

    def getLaneWithFewestBuildingsOpponent(self, building):
        lanes = []
        low = self.columns/2
        for i, lane in enumerate(self.opponent_buildings):
            if self.numBuildingsInRowEnemy(i, building) < low:
                lanes.clear()
                low = self.numBuildingsInRowEnemy(i, building)
                lanes.append(i)
            elif self.numBuildingsInRowEnemy(i, building) == low:
                lanes.append(i)
        return lanes

    def energyLogic(self):
        for i, lane in enumerate(self.player_buildings):
            if self.numBuildingsInRowPlayer(i, 3) > 2:
                continue
            x_list = self.getUnOccupied(lane)
            if len(x_list) > 0 and self.checkAttack(i) is False:
                self.buildEnergy(x_list, i)
                return
        i = random.choice(self.getLaneWithFewestBuildingsOpponent(1))
        x_list = self.getUnOccupied(self.player_buildings[i])
        self.buildEnergy(x_list, i)
        return


    def getOpponentLaneWithMostEnergy(self):
        highest = 0
        b_list = []
        for i, lane in enumerate(self.opponent_buildings):
            num = self.numBuildingsInRowEnemy(i, 3)
            if num > highest:
                b_list.clear()
                highest = num
                b_list.append(i)
            if num == highest:
                b_list.append(i)
        return b_list

    def getLaneToAttack(self):
        energy = []
        attack = []
        prio = []
        high = 0
        for i, lane in enumerate(self.player_buildings):
            value = self.numBuildingsInRowEnemy(i, 3) - self.numBuildingsInRowPlayer(i, 1)
            if value > high and 0 in lane:
                energy.clear()
                high = value
                energy.append(i)
            if value == high and 0 in lane:
                energy.append(i)
        if self.getTotalNumBuildingsOpponent(1) > 0:
            for i, lane in enumerate(self.player_buildings):
                value = self.numBuildingsInRowEnemy(i, 1)
                if self.checkAttack(i) and self.checkMyAttack(i) is False and self.checkMyEnergy(i) is False:
                    prio.append(i)
                if value > high and 0 in lane:
                    attack.clear()
                    high = value
                    attack.append(i)
                if value == high and 0 in lane:
                    attack.append(i)
        if len(attack) == 0 and len(energy) == 0:
            for i, lane in enumerate(self.player_buildings):
                if self.checkAttack(i) is False and self.checkEnergy(i) is False:
                    attack.append(i)
        lanes = energy
        lanes.extend(attack)
        if len(prio) == 0:
            return lanes
        else:
            return prio

    def attackLogic(self):
        # # if self.getTotalNumBuildings(1) == 0 and self.getTotalNumBuildings(2) == 0:
        # #     i = random.randint(0, 1)
        # #     x_list = self.getUnOccupied(self.player_buildings[i])
        # #     self.buildAttack(x_list, i)
        # #     return
        # i_list = self.getOpponentLaneWithMostEnergy()
        # # for i, lane in enumerate(self.player_buildings):
        # #     if self.checkMyAttack(i) is False and self.checkMyDefense(i) is True:
        # #         x_list = self.getXValueBehindDefence(self.player_buildings[i])
        # #         self.buildAttack(x_list, i)
        # #         return
        lane_number = self.getLaneToAttack()
        for j in enumerate(lane_number):
            i = random.choice(lane_number)
            x_list = self.getUnOccupied(self.player_buildings[i])
        if self.checkMyDefense(i):
            temp = self.getXValueBehindDefence(self.player_buildings[i])
            if len(temp) > 0:
                x_list = temp
        self.buildAttack(x_list, i)
        return

    def defenceLogic(self):
        place = []
        y = 0
        most_attacks = 0
        for i, lane in enumerate(self.player_buildings):
            if self.checkMyAttack(i) and self.checkAttack(i):
                if self.numBuildingsInRowPlayer(i, 2) < self.getMaxDefence(i) and self.numBuildingsInRowEnemy(i, 1) >= 2:
                    x_list = self.getUnOccupied(lane)
                    self.buildDefense(x_list, i)
                    return
        # for i, lane in enumerate(self.player_buildings):
        #     x_list = self.getUnOccupied(lane)
        #     num_attack = self.numBuildingsInRowEnemy(i, 1)
        #     if self.numBuildingsInRowPlayer(i, 2) < self.getMaxDefence(i):
        #         if len(x_list) > 0:
        #             if self.checkAttack(i) is True:
        #                 if num_attack > most_attacks:
        #                     most_attacks = num_attack
        #                     y = i
        #                     place = x_list
        # if len(place) > 0:
        #     self.buildDefense(place, y)
        #     return
        # else:
            self.attackLogic()

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

    def teslaLogic(self):
        i = random.choice(self.getOpponentBiggestLane())
        if i == 0:
            i += 1
        else:
            i -= 1
        x_list = self.getUnOccupied(self.player_buildings[i])
        if self.checkMyDefense(i) is True:
            x_list = self.getXValueBehindDefence(self.player_buildings[i])
            if len(x_list) > 0:
                self.buildTesla(x_list, i)
        elif self.checkAttack(i) is False:
            self.buildTesla(x_list, i)
        self.attackLogic()

    def checkIfBoardIsFull(self):
        for lane in self.player_buildings:
            b_list = list(lane)
            if b_list.count(0) > 0:
                return False
        return True

    def generateAction(self):
        if self.checkIfBoardIsFull():
            self.writeDoNothing()
            return
        if self.player_info['energy'] > 350:
            self.teslaLogic()
        elif self.checkAllLanesForBuilding(1) is True and self.checkAllLanesForDefence() is True\
                and self.getTotalNumBuildings(3) < self.rows * 2:
            if self.buildings_stats['ENERGY']['price'] <= self.player_info['energy']:
                self.energyLogic()
            else:
                self.writeDoNothing()
        elif self.player_info['energy'] >= self.buildings_stats['DEFENSE']['price']:
            self.defenceLogic()
        elif self.buildings_stats['ENERGY']['price'] <= self.player_info['energy'] <= 500:
            self.energyLogic()
        else:
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
