# -*- coding: UTF-8 -*-
"""
Repository: https://code.launchpad.net/~python-scrapers/python-html-sanitizer/trunk
Revision: r10
Site: https://launchpad.net/python-html-sanitizer
Licence: Simplified BSD License

some input filters, for regularising the html fragments from screen scraping and
browser-based editors into some semblance of sanity

TODO: turn the messy setting[method_name]=True filter syntax into a list of cleaning methods to invoke, so that they can be invoked in a specific order and multiple times.

AUTHORS:
Dan MacKinlay - https://launchpad.net/~dan-possumpalace
Collin Grady - http://launchpad.net/~collin-collingrady
Andreas Gustafsson - https://bugs.launchpad.net/~gson
Håkan W - https://launchpad.net/~hwaara-gmail
"""

import re
import sys
import copy
import HTMLParser

from bleach import clean

from mediadrop.lib.compat import any

s = lambda x: unicode(x)[:20].replace("\n", "")

ANTI_JS_RE=re.compile('j\s*a\s*v\s*a\s*s\s*c\s*r\s*i\s*p\s*t\s*:', re.IGNORECASE)
#These tags and attrs are sufficently liberal to let microformats through...
#it ruthlessly culls all the rdf, dublin core metadata and so on.
valid_tags = dict.fromkeys('p i em strong b u a h1 h2 h3 pre abbr br img dd dt ol ul li span sub sup ins del blockquote table tr td th address cite'.split()) #div?
valid_attrs = dict.fromkeys('href src rel title'.split())
valid_schemes = dict.fromkeys('http https ssh sftp ftp'.split())
elem_map = {'b' : 'strong', 'i': 'em'}
attrs_considered_links = dict.fromkeys("src href".split()) #should include
#courtesy http://developer.mozilla.org/en/docs/HTML:Block-level_elements
block_elements = dict.fromkeys(["p", "h1","h2", "h3", "h4", "h5", "h6", "ol", "ul", "pre", "address", "blockquote", "dl", "div", "fieldset", "form", "hr", "noscript", "table"])

#convenient default filter lists.
paranoid_filters = ["strip_comments", "strip_tags", "strip_attrs", "encode_xml_specials",
  "strip_schemes", "rename_tags", "wrap_string", "strip_empty_tags", ]
complete_filters = ["strip_comments", "rename_tags", "strip_tags", "strip_attrs", "encode_xml_specials",
    "strip_cdata", "strip_schemes",  "wrap_string", "strip_empty_tags", "rebase_links", "reparse"]

#set some conservative default string processings
default_settings = {
    "filters" : paranoid_filters,
    "block_elements" : block_elements, #xml or None for a more liberal version
    "convert_entities" : "html", #xml or None for a more liberal version
    "valid_tags" : valid_tags,
    "valid_attrs" : valid_attrs,
    "valid_schemes" : valid_schemes,
    "attrs_considered_links" : attrs_considered_links,
    "elem_map" : elem_map,
    "wrapping_element" : "p",
    "auto_clean" : False,
    "original_url" : "",
    "new_url" : "",
    "html5" : True
}
#processes I'd like but haven't implemented
#"encode_xml_specials", "ensure complete xhtml doc", "ensure_xhtml_fragment_only"
# and some handling of permitted namespaces for tags. for RDF, say. maybe.

# TLDs from:
# http://data.iana.org/TLD/tlds-alpha-by-domain.txt (july 2009)
tlds = "AC|AD|AE|AERO|AF|AG|AI|AL|AM|AN|AO|AQ|AR|ARPA|AS|ASIA|AT|AU|AW|AX|AZ|BA|BB|BD|BE|BF|BG|BH|BI|BIZ|BJ|BM|BN|BO|BR|BS|BT|BV|BW|BY|BZ|CA|CAT|CC|CD|CF|CG|CH|CI|CK|CL|CM|CN|CO|COM|COOP|CR|CU|CV|CX|CY|CZ|DE|DJ|DK|DM|DO|DZ|EC|EDU|EE|EG|ER|ES|ET|EU|FI|FJ|FK|FM|FO|FR|GA|GB|GD|GE|GF|GG|GH|GI|GL|GM|GN|GOV|GP|GQ|GR|GS|GT|GU|GW|GY|HK|HM|HN|HR|HT|HU|ID|IE|IL|IM|IN|INFO|INT|IO|IQ|IR|IS|IT|JE|JM|JO|JOBS|JP|KE|KG|KH|KI|KM|KN|KP|KR|KW|KY|KZ|LA|LB|LC|LI|LK|LR|LS|LT|LU|LV|LY|MA|MC|MD|ME|MG|MH|MIL|MK|ML|MM|MN|MO|MOBI|MP|MQ|MR|MS|MT|MU|MUSEUM|MV|MW|MX|MY|MZ|NA|NAME|NC|NE|NET|NF|NG|NI|NL|NO|NP|NR|NU|NZ|OM|ORG|PA|PE|PF|PG|PH|PK|PL|PM|PN|PR|PRO|PS|PT|PW|PY|QA|RE|RO|RS|RU|RW|SA|SB|SC|SD|SE|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SR|ST|SU|SV|SY|SZ|TC|TD|TEL|TF|TG|TH|TJ|TK|TL|TM|TN|TO|TP|TR|TRAVEL|TT|TV|TW|TZ|UA|UG|UK|US|UY|UZ|VA|VC|VE|VG|VI|VN|VU|WF|WS|YE|YT|YU|ZA|ZM|ZW"
# Sort the list of TLDs so that the longest TLDs come first.
# This forces the regex to match the longest possible TLD.
tlds = "|".join(sorted(tlds.split("|"), lambda a,b: cmp(len(b), len(a))))

