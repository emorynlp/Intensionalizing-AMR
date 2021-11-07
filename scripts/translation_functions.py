from nltk.sem.logic import LambdaExpression, ExistsExpression
from Operators import *

sem = Expression.fromstring


def translation_function(graph, tree_depth, world, store):
    free = set()
    triple_index = 0

    # handle quantifiers and negation
    graph, store = handle_quantifiers(graph, tree_depth, world, store)
    graph, store = handle_negation(graph, store)

    # translate root
    logical_form, triple_index = translation_step(graph, free, tree_depth, triple_index, world, store)

    # translate remaining graph and iteratively and join using And
    while triple_index < len(graph):
        lf, triple_index = translation_step(graph, free, tree_depth, triple_index, world, store)
        logical_form = And(logical_form, lf).evaluate

    # return closed logical form
    return close(logical_form, free, world, store)


def translation_step(graph, free, tree_depth, triple_index, world, store):
    triple = graph[triple_index]
    lf, triple_index = \
        scope_assignment(graph, tree_depth, triple_index, world, store) if triple[2] == 'scope' else \
        conjunction(graph, tree_depth, triple, world, store) if triple[2] == 'and' else \
        disjunction(graph, tree_depth, triple, world, store) if triple[2] == 'or' else \
        content_assignment(graph, tree_depth, triple, world, store) if triple[1] == ':content' else \
        (instance_assignment(triple, free), triple_index + 1) if triple[1] == ':instance' else \
        (role_assignment(triple), triple_index + 1)
    return lf, triple_index


def instance_assignment(triple, free):
    var = sem(triple[0])
    pred = sem(triple[2])
    free.add(var)
    return pred(var)


def role_assignment(triple):
    rel = sem(triple[1][1:])
    var1 = sem(triple[0])
    var2 = sem(triple[2])
    return rel(var1, var2)


def content_assignment(graph, tree_depth, triple, world, store):
    var = sem(triple[0])
    cont_rel = sem(triple[1][1:])

    # translate propositional scope of :content role
    content_lf, triple_index = translate_subgraph(graph, tree_depth, graph.index(triple), world, store)

    world.increase()
    return cont_rel(var, content_lf), triple_index


def disjunction(graph, tree_depth, triple, world, store):
    disjuncts = [trip for trip in graph if (trip[0] == triple[0]) & (':op' in trip[1])]

    # translate first disjunct
    disjunct1_index = graph.index(disjuncts[0])
    disjunction_lf, triple_index = translate_subgraph(graph, tree_depth, disjunct1_index, world, store)

    # iteratively combine remaining disjuncts with Or
    for remaining_triple in disjuncts[1:]:
        disjunct_index = graph.index(remaining_triple)
        disjunct, triple_index = translate_subgraph(graph, tree_depth, disjunct_index, world, store)
        disjunction_lf = Or(disjunction_lf, disjunct).evaluate

    return disjunction_lf, triple_index


def conjunction(graph, tree_depth, triple, world, store):
    conjuncts = [trip for trip in graph if (trip[0] == triple[0]) & (':op' in trip[1])]

    # translate first conjunct
    conjunct1_index = graph.index(conjuncts[0])
    conjunction_lf, triple_index = translate_subgraph(graph, tree_depth, conjunct1_index, world, store)

    # iteratively combine remaining conjuncts with And
    for remaining_triple in conjuncts[1:]:
        conjunct_index = graph.index(remaining_triple)
        conjunct, triple_index = translate_subgraph(graph, tree_depth, conjunct_index, world, store)
        conjunction_lf = And(conjunction_lf, conjunct).evaluate

    return conjunction_lf, triple_index


def translate_subgraph(graph, tree_depth, triple_index, world, store):
    subgraph = []
    triple = graph[triple_index]
    triple_index += 1

    # build subgraph by iterating through remaining graph triples, if depth of remaining_triple <= triple, break
    for remaining_triple in graph[triple_index:]:
        if tree_depth[remaining_triple] <= tree_depth[triple]:
            break
        else:
            subgraph.append(remaining_triple)
            triple_index += 1

    # translate subgraph and return it
    return translation_function(subgraph, tree_depth, world, store), triple_index


