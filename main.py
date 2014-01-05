import nltk
import urllib2
import csv 

legislators = []

with open("legislators.csv","rb") as csvfile:
    legislators.extend(list(csv.DictReader(csvfile)))

example = "http://www.theguardian.com/world/2014/jan/03/nsa-asked-spying-congress-bernie-sanders" 

badwords = ("Google", "Tweet", "Jump","Apple","Kindle","Digital","Courts","Guardian","Tech","News","Sport","Share","Film","Click")

def get_raw(url):
    return nltk.clean_html(urllib2.urlopen(url).read())

# Kay Hagan doesn't get picked up from here:
# http://dailycaller.com/2013/12/18/senate-dems-block-amendment-to-restore-veteran-benefits-by-closing-illegal-immigrant-welfare-loophole/

def find_legislators(string):
    persons = []
    tokens = nltk.word_tokenize(string)
    tags = nltk.pos_tag(tokens)
    entities = nltk.ne_chunk(tags)
    for e in entities:
        if type(e) is nltk.Tree and e.node == 'PERSON':
            name = tuple(map(lambda x: x[0],e.leaves()))
            if len(name) == 2:
                persons.append(name)

    mentioned = []
    for p in set(persons):     
        for l in legislators:            
            first = p[0] == l['firstname'] or p[0] == l['nickname']
            last  = p[1] == l['lastname']
            if first and last:
                mentioned.append(l)
    return mentioned

def scrape(url):
    return find_legislators(get_raw(url))

influence_url = "http://influenceexplorer.com/search?query="
call_url = "http://www.callcongressnow.org/profile/"
party_url = "http://politicalpartytime.org/pol/"

def legislator_comment(l):
    infl = influence_url+l['firstname']+"+"+l['lastname']
    call = call_url+l['bioguide_id']    
    poli = party_url+l['crp_id']    
    return (infl,call,poli)


comment = """
Howdy! I'm ThePoliticalHound, a bot that finds the names of
legislators from Congress in submissions and provides relevent
information about each of them. I include information about how to
contact legislators, lobbying contributions made to each senator, and
what the senator has been up to lately in terms of working the donor
circuit.

Name   Website OpenCongress Phone Fax Facebook Twitter Youtube Office
Person 
Person
Person

-----------------------

All the information I use was based on the Sunlight Foundation's work,
I am in no way supported or representing the Sunlight Foundation. If
you have any complaints, concerns, or compliments, please PM
/u/ErlenmeyerSpace or tweet [@ZackMaril](). 
"""
