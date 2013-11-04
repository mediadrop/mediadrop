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

import BeautifulSoup
import re
import sys
import copy

from mediadrop.lib.compat import any

s = lambda x: unicode(x)[:20].replace("\n", "")

"""
html5lib compatibility. Basically, we need to know that this still works whether html5lib
is imported or not. Should run complete suites of tests for both possible configs -
or test in virtual environments, but for now a basic sanity check will do.
>>> if html5:
>>>     c=Cleaner(html5=False)
>>>     c(u'<p>foo</p>)
u'<p>foo</p>'
"""
try:
    import html5lib
    from html5lib import sanitizer, treebuilders
    parser = html5lib.HTMLParser(
        tree=treebuilders.getTreeBuilder("beautifulsoup"),
        tokenizer=sanitizer.HTMLSanitizer
    )
    html5 = True
except ImportError:
    html5 = False

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
    "html5" : html5
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

    FIXME:
    WARNING: There is a bug between sgmllib.SGMLParser.goahead() and
    BeautifulSoup.BeautifulStoneSoup.handle_entityref() where entity-like
    strings that don't match known entities are guessed at (if they come in
    the middle of the text) or are omitted (if they come at the end of the
    text).

    Further, unrecognized entities will have their leading ampersand escaped
    and trailing semicolon (if it exists) stripped. Examples:

    Inputs "...&bob;...", "...&bob&...", "...&bob;", and "...&bob" will give
    outputs "...&amp;bob...", "...&amp;bob&...", "...&amp;bob", and "...",
    respectively.
    """
    soup = BeautifulSoup.BeautifulStoneSoup(text,
        convertEntities=BeautifulSoup.BeautifulStoneSoup.ALL_ENTITIES)
    string = unicode(soup)
    # for some reason plain old instances of &amp; aren't converted to & ??
    string = string.replace('&amp;', '&')
    return string

def encode_xhtml_entities(text):
    """Escapes only those entities that are required for XHTML compliance"""
    for e in XML_ENTITIES:
        text = text.replace(e[0], e[1])
    return text

class Stop:
    """
    handy class that we use as a stop input for our state machine in lieu of falling
    off the end of lists
    """
    pass


class Cleaner(object):
    r"""
    powerful and slow arbitrary HTML sanitisation. can deal (i hope) with most XSS
    vectors and layout-breaking badness.
    Probably overkill for content from trusted sources; defaults are accordingly
    set to be paranoid.
    >>> bad_html = '<p style="forbidden markup"><!-- XSS attach -->content</p'
    >>> good_html = u'<p>content</p>'
    >>> c = Cleaner()
    >>> c.string = bad_html
    >>> c.clean()
    >>> c.string == good_html
    True

    Also supports shorthand syntax:
    >>> c = Cleaner()
    >>> c(bad_html) == c(good_html)
    True
    """

    def __init__(self, string_or_soup="", *args,  **kwargs):
        self.settings = copy.deepcopy(default_settings)
        self.settings.update(kwargs)
        if args :
            self.settings['filters'] = args
        super(Cleaner, self).__init__()
        self.string = string_or_soup

    def __call__(self, string = None, **kwargs):
        """
        convenience method allowing one-step calling of an instance and returning
        a cleaned string.

        TODO: make this method preserve internal state- perhaps by creating a new
        instance.

        >>> s = 'input string'
        >>> c1 = Cleaner(s, auto_clean=True)
        >>> c2 = Cleaner("")
        >>> c1.string == c2(s)
        True

        """
        self.settings.update(kwargs)
        if not string == None :
            self.string = string
        self.clean()
        return self.string

    def _set_contents(self, string_or_soup):
        if isinstance(string_or_soup, BeautifulSoup.BeautifulSoup) :
            self._set_soup(string_or_soup)
        else :
            self._set_string(string_or_soup)

    def _set_string(self, html_fragment_string):
        if self.settings['html5']:
            s = parser.parse(html_fragment_string).body
        else:
            s = BeautifulSoup.BeautifulSoup(
                    html_fragment_string,
                    convertEntities=self.settings['convert_entities'])
        self._set_soup(s)

    def _set_soup(self, soup):
        """
        Does all the work of set_string, but bypasses a potential autoclean to avoid
        loops upon internal string setting ops.
        """
        self._soup = BeautifulSoup.BeautifulSoup(
            '<rootrootroot></rootrootroot>'
        )
        self.root=self._soup.contents[0]

        if len(soup.contents) :
            backwards_soup = [i for i in soup.contents]
            backwards_soup.reverse()
        else :
            backwards_soup = []
        for i in backwards_soup :
            i.extract()
            self.root.insert(0, i)

    def set_string(self, string) :
        ur"""
            sets the string to process and does the necessary input encoding too
        really intended to be invoked as a property.
        note the godawful rootrootroot element which we need because the
        BeautifulSoup object has all the same methods as a Tag, but
        behaves differently, silently failing on some inserts and appends

        >>> c = Cleaner(convert_entities="html")
        >>> c.string = '&eacute;'
        >>> c.string
        u'\xe9'
        >>> c = Cleaner(convert_entities="xml")
        >>> c.string = u'&eacute;'
        >>> c.string
        u'&eacute;'
        """
        self._set_string(string)
        if len(string) and self.settings['auto_clean'] : self.clean()

    def get_string(self):
        return self.root.renderContents().decode('utf-8')

    string = property(get_string, set_string)

    def checkit(self, method):
        np = lambda x, y: y.parent is None and sys.stderr.write('%s HAS NO PARENT: %s\n' % (x, y)) or None
        a = self.root.findAllNext(True)
        a.extend(self.root.findAllNext(text=True))
        b = self.root.findAll(True)
        b.extend(self.root.findAll(text=True))
        for x in a:
            np('A', x)
            if x not in b:
                print method, [s(x)], "NOT IN B"
        for x in b:
            np('B', x)
            if x not in a:
                print method, [s(x)], "NOT IN A"

    def clean(self):
        """
        invoke all cleaning processes stipulated in the settings
        """
        for method in self.settings['filters'] :
            print_error = lambda: sys.stderr.write('Warning, called unimplemented method %s\n' % method)

            try :
                getattr(self, method, print_error)()
                # Uncomment when running in development mode, under paster.
                # self.checkit(method)
            except NotImplementedError:
                print_error()

    def strip_comments(self):
        r"""
        XHTML comments are used as an XSS attack vector. they must die.

        >>> c = Cleaner("", "strip_comments")
        >>> c('<p>text<!-- comment --> More text</p>')
        u'<p>text More text</p>'
        """
        for comment in self.root.findAll(
            text = lambda text: isinstance(text, BeautifulSoup.Comment)
        ):
            comment.extract()

    def strip_cdata(self):
        for cdata in self.root.findAll(
            text = lambda text: isinstance(text, BeautifulSoup.CData)
        ):
            cdata.extract()

    def strip_tags(self):
        r"""
        ill-considered tags break our layout. they must die.
        >>> c = Cleaner("", "strip_tags", auto_clean=True)
        >>> c.string = '<div>A <strong>B C</strong></div>'
        >>> c.string
        u'A <strong>B C</strong>'
        >>> c.string = '<div>A <div>B C</div></div>'
        >>> c.string
        u'A B C'
        >>> c.string = '<div>A <br /><div>B C</div></div>'
        >>> c.string
        u'A <br />B C'
        >>> c.string = '<p>A <div>B C</div></p>'
        >>> c.string
        u'<p>A B C</p>'
        >>> c.string = 'A<div>B<div>C<div>D</div>E</div>F</div>G'
        >>> c.string
        u'ABCDEFG'
        >>> c.string = '<div>B<div>C<div>D</div>E</div>F</div>'
        >>> c.string
        u'BCDEF'
        """
        # Beautiful Soup doesn't support dynamic .findAll results when the tree is
        # modified in place.
        # going backwards doesn't seem to help.
        # so find one at a time
        while True :
            next_bad_tag = self.root.find(
              lambda tag : not tag.name in (self.settings['valid_tags'])
            )
            if next_bad_tag :
                self.disgorge_elem(next_bad_tag)
            else:
                break

    def strip_attrs(self):
        """
        preserve only those attributes we need in the soup
        >>> c = Cleaner("", "strip_attrs")
        >>> c('<div title="v" bad="v">A <strong title="v" bad="v">B C</strong></div>')
        u'<div title="v">A <strong title="v">B C</strong></div>'
        """
        for tag in self.root.findAll(True):
            tag.attrs = [(attr, val) for attr, val in tag.attrs
                         if attr in self.settings['valid_attrs']]

    def _all_links(self):
        """
        finds all tags with link attributes sequentially. safe against modification
        of said attributes in-place.
        """
        start = self.root
        while True:
            tag = start.findNext(
              lambda tag : any(
                [(tag.get(i) for i in self.settings['attrs_considered_links'])]
              ))
            if tag:
                start = tag
                yield tag
            else :
                break

    def _all_elems(self, *args, **kwargs):
        """
        replacement for self.root.findAll(**kwargs)
        finds all elements with the specified strainer properties
        safe against modification of said attributes in-place.
        """
        start = self.root
        while True:
            tag = start.findNext(*args, **kwargs)
            if tag:
                start = tag
                yield tag
            else :
                break

    def strip_schemes(self):
        """
        >>> c = Cleaner("", "strip_schemes")
        >>> c('<img src="javascript:alert();" />')
        u'<img />'
        >>> c('<a href="javascript:alert();">foo</a>')
        u'<a>foo</a>'
        """
        for tag in self._all_links() :
            for key in self.settings['attrs_considered_links'] :
                scheme_bits = tag.get(key, u"").split(u':',1)
                if len(scheme_bits) == 1 :
                    pass #relative link
                else:
                    if not scheme_bits[0] in self.settings['valid_schemes']:
                        del(tag[key])

    def clean_whitespace(self):
        """
        >>> c = Cleaner("", "strip_whitespace")
        >>> c('<p>\n\t\tfoo</p>"
        u'<p> foo</p>'
        >>> c('<p>\t  <span> bar</span></p>')
        u'<p> <span>bar</span></p>')
        """
        def is_text(node):
            return isinstance(node, BeautifulSoup.NavigableString)

        def is_tag(node):
            return isinstance(node, BeautifulSoup.Tag)

        def dfs(node, func):
            if isinstance(node, BeautifulSoup.Tag):
                for x in node.contents:
                    dfs(x, func)
            func(node)

        any_space = re.compile("\s+", re.M)
        start_space = re.compile("^\s+")

        def condense_whitespace():
            # Go over every string, replacing all whitespace with a single space
            for string in self.root.findAll(text=True):
                s = unicode(string)
                s = any_space.sub(" ", s)
                s = BeautifulSoup.NavigableString(s)
                string.replaceWith(s)

        def separate_strings(current, next):
            if is_text(current):
                if is_text(next):
                    # Two strings are beside eachother, merge them!
                    next.extract()
                    s = unicode(current) + unicode(next)
                    s = BeautifulSoup.NavigableString(s)
                    current.replaceWith(s)
                    return s
                else:
                    # The current string is as big as its going to get.
                    # Check if you can split off some whitespace from
                    # the beginning.
                    p = unicode(current)
                    split = start_space.split(p)

                    if len(split) > 1 and split[1]:
                        # BeautifulSoup can't cope when we insert
                        # an empty text node.

                        par = current.parent
                        index = par.contents.index(current)
                        current.extract()

                        w = BeautifulSoup.NavigableString(" ")
                        s = BeautifulSoup.NavigableString(split[1])

                        par.insert(index, s)
                        par.insert(index, w)
            return next

        def separate_all_strings(node):
            if is_tag(node):
                contents = [elem for elem in node.contents]
                contents.append(None)

                current = None
                for next in contents:
                    current = separate_strings(current, next)

        def reassign_whitespace():
            strings = self.root.findAll(text=True)
            i = len(strings) - 1

            after = None
            while i >= 0:
                current = strings[i]
                if is_text(after) and not after.strip():
                    # if 'after' holds only whitespace,
                    # remove it, and append it to 'current'
                    s = unicode(current) + unicode(after)
                    s = BeautifulSoup.NavigableString(s)
                    current.replaceWith(s)
                    after.extract()

                    current = s

                after = current
                i -= 1

        condense_whitespace()
        dfs(self.root, separate_all_strings)
        reassign_whitespace()
        condense_whitespace()


    def br_to_p(self):
        """
        >>> c = Cleaner("", "br_to_p")
        >>> c('<p>A<br />B</p>')
        u'<p>A</p><p>B</p>'
        >>> c('A<br />B')
        u'<p>A</p><p>B</p>'
        """
        block_elems = self.settings['block_elements'].copy()
        block_elems['br'] = None
        block_elems['p'] = None

        while True :
            next_br = self.root.find('br')
            if not next_br: break
            parent = next_br.parent
            self.wrap_string('p', start_at=parent, block_elems = block_elems)
            while True:
                useless_br=parent.find('br', recursive=False)
                if not useless_br: break
                useless_br.extract()
            if parent.name == 'p':
                self.disgorge_elem(parent)

    def add_nofollow(self):
        """
        >>> c = Cleaner("", "add_nofollow")
        >>> c('<p><a href="mysite.com">site</a></p>')
        u'<p><a href="mysite.com" rel="nofollow">site</a></p>'
        """
        for a in self.root.findAll(name='a'):
            rel = a.get('rel', u"")
            sep = u" "
            nofollow = u"nofollow"

            r = rel.split(sep)
            if not nofollow in r:
                r.append(nofollow)
            rel = sep.join(r).strip()
            a['rel'] = rel

    def make_links(self):
        """
        Search through all text nodes, creating <a>
        tags for text that looks like a URL.
        >>> c = Cleaner("", "make_links")
        >>> c('check out my website at mysite.com')
        u'check out my website at <a href="mysite.com">mysite.com</a>'
        """
        def linkify_text_node(node):
            index = node.parent.contents.index(node)
            parent = node.parent
            string = unicode(node)

            matches = URL_RE.finditer(string)
            end_re = re.compile('\W')
            new_content = []
            o = 0
            for m in matches:
                s, e = m.span()

                # if there are no more characters after the link
                # or if the character after the link is not a 'word character'
                if e >= len(string) or end_re.match(string[e]):
                    link = BeautifulSoup.Tag(self._soup, 'a', attrs=[('href',m.group())])
                    link_text = BeautifulSoup.NavigableString(m.group())
                    link.insert(0, link_text)
                    if o < s: # BeautifulSoup can't cope when we insert an empty text node
                        previous_text = BeautifulSoup.NavigableString(string[o:s])
                        new_content.append(previous_text)
                    new_content.append(link)
                    o = e

            # Only do actual replacement if necessary
            if o > 0:
                if o < len(string):
                    final_text = BeautifulSoup.NavigableString(string[o:])
                    new_content.append(final_text)

                # replace the text node with the new text
                node.extract()
                for x in new_content:
                    parent.insert(index, x)
                    index += 1

        # run the algorithm
        for node in self.root.findAll(text=True):
            # Only linkify if this node is not a decendant of a link already
            if not node.findParents(name='a'):
                linkify_text_node(node)



    def rename_tags(self):
        """
        >>> c = Cleaner("", "rename_tags", elem_map={'i': 'em'})
        >>> c('<b>A<i>B</i></b>')
        u'<b>A<em>B</em></b>'
        """
        for tag in self.root.findAll(self.settings['elem_map']) :
            tag.name = self.settings['elem_map'][tag.name]

    def wrap_string(self, wrapping_element = None, start_at=None, block_elems=None):
        """
        takes an html fragment, which may or may not have a single containing element,
        and guarantees what the tag name of the topmost elements are.
        TODO: is there some simpler way than a state machine to do this simple thing?
        >>> c = Cleaner("", "wrap_string")
        >>> c('A <strong>B C</strong>D')
        u'<p>A <strong>B C</strong>D</p>'
        >>> c('A <p>B C</p>D')
        u'<p>A </p><p>B C</p><p>D</p>'
        """
        if not start_at : start_at = self.root
        if not block_elems : block_elems = self.settings['block_elements']
        e = (wrapping_element or self.settings['wrapping_element'])
        paragraph_list = []
        children = [elem for elem in start_at.contents]

        # Remove all the children
        for elem in children:
            elem.extract()
        children.append(Stop())

        last_state = 'block'
        paragraph = BeautifulSoup.Tag(self._soup, e)

        # Wrap each inline element a tag specified by 'e'
        for node in children :
            if isinstance(node, Stop) :
                state = 'end'
            elif hasattr(node, 'name') and node.name in block_elems:
                state = 'block'
            else:
                state = 'inline'

            if last_state == 'block' and state == 'inline':
                #collate inline elements
                paragraph = BeautifulSoup.Tag(self._soup, e)

            if state == 'inline' :
                paragraph.append(node)

            if ((state <> 'inline') and last_state == 'inline') :
                paragraph_list.append(paragraph)

            if state == 'block' :
                paragraph_list.append(node)

            last_state = state

        # Add all of the newly wrapped children back
        paragraph_list.reverse()
        for paragraph in paragraph_list:
            start_at.insert(0, paragraph)

    def strip_empty_tags(self):
        """
        strip out all empty tags
        >>> c = Cleaner("", "strip_empty_tags")
        >>> c('<p>A</p><p></p><p>B</p><p></p>')
        u'<p>A</p><p>B</p>'
        >>> c('<p><a></a></p>')
        u'<p></p>'
        """
        def is_text(node):
            return isinstance(node, BeautifulSoup.NavigableString)

        def is_tag(node):
            return isinstance(node, BeautifulSoup.Tag)

        def is_empty(node):
            if is_text(node):
                a = not unicode(node)

            if is_tag(node):
                a = not node.contents

            return bool(a)

        def contains_only_whitespace(node):
            if is_tag(node):
                if not any([not is_text(s) for s in node.contents]):
                    if not any([unicode(s).strip() for s in node.contents]):
                        return True
            return False


        def dfs(node, func, i=1):
            if is_tag(node):
                contents = [x for x in node.contents]
                for x in contents:
                    dfs(x, func, i+1)
            func(node, i)

        def strip_empty(node, i):
            if is_empty(node):
                node.extract()
            elif contains_only_whitespace(node):
                try:
                    self.disgorge_elem(node)
                except AttributeError:
                    # Don't complain when trying to disgorge the root element,
                    # as it'll be removed later anyway.
                    pass

        dfs(self.root, strip_empty)

    def rebase_links(self, original_url="", new_url ="") :
        if not original_url : original_url = self.settings.get('original_url', '')
        if not new_url : new_url = self.settings.get('new_url', '')
        raise NotImplementedError

    def encode_xml_specials(self) :
        """
        BeautifulSoup will let some dangerous xml entities hang around
        in the navigable strings. destroy all monsters.
        >>> c = Cleaner(auto_clean=True, encode_xml_specials=True)
        >>> c('<<<<<')
        u'&lt;&lt;&lt;&lt;'
        """
        for string in self.root.findAll(text=True):
            s = unicode(string)
            s = encode_xhtml_entities(s)
            s = BeautifulSoup.NavigableString(s)
            string.replaceWith(s)

    def disgorge_elem(self, elem):
        """
        remove the given element from the soup and replaces it with its own contents
        actually tricky, since you can't replace an element with an list of elements
        using replaceWith
        >>> disgorgeable_string = '<body>A <em>B</em> C</body>'
        >>> c = Cleaner()
        >>> c.string = disgorgeable_string
        >>> elem = c._soup.find('em')
        >>> c.disgorge_elem(elem)
        >>> c.string
        u'<body>A B C</body>'
        >>> c.string = disgorgeable_string
        >>> elem = c._soup.find('body')
        >>> c.disgorge_elem(elem)
        >>> c.string
        u'A <em>B</em> C'
        >>> c.string = '<div>A <div id="inner">B C</div></div>'
        >>> elem = c._soup.find(id="inner")
        >>> c.disgorge_elem(elem)
        >>> c.string
        u'<div>A B C</div>'
        """
        if elem == self.root :
            raise AttributeError, "Can't disgorge root"

        # With in-place modification, BeautifulSoup occasionally can return
        # elements that think they are orphans
        # this lib is full of workarounds, but it's worth checking
        parent = elem.parent
        if parent == None:
            raise AttributeError, "AAAAAAAAGH! NO PARENTS! DEATH!"

        i = None
        for i in range(len(parent.contents)) :
            if parent.contents[i] == elem :
                index = i
                break

        elem.extract()

        #the proceeding method breaks horribly, sporadically.
        # for i in range(len(elem.contents)) :
        #     elem.contents[i].extract()
        #     parent.contents.insert(index+i, elem.contents[i])
        # return
        self._safe_inject(parent, index, elem.contents)

    def _safe_inject(self, dest, dest_index, node_list):
        #BeautifulSoup result sets look like lists but don't behave right
        # i.e. empty ones are still True,
        if not len(node_list) : return
        node_list = [i for i in node_list]
        node_list.reverse()
        for i in node_list :
            dest.insert(dest_index, i)


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


# def cast_input_to_soup(fn):
#     """
#     Decorate function to handle strings as BeautifulSoups transparently
#     """
#     def stringy_version(input, *args, **kwargs) :
#         if not isinstance(input,BeautifulSoup) :
#             input=BeautifulSoup(input)
#         return fn(input, *args, **kwargs)
#     return stringy_version
