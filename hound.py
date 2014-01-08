import nltk, urllib2, praw, time, pickle, os, argparse, httplib, gzip

from legislators import find_legislators
from comment     import add_single_comment, add_multiple_comments, MAX_SINGLE
from util        import log, unescape, fail, warn, success
from StringIO import StringIO


username = os.environ['HOUND_NAME'] if 'HOUND_NAME' in os.environ else "WOW"
password = os.environ['HOUND_PASSWORD'] if 'HOUND_PASSWORD' in os.environ else "SUCH DEMOCRACY"
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
    try:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
        req = urllib2.Request(unescape(url),headers={'User-Agent':'Mozilla/5.0'})
        response = opener.open(req)
        str = ""
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            str = f.read()
        else:
            str = response.read()
        str = nltk.clean_html(str)
        return str.decode("utf-8")
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
#TODO delete comments with -1 karma automatically

parser = argparse.ArgumentParser(description='Hunt some Congressfolk.')
parser.add_argument('--production', action='store_true')
args = parser.parse_args()

if args.production:
    warn("RUNNING IN PRODUCTION")
    subs.append("AnythingGoesNews")
    warn("ON THESE SUBREDDITS: {0}".format(subs))

if __name__ == "__main__":
    crawl_reddit()
