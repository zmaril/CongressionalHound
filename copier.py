import praw, time, pickle, os, argparse
from util import handle_ratelimit,log 

username = os.environ['HOUND_NAME'] if 'HOUND_NAME' in os.environ else "WOW"
password = os.environ['HOUND_PASSWORD'] if 'HOUND_PASSWORD' in os.environ else "SUCH DEMOCRACY"
r = praw.Reddit(user_agent="CongressionalHound by /u/ErlenmeyerSpace at /r/CongressionalHound, copying posts into /r/CongressionalHunting over for testing")
r.login(username=username,password=password)

subs = ["news","politics","AnythingGoesNews"]
h = "CongressionalHunting"

try:
    with open("copied"):
        print "Pickle exists"
except IOError:
    print "Creating pickle"
    file("copied", 'w').close()
    pickle.dump([],open("copied","r+"))
    print "Pickle Created"

def copy_subs():
    already_done = []
    while True:
        already_done=pickle.load(open("copied","r+"))
        for sub in subs:
            for s in r.get_subreddit(sub).get_new(limit=10):
                if s.id not in already_done:
                    already_done.append(s.id)
                    log("Submitting new story: {0}".format(s.short_link))
                    if len(s.selftext) is not 0:
                        handle_ratelimit(r.submit,h,s.title,text=s.selftext)
                    elif len(s.url) is not 0: 
                        handle_ratelimit(r.submit,h,s.title,url=s.url)
                    pickle.dump(already_done,open("copied","r+"))
        time.sleep(30)

if __name__ == "__main__":
    log("COPYING THESE SUBREDDITS: {0}".format(subs))
    copy_subs()

