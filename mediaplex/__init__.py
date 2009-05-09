import sys
def debug(*args):
       # print to stderr, for debuging
       print >> sys.stderr, "Mediaplex DEBUG", args
       return None

