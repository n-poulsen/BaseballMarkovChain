import numpy as np
import time
from baseballTeam import loadData
from baseballTeam import Team
from baseballPlayer import Player
from baseballMC import State, getID

teamsAL = ['angels', 'astros', 'athletics', 'bluejays', 'indians',\
           'mariners', 'orioles', 'rangers', 'rays', 'redsox', 'royals',\
           'tigers', 'twins', 'whitesox', 'yankees']

runsPerGame = [4.45, 4.92, 5.02, 4.38, 5.05,\
              4.18, 3.84, 4.55, 4.42, 5.41, 3.94,\
              3.89, 4.56, 4.05, 5.25]

def game(team1, team2):
    """
    Simulates a game between two baseball Teams, prints the probability that team1 wins,
        and returns the probability that the home team wins.
    :param team1: Team. The home baseball team in the baseball game.
    :param team2: Team. The away baseball team in the baseball game.
    :return: Float. The probability that the home team wins
    """
    lineup1 = formBestLineup(team1)
    lineup2 = formBestLineup(team2)
    expRun1 = expectedRuns(lineup1)
    expRun2 = expectedRuns(lineup2)
    p = 0
    for i in range(1, 21):
        for j in range(0, i):
            p += expRun1[i] * expRun2[j]
    print('\n\nProbability that '+team1.name+' beats '+team2.name+' is about '+str(round(100*p, 2))+'%.\n\n')
    return round(100*p, 2)


def expectedRuns(lineup):
    """
    Computes the expected run distribution of a given baseball lineup.
    :param lineup: [Batter]. List containing the 9 batters in the lineup, in order.
    :return: np.array. An array containing 21 elements. The i-th element is the probability
        that the lineup will score i runs.
    """
    transitionsMatrices = list(map(lambda Batter: Batter.transitionMatrixSimple(), lineup))
    return simulateMarkovChain(transitionsMatrices)[:, 216]


def simulateMarkovChain(transitionMatrices):
    """
    Finds the near-steady state distribution of the MC representing our baseball game.
    :param transitionMatrices: [numpy array]. List containing the 9 (217 by 217) transition matrices
        for the batters in the lineup, in order.
    :return: numpy 21x217 array. The i-th row in the array represents the states where i runs have been scored.
    """
    u = np.zeros((21, 217))
    u[0][0] = 1
    iterations = 0
    batter = 0
    while sum(u)[216] < 0.999 and iterations < 1000:
        p = transitionMatrices[batter]
        next_u = np.zeros((21, 217))
        for i in range(21):
            for j in range(5):
                if i - j >= 0:
                    next_u[i] += u[i-j] @ p[j]
        u = next_u
        batter = (batter + 1) % 9 
        iterations += 1
    return u


def formBestLineup(team):
    """
    Creates a nearly optimal batting order, by assigning the best and worst player to their best possible positions
        when all other players are average, and then the second best and second worst around them, etc... until all
        positions are filled.
    :param team: The team for which an optimal batting order is needed. Must contain 9 batters.
    :return: [Batter]. A list containing the 9 batters from the given team, in an order that is near-optimal with 
        regards to the expected number of runs scored.
    """
    players = list(map(lambda Batter: Batter.transitionMatrixSimple(), team.batters))
    averagePlayer = team.averagePlayer().transitionMatrixSimple()
    availablePositions = set(range(9))
    bestLineup = [team.averagePlayer()] * 9
    for bestRemaining in range(4):
        worstRemaining = 8 - bestRemaining
        # Expected runs, best placement, worst placement
        bestPerforming = (0, 0, 0)
        for bestPos in availablePositions:
            for worstPos in availablePositions:
                if bestPos != worstPos:
                    matrices = [averagePlayer] * 9
                    matrices[bestPos] = players[bestRemaining]
                    matrices[worstPos] = players[worstRemaining]
                    scoreDistribution = simulateMarkovChain(matrices)[:, 216]
                    expRuns = 0
                    for i in range(21):
                        expRuns += i * scoreDistribution[i]
                    if expRuns > bestPerforming[0]:
                        bestPerforming = (expRuns, bestPos, worstPos)
        availablePositions.remove(bestPerforming[1])
        availablePositions.remove(bestPerforming[2])
        bestLineup[bestPerforming[1]] = team.batters[bestRemaining]
        bestLineup[bestPerforming[2]] = team.batters[worstRemaining]
    bestLineup[availablePositions.pop()] = team.batters[4]
    return bestLineup


