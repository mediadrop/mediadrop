"""ASCII transliterations of Unicode text

COPYRIGHT
    Character transliteration tables:
    Copyright 2001, Sean M. Burke <sburke@cpan.org>, all rights reserved.

    Python code:
    Copyright 2009, Tomaz Solc <tomaz@zemanta.com>

The programs and documentation in this dist are distributed in the
hope that they will be useful, but without any warranty; without even
the implied warranty of merchantability or fitness for a particular
purpose.

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl.
"""
Char = {}

NULLMAP = [ '' * 0x100 ]

def unidecode(string):
	"""Transliterate an Unicode object into an ASCII string

	>>> unidecode(u"\u5317\u4EB0")
	"Bei Jing "
	"""

	retval = []

	for char in string:
		o = ord(char)

		if o < 0x80:
			retval.append(char)
			continue

		h = o >> 8
		l = o & 0xff

		c = Char.get(h, None)
		
		if c == None:
			try:
				mod = __import__('unidecode.x%02x'%(h), [], [], ['data'])
			except ImportError:
				Char[h] = NULLMAP
				retval.append('')
				continue

			Char[h] = mod.data

			try:
				retval.append( mod.data[l] )
			except IndexError:
				retval.append( '' )
		else:
			try:
				retval.append( c[l] )
			except IndexError:
				retval.append( '' )

	return ''.join(retval)
