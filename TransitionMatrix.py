import sys
import numpy as np
from scipy.optimize import minimize
# States: 
# State 0: Easy 
# State 1: Medium
# State 2: Hard
# Given a difficulty level 0-100, design a transition matrix that
# gives the probability of moving from one state (e.g. medium)
# to another (e.g. easy)
# Difficulty of 0 means stay in the easy state
# Difficulty of 50 gives a round robin, states 0,1,2,0,1,2, etc
# Difficulty of 100 means stay in the hard state

def get_matrix(level):
    if int(level) > 100 or int(level) < 0:
        print("Invalid level 0-100")
        sys.exit(1)

    level = int(level)

    if level >= 50:
        # First row, Row #0
        A = np.array([[0.5, 1.0],
                      [1.0, 1.0]])
        y = np.array([level, 100])
        n = len(y)
        #x = np.linalg.solve(A, y)
        #x = np.insert(x, 0, [0]) 


        fun = lambda x: np.linalg.norm(np.dot(A,x)-y)
        # xo = np.linalg.solve(A,b)
        # sol = minimize(fun, xo, method='SLSQP', constraints={'type': 'ineq', 'fun': lambda x:  x})
        sol = minimize(fun, np.zeros(n), method='L-BFGS-B', bounds=[(0.,None) for x in range(n)])

        x = sol['x'] 
        x = np.insert(x, 0, [0]) 
        row_0 = x.round(2)

        #print("Row #0:")
        #print(row_0)
        #print("Row #1:")
        row_1 = np.array([0.0,0.0,100.0])
        #print(row_1)        

        # Last row, Row #2
        # Easy is a parabola passing through (0.5, 1.0), (0.75, .2), (1.0, 0)
        # Hard is exponential grown (0.5, 0.0), (0.75, .2), (1.0, 1.0)
        # So Medium is a parabola such that the sum of all three of the above = 1 at any point
        level *= .01
        easy = (24/5)*level**2 - (46/5)*level + (22/5)
        hard = (24/5)*level**2 - (26/5)*level + (7/5)
        medium = 1 - (easy+hard)
        row_2 = np.array([easy, medium, hard])
        row_2 = np.round(row_2, 2) 
        row_2 = np.clip(row_2, 0, 1)
        row_2 *= 100
              
        #print("Row #2:")
        #print(row_2)

    else:
        # First row, Row #0
        A = np.array([[0.0, 0.5],
                      [1.0, 1.0]])
        y = np.array([level, 100])
        n = len(y)
        #x = np.linalg.solve(A, y)
        #x = np.insert(x, 0, [0]) 


        fun = lambda x: np.linalg.norm(np.dot(A,x)-y)
        # xo = np.linalg.solve(A,b)
        # sol = minimize(fun, xo, method='SLSQP', constraints={'type': 'ineq', 'fun': lambda x:  x})
        sol = minimize(fun, np.zeros(n), method='L-BFGS-B', bounds=[(0.,None) for x in range(n)])

        x = sol['x'] 
        x = np.insert(x, 2, [0]) 
        row_0 = x.round(2)

        #print("Row #0:")
        #print(row_0)
        #print("Row #1:")
        #print(row_1)        

        # Last row, Row #2
        # Easy is a parabola passing through (0.5, 1.0), (0.75, .2), (1.0, 0)
        # Hard is exponential grown (0.5, 0.0), (0.75, .2), (1.0, 1.0)
        # So Medium is a parabola such that the sum of all three of the above = 1 at any point
        level *= .01
        easy = (24/5)*level**2 - (22/5)*level + 1
        hard = (24/5)*level**2 - (2/5)*level 
        medium = 1 - (easy+hard)
        row_1 = np.array([easy, medium, hard])
        row_1 = np.round(row_1, 2) 
        row_1 = np.clip(row_1, 0, 1)
        row_1 *= 100
              
        #print("Row #2:")
        #print(row_2)        

        row_2 = np.array([100.0,0.0,0.0])

    matrix = np.matrix([row_0, row_1, row_2])
    print(matrix)
    return matrix

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <0-100>")
        sys.exit(1)
    get_matrix(sys.argv[1])