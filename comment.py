import subprocess 

influence_url = "http://influenceexplorer.com/search?query="
call_url = "http://www.callcongressnow.org/profile/"
party_url = "http://politicalpartytime.org/pol/"
commit = subprocess.check_output(["git","rev-parse","HEAD"])[:-1]

intro = """
Hiya! I'm a bot that hunts for members of Congress in stories and finds information about them. 
"""

footer = """
Context for links:

* "Website" is the legislators main website.
* "Contact form" is the member of Congress' official contact form.  
* "Open Congress" provides a wealth of general information, including vote history, funding, and videos. 
* "Influence Explorer" dives deep into campaign finance and provides fascinating data about lobbying.       
* "Party Time" aggregates information concerning fundraising events for legislators. 
* "Call Congress Now" (the phone link) turns your browser into a phone for free and let's you call the D.C. office for a member of Congress.
                                                                                                                                                     
-----------------------                                                                                                                              

Did I make a mistake?  Please PM me or tweet [@ZackMaril](https://twitter.com/zackmaril) with any suggestions, complaints, or concerns.

------------------------

I depend heavily on projects built by the [Sunlight Foundation](http://sunlightfoundation.com/). They do awesome work; please consider [donating to them](http://sunlightfoundation.com/join/).  If you are interested in supporting my development and maintenance, please [consider using gittip](https://www.gittip.com/ZackMaril/).    

----------------------

I am an [open source](https://github.com/zmaril/CongressionalHound) bot. This comment was generated from commit [{0}](https://github.com/zmaril/CongressionalHound/tree/{1}). I only run on subreddits where I am invited or have received permission to operate in. If you are mod and want me to show up in your subreddit, just PM me and I'll be there soon. If you are a user of a particular subreddit, PM your mods and tell them to get in touch. 
"""


def link(text,href):
    if href == None or href == "":
        return "N/A"
    else:
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
        if d['twitter_id'] != "":
            props.append(link("@"+d['twitter_id'],"http://www.twitter.com/"+d['twitter_id'])) 
        else:
            props.append("N/A")
        if d['facebook_id'] != "":
            props.append(link("link","http://www.facebook.com/"+d['facebook_id'])) 
        else:
            props.append("N/A")

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

def generate_comment(victims):
    str = basic(victims)+contact(victims)+further(victims)
    str = intro+str+footer.format(commit[0:10],commit)
    return str
