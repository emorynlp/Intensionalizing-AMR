import penman
from World import World
from node_depth import node_depth
from translation_functions import *

"""
This script uses translation functions from translation_functions to recursively translate AMR penman.Graph objects
into nltk.sem.logic.Expression objects.
"""

if __name__ == '__main__':

    # reentrant node
    ex1 = "(a / admire-01 :ARG0 (b / boy) :ARG1 b))"  
    # :content role
    ex2 = "(w / want-01 :ARG0 (b / boy) :content (b2 / believe-01 :ARG0 (g / girl) :ARG1 b))"   
    # scope node
    ex3 = "(s / scope :ARG0 b :ARG1 b2 :pred (r / read-01 :ARG0 (b / boy :quant every) :ARG1 (b2 / book :quant some)))" 
    # intermediate scope
    ex4 = "(t / think-01 :ARG0 (b / boy) :content (s / scope :ARG0 v :pred (h / hope-01 :ARG0 (g / girl)" \
          " :content (b2 / buy-01 :ARG0 g :ARG1 (v / violin :quant a)))))"  
    # disjunction and conjunction
    ex5 = "(o / or :op1 (r / rain) :op2 (a / and :op1 (s / sun) :op2 (s2 / snow)))"  
    # wide scope negation
    ex6 = "(s / scope :ARG0 n :ARG1 g :pred (a / arrive-01 :ARG0 (g / girl :quant every) :polarity (n / -)))"  
    # higher-order quantifiers
    ex7 = "(s / scope :ARG0 t :ARG1 w :pred (t2 / touch :ARG0 (t / table :quant most) " \
          ":ARG1 (w / wall :quant exactly-one)))"   

    for ex in [ex1, ex2, ex3, ex4, ex5, ex6, ex7]:
        print(f'[[ {ex} ]]')
        ex = ex.replace('-', r'_')
        g = penman.decode(ex)
        tree_depth = node_depth(g.epidata)
        graph = g.triples
        world = World()
        store = {}
        logicalForm = translation_function(graph, tree_depth, world, store)

        print('=', logicalForm)
        print('-' * 20)



