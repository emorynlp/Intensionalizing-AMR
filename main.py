import penman
from World import World
from node_depth import node_depth
from translation_functions import *

"""
This script uses translation functions from translation_functions to recursively translate AMR penman.Graph objects
into nltk.sem.logic.Expression objects.
"""

if __name__ == '__main__':

    ex1 = '(a / admire-01 :ARG0 (b / boy) :ARG1 b))'
    ex2 = "(w / want-01 :ARG0 (b / boy) :content (b2 / believe-01 :ARG0 (g / girl) :content " \
          " (h / hope-01 :content (r / rain))))"
    ex3 = "(t / think-01 :ARG0 (b / boy) :content (h / hope-01 :ARG0 (g / girl) " \
          ":content (b2 / buy-01 :ARG0 g :ARG1 (v / violin))))"
    ex4 = '(o / or :op1 (r / rain) :op2 (a / and :op1 (s / snow) :op2 (s2 / sleet)))'
    ex5 = '(s / scope :ARG0 b :ARG1 g :pred (k / kiss :ARG0 (b / boy :quant every) :ARG1 (g / girl :quant some)))'
    ex6 = "(t / think-01 :ARG0 (b / boy) :content (s / scope :ARG0 v :pred (h / hope-01 :ARG0 (g / girl)" \
          " :content (b2 / buy-01 :ARG0 g :ARG1 (v / violin :quant a)))))"
    ex7 = "(s / scope :ARG0 t :ARG1 w :pred (t2 / touch :ARG0 (t / table :quant most) " \
          ":ARG1 (w / wall :quant exactly-one)))"

    for ex in [ex1, ex2, ex3, ex4, ex5, ex6, ex7]:
        print(f'[[ {ex} ]]')
        ex = ex.replace('-', r'_')
        g = penman.decode(ex)
        tree_depth = node_depth(g.epidata)
        graph = g.triples
        world = World()
        logicalForm = translation_function(graph, tree_depth, world, {})

        print('=', logicalForm)
        print('-' * 20)

