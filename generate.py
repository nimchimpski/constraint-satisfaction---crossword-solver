import sys
import copy
import time
from operator import itemgetter
from collections import deque

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """


        self.enforce_node_consistency()

     

        self.ac3()

      
        # print(f"\n///first ac3 finished\n")
        # for var in self.domains:
        #     print(f"---self.domains={var}={self.domains[var]}")

        # return {Variable(0,1, 'down', 5): 'cocks'}

     
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        """
        !!! change this to .remove() !!!
        """
        for var in self.domains:
            # print(f"+++{self.domains[var]}")
            # print(f">>>{var.length}")
            toremove = set()
            for value in self.domains[var]:
                if len(value) != var.length:
                    toremove.add(value)
            # print(f"---toremove= {toremove}")
            self.domains[var] -= toremove


        # print(f"---domains= {self.domains[Variable(0, 1, 'down', 5)]}")

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # print(f"\n+++IN REVISE FN")
        overlap =  self.crossword.overlaps[x,y]
        # print(f"---overlap= {overlap}")
        
        if overlap is None:
            return False
        else:
          

            toremove = set()
            ####   LOOP THRU WORDS FOR X - DO THEY HAVE A MATCH?
            for xdomain in self.domains[x]:
                wordfits = False
                for ydomain in self.domains[y]:
                    if wordfits == True:
                        break
                    # print(f"---x = {xdomain}")
                    # pri nt(f"---y = {ydomain}")
                    
                    if  self.checkwordsfit(x,xdomain, y, ydomain):
                        # print(f"---{xdomain} fits with {ydomain}")
                        wordfits = True
                # print(f"--wordfits={wordfits}")

                # ADD TO REMOVE SET
                if wordfits == False:
                    # print(f"---{xdomain} didnt find a match: added it to 'toremove' set ")
                    toremove.add(xdomain)

            if len(toremove) == 0:
                # print("---NO REVISION MADE")
                return False
            else:
                self.domains[x] -= toremove
                    
                # print(f"---***REVISION MADE to {x}. values now= {self.domains[x]}")
                return True
     
    def getarcs(self, fromvar=None, tovar=None, arcs=None):
        # print(f"+++IN GETARCS fromvar={fromvar} tovar={tovar}")
        arcs = []
        if tovar is not None:
            neighbors = self.crossword.neighbors(tovar)  
            for neighbor in neighbors:
                arc = (neighbor, tovar)
                if arc not in arcs:
                    arcs.append(arc)
                # print(f"---tovar arcs = {arcs}")
        elif fromvar is not None:
            # print(f"---from var is not None")
            neighbors = self.crossword.neighbors(fromvar)  
            # print(f"---neighbors={neighbors}")
            for neighbor in neighbors:
                arc = (fromvar, neighbor)
                if arc not in arcs:
                    arcs.append(arc)
                # print(f"---fromvar arcs = {arcs}")

        else:
            arcs.append((fromvar, tovar))
        # print(f"---getarcs FN returning = {arcs}")
        return arcs

        

    
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # print("\n+++IN AC3 FN")

        # CREATE A COMPLETE QUEUE IF THERE IS NONE
        if arcs == None:
            arcs = deque()
            # GET EACH VARIABLE
            for var in self.domains:
                # GET ALL NEIGHBORS
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    if (var, neighbor) not in arcs:
                        arcs += self.getarcs(var, neighbor)
              
        # print(f"---ac3 all arcs = {arcs}")

        # KEEP LOOPING THRU ARCS QUEUE TILL EMPTY
        while len(arcs) > 0:
            # print(f"\n---arcs length = {len(arcs)}")

        # ADD FILTER TO PRIORITIZE ARC WITH VAR WITH MOST NEIGHBORS ??????

            arc = arcs.popleft()
            revised =  self.revise(arc[0], arc[1])
   

            # IF REVISED, SEND RELATED ARCS TO QUEUE 
            if revised:

                # IF THE DOMAIN IS EMPTY RETURN FALSE
                if len(self.domains[arc[0]]) == 0:
                    return False
                
                # GET ALL ARCS POINTING TO ARC1[0], ADD THEM TO ARCS
                newarcs = self.getarcs(None, arc[0], arcs)
                # print(f"---newarcs1={newarcs}")

                # GET RID OF THE ARC WITH VAR WE JUST REVISED
                newarcs= [(x,y) for x,y in newarcs if (x,y) != ((arc[1],arc[0])) and (x,y) not in arcs]
                # print(f"---newarcs2={newarcs}")

                arcs += newarcs
                
                # print(f"---arcs= {arcs}")



        for var in self.domains:
            if not var:
                # print(f"---emprty var in ac3")
                return False
        return True
        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # print("\n+++in assignment_complete fn")
        # print(f"---assignment={assignment}")
        if not assignment:
            return False
        for var in self.domains:
            # print(f"---self.domains={self.domains}")
            # print(f"---var= {var}")
            # if a variable has no domains
            # print(f"---assignmnet={assignment}")
            if var not in assignment or self.domains[var] == None:
                # print(f"---not complete")
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # print("\n+++in consistent fn")
        # if self.assignment_complete(assignment) == False:
            # return False
         

        for var in assignment:
            # print(f"+++checking {var} in consistent fn")
            # 1 make sure theres only one word per variable
            # print(f"---checking this var ={var} = {assignment[var]}")
     

            #  2 CHECK all values are distinct
            uniquewords = set()
            for var2 in assignment:
                word = assignment[var2]
                if word in uniquewords:
                    # print(f"---{var2} is not unique from {var}")
                    return False
                uniquewords.add(word)


            #  3 CHECK every value is the correct length
            if len(assignment[var]) != var.length:
                # print("WORD WRONG LENGTH")
                return False
            

            #  4 CHECK There are no conflicts between neighboring variables.
            
            # print(f"---neighbors= {neighbors, type(neighbors)}")
            # print(f"---checking this var2 ={var} = {assignment[var]}")
            assigned_neighbors =  [neighbor for neighbor in self.crossword.neighbors(var) if neighbor in assignment]
            for assigned_neighbor in assigned_neighbors:
                 if not self.checkwordsfit(var, assignment[var], assigned_neighbor, assignment[assigned_neighbor]):
                    #  print(f"---{assignment[var]} and {assignment[assigned_neighbor]} didnt match")
                     return False


                
        # print(f"---consistent!")
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # print(f"+++order_domain_values")
        if var in assignment:
            # print(f"---var is in assignment={assignment[var], type(assignment[var])}")
            return assignment[var]
        else:
          

            # print(f"---considering >{var}<, not in assignment= ")
            # print(f"---neighborslist= {neighborslist}")            
            rankedwords = []
            # make a list of vars words
            # loop thru varswords:
            # print(f"\n---Loop vars words")

            for word in self.domains[var]:
                # print(f"\n---considering varsword {word}\n")
                ruledout = 0
                # make a list of neighbors

                # loop thru neighbors
                for neighbor in self.crossword.neighbors(var):
                    # print(f"---considering this neighbor= {neighbor}")
                    # loop thru neighbors words:
                    for neighborword in self.domains[neighbor]:
                        # print(f"\n---considering neighbor word= {neighborword}")

                        if not self.checkwordsfit(var, word , neighbor, neighborword):
                            ruledout += 1

                rankedwords.append((word, ruledout))
            # order the list
            # print(f"---rankedwords b4= {rankedwords}")

            rankedwords = sorted(rankedwords, key=lambda words : words[1])
            # print(f"---rankedwords= {rankedwords}")
            justwords = [x[0] for x in rankedwords]
            # print(f"---justwords= {justwords}")
            return justwords


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # print(f"+++ in select_unassigned_values")
        randomlist = []
        for var in self.domains:
            # print(f"---var = {var}")
            if var in assignment:
                # (print(f"--->{var}< is already in assignment"))
                continue
            # print(f"|||>{var}< is not in assignment")
            # print(f"---returning select_unassigned_variable= {var}")
            # count vars words
            # what is degree of each var
            
            numwordsrev = len(self.domains[var])
            numarcs = 1 - len(self.crossword.neighbors(var))
            randomlist.append((var, numwordsrev, numarcs))
        # print(f"---randomlist= {randomlist}")
        # return "STOP"
        sortedlist = sorted(randomlist, key=itemgetter(1,2))
        # print(f"---sortedlist= {sortedlist}")
        # print(f"returning={sortedlist[0][0]}")
        return sortedlist[0][0]

   
        
        


    ####     WITH AC3 INTERLEAVED
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # print(f'+++in backtrack: assignmnet ')
        self.print(assignment)
        time.sleep(.1)
        ######        if assignment complete:
        #########     return assignment
        if self.assignment_complete(assignment):
            # print(f"---assignment complete!")
            if self.consistent(assignment):
                return assignment
            else:
                # print(f"---assignment doesnt work")
                return None

        #####     choose a variable to fill
        var = self.select_unassigned_variable(assignment)
        # print(f"---selected var= {var}")
        
        ####      choose a  possible word from that variable
        for word in self.order_domain_values(var, assignment):
            '''
            # if word consistent with assignment:
            '''
            ####       check if word unique (ie. already in assignment?)
            # print(f"---word={word}")
            if word in assignment.values():
                # print(f"---word already used - skip!")
                continue

            ####           must fit with all neighbors in assignment
            wordfits = True
       
            for neighbor in self.crossword.neighbors(var):
                # print(f"--neighbor={neighbor}")
                # print(f"---assignment={assignment}")
                ####    neighbor must  be in assignment
                if neighbor not in assignment:
                    # print(f"---neighbor not in assignment")
                    continue
                ####    if we get to this point with False, BREAK TO NEXT vars'-word choice
                if wordfits == False:
                    break
                # print(f"---aneighbor in assignment={assignment[neighbor]}")
                # print(f"---matching {var, word, neighbor, assignment[neighbor]}")
                # print(f"!!!{assignment[neighbor]}")
                ####    IF WORD MATCHES THIS NEIGHBOR, GO TO NEXT NEIGHBOR
                if  self.checkwordsfit(var, word, neighbor, assignment[neighbor]):
                    # print(f"---checkwords OK")
                    continue
                else:
                    wordfits = False
                    # print(f"---checkwords failed")
                    break
                # add {var = value} to assignment

            ####     IF WORD MATCHED ALL ASSIGNED NEIGHBORS, ASSIGN IT
            if wordfits == True:
                # self.print(assignment)
                # print(f"---assignment b4={assignment}")
                assignment[var] = word
            else:
                continue
                '''
                # ADD AC3 HERE???
                '''
            ####     MAKE NEW QUEUE OF ALL ARCS. ONLY WHICH LINK TO VAR
            arcs = deque()
            for i in self.crossword.neighbors(var):
                arc = (i, var)
                arcs.append(arc)
            # print(F"---ARCS={arcs, type(arcs)}")
            ### UPDATE THE DOMAIN FOR VAR TEMPORARILY
            domainscopy = self.domains[var].copy()
            # print(f"---self.domains[var]={self.domains[var]}")
            # print(f"---domainscopy= {domainscopy}{type(domainscopy)}")
            self.domains[var] = {word}
            ###      UPDATE ALL ASSIGNED VARS NEIGHBORS IN SELF.DOMAINS 
            ####     WAS IT POSSIBLE?
            if self.ac3(arcs):
                #### CAN WE ASSIGN ANY NEW SINGLE DOMAINS?
                ###    MAKE ASSIGNMENT COPY IN CASE NEXT RECUR`SION FAILS
                assignmentcopy = assignment.copy()
                for key, value in self.domains.items():
                    # print(f"---key, value={key} {value}")
                    if len(value) == 1 and key not in assignment:
                        valuecopy = value.copy()
                        assignment[key] = valuecopy.pop()
                #### NEW VAR DOMAIN VALUE CAN REMAIN, RECURSE TO NEXT VAR
                result = self.backtrack(assignment)
                if (self.assignment_complete(result)) and (self.consistent(result)):
                    return result
                #### OTHERWISE THAT VARS' WORDS FAILED.  RESTORE DOMAINS[VAR], ASSIGNMENT AND DELETE ASSIGNED WORD LAST
                else:
                    # print(f"---deleting {var} from assignment")
                
                    # self.domains[var] = domainscopy
                    # print(f"---self.domains[var]2={self.domains[var]}")
                    assignment = assignmentcopy
                    del assignment[var]

                    
                    # assignment = assignmentcopy
        return None
        
        




    def checkwordsfit(self, var1, word1, var2, word2):
        # print(f"---types={type(var1), type(word1), type(var2), type(word2)}")
        # print(f"+++in checkwordsfit()")
        overlap = self.crossword.overlaps[var1, var2]
                # print(f"---overlap= {overlap}")
                # print(f"---overlap[1] = {overlap[1]}")
                # print(f'---len(neighorword= {len(neighborword)})')
        if (len(word1) < overlap[0]+1) or (len(word2) < overlap[1]+1):
            # print(f"---neighborword too short")
            return False
                # print(f"---neighborword[overlap[1]] = {neighborword[overlap[1]]}")
        if word1[overlap[0]] == word2[overlap[1]]:
            return True

    def wordcount(self, words, length):
        counter = 0
        for word in words:
            if len(word) == length:
                counter += 1

        return counter

def main():
    start_time = time.time()

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    # wordcount3 = creator.wordcount(crossword.words, 6)
    # print(f"///wordcount3 = {wordcount3}")
    # creator.enforce_node_consistency()

    '''
    chekk revise works
    '''
    # v1 = Variable(0, 1, 'across', 3)
    # print(f"///v1 = {v1, type(v1)}")
    # print(f"///domains for v1={creator.domains[v1]}")
    # neighbors = crossword.neighbors(v1)
    # print("///neighbors for v1= ",neighbors)
    # v2 = neighbors.pop()
    # print(f"///n1={v2}")
    # print(f"///domains for v2={creator.domains[v2]}")
    # creator.revise(v1,v2)
    # print(f"///domains for v1={creator.domains[v1]}")
    # creator.revise(v2,v1)
    # print(f"///domains for v2={creator.domains[v2]}")
    '''
    check ac3 works
    '''
    # v1 = Variable(0, 1, 'across', 3)
    # v2 = Variable(0,1, 'down', 5)
    # v3 = Variable(4,1, 'across', 4)
    # v4 = Variable(1,4, 'down', 4)
    # print(f"///original domains for v1={creator.domains[v1]}")
    # print(f"///originial domains for v2={creator.domains[v2]}")
    # print(f"///originial domains for v3={creator.domains[v3]}")
    # print(f"///originial domains for v4={creator.domains[v4]}")
    # arcs= [(v1, v2), (v2, v1), (v2, v3), (v3, v2), (v3,v4), (v4, v3)]
    # ac3test = creator.ac3()
    # print(f"///domains for v1={creator.domains[v1]}")
    # print(f"///domains for v2={creator.domains[v2]}")
    # print(f"///domains for v3={creator.domains[v3]}")
    # print(f"///domains for v4={creator.domains[v4]}")
    # print(f"///{ac3test}")
    '''
    check complete
    '''
    # print(f'///creator.domains= {creator.domains}')
    # assignment =  {Variable(0, 1, 'across' , 3): 'SIX' , Variable(1, 4, 'down', 4):  'FIVE' ,  Variable(4, 1, 'across', 4):  'NINE' }
    '''
    check consistent
    '''
    # print(f'///consistent = {creator.consistent(assignment)}')
    # print(f" ///assignment = {assignment}")
    # consistent = creator.consistent(assignment)
    # print(f'///consistent = {consistent}')
    '''
    check order_domain_values
    '''
    # orderdomains = creator.order_domain_values(Variable(0, 1, 'down', 5), assignment)
    # print(f"///orderdomains= {orderdomains}")
    '''
    check select_unassigned_variable
    '''
    # choice = creator.select_unassigned_variable(assignment)
    # print(f"///choice = {choice}")
    # print(f"///domains for v1={creator.domains[v1]}")
    # print(f"///domains for v2={creator.domains[v2]}")
    # print(f"///domains for v3={creator.domains[v3]}")
    # print(f"///domains for v4={creator.domains[v4]}")




   
    assignment = creator.solve()
    # print(f'///assigment= {assignment}')
    
    

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
  



if __name__ == "__main__":
    main()
