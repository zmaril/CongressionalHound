import re, htmlentitydefs, time, praw

##
# Removes HTML or XML character references and entities from a text string. http://effbot.org/zone/re-sub.htm#unescape-html
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def formatted(*args):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) 
    return "["+now+"] "+" ".join(map(str,args))


def log(*args):    
    print apply(formatted,args)

def fail(*args):
    print '\033[91m'+apply(formatted,args)+'\033[0m'

def warn(*args):
    print '\033[93m'+apply(formatted,args)+'\033[0m'

def success(*args):
    print '\033[92m'+apply(formatted,args)+'\033[0m'

def handle_ratelimit(func, *args, **kwargs):
    while True:
        try:
            func(*args, **kwargs)
            break
        except praw.errors.RateLimitExceeded as error:
            warn('\tSleeping for %d seconds' % error.sleep_time)
            time.sleep(error.sleep_time)
        except Exception as e:
            fail(func,args,e)
            break
