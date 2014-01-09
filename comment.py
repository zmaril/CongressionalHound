import subprocess 
from math import ceil
from util import handle_ratelimit
influence_url = "http://influenceexplorer.com/search?query="
call_url = "http://www.callcongressnow.org/profile/"
party_url = "http://politicalpartytime.org/pol/"
commit = subprocess.check_output(["git","rev-parse","HEAD"])[:-1]

intro = """
[Owoooooooooooooo](https://www.youtube.com/watch?v=mAAoU_ZGt1Q)! I'm a
bot that hunts for members of Congress in submitted articles and
displays information about them.
"""

footer = """
----------------------

[???](http://reddit.com/r/CongressionalHound/wiki)
[@@@](http://www.twitter.com/ZackMaril)
[$$$](http://www.reddit.com/r/CongressionalHound/wiki/index#wiki_are_you_going_to_earn_money_from_this_bot.3F)
[!!!](http://www.reddit.com/r/CongressionalHound/wiki/index#wiki_why_does_the_bot_keep_talking_about_ron_paul.2C_that_one_electrician_from_kentucky.3F)
[{0}](https://github.com/zmaril/CongressionalHound/tree/{1})
"""


def link(text,href):
    if href == None or href == "":
        return "N/A"
    else:
        return "[{0}]({1})".format(text,href)

def info(victims):
    str = """
|Name|Website|[Phone](http://www.callcongressnow.org/)|Twitter|FB|[Open Congress](http://www.opencongress.org/)|[Finances](http://influenceexplorer.com/)|[Fundraising](http://politicalpartytime.org/)|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
"""
    for v in victims:
        d = v.d
        fname = d['nickname'] if d['nickname'] != '' else d['firstname']
        name = fname+" "+d['lastname']
        props = [name]
        props.append(link("link",d['website'])+"/"+link("contact",d['webform']))
        props.append(link(d['phone'],"http://www.callcongressnow.org/profile/"+d['bioguide_id']))
        if d['twitter_id'] != "":
            props.append(link("@"+d['twitter_id'],"http://www.twitter.com/"+d['twitter_id'])) 
        else:
            props.append("N/A")
        if d['facebook_id'] != "":
            props.append(link("link","http://www.facebook.com/"+d['facebook_id'])) 
        else:
            props.append("N/A")
        props.append(link("link",d['congresspedia_url']))
        props.append(link("link","http://influenceexplorer.com/search?query="+d['firstname']+"+"+d['lastname']))
        props.append(link("link","http://politicalpartytime.org/pol/"+d['crp_id']))
        str += "|"+"|".join(props)+"|\n"
    return str

MAX_SINGLE=13
MAX_DISPLAY=17

def add_single_comment(submission,victims):
    str = intro+info(victims)+footer.format(commit[0:MAX_SINGLE],commit)
    return handle_ratelimit(submission.add_comment,str)

contd = """
(cont'd)
"""

def add_multiple_comments(submission,victims):
    comment = add_single_comment(submission,victims[0:MAX_SINGLE])
    for i in range(1,int(ceil(len(victims)/float(MAX_DISPLAY)))):
        v = victims[MAX_DISPLAY*i:MAX_DISPLAY*(i+1)]
        str = contd+info(v)
        handle_ratelimt(comment.reply,str)
    return comment
