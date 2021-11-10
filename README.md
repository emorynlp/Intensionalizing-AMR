# Intensionalizing-AMR

Accompanying code for Williamson et al. (2021). Intensionalizing Abstract Meaning Representations: Non-Veridicality and Scope. In _Proceedings of The Joint 15th Linguistic Annotation Workshop and 3rd Designing Meaning Representations Workshop_.

## Contents `translation-scripts`

- main.py : converts AMR penman.Graph objects into nltk.sem.logic.Expression objects.
- node_depth.py : uses penman.Graph.epidata to create tree information stored as a dictionary of triple-depth key-value pairs.
- translation_functions.py : contains translation functions.
- World.py : defines the World class.
- Operators.py : defines Existential class, Universal class, and HigherOrder class for representing quantificational determiners. Defines Negation, And, Or classes for propositional negation and connectives.

## Contents `conversion-script`
- convert_content_role.py : converts AMR :ARG-roles under intensional contexts to `:content` role.
     - Mega-veridical verbs are extracted from the MegaVeridicality Project v1 (http://megaattitude.io/projects/mega-veridicality/)
     - Reference: White, Aaron Steven, and Kyle Rawlins. 2018. The Role of Veridicality and Factivity in Clause Selection. In _Proceedings of the 48th Annual Meeting of the North East Linguistic Society_, edited by Sherry Hucklebridge and Max Nelson, 221–234. Amherst, MA: GLSA Publications.


