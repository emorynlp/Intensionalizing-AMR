

class World:
    def __init__(self):
        self.index = 1

    def __str__(self):
        return f'w0{self.index}'

    def increase(self):
        self.index += 1