def formWorstLineup(team):
    """
    Creates a nearly optimally worst batting order, by assigning the best and worst player to their best possible positions
        when all other players are average, and then the second best and second worst around them, etc... until all
        positions are filled.
    :param team: The team for which an optimally worst batting order is needed. Must contain 9 batters.
    :return: [Batter]. A list containing the 9 batters from the given team, in an order that is near-optimally worst with 
        regards to the expected number of runs scored.
    """
    players = list(map(lambda Batter: Batter.transitionMatrixSimple(), team.batters))
    averagePlayer = team.averagePlayer().transitionMatrixSimple()
    availablePositions = set(range(9))
    worstLineup = [team.averagePlayer()] * 9
    for bestRemaining in range(4):
        worstRemaining = 8 - bestRemaining
        # Expected runs, best placement, worst placement
        worstPerforming = (10, 0, 0)
        for bestPos in availablePositions:
            for worstPos in availablePositions:
                if bestPos != worstPos:
                    matrices = [averagePlayer] * 9
                    matrices[bestPos] = players[bestRemaining]
                    matrices[worstPos] = players[worstRemaining]
                    scoreDistribution = simulateMarkovChain(matrices)[:, 216]
                    expRuns = 0
                    for i in range(21):
                        expRuns += i * scoreDistribution[i]
                    if expRuns < worstPerforming[0]:
                        worstPerforming = (expRuns, bestPos, worstPos)
        availablePositions.remove(worstPerforming[1])
        availablePositions.remove(worstPerforming[2])
        worstLineup[worstPerforming[1]] = team.batters[bestRemaining]
        worstLineup[worstPerforming[2]] = team.batters[worstRemaining]
    worstLineup[availablePositions.pop()] = team.batters[4]
    return worstLineup


def teamExpectedRuns(teamName, fileName):
    print('\nTeam: ' + teamName + '\n')
    team = loadData(fileName)
    start = time.time()
    lineup = formBestLineup(team)
    end = time.time()
    print('Lineup calculator time: ' + str(end - start))
    print('Best lineup found: ' + str(list(map(lambda Batter: Batter.name, lineup))) + '\n')
    u = expectedRuns(lineup)
    print('Probability of the game having ended: ' + str(sum(u)) + '\n')
    print('Probability of each score:')
    expRuns = 0
    for i in range(21):
        expRuns += i * u[i]
        print(str(i) + ': ' + str(u[i]))
    print('\nExpected number of runs: ' + str(expRuns) + '\n')
    return (u, expRuns)


def expectedRemainingRuns(lineup, batterUp, startState):
    """
    Computes the expected number of runs a team will score from a given point in a game.
    :param lineup: A list of 9 batters
    :param batterUp: An integer in [0, 8], representing whose turn to bat it is in the lineup
    :param startState: The state the game is in
    :return: The expected number of runs the team will score from startState.
    """
    transitionsMatrices = list(map(lambda Batter: Batter.transitionMatrixSimple(), lineup))
    u = np.zeros((21, 217))
    u[0][startState.id] = 1
    iterations = 0
    batter = batterUp
    while sum(u)[216] < 0.999 and iterations < 1000:
        p = transitionsMatrices[batter]
        next_u = np.zeros((21, 217))
        for i in range(21):
            for j in range(5):
                if i - j >= 0:
                    next_u[i] += u[i-j] @ p[j]
        u = next_u
        batter = (batter + 1) % 9 
        iterations += 1
    u = u[:, 216]
    expRuns = 0
    for i in range(21):
        expRuns += i * u[i]
    return expRuns


