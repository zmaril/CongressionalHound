import nltk, urllib2, praw, time, pickle, os, argparse
import httplib, json, urllib

from legislators import find_legislators
from comment     import add_single_comment, add_multiple_comments, MAX_SINGLE
from util        import log, unescape, fail, warn, success
from StringIO import StringIO

#Set your environmental variables fool. 
username = os.environ['HOUND_NAME']
password = os.environ['HOUND_PASSWORD']
token = os.environ['READABILITY_TOKEN']
readability = "https://www.readability.com/api/content/v1/parser"

r = praw.Reddit(user_agent="Congressional Hound")
r.login(username=username,password=password)

subs = ["CongressionalHunting"]

try:
    with open("stories"):
        print "Pickle exists"
except IOError:
    print "Creating pickle"
    file("stories", 'w').close()
    pickle.dump([],open("stories","r+"))
    print "Pickle Created"

def get_raw(url):    
    ending = url[-4:]
    if ending in [".png",".jpg"]:
        return ""
    try:
        query = urllib.urlencode({'token':token,'url':url})        
        str = json.load(urllib2.urlopen(readability+"?"+query))['content']
        str = nltk.clean_html(str)
        return str
    except urllib2.HTTPError as e:
        fail("HTTP EXCEPTION:",e.code,e.reason,url)
        return ""
    except httplib.BadStatusLine as e:
        fail("BAD STATUS EXCEPTION",url)
        return ""

def crawl_reddit():
    already_done = []
    while True:
        already_done=pickle.load(open("stories","r+"))
        for sub in subs:
            for submission in r.get_subreddit(sub).get_new(limit=50):
                if submission.id not in already_done:
                    log("New story: "+sub+" "+submission.short_link+" "+submission.url)

                    already_done.append(submission.id)
                    raw = get_raw(submission.url)+" "+submission.title+" "+submission.selftext
                    victims = find_legislators(raw)
                    if len(victims) is not 0:
                        success("Found {0} congressfolk!".format(len(victims)))                        
                        if len(victims) < MAX_SINGLE: 
                            add_single_comment(submission,victims)
                            success("Added comment")
                        else:
                            add_multiple_comments(submission,victims)
                            success("Added multiple comments")
                    pickle.dump(already_done,open("stories","r+"))
       #TODO make pickle filter out anything over an hour old or
       #something?  Or make it only look back for the last 30 seconds
       #of posts?
        time.sleep(30)

#TODO look for words like congress, senate, republican, government,
#anythign to avoid misidentifying 
#TODO Rewrite the comment to point to the subreddit wiki
parser = argparse.ArgumentParser(description='Hunt some Congressfolk.')
parser.add_argument('--production', action='store_true')
args = parser.parse_args()

if args.production:
    warn("RUNNING IN PRODUCTION")
    subs.append("AnythingGoesNews")
    warn("ON THESE SUBREDDITS: {0}".format(subs))

if __name__ == "__main__":
    crawl_reddit()
