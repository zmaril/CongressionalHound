import csv 
import nltk 
import string

legislators = {}

class Legislator:
    def __init__(self,dict):
        self.d=dict 
    def __hash__(self):
        return hash(self.d['bioguide_id'])
    def __str__(self):
        return "Legislator: "+self.d['firstname']+self.d['lastname']

with open("legislators.csv","rb") as csvfile:
    for l in csv.DictReader(csvfile):
        if l['in_office'] == '1' and not (l['firstname'] == "Adam" and l['lastname'] == "Smith"):
            legislators[l['firstname']+l['lastname']]=Legislator(l)
            if l['nickname'] != '':
                legislators[l['nickname']+l['lastname']]=Legislator(l)
            if (l['firstname'] == "Sheila" and l['lastname'] == "Jackson Lee"):
                legislators["SheilaJackson"] = l
                legislators["JacksonLee"]    = l
def CQ(word):
    return word[0] in string.ascii_uppercase

def find_legislators(tokens):
    #TODO Mark S. Kirk doesn't hit. Filter out tokens that are 1/2 long? 
    mentioned = []
    for i in range(0,len(tokens)-1):
        tn = tokens[i]
        tf = tokens[i+1]
        if CQ(tn) and CQ(tf) and tn+tf in legislators:
          mentioned.append(legislators[tn+tf])
    uniqued = list(set(mentioned))
    return sorted(uniqued,key=lambda x: x.d['lastname'])