if __name__ == "__main__":
    runApp1 = True
    runApp2 = True
    runApp3 = True
    runApp4 = True
    
    # For all teams in the american league:
    #    Computing the expected run distribution
    #    Comparing Runs per Game to Expected Runs per Game
    #    Computing average error
    if runApp1:
        print('\n######################\nApplication 1: Computing expected run distributions\n######################\n')
        error = 0
        for i in range(15):
            teamName = teamsAL[i]
            (dist, expRuns) = teamExpectedRuns(teamName, teamName)
            error += (runsPerGame[i] - expRuns)
        print('Average error: ' + str(error/15))

    # Finding the best and worst lineup for each team, and comparing them
    if runApp2:
        print('\n######################\nApplication 2: Finding Optimal Lineups\n######################\n')
        difference = 0
        maxDifference = 0
        for i in range(15):
            teamName = teamsAL[i]
            print('\nTeam name: ' + teamName)
            team = loadData(teamName)
            bestLineup = formBestLineup(team)
            worstLineup = formWorstLineup(team)
            u = expectedRuns(bestLineup)
            v = expectedRuns(worstLineup)
            expRunsBest = 0
            expRunsWorst = 0
            for i in range(21):
                expRunsBest += i * u[i]
                expRunsWorst += i * v[i]
            print('\nBest expected number of runs: ' + str(expRunsBest) + '\n')
            print('\nWorst expected number of runs: ' + str(expRunsWorst) + '\n')
            diff = expRunsBest - expRunsWorst
            if diff > maxDifference:
                maxDifference = diff
            difference += diff
        difference /= 15
        print('Average difference: ' + str(difference))
        print('Max difference: ' + str(maxDifference))

    # Determining expected number of runs scored with or without a stolen base
    if runApp3:
        print('\n######################\nApplication 3: Stolen bases\n######################\n')
        angels = loadData('angels')
        angelsLineup = formBestLineup(angels)
        print('Best lineup found: ' + str(list(map(lambda Batter: Batter.name, angelsLineup))) + '\n')
        expNo = expectedRemainingRuns(angelsLineup, 1, State(getID(1, 0, 0, 0, 9)))
        expSucc = expectedRemainingRuns(angelsLineup, 1, State(getID(0, 1, 0, 0, 9)))
        expFail = expectedRemainingRuns(angelsLineup, 1, State(getID(0, 0, 0, 1, 9)))
        print('With Mike Trout on first base:')
        print('Expected runs without stealing: ' + str(expNo))
        print('Expected runs with a successfull steal: ' + str(expSucc))
        print('Expected runs with a failed steal: ' + str(expFail))

        expNo = expectedRemainingRuns(angelsLineup, 0, State(getID(1, 0, 0, 0, 9)))
        expSucc = expectedRemainingRuns(angelsLineup, 0, State(getID(0, 1, 0, 0, 9)))
        expFail = expectedRemainingRuns(angelsLineup, 0, State(getID(0, 0, 0, 1, 9)))
        print('With Kole Calhoun on first base:')
        print('Expected runs without stealing: ' + str(expNo))
        print('Expected runs with a successfull steal: ' + str(expSucc))
        print('Expected runs with a failed steal: ' + str(expFail))

    # Computing the effect of changing a player in the lineup to the expected number of runs
    if runApp4:
        print('\n######################\nApplication 4: Player replacement\n######################\n')
        (dist, expRuns) = teamExpectedRuns('Boston Red Sox, with J.T. Realmuto', 'redsoxJT')
        (dist, expRuns) = teamExpectedRuns('Houston Astros with Mookie Betts', 'astrosMookie')