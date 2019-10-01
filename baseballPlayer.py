import numpy as np
from baseballMC import State

class Player:
    """
    Represents a baseball player.
    """
    def __init__(self, playerID, name, pa, b1, b2, b3, b4, bb, ops):
        """
        :param playerID: int. A unique identifier for the player.
        :param name: string. The player's name.
        :param pa: int. The number of plate appearences for the player.
        :param b1: int. The number of singles hit by the player.
        :param b2: int. The number of doubles hit by the player.
        :param b3: int. The number of triples hit by the player.
        :param b4: int. The number of home runs hit by the player.
        :param bb: int. The number of walks, IBBs and HBPs for the player.
        :param ops: float. The player's ops.
        """
        self.id = playerID
        self.name = name
        self.pa = pa
        self.outs = pa - b1 - b2 - b3 - b4 - bb
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.b4 = b4
        self.bb = bb
        self.ops = ops

    def transitionMatrixSimple(self):
        """
        Computes the transition matrix for this player for the baseball MC.
        :return: numpy (217, 217) array. The transition matrix for this player.
        """
        # p[i]: the transition matrix when i runs score
        p = np.zeros((5, 217, 217))
        
        # Once a state with 9 innings and three outs is reached, it never changes again.
        p[0][216][216] = 1

        # Compute all the transition probabilities
        for i in range(216):
            # Current state
            currState = State(i)
            # If the batter gets walked
            (nextState, runs) = currState.walk()
            p[runs][i][nextState] += self.bb/self.pa
            # If the batter hits a single
            (nextState, runs) = currState.single()
            p[runs][i][nextState] += self.b1/self.pa
            # If the batter hits a double
            (nextState, runs) = currState.double()
            p[runs][i][nextState] += self.b2/self.pa
            # If the batter hits a triple
            (nextState, runs) = currState.triple()
            p[runs][i][nextState] += self.b3/self.pa
            # If the batter hits a home run
            (nextState, runs) = currState.homeRun()
            p[runs][i][nextState] += self.b4/self.pa
            # If the batter gets out
            (nextState, runs) = currState.out()
            p[runs][i][nextState] += self.outs/self.pa
        return p

