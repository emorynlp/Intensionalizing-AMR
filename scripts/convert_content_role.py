import pandas as pd
import re
import penman
from penman import surface
from nltk.stem import WordNetLemmatizer
from nltk.parse.corenlp import CoreNLPParser

parser = CoreNLPParser()
lemmatizer = WordNetLemmatizer()

# Mega-veridicality verbs are extracted from the MegaVeridicality Project v1 (http://megaattitude.io/projects/mega-veridicality/)
# Reference: White, Aaron Steven, and Kyle Rawlins. 2018. The Role of Veridicality and Factivity in Clause Selection. In Proceedings of the 48th Annual Meeting of the North East Linguistic Society, edited by Sherry Hucklebridge and Max Nelson, 221–234. Amherst, MA: GLSA Publications.
attitude_verbs = list(pd.read_csv('megaveridicality-verb-list1.csv')['0'])

def get_parsed(snt):
    return next(parser.raw_parse(snt, verbose=False))


def get_treeLabels(tree, path):
    '''
    get the labels of the path to a tree node
    '''
    label = []
    for i in range(len(path)):
            label.append(tree[path[:i]].label())
    return label


def check_SBAR(tree, index):
    '''
    check if a verb is followed by a sentential complement
    :param tree: a dependency tree
    :param index: the index of the verb
    :return: BOOLEAN, True if it is followed by SBAR, False otherwise
    '''
    result = False
    path1 = tree.leaf_treeposition(index)[:-1]
    label1 = get_treeLabels(tree, path1)
    for i in range(index + 1, len(tree.leaves())):
        path2 = tree.leaf_treeposition(i)
        label2 = get_treeLabels(tree, path2)
        if label2[0:len(path1)] == label1:
            if 'SBAR' in label2:
                result = True
                break
    return result


def convert_content(snt, g):
    '''
    Conver the :ARG-role to :content role for attitude verbs used with sentential complements
    '''
    tree = get_parsed(snt) # get constituency tree
    triples = g.triples
    tokens = snt.split(" ")
    # obtain alignments
    alignments = surface.alignments(g)
    aligns = {}
    for align in alignments.keys():
        value = str(alignments[align])[1:]
        aligns[value] = align

    for i in range(len(tokens)):
        # check if the verb has intensional usage
        if lemmatizer.lemmatize(tokens[i], pos='v') in attitude_verbs:
            # check if there is an intensional context
            if check_SBAR(tree, i):
                # check if exist in alignment
                trip = aligns[str(i)] if str(i) in aligns.keys() else None
                if trip is None: continue
                # Check the arg role with intensional context
                arg_roles = [item for item in triples if item[0]==trip[0] and re.search(r":ARG[1-9]", item[1])]
                if len(arg_roles) == 1:
                    arg_role = arg_roles[0]
                elif len(arg_roles) > 1:
                    for k in arg_roles:
                        var = [item[2] for item in triples if item[0]==k[0] and item[1]==':instance'][0]
                        if re.search(r".+-\d+", var):
                            arg_role = k
                else:
                    continue
                # convert content role
                for j in range(len(triples)):
                    # if triples[j][0] == trip[0] and triples[j][1] == ':ARG1':
                    if triples[j] == arg_role:
                        triples[j] = list(triples[j])
                        triples[j][1] = ':content'
                        triples[j] = tuple(triples[j])
    print(penman.encode(g))

snt1 = 'The boy believes that a girl is sick .'
ex1 = '''
(b / believe-01~2
    :ARG0 (b2 / boy~1)
    :ARG1 (s / sick-05~6
        :ARG1 (g / girl~4)))
'''
g = penman.decode(ex1)
print('# Example 1: Intensional Operator \'believe\'')
print('# snt: %s \nBasic AMR:\n%s \nEnriched AMR:' % (snt1, penman.encode(g)))
convert_content(snt1, g)

snt2 = 'The boy believes the girl .'
ex2 = '''
(b / believe-01~2
    :ARG0 (b2 / boy~1)
    :ARG1 (g / girl~4)))
'''
g = penman.decode(ex2)
print('\n\n# Example 2: Non-Intensional context')
print('# snt: %s \nBasic AMR:\n%s \nEnriched AMR:' % (snt2, penman.encode(g)))
convert_content(snt2, g)

snt3 = 'The boy persuades the girl that the child is sick .'
ex3 = '''
(p / persuade-01~2
    :ARG0 (b / boy~1)
    :ARG1 (g / girl~4)
    :ARG2 (s / sick-05~9
        :ARG1 (c / child~7)))
'''
g = penman.decode(ex3)
print('\n\n# Example 3: Intensional Operator \'persuade\' that takes three :ARG-roles')
print('# snt: %s \nBasic AMR:\n%s \nEnriched AMR:' % (snt3, penman.encode(g)))
convert_content(snt3, g)

