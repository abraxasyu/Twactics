from math import pi
class Tile:
    def __init__(self,name,position,vertices,neighbors):
        self.name=name
        self.position=position
        self.vertices=vertices
        self.neighbors=neighbors
        self.team=None
        self.votes={}
        self.weightedvotes={}
        self.arcvotes=[]

    #processing irc command to add vote
    def addvote(self,team,teamdict): #team is string
        if team in self.votes:
            self.votes[team]+=1
        else:
            self.votes[team]=1
        teamdict[team].votes+=1

    def updatevote(self,teamdict):
        self.weightedvotes={}
        totvote=0
        for team in self.votes:
            clout=(teamdict[team].numtiles or 1)
            self.weightedvotes[team]=self.votes[team]*clout/teamdict[team].votes
            totvote+=self.weightedvotes[team]
        curstart=0
        self.arcvotes=[]
        teamvotes=self.weightedvotes.copy()
        while len(teamvotes)>0:
            maxteam=None
            maxvote=0
            for team in teamvotes: #find the max team/vote
                if teamvotes[team]>maxvote:
                    maxteam=team
                    maxvote=teamvotes[team]
            end=curstart+maxvote/totvote*2*pi

            #self.arcvotes.append({'col':teamdict[maxteam].col,'start':curstart+pi/2,'end':end+pi/2})
            self.arcvotes.append({'col':teamdict[maxteam].col,'start':curstart+pi/2,'end':end+pi/2})
            curstart=end
            teamvotes.pop(maxteam)

    def teamchange(self):
        maxvote=0
        maxvote2=0
        maxteam=None
        for team in self.weightedvotes:
            if self.weightedvotes[team]>=maxvote:
                maxteam=team
                maxvote2=maxvote
                maxvote=self.weightedvotes[team]
        if (maxvote2==maxvote):
            maxteam=None
        if maxteam!=self.team:
            return(maxteam)

    #figure out team based on votes
    def resolvevote(self):
        maxvote=0
        maxvote2=0
        maxteam=None
        for team in self.weightedvotes:
            if self.weightedvotes[team]>=maxvote:
                maxteam=team
                maxvote2=maxvote
                maxvote=self.weightedvotes[team]
        if (maxteam is not None) and (maxvote2!=maxvote):
            self.team=maxteam
        self.votes={}
        self.arcvotes=[]