# This might not be the full regex. It is modified from the discussion at:
# http://geekswithblogs.net/casualjim/archive/2005/12/01/61722.aspx
url_regex = r"(?#Protocol)(?:([a-z\d]+)\:\/\/|~/|/)?" \
          + r"(?#Username:Password)(?:\w+:\w+@)?" \
          + r"(?#Host)(" \
              + r"((?#Subdomains)(?:(?:[-\w]+\.)+)" \
              + r"(?#TopLevel Domains)(?:%s))" % tlds \
              + r"|" \
              + r"(?#IPAddr)(([\d]{1,3}\.){3}[\d]{1,3})" \
          + r")" \
          + r"(?#Port)(?::[\d]{1,5})?" \
          + r"(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?" \
          + r"(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*" \
          + r"(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"

# NB: The order of these entities is very important
#     when performing search and replace!
XML_ENTITIES = [
    (u"&", u"&amp;"),
#    (u"'", u"&#39;"),
    (u'"', u"&quot;"),
    (u"<", u"&lt;"),
    (u">", u"&gt;")
]
LINE_EXTRACTION_RE = re.compile(".+", re.MULTILINE)
BR_EXTRACTION_RE = re.compile("</?br ?/?>", re.MULTILINE)
URL_RE = re.compile(url_regex, re.IGNORECASE)

def entities_to_unicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'.

    This further gets sanitized by bleach to make sure resulting text doesn't
    form injectable xhtml of its own, such as having &lt;script&gt;, etc.
    This is done by round-tripping twice through the HTMLParser.unescape().
    The first pass will unescape everything.  Then clean() will remove and
    strip evil xhtml tags, but clean() re-escapes the good tags, like &amp;.
    So a second call to unescape() produces clean unicode text without any
    hidden markup.
    """
    html_parser = HTMLParser.HTMLParser()
    insecure_text = html_parser.unescape(text)
    escaped_html = clean(insecure_text, strip=True)
    return html_parser.unescape(escaped_html)

def encode_xhtml_entities(text):
    """Escapes only those entities that are required for XHTML compliance"""
    for e in XML_ENTITIES:
        text = text.replace(e[0], e[1])
    return text

class Htmlator(object) :
    """
    converts a string into a series of html paragraphs
    """
    settings = {
        "encode_xml_specials" : True,
        "is_plaintext" : True,
        "convert_newlines" : False,
        "make_links" : True,
        "auto_convert" : False,
        "valid_schemes" : valid_schemes,
    }
    def __init__(self, string = "",  **kwargs):
        self.settings.update(kwargs)
        super(Htmlator, self).__init__(string, **kwargs)
        self.string = string

    def _set_string(self, string):
        self._string = unicode(string)
        if self.settings['auto_convert'] : self.convert()

    def _get_string(self):
        return self._string

    string = property(_get_string, _set_string)

    def __call__(self, string):
        """
        convenience method supporting one-step calling of an instance
        as a string cleaning function
        """
        self.string = string
        self.convert()
        return self.string

    def convert(self):
        for method in ["encode_xml_specials", "convert_newlines",
          "make_links"] :
            if self.settings.get(method, False):
                getattr(self, method)()

    def encode_xml_specials(self) :
        self._string = entities_to_unicode(self._string)
        self._string = encode_xhtml_entities(self._string)


    def make_links(self):
        matches = URL_RE.finditer(self._string)
        end_re = re.compile('\W')
        o = 0
        for m in matches:
            s, e = m.span()

            # if there are no more characters after the link
            # or if the character after the link is not a 'word character'
            if e > len(self._string) or end_re.match(self._string[e]):
                # take into account the added length of previous links
                s, e = s+o, e+o
                link = "<a href=\"%s\">%s</a>" % (m.group(), m.group())
                o += len(link) - len(m.group())
                self._string = self._string[:s] + link + self._string[e:]

    def convert_newlines(self) :
        # remove whitespace
        self._string = "\n".join([l.strip() for l in self.string.split("\n")])
        # remove duplicate line breaks
        self._string = re.sub("\n+", "\n", self._string).strip("\n")
        # wrap each line in <p> tags.
        self.string = ''.join([
            '<p>' + line.strip() + '</p>' for line in self.string.split('\n')
        ])

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
