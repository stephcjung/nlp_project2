"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        
        The grammar is valid if:
            1.  each rule corresponds to one of the formats permitted in CNF. This means:
                - valid nonterminal
                - RHS must either be 2 non-terminals or 1 terminal
                - assume language does not contain empty symbol
            2. ensure all probabilities for the same lhs symbol sum to 1.0 (approximately)
            
        """
        # TODO, Part 1
        
        for nonterm, rules in self.lhs_to_rules.items():
            #https://www.w3schools.com/python/ref_string_isupper.asp#:~:text=The%20isupper()%20method%20returns,not%20checked%2C%20only%20alphabet%20characters.
            #First check if the nonterminal is valid
            if not nonterm.isupper():
                return False
            probs = []
            for rule in rules:
                if rule[0]!=nonterm:
                    return False
                if len(rule[1])not in (1,2):
                    return False
                #check to make sure RHS is either one terminal
                if len(rule[1]) == 1 and rule[1][0].isupper():
                    return False
                #or if not, check to make sure RHS is two non-terminals
                if len(rule[1]) == 2 and not rule[1][0].isupper() and not rule[1][1].isupper():
                    return False
                #finally, check to make sure the probabilities sum to 1
                probs.append(rule[2])
            total_prob = fsum(probs)
            import math
            if not math.isclose(total_prob, 1.000):
                return False
        return True 


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        if (grammar.verify_grammar()):
            print("Grammar is a valid PCFG in CNF")
        else:
            print("WARNING: Grammar is NOT a valid PCFG in CNF!")
        
