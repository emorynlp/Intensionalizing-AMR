from nltk.sem.logic import Expression
sem = Expression.fromstring


class Existential:

    def __init__(self, lf):
        self.semantics = sem(f'\\P Q w.(exists x.(P(x,w) & Q(x,w)))')
        self.evaluate = self.semantics(lf).simplify()


class Universal:

    def __init__(self, lf):
        self.semantics = sem(f'\\P Q w.(all x.(P(x,w) -> Q(x,w)))')
        self.evaluate = self.semantics(lf).simplify()


class HigherOrder:

    def __init__(self, lf, quantifier):
        self.semantics = sem(f'\\P Q w.({quantifier}(\\x. P(x,w),\\x. Q(x,w)))')
        self.evaluate = self.semantics(lf).simplify()


class Negation:

    def __init__(self):
        self.semantics = sem(r'\P w. -P(w)')

    def apply(self, lf):
        return self.semantics(lf).simplify()


class And:

    def __init__(self, lf1, lf2):
        self.semantics = sem(r'\P Q w.(P(w) & Q(w))')
        self.evaluate = self.semantics(lf1, lf2)


class Or:

    def __init__(self, lf1, lf2):
        self.semantics = sem(r'\P Q w.(P(w) | Q(w))')
        self.evaluate = self.semantics(lf1, lf2)