def close(lf, free, world, store):

    # remove variables in store from free
    free -= set([x for x in store])

    # apply world variable to logical form
    world_var = sem(f'{world}')
    truth_conditions = lf(world_var).simplify()

    # existentially close variables from free
    for var in free:
        truth_conditions = ExistsExpression(var.variable, truth_conditions)

    # abstract over world variable in lf and return lf
    return LambdaExpression(world_var.variable, truth_conditions)


def handle_negation(graph, store):
    for triple in graph:
        if triple[1] == ':polarity':
            var = sem(triple[2])

            # remove negation from graph
            graph.remove(triple)

            # store negation
            store[var] = Negation()
    return graph, store


def handle_quantifiers(graph, tree_depth, world, store):

    for triple in graph:
        if triple[1] == ':quant':

            # build generalized quantifier subgraph
            subgraph = build_gq(graph, tree_depth, triple)

            # remove generalized quantifier from the graph
            [graph.remove(sub_triple) for sub_triple in subgraph]

            # translate restrictor
            var = sem(triple[0])
            restrictor_lf = translate_restrictor(subgraph, tree_depth, var, world, store)

            # create generalized quantifier lf
            determiner = triple[2]
            gq = gq_lf(restrictor_lf, var, determiner)

            # store generalized quantifier in store
            store[var] = gq

    return graph, store


def build_gq(graph, tree_depth, triple):

    subgraph = []

    # identify start of restrictor argument
    for triple2 in [trip for trip in graph if (trip[0] == triple[0]) & (trip[1] == ':instance')]:

        # build restrictor by iterating through remaining graph triples, if depth of remaining_triple < triple2, break
        for remaining_triple in graph[graph.index(triple2):]:
            if tree_depth[remaining_triple] < tree_depth[triple2]:
                break
            else:
                subgraph.append(remaining_triple)

    return subgraph


def translate_restrictor(subgraph, tree_depth, var, world, store):

    # keep var in store while restrictor lf is built (to avoid binding var in restrictor)
    store[var] = 'place_holder'

    to_translate = [trip for trip in subgraph if trip[1] != ':quant']
    return translation_function(to_translate, tree_depth, world, store)


def gq_lf(restrictor_lf, var, determiner):
    lambda_exp = LambdaExpression(var.variable, restrictor_lf)
    gq = \
        Existential(lambda_exp).evaluate if determiner in ['some', 'a', 'an', 'exists'] else \
        Universal(lambda_exp).evaluate if determiner in ['every', 'each', 'all'] else \
        HigherOrder(lambda_exp, determiner).evaluate
    return gq


def scope_assignment(graph, tree_depth, triple_index, world, store):
    scope_node_var = graph[triple_index][0]

    # order generalized quantifiers (in case not in order)
    scope_order = [triple for triple in graph if (triple[0] == scope_node_var) & (':ARG' in triple[1])]
    scope_order.sort(key=lambda x: x[1], reverse=True)

    # translate :pred argument
    lf, triple_index = translate_pred(graph, tree_depth, scope_node_var, world, store)

    # pop generalized quantifiers in order, iteratively applying them to lf
    for triple in scope_order:
        var = sem(triple[2])
        lf = pop_gqs(var, lf, store)

    return lf, triple_index


def translate_pred(graph, tree_depth, scope_node_var, world, store):
    for triple in graph:
        if (triple[0] == scope_node_var) & (triple[1] == ':pred'):
            return translate_subgraph(graph, tree_depth, graph.index(triple), world, store)


def pop_gqs(var, lf, store):
    if isinstance(store[var], Negation):
        neg = store.pop(var)
        return neg.apply(lf)
    else:
        gq = store.pop(var)
        scope = LambdaExpression(var.variable, lf)
        return gq(scope).simplify()
