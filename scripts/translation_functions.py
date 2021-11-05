from nltk.sem.logic import LambdaExpression, ExistsExpression
from Operators import *

sem = Expression.fromstring


def translation_function(graph, tree_depth, world, store):

    free = set()
    triple_index = 0

    graph, store = quant_store(graph, tree_depth, world, store)
    graph, store = neg_store(graph, store)

    # Translate root
    logical_form, free, triple_index = translate(graph, free, tree_depth, triple_index, world, store)

    # Translate remaining graph and iteratively join with prop_and
    while triple_index < len(graph):
        lf, free, triple_index = translate(graph, free, tree_depth, triple_index, world, store)

        logical_form = And(logical_form, lf).evaluate

    logical_form, store = close(logical_form, free, world, store)

    return logical_form


def translate(graph, free, tree_depth, triple_index, world, store):

    triple = graph[triple_index]

    if triple[2] == 'scope':
        lf, store, triple_index = scope_assignment(graph, tree_depth, triple_index, world, store)
    elif triple[2] == 'and':
        lf, triple_index = conjunction(graph, tree_depth, triple, world, store)
    elif triple[2] == 'or':
        lf, triple_index = disjunction(graph, tree_depth, triple, world, store)
    elif triple[1] == ':content':
        lf, triple_index = cont_assignment(graph, tree_depth, triple_index, world, store)
    elif triple[1] == ':instance':
        lf, free = instance_assignment(triple, free)
        triple_index += 1
    else:
        lf = role_assignment(triple)
        triple_index += 1

    return lf, free, triple_index


def instance_assignment(triple, free):
    lf = sem(f'{triple[2]}({triple[0]})')
    var = sem(triple[0])
    free.add(var)
    return lf, free


def role_assignment(triple):
    lf = sem(f'{triple[1][1:]}({triple[0]},{triple[2]})')
    return lf


def cont_assignment(graph, tree_depth, triple_index, world, store):

    triple = graph[triple_index]
    content_lf, triple_index = translate_subgraph(graph, tree_depth, triple_index, world, store)
    world.increase()
    lf = sem(f'cont({triple[0]},{content_lf})')
    return lf, triple_index


def disjunction(graph, tree_depth, triple, world, store):

    disjuncts = [x for x in graph if (x[0] == triple[0]) & (':op' in x[1])]

    disjunct1_index = graph.index(disjuncts[0])
    disjunction_lf, triple_index = translate_subgraph(graph, tree_depth, disjunct1_index, world, store)

    for remaining_triple in disjuncts[1:]:
        disjunct_index = graph.index(remaining_triple)
        disjunct, triple_index = translate_subgraph(graph, tree_depth, disjunct_index, world, store)
        disjunction_lf = Or(disjunction_lf, disjunct).evaluate

    return disjunction_lf, triple_index


def conjunction(graph, tree_depth, triple, world, store):

    conjuncts = [x for x in graph if (x[0] == triple[0]) & (':op' in x[1])]

    conjunct1_index = graph.index(conjuncts[0])
    conjunction_lf, triple_index = translate_subgraph(graph, tree_depth, conjunct1_index, world, store)

    for remaining_triple in conjuncts[1:]:
        conjunct_index = graph.index(remaining_triple)
        conjunct, triple_index = translate_subgraph(graph, tree_depth, conjunct_index, world, store)
        conjunction_lf = And(conjunction_lf, conjunct).evaluate

    return conjunction_lf, triple_index


def translate_subgraph(graph, tree_depth, triple_index, world, store):

    subgraph = []
    triple = graph[triple_index]
    triple_index += 1

    for remaining_triple in graph[triple_index:]:
        if tree_depth[remaining_triple] <= tree_depth[triple]:
            break
        else:
            subgraph.append(remaining_triple)
            triple_index += 1

    subgraph_lf = translation_function(subgraph, tree_depth, world, store)

    return subgraph_lf, triple_index


def close(lf, free, world, store):

    world_var = sem(f'{world}')
    truth_conditions = lf(world_var).simplify()  # Apply proposition to world variable

    free -= set([x for x in store])

    for var in free:
        truth_conditions = ExistsExpression(var.variable, truth_conditions)     # Existentially close

    lf = LambdaExpression(world_var.variable, truth_conditions)  # abstract over world variable

    return lf, store


def neg_store(graph, store):

    for triple in graph:
        if triple[1] == ':polarity':
            var = sem(triple[2])
            graph.remove(triple)
            neg = Negation()
            store[var] = neg

            for triple2 in graph:
                if triple2[0] == triple[2]:
                    graph.remove(triple2)

    return graph, store


def quant_store(graph, tree_depth, world, store):

    for triple in graph:
        if triple[1] == ':quant':
            var = triple[0]

            # Find triple and index for start of restrictor argument
            for triple2 in graph:
                if (triple2[0] == var) & (triple2[1] == ':instance'):
                    restrictor = triple2
                    i_restrictor = graph.index(restrictor)
                    break

            # Build restrictor subgraph by iterating through remaining triples, if tree_depth < triple, break
            subgraph = []
            for remaining_triple in graph[i_restrictor:]:
                if tree_depth[remaining_triple] < tree_depth[restrictor]:
                    break
                else:
                    subgraph.append(remaining_triple)

            # Remove generalized quantifiers from the graph
            for sub_triple in subgraph:
                graph.remove(sub_triple)

            # Translate generalized quantifiers
            to_translate = [x for x in subgraph if x[1] != ':quant']
            var = sem(var)
            store[var] = '_'    # This place holder keeps the variable in the store while the restrictor lf built
            restrictor_lf = translation_function(to_translate, tree_depth, world, store)

            # Store GQ in store
            lambda_exp = LambdaExpression(var.variable, restrictor_lf)

            if triple[2] in ['some', 'a', 'an', 'exists']:
                existential = Existential(lambda_exp)
                gq = existential.evaluate
            elif triple[2] in ['every', 'each', 'all']:
                universal = Universal(lambda_exp)
                gq = universal.evaluate
            else:
                higher = HigherOrder(lambda_exp, triple[2])
                gq = higher.evaluate
            store[var] = gq

    return graph, store


def scope_assignment(graph, tree_depth, triple_index, world, store):

    scope_node_var = graph[triple_index][0]
    scope_order = []

    # order GQs (in case not in order)
    for triple in [x for x in graph if (x[0] == scope_node_var) & (':ARG' in x[1])]:
        scope_order.append(triple)

    scope_order.sort(key=lambda x: x[1], reverse=True)

    # translate the :pred argument
    for triple in [x for x in graph if (x[0] == scope_node_var) & (x[1] == ':pred')]:
        pred_index = graph.index(triple)
        lf, triple_index = translate_subgraph(graph, tree_depth, pred_index, world, store)

    # pop GQs from store
    for triple in scope_order:
        var = sem(triple[2])
        if isinstance(store[var], Negation):
            neg = store[var]
            lf = neg.apply(lf)
        else:
            gq = store.pop(var)
            scope = LambdaExpression(var.variable, lf)
            lf = gq(scope).simplify()

    return lf, store, triple_index

