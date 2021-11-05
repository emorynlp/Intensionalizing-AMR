import penman


def node_depth(epidata):
    """
    Uses penman epidata to determine node depth
    :param epidata: penman.Graph.epidata
    :return: dictionary {triple : depth} for triple in epidata where depth = depth of first node in triple
    """

    depth = 0
    tree_depth = {}

    for triple in epidata:
        tree_depth[triple] = depth
        if epidata[triple]:
            for stack_op in epidata[triple]:
                if isinstance(stack_op, penman.layout.Push):
                    depth += 1
                elif isinstance(stack_op, penman.layout.Pop):
                    depth -= 1
    return tree_depth

