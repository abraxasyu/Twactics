class Team:
    def __init__(self,namein,colin,userin,tilelistin):
        self.name = namein
        self.col = colin
        self.users = [userin]
        self.numtiles = 0
        self.votes = 0
        self.attackable = tilelistin.keys()