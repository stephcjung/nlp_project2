"""
COMS W4705 - Natural Language Processing - Spring 2024
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Professor Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        
        #first, create table (a list of lists)
        length = len(tokens)
        table = []
        for x in range(length+1):
            table.append([])
            for y in range(length+1):
                table[x].append([])
                
        #fill diagonals with list of nonterminals (LHS of rules where token is RHS)
        for i in range(length):
            if (tokens[i],) in self.grammar.rhs_to_rules:
                for rule in self.grammar.rhs_to_rules:
                    table[i][i+1].append(rule[0])
        
        #check all combinations
        for z in range(2, length+1):
            for i in range(0, length-z+1):
                j = i+z
                for k in range(i+1, j):
                    B = table[i][k]
                    C = table[k][j]
                                
                    for rhs, rules in self.grammar.rhs_to_rules.items():
                        if (len(rhs) == 2 and rhs[0] in B and rhs[1] in C):
                            for rule in rules:
                                table[i][j].extend(rule[0])
        
        return self.grammar.startsymbol in table[0][length]

       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        table= {}
        probs = {}
        
        #create table
        length = len(tokens)
        for x in range(length+1):
            for y in range(length+1):
                table[(x,y)] = {}
                probs[(x,y)] = {}
                
        #fill diagonals with list of nonterminals (LHS of rules where token is RHS)
        for i in range(length):
            if (tokens[i],) in self.grammar.rhs_to_rules:
                for rule in self.grammar.rhs_to_rules[(tokens[i],)]:
                    #only look at rules whose rhs begins with the terminal
                    table[(i, i+1)][rule[0]] = rule[1][0]           #this assigns the diagonals the backpointer of the terminal (consider like base case)
                    probs[(i, i+1)][rule[0]] = math.log2(rule[2])   #this assigns the diagonals their initial log probability
        
        #check all combinations
        for z in range(2, length+1):
            for i in range(0, length-z+1):
                j = i+z
                for k in range(i+1, j):
                    B = table[(i, k)]
                    C = table[(k, j)]
                                
                    for rhs, rules in self.grammar.rhs_to_rules.items():
                        if (len(rhs) == 2 and rhs[0] in B and rhs[1] in C):
                            for rule in rules:
                                #table[i][j].extend(rule[0])
                                #if the new probability is the highest, replace current backpointer with this backpointer
                                
                                #first, get probability with this split
                                #we're using log probabilities so do sum, not product sum
                                new_prob = math.log2(rule[2]) + probs[(i,k)][rhs[0]] + probs[(k,j)][rhs[1]]
                                #if there's no current probability, or if the new probability is greater than what's already there:
                                #note, rule[0] is the lhs nonterminal
                                if (rule[0] not in probs[(i,j)] or new_prob>probs[(i,j)][rule[0]]):
                                    #insert in the new prob 
                                    probs[(i,j)][rule[0]] = new_prob
                                    #and insert the backpointer: (B,C) where A-> BC
                                    # B is rhs[0] and C is rhs[1]
                                    table[(i,j)][rule[0]] = ((rhs[0],i,k),(rhs[1],k,j))
        
        return table, probs


def get_tree(chart, i, j, nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    #base case:
    if (j == i+1):
        return (nt, chart[(i,j)][nt])
    
    left_nt = chart[(i,j)][nt][0][0]
    left_i = chart[(i,j)][nt][0][1]
    left_j = chart[(i,j)][nt][0][2]
    
    right_nt = chart[(i,j)][nt][1][0]
    right_i = chart[(i,j)][nt][1][1]
    right_j = chart[(i,j)][nt][1][2]
    
    return (nt, get_tree(chart, left_i, left_j, left_nt), get_tree(chart, right_i, right_j, right_nt)) 
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        
