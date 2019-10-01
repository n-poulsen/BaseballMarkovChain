"""
Contains all classes and methods that define the states of a Baseball game as states
in a Markov Chain.
"""

def getID(first, second, third, outs, inning):
    """
    :returns: int. The stateID of the state described by the parameters.
    """
    return first + 2 * second + 4 * third + 8 * outs + 24 * (inning - 1)


class State:
    """
    Represents a state in the Markov Chain
    Can be seen as the tuple (f, s, t, o, i), where:
        f = 0 if first base is empty, 1 if there is a runner
        s = 0 if second base is empty, 1 if there is a runner
        t = 0 if third base is empty, 1 if there is a runner
        o in {0, 1, 2} the number of outs
        i in {1, 2, ..., 8, 9} the number of innings
    There is an extra state, which is the absorbing state, with 3 outs in the 9th inning, (0, 0, 0, 3, 9). 
    There are 217 total states, with IDs in [0, 216]. 
    Each state has a unique number, which is: (f + 2*s + 4*t + 8*o + 24*(i-1))
    """
    def __init__(self, stateID):
        self.id = stateID
        if stateID == 216:
            self.i = 9
            self.o = 3
            self.t = 0
            self.s = 0
            self.f = 0
        else:  
            self.i = (stateID // 24) + 1
            stateID -= (self.i - 1) * 24
            self.o = stateID // 8
            stateID -= self.o * 8
            self.t = stateID // 4
            stateID -= self.t * 4
            self.s = stateID // 2
            stateID -= self.s * 2
            self.f = stateID


    def walk(self):
        """
        :returns: (int, int). The stateID of the new state and number of runs scored when the game is in state self and the 
        batter walks, is intentionally walked or is hit by a pitch.
        """
        if self.f == 1:
            if self.s == 1:
                if self.t == 1:
                    return (getID(1, 1, 1, self.o, self.i), 1)
                else:
                    return (getID(1, 1, 1, self.o, self.i), 0)
            else:
                return (getID(1, 1, self.t, self.o, self.i), 0)
        else:
            return (getID(1, self.s, self.t, self.o, self.i), 0)


    def single(self):
        """
        :returns: (int, int). The stateID of the new state and number of runs scored when the game is in state self and the 
        batter hits a single.
        """
        return (getID(1, self.f, self.s, self.o, self.i), self.t)


    def double(self):
        """
        :returns: (int, int). The stateID of the new state and number of runs scored when the game is in state self and the 
        batter hits a double.
        """
        return (getID(0, 1, self.f, self.o, self.i), self.s + self.t)


    def triple(self):
        """
        :returns: (int, int). The stateID of the new state and number of runs scored when the game is in state self and the 
        batter hits a triple.
        """
        return (getID(0, 0, 1, self.o, self.i), self.f + self.s + self.t)


    def homeRun(self):
        """
        :returns: (int, int). The stateID of the new state and number of runs scored when the game is in state self and the 
        batter hits a home run.
        """
        return (getID(0, 0, 0, self.o, self.i), 1 + self.f + self.s + self.t)


    def out(self):
        """
        :returns: (int, int). The stateID of the new state and number of runs scored when the game is in state self and the 
        batter bats into an out.
        """
        if self.o == 2:
            # Tranistion to next inning
            return (getID(0, 0, 0, 0, self.i + 1), 0)
        else:
            return (getID(self.f, self.s, self.t, self.o + 1, self.i), 0)