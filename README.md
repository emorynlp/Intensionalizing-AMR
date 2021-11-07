# Intensionalizing-AMR

Accompanying code for Williamson et al. (2021). Intensionalizing Abstract Meaning Representations: Non-Veridicality and Scope. In _Proceedings of The Joint 15th Linguistic Annotation Workshop and 3rd Designing Meaning Representations Workshop_.

## Contents

- main.py : converts AMR penman.Graph objects into nltk.sem.logic.Expression objects.
- node_depth.py : uses penman.Graph.epidata to create tree information stored as a dictionary of triple-depth key-value pairs.
- translation_functions.py : contains multiple translation functions.
- World.py : defines the World class.
- Operators.py : defines Existential class, Universal class, and HigherOrder class for representing quantificational determiners. Defines Negation, And, Or classes for propositional negation and connectivs.
