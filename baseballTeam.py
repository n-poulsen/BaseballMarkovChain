import csv
from baseballPlayer import Player


class Team:
    """
    Represents a Baseball team, through the pitchers and batters in the team.
    """

    def __init__(self, teamName, batters, pitchers):
        """
        :param teamName: String. The team's name
        :param batters: [Batter]. A list containing the 9 batters in the team.
        :param teamName: []. A list containing the pitchers in the team (ignored for now)
        """
        self.name = teamName
        self.batters = sorted(batters, key=lambda Player: Player.ops)
        self.pitchers = pitchers

    def averagePlayer(self):
        """
        Computes an average player for the team.
        :return: Batter. An average batter in self.
        """
        pa = 0
        outs = 0
        b1 = 0
        b2 = 0
        b3 = 0
        b4 = 0
        bb = 0
        ops = 0
        for b in self.batters:
            pa += b.pa
            outs += b.outs
            b1 += b.b1
            b2 += b.b2
            b3 += b.b3
            b4 += b.b4
            bb += b.bb
            ops += b.ops
        pa /= 9
        outs /= 9
        b1 /= 9
        b2 /= 9
        b3 /= 9
        b4 /= 9
        bb /= 9
        ops /= 9
        return Player(0, self.name, pa, b1, b2, b3, b4, bb, ops)
    

def loadData(team):
    """
    Loads team data from a csv file that contains 9 batters.
    :param team: the name of the csv file.
    :return: Team. The team contained in the given csv file.
    """
    with open('TeamData/AL/' + team + '.csv', newline='') as csvfile:
        datareader = csv.DictReader(csvfile)
        batters = []
        # For each batter, extract the information\n",
        for row in datareader:
            playerID = row['playerid']
            name = row['Name']
            b1 = int(row['1B'])
            b2 = int(row['2B'])
            b3 = int(row['3B'])
            b4 = int(row['HR'])
            bb = int(row['BB']) + int(row['IBB']) + int(row['HBP'])
            pa = int(row['AB']) + bb
            ops = float(row['OPS'])
            batters.append(Player(playerID, name, pa, b1, b2, b3, b4, bb, ops))
    return Team(team, batters, [])

