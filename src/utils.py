class Coordinate:
    def __init__(self, x=0, y=0):
        if type(x) != int or type(y) != int:
            raise ValueError

        self.x = x
        self.y = y
