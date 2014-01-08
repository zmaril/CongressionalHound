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
        if l['in_office'] == '1':
            legislators[l['firstname']+l['lastname']]=Legislator(l)
            if l['nickname'] != '':
                legislators[l['nickname']+l['lastname']]=Legislator(l)

def CQ(word):
    return word[0] in string.ascii_uppercase

def find_legislators(string):
    mentioned = []
    tokens = nltk.word_tokenize(string)
    for i in range(0,len(tokens)-1):
        tn = tokens[i]
        tf = tokens[i+1]
        if CQ(tn) and CQ(tf) and tn+tf in legislators:
          mentioned.append(legislators[tn+tf])
    return list(set(mentioned))
