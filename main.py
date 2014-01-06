import nltk
import urllib2
import csv 
import string 
import subprocess
import os

example = "http://www.theguardian.com/world/2014/jan/03/nsa-asked-spying-congress-bernie-sanders" 
legislators = {}
influence_url = "http://influenceexplorer.com/search?query="
call_url = "http://www.callcongressnow.org/profile/"
party_url = "http://politicalpartytime.org/pol/"
commit = subprocess.check_output(["git","rev-parse","HEAD"])[:-1]

class Legislator:
    def __init__(self,dict):
        self.d=dict 
    def __hash__(self):
        return hash(self.d['bioguide_id'])
    def __str__(self):
        return "Legislator: "+self.d['firstname']+self.d['lastname']

with open("legislators.csv","rb") as csvfile:
    for l in csv.DictReader(csvfile):
        legislators[l['firstname']+l['lastname']]=Legislator(l)
        if l['nickname'] != '':
            legislators[l['nickname']+l['lastname']]=Legislator(l)

def get_raw(url):
    return nltk.clean_html(urllib2.urlopen(url).read())

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

intro = """
Hiya! I'm a bot that hunts for members of Congress in stories and finds information about them. 
"""

footer = """
Context for links:

* "Website" is the legislators main website.
* "Contact from" is the member of Congress' official contact form.  
* "Open Congress" provides a wealth of general information, including vote history, funding, and videos. 
* "Influence Explorer" dives deep into campaign finance and provides fascinating data about lobbying.       
* "Party Time" aggregates information concerning fundraising events for legislators. 
* "Call Congress Now" (the phone link) turns your browser into a phone for free and let's you call the D.C. office for a member of Congress.
                                                                                                                                                     
-----------------------                                                                                                                              

Did I make a mistake?  Please PM /u/ErlenmeyerSpace or tweet [@ZackMaril](https://twitter.com/zackmaril) with any suggestions, complaints, or concerns. Please do not PM me, I don't read your messages! 

I depend heavily on projects built by the [Sunlight Foundation](http://sunlightfoundation.com/). They do awesome work; please consider [donating to them](http://sunlightfoundation.com/join/).  If you are interested in supporting my development and maintenance, please use [gittip](https://www.gittip.com/ZackMaril/).    

----------------------

I am an [open source](https://github.com/zmaril/CongressionalHound) bot. This comment was generated from commit [{0}](https://github.com/zmaril/CongressionalHound/tree/{1}).
"""

def link(text,href):
    return "[{0}]({1})".format(text,href)

def basic(victims):
    str = """
###Basic Information 

| Full Name | Gender | Nickname | Birthdate | Party | Title |
|:--:|:-:|:-:|:-:|:-:|:-:|
"""
    for v in victims:
        d = v.d 
        name = d['firstname']+" "+d['lastname']
        props = [name,d['gender'],d['nickname'],d['birthdate'],d['party'],d['title']]
        str += "|"+"|".join(props)+"|\n"
    return str
    
def contact(victims):
    str = """
###Contact Information

| Name | Contact Form | [Phone](http://www.callcongressnow.org/)|  Twitter | Facebook | Youtube |  Address | 
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
"""
    for v in victims:
        d = v.d 
        props = [d['lastname']]
        props.append(link("link",d['webform']))
        props.append(link(d['phone'],"http://www.callcongressnow.org/profile/"+d['bioguide_id']))
        props.append(link("@"+d['twitter_id'],"http://www.twitter.com/"+d['twitter_id']))
        props.append(link("link","http://www.facebook.com/"+d['facebook_id']))
        props.append(link("link",d['youtube_url']))
        props.append(d['congress_office'])
        str += "|"+"|".join(props)+"|\n"
    return str

def further(victims):
    str = """
###Further Information
                                                                                                                           
| Name | Website | [Open Congress](http://www.opencongress.org/) | [Influence Explorer](http://influenceexplorer.com/) | [Party Time](http://politicalpartytime.org/) |
|:-:|:-:|:-:|:-:|:-:|            
"""
    for v in victims:
        d = v.d 
        props = [d['lastname']]
        props.append(link("link",d['website']))
        props.append(link("link",d['congresspedia_url']))
        props.append(link("link","http://influenceexplorer.com/search?query="+d['firstname']+"+"+d['lastname']))
        props.append(link("link","http://politicalpartytime.org/pol/"+d['crp_id']))
        str += "|"+"|".join(props)+"|\n"
    return str

def generate_comment(url):
    victims = find_legislators(get_raw(url))
    if len(victims) == 0:
        return None
    else:
        str = basic(victims)+contact(victims)+further(victims)
        str = intro+str+footer.format(commit[0:10],commit)
        return str

import praw


username = os.environ['HOUND_NAME'] if 'HOUND_NAME' in os.environ else "WOW"
password = os.environ['HOUND_PASSWORD'] if 'HOUND_PASSWORD' in os.environ else "SUCH DEMOCRACY"
r = praw.Reddit(user_agent="Congressional Hound")
r.login(username=username,password=password)

subs = ["CongressionalHound"]
def crawl_reddit():
    for sub in subs:
        for submission in r.get_subreddit(sub).get_new(limit=10):
            comment = generate_comment(submission.url)
            submission.add_comment(comment)

if __name__ == "__main__":
    crawl_reddit()
