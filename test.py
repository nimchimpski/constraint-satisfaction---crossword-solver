import sys
import copy
import time
from operator import itemgetter
from collections import deque
from crossword import *
from generate_comments import *


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    
    arcs = creator.getarcs(Variable(0,1, 'down', 5))
    
    
    print(f"---arc={arcs}")
    # print(f"---overlaps= {c.overlaps ,type(c.overlaps)}")
    # print(f"---overlap v= {c.overlaps[(Variable(0, 1, 'down', 5), Variable(0, 1, 'across', 3))]}")
    
    # print(f"---neighbors= {c.neighbors(Variable(0, 1, 'down', 5))}")
    
    # Print result
    # if assignment is None:
    #     print("No solution.")
    # else:
    #     creator.print(assignment)
    #     if output:
    #         creator.save(assignment, output)
    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"Elapsed time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()