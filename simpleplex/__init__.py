import sys
def debug(*args):
       # print to stderr, for debuging
       # TODO: Perhaps replace with with more robust logging.
       print >> sys.stderr, "Simpleplex DEBUG", args
       return None

