import nltk, urllib2, praw, time, pickle, os 

from legislators import find_legislators
from comment     import generate_comment
from util        import log, unescape

username = os.environ['HOUND_NAME'] if 'HOUND_NAME' in os.environ else "WOW"
password = os.environ['HOUND_PASSWORD'] if 'HOUND_PASSWORD' in os.environ else "SUCH DEMOCRACY"
r = praw.Reddit(user_agent="Congressional Hound")
r.login(username=username,password=password)

subs = ["CongressionalHound"]

try:
    with open("stories"):
        print "Pickle exists"
except IOError:
    print "Creating pickle"
    file("stories", 'w').close()
    pickle.dump([],open("stories","r+"))
    print "Pickle Created"

def get_raw(url):    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
    req = urllib2.Request(unescape(url),headers={'User-Agent':'Mozilla/5.0'})
    str = opener.open(req).read()
    str = nltk.clean_html(str)
    return str.decode("utf-8")

already_done = []

def crawl_reddit():
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
                        log("Found {0} congressfolk!".format(len(victims)))
                        submission.add_comment(generate_comment(victims))
                        log("Added comment")
                    pickle.dump(already_done,open("stories","r+"))
       #TODO make pickle filter out anything over an hour old or
       #something?  Or make it only look back for the last 30 seconds
       #of information?
        time.sleep(30)

if __name__ == "__main__":
    crawl_reddit()
