//MooTools More, <http://mootools.net/more>. Copyright (c) 2006-2009 Aaron Newton <http://clientcide.com/>, Valerio Proietti <http://mad4milk.net> & the MooTools team <http://mootools.net/developers>, MIT Style License.

/*
---

script: More.js

description: MooTools More

license: MIT-style license

authors:
- Guillermo Rauch
- Thomas Aylott
- Scott Kyle

requires:
- core:1.2.4/MooTools

provides: [MooTools.More]

...
*/

MooTools.More = {
	'version': '1.2.4.4',
	'build': '6f6057dc645fdb7547689183b2311063bd653ddf'
};

/*
---

script: MooTools.Lang.js

description: Provides methods for localization.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Events
- /MooTools.More

provides: [MooTools.Lang]

...
*/

(function(){

	var data = {
		language: 'en-US',
		languages: {
			'en-US': {}
		},
		cascades: ['en-US']
	};
	
	var cascaded;

	MooTools.lang = new Events();

	$extend(MooTools.lang, {

		setLanguage: function(lang){
			if (!data.languages[lang]) return this;
			data.language = lang;
			this.load();
			this.fireEvent('langChange', lang);
			return this;
		},

		load: function() {
			var langs = this.cascade(this.getCurrentLanguage());
			cascaded = {};
			$each(langs, function(set, setName){
				cascaded[setName] = this.lambda(set);
			}, this);
		},

		getCurrentLanguage: function(){
			return data.language;
		},

		addLanguage: function(lang){
			data.languages[lang] = data.languages[lang] || {};
			return this;
		},

		cascade: function(lang){
			var cascades = (data.languages[lang] || {}).cascades || [];
			cascades.combine(data.cascades);
			cascades.erase(lang).push(lang);
			var langs = cascades.map(function(lng){
				return data.languages[lng];
			}, this);
			return $merge.apply(this, langs);
		},

		lambda: function(set) {
			(set || {}).get = function(key, args){
				return $lambda(set[key]).apply(this, $splat(args));
			};
			return set;
		},

		get: function(set, key, args){
			if (cascaded && cascaded[set]) return (key ? cascaded[set].get(key, args) : cascaded[set]);
		},

		set: function(lang, set, members){
			this.addLanguage(lang);
			langData = data.languages[lang];
			if (!langData[set]) langData[set] = {};
			$extend(langData[set], members);
			if (lang == this.getCurrentLanguage()){
				this.load();
				this.fireEvent('langChange', lang);
			}
			return this;
		},

		list: function(){
			return Hash.getKeys(data.languages);
		}

	});

})();

/*
---

script: Log.js

description: Provides basic logging functionality for plugins to implement.

license: MIT-style license

authors:
- Guillermo Rauch
- Thomas Aylott
- Scott Kyle

requires:
- core:1.2.4/Class
- /MooTools.More

provides: [Log]

...
*/

(function(){

var global = this;

var log = function(){
	if (global.console && console.log){
		try {
			console.log.apply(console, arguments);
		} catch(e) {
			console.log(Array.slice(arguments));
		}
	} else {
		Log.logged.push(arguments);
	}
	return this;
};

var disabled = function(){
	this.logged.push(arguments);
	return this;
};

this.Log = new Class({
	
	logged: [],
	
	log: disabled,
	
	resetLog: function(){
		this.logged.empty();
		return this;
	},

	enableLog: function(){
		this.log = log;
		this.logged.each(function(args){
			this.log.apply(this, args);
		}, this);
		return this.resetLog();
	},

	disableLog: function(){
		this.log = disabled;
		return this;
	}
	
});

Log.extend(new Log).enableLog();

// legacy
Log.logger = function(){
	return this.log.apply(this, arguments);
};

})();

/*
---

script: Class.Refactor.js

description: Extends a class onto itself with new property, preserving any items attached to the class's namespace.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Class
- /MooTools.More

provides: [Class.refactor]

...
*/

Class.refactor = function(original, refactors){

	$each(refactors, function(item, name){
		var origin = original.prototype[name];
		if (origin && (origin = origin._origin) && typeof item == 'function') original.implement(name, function(){
			var old = this.previous;
			this.previous = origin;
			var value = item.apply(this, arguments);
			this.previous = old;
			return value;
		}); else original.implement(name, item);
	});

	return original;

};

/*
---

script: Class.Binds.js

description: Automagically binds specified methods in a class to the instance of the class.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Class
- /MooTools.More

provides: [Class.Binds]

...
*/

Class.Mutators.Binds = function(binds){
    return binds;
};

Class.Mutators.initialize = function(initialize){
	return function(){
		$splat(this.Binds).each(function(name){
			var original = this[name];
			if (original) this[name] = original.bind(this);
		}, this);
		return initialize.apply(this, arguments);
	};
};


/*
---

script: Class.Occlude.js

description: Prevents a class from being applied to a DOM element twice.

license: MIT-style license.

authors:
- Aaron Newton

requires: 
- core/1.2.4/Class
- core:1.2.4/Element
- /MooTools.More

provides: [Class.Occlude]

...
*/

Class.Occlude = new Class({

	occlude: function(property, element){
		element = document.id(element || this.element);
		var instance = element.retrieve(property || this.property);
		if (instance && !$defined(this.occluded))
			return this.occluded = instance;

		this.occluded = false;
		element.store(property || this.property, this);
		return this.occluded;
	}

});

/*
---

script: Date.js

description: Extends the Date native object to include methods useful in managing dates.

license: MIT-style license

authors:
- Aaron Newton
- Nicholas Barthelemy - https://svn.nbarthelemy.com/date-js/
- Harald Kirshner - mail [at] digitarald.de; http://digitarald.de
- Scott Kyle - scott [at] appden.com; http://appden.com

requires:
- core:1.2.4/Array
- core:1.2.4/String
- core:1.2.4/Number
- core:1.2.4/Lang
- core:1.2.4/Date.English.US
- /MooTools.More

provides: [Date]

...
*/

(function(){

var Date = this.Date;

if (!Date.now) Date.now = $time;

Date.Methods = {
	ms: 'Milliseconds',
	year: 'FullYear',
	min: 'Minutes',
	mo: 'Month',
	sec: 'Seconds',
	hr: 'Hours'
};

['Date', 'Day', 'FullYear', 'Hours', 'Milliseconds', 'Minutes', 'Month', 'Seconds', 'Time', 'TimezoneOffset',
	'Week', 'Timezone', 'GMTOffset', 'DayOfYear', 'LastMonth', 'LastDayOfMonth', 'UTCDate', 'UTCDay', 'UTCFullYear',
	'AMPM', 'Ordinal', 'UTCHours', 'UTCMilliseconds', 'UTCMinutes', 'UTCMonth', 'UTCSeconds'].each(function(method){
	Date.Methods[method.toLowerCase()] = method;
});

var pad = function(what, length){
	return new Array(length - String(what).length + 1).join('0') + what;
};

Date.implement({

	set: function(prop, value){
		switch ($type(prop)){
			case 'object':
				for (var p in prop) this.set(p, prop[p]);
				break;
			case 'string':
				prop = prop.toLowerCase();
				var m = Date.Methods;
				if (m[prop]) this['set' + m[prop]](value);
		}
		return this;
	},

	get: function(prop){
		prop = prop.toLowerCase();
		var m = Date.Methods;
		if (m[prop]) return this['get' + m[prop]]();
		return null;
	},

	clone: function(){
		return new Date(this.get('time'));
	},

	increment: function(interval, times){
		interval = interval || 'day';
		times = $pick(times, 1);

		switch (interval){
			case 'year':
				return this.increment('month', times * 12);
			case 'month':
				var d = this.get('date');
				this.set('date', 1).set('mo', this.get('mo') + times);
				return this.set('date', d.min(this.get('lastdayofmonth')));
			case 'week':
				return this.increment('day', times * 7);
			case 'day':
				return this.set('date', this.get('date') + times);
		}

		if (!Date.units[interval]) throw new Error(interval + ' is not a supported interval');

		return this.set('time', this.get('time') + times * Date.units[interval]());
	},

	decrement: function(interval, times){
		return this.increment(interval, -1 * $pick(times, 1));
	},

	isLeapYear: function(){
		return Date.isLeapYear(this.get('year'));
	},

	clearTime: function(){
		return this.set({hr: 0, min: 0, sec: 0, ms: 0});
	},

	diff: function(date, resolution){
		if ($type(date) == 'string') date = Date.parse(date);
		
		return ((date - this) / Date.units[resolution || 'day'](3, 3)).toInt(); // non-leap year, 30-day month
	},

	getLastDayOfMonth: function(){
		return Date.daysInMonth(this.get('mo'), this.get('year'));
	},

	getDayOfYear: function(){
		return (Date.UTC(this.get('year'), this.get('mo'), this.get('date') + 1) 
			- Date.UTC(this.get('year'), 0, 1)) / Date.units.day();
	},

	getWeek: function(){
		return (this.get('dayofyear') / 7).ceil();
	},
	
	getOrdinal: function(day){
		return Date.getMsg('ordinal', day || this.get('date'));
	},

	getTimezone: function(){
		return this.toString()
			.replace(/^.*? ([A-Z]{3}).[0-9]{4}.*$/, '$1')
			.replace(/^.*?\(([A-Z])[a-z]+ ([A-Z])[a-z]+ ([A-Z])[a-z]+\)$/, '$1$2$3');
	},

	getGMTOffset: function(){
		var off = this.get('timezoneOffset');
		return ((off > 0) ? '-' : '+') + pad((off.abs() / 60).floor(), 2) + pad(off % 60, 2);
	},

	setAMPM: function(ampm){
		ampm = ampm.toUpperCase();
		var hr = this.get('hr');
		if (hr > 11 && ampm == 'AM') return this.decrement('hour', 12);
		else if (hr < 12 && ampm == 'PM') return this.increment('hour', 12);
		return this;
	},

	getAMPM: function(){
		return (this.get('hr') < 12) ? 'AM' : 'PM';
	},

	parse: function(str){
		this.set('time', Date.parse(str));
		return this;
	},

	isValid: function(date) {
		return !!(date || this).valueOf();
	},

	format: function(f){
		if (!this.isValid()) return 'invalid date';
		f = f || '%x %X';
		f = formats[f.toLowerCase()] || f; // replace short-hand with actual format
		var d = this;
		return f.replace(/%([a-z%])/gi,
			function($0, $1){
				switch ($1){
					case 'a': return Date.getMsg('days')[d.get('day')].substr(0, 3);
					case 'A': return Date.getMsg('days')[d.get('day')];
					case 'b': return Date.getMsg('months')[d.get('month')].substr(0, 3);
					case 'B': return Date.getMsg('months')[d.get('month')];
					case 'c': return d.toString();
					case 'd': return pad(d.get('date'), 2);
					case 'H': return pad(d.get('hr'), 2);
					case 'I': return ((d.get('hr') % 12) || 12);
					case 'j': return pad(d.get('dayofyear'), 3);
					case 'm': return pad((d.get('mo') + 1), 2);
					case 'M': return pad(d.get('min'), 2);
					case 'o': return d.get('ordinal');
					case 'p': return Date.getMsg(d.get('ampm'));
					case 'S': return pad(d.get('seconds'), 2);
					case 'U': return pad(d.get('week'), 2);
					case 'w': return d.get('day');
					case 'x': return d.format(Date.getMsg('shortDate'));
					case 'X': return d.format(Date.getMsg('shortTime'));
					case 'y': return d.get('year').toString().substr(2);
					case 'Y': return d.get('year');
					case 'T': return d.get('GMTOffset');
					case 'Z': return d.get('Timezone');
				}
				return $1;
			}
		);
	},

	toISOString: function(){
		return this.format('iso8601');
	}

});

Date.alias('toISOString', 'toJSON');
Date.alias('diff', 'compare');
Date.alias('format', 'strftime');

var formats = {
	db: '%Y-%m-%d %H:%M:%S',
	compact: '%Y%m%dT%H%M%S',
	iso8601: '%Y-%m-%dT%H:%M:%S%T',
	rfc822: '%a, %d %b %Y %H:%M:%S %Z',
	'short': '%d %b %H:%M',
	'long': '%B %d, %Y %H:%M'
};

var parsePatterns = [];
var nativeParse = Date.parse;

var parseWord = function(type, word, num){
	var ret = -1;
	var translated = Date.getMsg(type + 's');

	switch ($type(word)){
		case 'object':
			ret = translated[word.get(type)];
			break;
		case 'number':
			ret = translated[month - 1];
			if (!ret) throw new Error('Invalid ' + type + ' index: ' + index);
			break;
		case 'string':
			var match = translated.filter(function(name){
				return this.test(name);
			}, new RegExp('^' + word, 'i'));
			if (!match.length)    throw new Error('Invalid ' + type + ' string');
			if (match.length > 1) throw new Error('Ambiguous ' + type);
			ret = match[0];
	}

	return (num) ? translated.indexOf(ret) : ret;
};

Date.extend({

	getMsg: function(key, args) {
		return MooTools.lang.get('Date', key, args);
	},

	units: {
		ms: $lambda(1),
		second: $lambda(1000),
		minute: $lambda(60000),
		hour: $lambda(3600000),
		day: $lambda(86400000),
		week: $lambda(608400000),
		month: function(month, year){
			var d = new Date;
			return Date.daysInMonth($pick(month, d.get('mo')), $pick(year, d.get('year'))) * 86400000;
		},
		year: function(year){
			year = year || new Date().get('year');
			return Date.isLeapYear(year) ? 31622400000 : 31536000000;
		}
	},

	daysInMonth: function(month, year){
		return [31, Date.isLeapYear(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month];
	},

	isLeapYear: function(year){
		return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
	},

	parse: function(from){
		var t = $type(from);
		if (t == 'number') return new Date(from);
		if (t != 'string') return from;
		from = from.clean();
		if (!from.length) return null;

		var parsed;
		parsePatterns.some(function(pattern){
			var bits = pattern.re.exec(from);
			return (bits) ? (parsed = pattern.handler(bits)) : false;
		});

		return parsed || new Date(nativeParse(from));
	},

	parseDay: function(day, num){
		return parseWord('day', day, num);
	},

	parseMonth: function(month, num){
		return parseWord('month', month, num);
	},

	parseUTC: function(value){
		var localDate = new Date(value);
		var utcSeconds = Date.UTC(
			localDate.get('year'),
			localDate.get('mo'),
			localDate.get('date'),
			localDate.get('hr'),
			localDate.get('min'),
			localDate.get('sec')
		);
		return new Date(utcSeconds);
	},

	orderIndex: function(unit){
		return Date.getMsg('dateOrder').indexOf(unit) + 1;
	},

	defineFormat: function(name, format){
		formats[name] = format;
	},

	defineFormats: function(formats){
		for (var name in formats) Date.defineFormat(name, formats[name]);
	},

	parsePatterns: parsePatterns, // this is deprecated
	
	defineParser: function(pattern){
		parsePatterns.push((pattern.re && pattern.handler) ? pattern : build(pattern));
	},
	
	defineParsers: function(){
		Array.flatten(arguments).each(Date.defineParser);
	},
	
	define2DigitYearStart: function(year){
		startYear = year % 100;
		startCentury = year - startYear;
	}

});

var startCentury = 1900;
var startYear = 70;

var regexOf = function(type){
	return new RegExp('(?:' + Date.getMsg(type).map(function(name){
		return name.substr(0, 3);
	}).join('|') + ')[a-z]*');
};

var replacers = function(key){
	switch(key){
		case 'x': // iso8601 covers yyyy-mm-dd, so just check if month is first
			return ((Date.orderIndex('month') == 1) ? '%m[.-/]%d' : '%d[.-/]%m') + '([.-/]%y)?';
		case 'X':
			return '%H([.:]%M)?([.:]%S([.:]%s)?)? ?%p? ?%T?';
	}
	return null;
};

var keys = {
	d: /[0-2]?[0-9]|3[01]/,
	H: /[01]?[0-9]|2[0-3]/,
	I: /0?[1-9]|1[0-2]/,
	M: /[0-5]?\d/,
	s: /\d+/,
	o: /[a-z]*/,
	p: /[ap]\.?m\.?/,
	y: /\d{2}|\d{4}/,
	Y: /\d{4}/,
	T: /Z|[+-]\d{2}(?::?\d{2})?/
};

keys.m = keys.I;
keys.S = keys.M;

var currentLanguage;

var recompile = function(language){
	currentLanguage = language;
	
	keys.a = keys.A = regexOf('days');
	keys.b = keys.B = regexOf('months');
	
	parsePatterns.each(function(pattern, i){
		if (pattern.format) parsePatterns[i] = build(pattern.format);
	});
};

var build = function(format){
	if (!currentLanguage) return {format: format};
	
	var parsed = [];
	var re = (format.source || format) // allow format to be regex
	 .replace(/%([a-z])/gi,
		function($0, $1){
			return replacers($1) || $0;
		}
	).replace(/\((?!\?)/g, '(?:') // make all groups non-capturing
	 .replace(/ (?!\?|\*)/g, ',? ') // be forgiving with spaces and commas
	 .replace(/%([a-z%])/gi,
		function($0, $1){
			var p = keys[$1];
			if (!p) return $1;
			parsed.push($1);
			return '(' + p.source + ')';
		}
	).replace(/\[a-z\]/gi, '[a-z\\u00c0-\\uffff]'); // handle unicode words

	return {
		format: format,
		re: new RegExp('^' + re + '$', 'i'),
		handler: function(bits){
			bits = bits.slice(1).associate(parsed);
			var date = new Date().clearTime();
			if ('d' in bits) handle.call(date, 'd', 1);
			if ('m' in bits || 'b' in bits || 'B' in bits) handle.call(date, 'm', 1);
			for (var key in bits) handle.call(date, key, bits[key]);
			return date;
		}
	};
};

var handle = function(key, value){
	if (!value) return this;

	switch(key){
		case 'a': case 'A': return this.set('day', Date.parseDay(value, true));
		case 'b': case 'B': return this.set('mo', Date.parseMonth(value, true));
		case 'd': return this.set('date', value);
		case 'H': case 'I': return this.set('hr', value);
		case 'm': return this.set('mo', value - 1);
		case 'M': return this.set('min', value);
		case 'p': return this.set('ampm', value.replace(/\./g, ''));
		case 'S': return this.set('sec', value);
		case 's': return this.set('ms', ('0.' + value) * 1000);
		case 'w': return this.set('day', value);
		case 'Y': return this.set('year', value);
		case 'y':
			value = +value;
			if (value < 100) value += startCentury + (value < startYear ? 100 : 0);
			return this.set('year', value);
		case 'T':
			if (value == 'Z') value = '+00';
			var offset = value.match(/([+-])(\d{2}):?(\d{2})?/);
			offset = (offset[1] + '1') * (offset[2] * 60 + (+offset[3] || 0)) + this.getTimezoneOffset();
			return this.set('time', this - offset * 60000);
	}

	return this;
};

Date.defineParsers(
	'%Y([-./]%m([-./]%d((T| )%X)?)?)?', // "1999-12-31", "1999-12-31 11:59pm", "1999-12-31 23:59:59", ISO8601
	'%Y%m%d(T%H(%M%S?)?)?', // "19991231", "19991231T1159", compact
	'%x( %X)?', // "12/31", "12.31.99", "12-31-1999", "12/31/2008 11:59 PM"
	'%d%o( %b( %Y)?)?( %X)?', // "31st", "31st December", "31 Dec 1999", "31 Dec 1999 11:59pm"
	'%b( %d%o)?( %Y)?( %X)?', // Same as above with month and day switched
	'%Y %b( %d%o( %X)?)?', // Same as above with year coming first
	'%o %b %d %X %T %Y' // "Thu Oct 22 08:11:23 +0000 2009"
);

MooTools.lang.addEvent('langChange', function(language){
	if (MooTools.lang.get('Date')) recompile(language);
}).fireEvent('langChange', MooTools.lang.getCurrentLanguage());

})();

/*
---

script: Hash.Extras.js

description: Extends the Hash native object to include getFromPath which allows a path notation to child elements.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Hash.base
- /MooTools.More

provides: [Hash.Extras]

...
*/

Hash.implement({

	getFromPath: function(notation){
		var source = this.getClean();
		notation.replace(/\[([^\]]+)\]|\.([^.[]+)|[^[.]+/g, function(match){
			if (!source) return null;
			var prop = arguments[2] || arguments[1] || arguments[0];
			source = (prop in source) ? source[prop] : null;
			return match;
		});
		return source;
	},

	cleanValues: function(method){
		method = method || $defined;
		this.each(function(v, k){
			if (!method(v)) this.erase(k);
		}, this);
		return this;
	},

	run: function(){
		var args = arguments;
		this.each(function(v, k){
			if ($type(v) == 'function') v.run(args);
		});
	}

});

/*
---

script: String.Extras.js

description: Extends the String native object to include methods useful in managing various kinds of strings (query strings, urls, html, etc).

license: MIT-style license

authors:
- Aaron Newton
- Guillermo Rauch

requires:
- core:1.2.4/String
- core:1.2.4/$util
- core:1.2.4/Array

provides: [String.Extras]

...
*/

(function(){
  
var special = ['À','à','Á','á','Â','â','Ã','ã','Ä','ä','Å','å','Ă','ă','Ą','ą','Ć','ć','Č','č','Ç','ç', 'Ď','ď','Đ','đ', 'È','è','É','é','Ê','ê','Ë','ë','Ě','ě','Ę','ę', 'Ğ','ğ','Ì','ì','Í','í','Î','î','Ï','ï', 'Ĺ','ĺ','Ľ','ľ','Ł','ł', 'Ñ','ñ','Ň','ň','Ń','ń','Ò','ò','Ó','ó','Ô','ô','Õ','õ','Ö','ö','Ø','ø','ő','Ř','ř','Ŕ','ŕ','Š','š','Ş','ş','Ś','ś', 'Ť','ť','Ť','ť','Ţ','ţ','Ù','ù','Ú','ú','Û','û','Ü','ü','Ů','ů', 'Ÿ','ÿ','ý','Ý','Ž','ž','Ź','ź','Ż','ż', 'Þ','þ','Ð','ð','ß','Œ','œ','Æ','æ','µ'];

var standard = ['A','a','A','a','A','a','A','a','Ae','ae','A','a','A','a','A','a','C','c','C','c','C','c','D','d','D','d', 'E','e','E','e','E','e','E','e','E','e','E','e','G','g','I','i','I','i','I','i','I','i','L','l','L','l','L','l', 'N','n','N','n','N','n', 'O','o','O','o','O','o','O','o','Oe','oe','O','o','o', 'R','r','R','r', 'S','s','S','s','S','s','T','t','T','t','T','t', 'U','u','U','u','U','u','Ue','ue','U','u','Y','y','Y','y','Z','z','Z','z','Z','z','TH','th','DH','dh','ss','OE','oe','AE','ae','u'];

var tidymap = {
	"[\xa0\u2002\u2003\u2009]": " ",
	"\xb7": "*",
	"[\u2018\u2019]": "'",
	"[\u201c\u201d]": '"',
	"\u2026": "...",
	"\u2013": "-",
	"\u2014": "--",
	"\uFFFD": "&raquo;"
};

var getRegForTag = function(tag, contents) {
	tag = tag || '';
	var regstr = contents ? "<" + tag + "[^>]*>([\\s\\S]*?)<\/" + tag + ">" : "<\/?" + tag + "([^>]+)?>";
	reg = new RegExp(regstr, "gi");
	return reg;
};

String.implement({

	standardize: function(){
		var text = this;
		special.each(function(ch, i){
			text = text.replace(new RegExp(ch, 'g'), standard[i]);
		});
		return text;
	},

	repeat: function(times){
		return new Array(times + 1).join(this);
	},

	pad: function(length, str, dir){
		if (this.length >= length) return this;
		var pad = (str == null ? ' ' : '' + str).repeat(length - this.length).substr(0, length - this.length);
		if (!dir || dir == 'right') return this + pad;
		if (dir == 'left') return pad + this;
		return pad.substr(0, (pad.length / 2).floor()) + this + pad.substr(0, (pad.length / 2).ceil());
	},

	getTags: function(tag, contents){
		return this.match(getRegForTag(tag, contents)) || [];
	},

	stripTags: function(tag, contents){
		return this.replace(getRegForTag(tag, contents), '');
	},

	tidy: function(){
		var txt = this.toString();
		$each(tidymap, function(value, key){
			txt = txt.replace(new RegExp(key, 'g'), value);
		});
		return txt;
	}

});

})();

/*
---

script: String.QueryString.js

description: Methods for dealing with URI query strings.

license: MIT-style license

authors:
- Sebastian Markbåge, Aaron Newton, Lennart Pilon, Valerio Proietti

requires:
- core:1.2.4/Array
- core:1.2.4/String
- /MooTools.More

provides: [String.QueryString]

...
*/

String.implement({

	parseQueryString: function(){
		var vars = this.split(/[&;]/), res = {};
		if (vars.length) vars.each(function(val){
			var index = val.indexOf('='),
				keys = index < 0 ? [''] : val.substr(0, index).match(/[^\]\[]+/g),
				value = decodeURIComponent(val.substr(index + 1)),
				obj = res;
			keys.each(function(key, i){
				var current = obj[key];
				if(i < keys.length - 1)
					obj = obj[key] = current || {};
				else if($type(current) == 'array')
					current.push(value);
				else
					obj[key] = $defined(current) ? [current, value] : value;
			});
		});
		return res;
	},

	cleanQueryString: function(method){
		return this.split('&').filter(function(val){
			var index = val.indexOf('='),
			key = index < 0 ? '' : val.substr(0, index),
			value = val.substr(index + 1);
			return method ? method.run([key, value]) : $chk(value);
		}).join('&');
	}

});

/*
---

script: URI.js

description: Provides methods useful in managing the window location and uris.

license: MIT-style license

authors:
- Sebastian Markb�ge
- Aaron Newton

requires:
- core:1.2.4/Selectors
- /String.QueryString

provides: URI

...
*/

var URI = new Class({

	Implements: Options,

	options: {
		/*base: false*/
	},

	regex: /^(?:(\w+):)?(?:\/\/(?:(?:([^:@\/]*):?([^:@\/]*))?@)?([^:\/?#]*)(?::(\d*))?)?(\.\.?$|(?:[^?#\/]*\/)*)([^?#]*)(?:\?([^#]*))?(?:#(.*))?/,
	parts: ['scheme', 'user', 'password', 'host', 'port', 'directory', 'file', 'query', 'fragment'],
	schemes: {http: 80, https: 443, ftp: 21, rtsp: 554, mms: 1755, file: 0},

	initialize: function(uri, options){
		this.setOptions(options);
		var base = this.options.base || URI.base;
		if(!uri) uri = base;
		
		if (uri && uri.parsed) this.parsed = $unlink(uri.parsed);
		else this.set('value', uri.href || uri.toString(), base ? new URI(base) : false);
	},

	parse: function(value, base){
		var bits = value.match(this.regex);
		if (!bits) return false;
		bits.shift();
		return this.merge(bits.associate(this.parts), base);
	},

	merge: function(bits, base){
		if ((!bits || !bits.scheme) && (!base || !base.scheme)) return false;
		if (base){
			this.parts.every(function(part){
				if (bits[part]) return false;
				bits[part] = base[part] || '';
				return true;
			});
		}
		bits.port = bits.port || this.schemes[bits.scheme.toLowerCase()];
		bits.directory = bits.directory ? this.parseDirectory(bits.directory, base ? base.directory : '') : '/';
		return bits;
	},

	parseDirectory: function(directory, baseDirectory) {
		directory = (directory.substr(0, 1) == '/' ? '' : (baseDirectory || '/')) + directory;
		if (!directory.test(URI.regs.directoryDot)) return directory;
		var result = [];
		directory.replace(URI.regs.endSlash, '').split('/').each(function(dir){
			if (dir == '..' && result.length > 0) result.pop();
			else if (dir != '.') result.push(dir);
		});
		return result.join('/') + '/';
	},

	combine: function(bits){
		return bits.value || bits.scheme + '://' +
			(bits.user ? bits.user + (bits.password ? ':' + bits.password : '') + '@' : '') +
			(bits.host || '') + (bits.port && bits.port != this.schemes[bits.scheme] ? ':' + bits.port : '') +
			(bits.directory || '/') + (bits.file || '') +
			(bits.query ? '?' + bits.query : '') +
			(bits.fragment ? '#' + bits.fragment : '');
	},

	set: function(part, value, base){
		if (part == 'value'){
			var scheme = value.match(URI.regs.scheme);
			if (scheme) scheme = scheme[1];
			if (scheme && !$defined(this.schemes[scheme.toLowerCase()])) this.parsed = { scheme: scheme, value: value };
			else this.parsed = this.parse(value, (base || this).parsed) || (scheme ? { scheme: scheme, value: value } : { value: value });
		} else if (part == 'data') {
			this.setData(value);
		} else {
			this.parsed[part] = value;
		}
		return this;
	},

	get: function(part, base){
		switch(part){
			case 'value': return this.combine(this.parsed, base ? base.parsed : false);
			case 'data' : return this.getData();
		}
		return this.parsed[part] || '';
	},

	go: function(){
		document.location.href = this.toString();
	},

	toURI: function(){
		return this;
	},

	getData: function(key, part){
		var qs = this.get(part || 'query');
		if (!$chk(qs)) return key ? null : {};
		var obj = qs.parseQueryString();
		return key ? obj[key] : obj;
	},

	setData: function(values, merge, part){
		if (typeof values == 'string'){
			data = this.getData();
			data[arguments[0]] = arguments[1];
			values = data;
		} else if (merge) {
			values = $merge(this.getData(), values);
		}
		return this.set(part || 'query', Hash.toQueryString(values));
	},

	clearData: function(part){
		return this.set(part || 'query', '');
	}

});

URI.prototype.toString = URI.prototype.valueOf = function(){
	return this.get('value');
};

URI.regs = {
	endSlash: /\/$/,
	scheme: /^(\w+):/,
	directoryDot: /\.\/|\.$/
};

URI.base = new URI(document.getElements('base[href]', true).getLast(), {base: document.location});

String.implement({

	toURI: function(options){
		return new URI(this, options);
	}

});

/*
---

script: Element.Forms.js

description: Extends the Element native object to include methods useful in managing inputs.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Element
- /MooTools.More

provides: [Element.Forms]

...
*/

Element.implement({

	tidy: function(){
		this.set('value', this.get('value').tidy());
	},

	getTextInRange: function(start, end){
		return this.get('value').substring(start, end);
	},

	getSelectedText: function(){
		if (this.setSelectionRange) return this.getTextInRange(this.getSelectionStart(), this.getSelectionEnd());
		return document.selection.createRange().text;
	},

	getSelectedRange: function() {
		if ($defined(this.selectionStart)) return {start: this.selectionStart, end: this.selectionEnd};
		var pos = {start: 0, end: 0};
		var range = this.getDocument().selection.createRange();
		if (!range || range.parentElement() != this) return pos;
		var dup = range.duplicate();
		if (this.type == 'text') {
			pos.start = 0 - dup.moveStart('character', -100000);
			pos.end = pos.start + range.text.length;
		} else {
			var value = this.get('value');
			var offset = value.length;
			dup.moveToElementText(this);
			dup.setEndPoint('StartToEnd', range);
			if(dup.text.length) offset -= value.match(/[\n\r]*$/)[0].length;
			pos.end = offset - dup.text.length;
			dup.setEndPoint('StartToStart', range);
			pos.start = offset - dup.text.length;
		}
		return pos;
	},

	getSelectionStart: function(){
		return this.getSelectedRange().start;
	},

	getSelectionEnd: function(){
		return this.getSelectedRange().end;
	},

	setCaretPosition: function(pos){
		if (pos == 'end') pos = this.get('value').length;
		this.selectRange(pos, pos);
		return this;
	},

	getCaretPosition: function(){
		return this.getSelectedRange().start;
	},

	selectRange: function(start, end){
		if (this.setSelectionRange) {
			this.focus();
			this.setSelectionRange(start, end);
		} else {
			var value = this.get('value');
			var diff = value.substr(start, end - start).replace(/\r/g, '').length;
			start = value.substr(0, start).replace(/\r/g, '').length;
			var range = this.createTextRange();
			range.collapse(true);
			range.moveEnd('character', start + diff);
			range.moveStart('character', start);
			range.select();
		}
		return this;
	},

	insertAtCursor: function(value, select){
		var pos = this.getSelectedRange();
		var text = this.get('value');
		this.set('value', text.substring(0, pos.start) + value + text.substring(pos.end, text.length));
		if ($pick(select, true)) this.selectRange(pos.start, pos.start + value.length);
		else this.setCaretPosition(pos.start + value.length);
		return this;
	},

	insertAroundCursor: function(options, select){
		options = $extend({
			before: '',
			defaultMiddle: '',
			after: ''
		}, options);
		var value = this.getSelectedText() || options.defaultMiddle;
		var pos = this.getSelectedRange();
		var text = this.get('value');
		if (pos.start == pos.end){
			this.set('value', text.substring(0, pos.start) + options.before + value + options.after + text.substring(pos.end, text.length));
			this.selectRange(pos.start + options.before.length, pos.end + options.before.length + value.length);
		} else {
			var current = text.substring(pos.start, pos.end);
			this.set('value', text.substring(0, pos.start) + options.before + current + options.after + text.substring(pos.end, text.length));
			var selStart = pos.start + options.before.length;
			if ($pick(select, true)) this.selectRange(selStart, selStart + current.length);
			else this.setCaretPosition(selStart + text.length);
		}
		return this;
	}

});

/*
---

script: Elements.From.js

description: Returns a collection of elements from a string of html.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Element
- /MooTools.More

provides: [Elements.from]

...
*/

Elements.from = function(text, excludeScripts){
	if ($pick(excludeScripts, true)) text = text.stripScripts();

	var container, match = text.match(/^\s*<(t[dhr]|tbody|tfoot|thead)/i);

	if (match){
		container = new Element('table');
		var tag = match[1].toLowerCase();
		if (['td', 'th', 'tr'].contains(tag)){
			container = new Element('tbody').inject(container);
			if (tag != 'tr') container = new Element('tr').inject(container);
		}
	}

	return (container || new Element('div')).set('html', text).getChildren();
};

/*
---

script: Element.Delegation.js

description: Extends the Element native object to include the delegate method for more efficient event management.

credits:
- "Event checking based on the work of Daniel Steigerwald. License: MIT-style license.	Copyright: Copyright (c) 2008 Daniel Steigerwald, daniel.steigerwald.cz"

license: MIT-style license

authors:
- Aaron Newton
- Daniel Steigerwald

requires:
- core:1.2.4/Element.Event
- core:1.2.4/Selectors
- /MooTools.More

provides: [Element.Delegation]

...
*/

(function(addEvent, removeEvent){
	
	var match = /(.*?):relay\(([^)]+)\)$/,
		combinators = /[+>~\s]/,
		splitType = function(type){
			var bits = type.match(match);
			return !bits ? {event: type} : {
				event: bits[1],
				selector: bits[2]
			};
		},
		check = function(e, selector){
			var t = e.target;
			if (combinators.test(selector = selector.trim())){
				var els = this.getElements(selector);
				for (var i = els.length; i--; ){
					var el = els[i];
					if (t == el || el.hasChild(t)) return el;
				}
			} else {
				for ( ; t && t != this; t = t.parentNode){
					if (Element.match(t, selector)) return document.id(t);
				}
			}
			return null;
		};

	Element.implement({

		addEvent: function(type, fn){
			var splitted = splitType(type);
			if (splitted.selector){
				var monitors = this.retrieve('$moo:delegateMonitors', {});
				if (!monitors[type]){
					var monitor = function(e){
						var el = check.call(this, e, splitted.selector);
						if (el) this.fireEvent(type, [e, el], 0, el);
					}.bind(this);
					monitors[type] = monitor;
					addEvent.call(this, splitted.event, monitor);
				}
			}
			return addEvent.apply(this, arguments);
		},

		removeEvent: function(type, fn){
			var splitted = splitType(type);
			if (splitted.selector){
				var events = this.retrieve('events');
				if (!events || !events[type] || (fn && !events[type].keys.contains(fn))) return this;

				if (fn) removeEvent.apply(this, [type, fn]);
				else removeEvent.apply(this, type);

				events = this.retrieve('events');
				if (events && events[type] && events[type].keys.length == 0){
					var monitors = this.retrieve('$moo:delegateMonitors', {});
					removeEvent.apply(this, [splitted.event, monitors[type]]);
					delete monitors[type];
				}
				return this;
			}
			return removeEvent.apply(this, arguments);
		},

		fireEvent: function(type, args, delay, bind){
			var events = this.retrieve('events');
			if (!events || !events[type]) return this;
			events[type].keys.each(function(fn){
				fn.create({bind: bind || this, delay: delay, arguments: args})();
			}, this);
			return this;
		}

	});

})(Element.prototype.addEvent, Element.prototype.removeEvent);

/*
---

script: Element.Measure.js

description: Extends the Element native object to include methods useful in measuring dimensions.

credits: "Element.measure / .expose methods by Daniel Steigerwald License: MIT-style license. Copyright: Copyright (c) 2008 Daniel Steigerwald, daniel.steigerwald.cz"

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Element.Style
- core:1.2.4/Element.Dimensions
- /MooTools.More

provides: [Element.Measure]

...
*/

Element.implement({

	measure: function(fn){
		var vis = function(el) {
			return !!(!el || el.offsetHeight || el.offsetWidth);
		};
		if (vis(this)) return fn.apply(this);
		var parent = this.getParent(),
			restorers = [],
			toMeasure = []; 
		while (!vis(parent) && parent != document.body) {
			toMeasure.push(parent.expose());
			parent = parent.getParent();
		}
		var restore = this.expose();
		var result = fn.apply(this);
		restore();
		toMeasure.each(function(restore){
			restore();
		});
		return result;
	},

	expose: function(){
		if (this.getStyle('display') != 'none') return $empty;
		var before = this.style.cssText;
		this.setStyles({
			display: 'block',
			position: 'absolute',
			visibility: 'hidden'
		});
		return function(){
			this.style.cssText = before;
		}.bind(this);
	},

	getDimensions: function(options){
		options = $merge({computeSize: false},options);
		var dim = {};
		var getSize = function(el, options){
			return (options.computeSize)?el.getComputedSize(options):el.getSize();
		};
		var parent = this.getParent('body');
		if (parent && this.getStyle('display') == 'none'){
			dim = this.measure(function(){
				return getSize(this, options);
			});
		} else if (parent){
			try { //safari sometimes crashes here, so catch it
				dim = getSize(this, options);
			}catch(e){}
		} else {
			dim = {x: 0, y: 0};
		}
		return $chk(dim.x) ? $extend(dim, {width: dim.x, height: dim.y}) : $extend(dim, {x: dim.width, y: dim.height});
	},

	getComputedSize: function(options){
		options = $merge({
			styles: ['padding','border'],
			plains: {
				height: ['top','bottom'],
				width: ['left','right']
			},
			mode: 'both'
		}, options);
		var size = {width: 0,height: 0};
		switch (options.mode){
			case 'vertical':
				delete size.width;
				delete options.plains.width;
				break;
			case 'horizontal':
				delete size.height;
				delete options.plains.height;
				break;
		}
		var getStyles = [];
		//this function might be useful in other places; perhaps it should be outside this function?
		$each(options.plains, function(plain, key){
			plain.each(function(edge){
				options.styles.each(function(style){
					getStyles.push((style == 'border') ? style + '-' + edge + '-' + 'width' : style + '-' + edge);
				});
			});
		});
		var styles = {};
		getStyles.each(function(style){ styles[style] = this.getComputedStyle(style); }, this);
		var subtracted = [];
		$each(options.plains, function(plain, key){ //keys: width, height, plains: ['left', 'right'], ['top','bottom']
			var capitalized = key.capitalize();
			size['total' + capitalized] = size['computed' + capitalized] = 0;
			plain.each(function(edge){ //top, left, right, bottom
				size['computed' + edge.capitalize()] = 0;
				getStyles.each(function(style, i){ //padding, border, etc.
					//'padding-left'.test('left') size['totalWidth'] = size['width'] + [padding-left]
					if (style.test(edge)){
						styles[style] = styles[style].toInt() || 0; //styles['padding-left'] = 5;
						size['total' + capitalized] = size['total' + capitalized] + styles[style];
						size['computed' + edge.capitalize()] = size['computed' + edge.capitalize()] + styles[style];
					}
					//if width != width (so, padding-left, for instance), then subtract that from the total
					if (style.test(edge) && key != style &&
						(style.test('border') || style.test('padding')) && !subtracted.contains(style)){
						subtracted.push(style);
						size['computed' + capitalized] = size['computed' + capitalized]-styles[style];
					}
				});
			});
		});

		['Width', 'Height'].each(function(value){
			var lower = value.toLowerCase();
			if(!$chk(size[lower])) return;

			size[lower] = size[lower] + this['offset' + value] + size['computed' + value];
			size['total' + value] = size[lower] + size['total' + value];
			delete size['computed' + value];
		}, this);

		return $extend(styles, size);
	}

});

/*
---

script: Element.Position.js

description: Extends the Element native object to include methods useful positioning elements relative to others.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Element.Dimensions
- /Element.Measure

provides: [Elements.Position]

...
*/

(function(){

var original = Element.prototype.position;

Element.implement({

	position: function(options){
		//call original position if the options are x/y values
		if (options && ($defined(options.x) || $defined(options.y))) return original ? original.apply(this, arguments) : this;
		$each(options||{}, function(v, k){ if (!$defined(v)) delete options[k]; });
		options = $merge({
			// minimum: { x: 0, y: 0 },
			// maximum: { x: 0, y: 0},
			relativeTo: document.body,
			position: {
				x: 'center', //left, center, right
				y: 'center' //top, center, bottom
			},
			edge: false,
			offset: {x: 0, y: 0},
			returnPos: false,
			relFixedPosition: false,
			ignoreMargins: false,
			ignoreScroll: false,
			allowNegative: false
		}, options);
		//compute the offset of the parent positioned element if this element is in one
		var parentOffset = {x: 0, y: 0}, 
				parentPositioned = false;
		/* dollar around getOffsetParent should not be necessary, but as it does not return
		 * a mootools extended element in IE, an error occurs on the call to expose. See:
		 * http://mootools.lighthouseapp.com/projects/2706/tickets/333-element-getoffsetparent-inconsistency-between-ie-and-other-browsers */
		var offsetParent = this.measure(function(){
			return document.id(this.getOffsetParent());
		});
		if (offsetParent && offsetParent != this.getDocument().body){
			parentOffset = offsetParent.measure(function(){
				return this.getPosition();
			});
			parentPositioned = offsetParent != document.id(options.relativeTo);
			options.offset.x = options.offset.x - parentOffset.x;
			options.offset.y = options.offset.y - parentOffset.y;
		}
		//upperRight, bottomRight, centerRight, upperLeft, bottomLeft, centerLeft
		//topRight, topLeft, centerTop, centerBottom, center
		var fixValue = function(option){
			if ($type(option) != 'string') return option;
			option = option.toLowerCase();
			var val = {};
			if (option.test('left')) val.x = 'left';
			else if (option.test('right')) val.x = 'right';
			else val.x = 'center';
			if (option.test('upper') || option.test('top')) val.y = 'top';
			else if (option.test('bottom')) val.y = 'bottom';
			else val.y = 'center';
			return val;
		};
		options.edge = fixValue(options.edge);
		options.position = fixValue(options.position);
		if (!options.edge){
			if (options.position.x == 'center' && options.position.y == 'center') options.edge = {x:'center', y:'center'};
			else options.edge = {x:'left', y:'top'};
		}

		this.setStyle('position', 'absolute');
		var rel = document.id(options.relativeTo) || document.body,
				calc = rel == document.body ? window.getScroll() : rel.getPosition(),
				top = calc.y, left = calc.x;

		var dim = this.getDimensions({computeSize: true, styles:['padding', 'border','margin']});
		var pos = {},
				prefY = options.offset.y,
				prefX = options.offset.x,
				winSize = window.getSize();
		switch(options.position.x){
			case 'left':
				pos.x = left + prefX;
				break;
			case 'right':
				pos.x = left + prefX + rel.offsetWidth;
				break;
			default: //center
				pos.x = left + ((rel == document.body ? winSize.x : rel.offsetWidth)/2) + prefX;
				break;
		}
		switch(options.position.y){
			case 'top':
				pos.y = top + prefY;
				break;
			case 'bottom':
				pos.y = top + prefY + rel.offsetHeight;
				break;
			default: //center
				pos.y = top + ((rel == document.body ? winSize.y : rel.offsetHeight)/2) + prefY;
				break;
		}
		if (options.edge){
			var edgeOffset = {};

			switch(options.edge.x){
				case 'left':
					edgeOffset.x = 0;
					break;
				case 'right':
					edgeOffset.x = -dim.x-dim.computedRight-dim.computedLeft;
					break;
				default: //center
					edgeOffset.x = -(dim.totalWidth/2);
					break;
			}
			switch(options.edge.y){
				case 'top':
					edgeOffset.y = 0;
					break;
				case 'bottom':
					edgeOffset.y = -dim.y-dim.computedTop-dim.computedBottom;
					break;
				default: //center
					edgeOffset.y = -(dim.totalHeight/2);
					break;
			}
			pos.x += edgeOffset.x;
			pos.y += edgeOffset.y;
		}
		pos = {
			left: ((pos.x >= 0 || parentPositioned || options.allowNegative) ? pos.x : 0).toInt(),
			top: ((pos.y >= 0 || parentPositioned || options.allowNegative) ? pos.y : 0).toInt()
		};
		var xy = {left: 'x', top: 'y'};
		['minimum', 'maximum'].each(function(minmax) {
			['left', 'top'].each(function(lr) {
				var val = options[minmax] ? options[minmax][xy[lr]] : null;
				if (val != null && pos[lr] < val) pos[lr] = val;
			});
		});
		if (rel.getStyle('position') == 'fixed' || options.relFixedPosition){
			var winScroll = window.getScroll();
			pos.top+= winScroll.y;
			pos.left+= winScroll.x;
		}
		if (options.ignoreScroll) {
			var relScroll = rel.getScroll();
			pos.top-= relScroll.y;
			pos.left-= relScroll.x;
		}
		if (options.ignoreMargins) {
			pos.left += (
				options.edge.x == 'right' ? dim['margin-right'] : 
				options.edge.x == 'center' ? -dim['margin-left'] + ((dim['margin-right'] + dim['margin-left'])/2) : 
					- dim['margin-left']
			);
			pos.top += (
				options.edge.y == 'bottom' ? dim['margin-bottom'] : 
				options.edge.y == 'center' ? -dim['margin-top'] + ((dim['margin-bottom'] + dim['margin-top'])/2) : 
					- dim['margin-top']
			);
		}
		pos.left = Math.ceil(pos.left);
		pos.top = Math.ceil(pos.top);
		if (options.returnPos) return pos;
		else this.setStyles(pos);
		return this;
	}

});

})();

/*
---

script: Element.Shortcuts.js

description: Extends the Element native object to include some shortcut methods.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Element.Style
- /MooTools.More

provides: [Element.Shortcuts]

...
*/

Element.implement({

	isDisplayed: function(){
		return this.getStyle('display') != 'none';
	},

	isVisible: function(){
		var w = this.offsetWidth,
			h = this.offsetHeight;
		return (w == 0 && h == 0) ? false : (w > 0 && h > 0) ? true : this.isDisplayed();
	},

	toggle: function(){
		return this[this.isDisplayed() ? 'hide' : 'show']();
	},

	hide: function(){
		var d;
		try {
			//IE fails here if the element is not in the dom
			d = this.getStyle('display');
		} catch(e){}
		return this.store('originalDisplay', d || '').setStyle('display', 'none');
	},

	show: function(display){
		display = display || this.retrieve('originalDisplay') || 'block';
		return this.setStyle('display', (display == 'none') ? 'block' : display);
	},

	swapClass: function(remove, add){
		return this.removeClass(remove).addClass(add);
	}

});


/*
---

script: OverText.js

description: Shows text over an input that disappears when the user clicks into it. The text remains hidden if the user adds a value.

license: MIT-style license

authors:
- Aaron Newton

requires:
- core:1.2.4/Options
- core:1.2.4/Events
- core:1.2.4/Element.Event
- /Class.Binds
- /Class.Occlude
- /Element.Position
- /Element.Shortcuts

provides: [OverText]

...
*/

var OverText = new Class({

	Implements: [Options, Events, Class.Occlude],

	Binds: ['reposition', 'assert', 'focus', 'hide'],

	options: {/*
		textOverride: null,
		onFocus: $empty()
		onTextHide: $empty(textEl, inputEl),
		onTextShow: $empty(textEl, inputEl), */
		element: 'label',
		positionOptions: {
			position: 'upperLeft',
			edge: 'upperLeft',
			offset: {
				x: 4,
				y: 2
			}
		},
		poll: false,
		pollInterval: 250,
		wrap: false
	},

	property: 'OverText',

	initialize: function(element, options){
		this.element = document.id(element);
		if (this.occlude()) return this.occluded;
		this.setOptions(options);
		this.attach(this.element);
		OverText.instances.push(this);
		if (this.options.poll) this.poll();
		return this;
	},

	toElement: function(){
		return this.element;
	},

	attach: function(){
		var val = this.options.textOverride || this.element.get('alt') || this.element.get('title');
		if (!val) return;
		this.text = new Element(this.options.element, {
			'class': 'overTxtLabel',
			styles: {
				lineHeight: 'normal',
				position: 'absolute',
				cursor: 'text'
			},
			html: val,
			events: {
				click: this.hide.pass(this.options.element == 'label', this)
			}
		}).inject(this.element, 'after');
		if (this.options.element == 'label') {
			if (!this.element.get('id')) this.element.set('id', 'input_' + new Date().getTime());
			this.text.set('for', this.element.get('id'));
		}

		if (this.options.wrap) {
			this.textHolder = new Element('div', {
				styles: {
					lineHeight: 'normal',
					position: 'relative'
				},
				'class':'overTxtWrapper'
			}).adopt(this.text).inject(this.element, 'before');
		}

		this.element.addEvents({
			focus: this.focus,
			blur: this.assert,
			change: this.assert
		}).store('OverTextDiv', this.text);
		window.addEvent('resize', this.reposition.bind(this));
		this.assert(true);
		this.reposition();
	},

	wrap: function(){
		if (this.options.element == 'label') {
			if (!this.element.get('id')) this.element.set('id', 'input_' + new Date().getTime());
			this.text.set('for', this.element.get('id'));
		}
	},

	startPolling: function(){
		this.pollingPaused = false;
		return this.poll();
	},

	poll: function(stop){
		//start immediately
		//pause on focus
		//resumeon blur
		if (this.poller && !stop) return this;
		var test = function(){
			if (!this.pollingPaused) this.assert(true);
		}.bind(this);
		if (stop) $clear(this.poller);
		else this.poller = test.periodical(this.options.pollInterval, this);
		return this;
	},

	stopPolling: function(){
		this.pollingPaused = true;
		return this.poll(true);
	},

	focus: function(){
		if (this.text && (!this.text.isDisplayed() || this.element.get('disabled'))) return;
		this.hide();
	},

	hide: function(suppressFocus, force){
		if (this.text && (this.text.isDisplayed() && (!this.element.get('disabled') || force))){
			this.text.hide();
			this.fireEvent('textHide', [this.text, this.element]);
			this.pollingPaused = true;
			if (!suppressFocus){
				try {
					this.element.fireEvent('focus');
					this.element.focus();
				} catch(e){} //IE barfs if you call focus on hidden elements
			}
		}
		return this;
	},

	show: function(){
		if (this.text && !this.text.isDisplayed()){
			this.text.show();
			this.reposition();
			this.fireEvent('textShow', [this.text, this.element]);
			this.pollingPaused = false;
		}
		return this;
	},

	assert: function(suppressFocus){
		this[this.test() ? 'show' : 'hide'](suppressFocus);
	},

	test: function(){
		var v = this.element.get('value');
		return !v;
	},

	reposition: function(){
		this.assert(true);
		if (!this.element.isVisible()) return this.stopPolling().hide();
		if (this.text && this.test()) this.text.position($merge(this.options.positionOptions, {relativeTo: this.element}));
		return this;
	}

});

OverText.instances = [];

$extend(OverText, {

	each: function(fn) {
		return OverText.instances.map(function(ot, i){
			if (ot.element && ot.text) return fn.apply(OverText, [ot, i]);
			return null; //the input or the text was destroyed
		});
	},
	
	update: function(){

		return OverText.each(function(ot){
			return ot.reposition();
		});

	},

	hideAll: function(){

		return OverText.each(function(ot){
			return ot.hide(true, true);
		});

	},

	showAll: function(){
		return OverText.each(function(ot) {
			return ot.show();
		});
	}

});

if (window.Fx && Fx.Reveal) {
	Fx.Reveal.implement({
		hideInputs: Browser.Engine.trident ? 'select, input, textarea, object, embed, .overTxtLabel' : false
	});
}

/*
---

script: Fx.Slide.js

description: Effect to slide an element in and out of view.

license: MIT-style license

authors:
- Valerio Proietti

requires:
- core:1.2.4/Fx Element.Style
- /MooTools.More

provides: [Fx.Slide]

...
*/

Fx.Slide = new Class({

	Extends: Fx,

	options: {
		mode: 'vertical',
		wrapper: false,
		hideOverflow: true
	},

	initialize: function(element, options){
		this.addEvent('complete', function(){
			this.open = (this.wrapper['offset' + this.layout.capitalize()] != 0);
			if (this.open) this.wrapper.setStyle('height', '');
			if (this.open && Browser.Engine.webkit419) this.element.dispose().inject(this.wrapper);
		}, true);
		this.element = this.subject = document.id(element);
		this.parent(options);
		var wrapper = this.element.retrieve('wrapper');
		var styles = this.element.getStyles('margin', 'position', 'overflow');
		if (this.options.hideOverflow) styles = $extend(styles, {overflow: 'hidden'});
		if (this.options.wrapper) wrapper = document.id(this.options.wrapper).setStyles(styles);
		this.wrapper = wrapper || new Element('div', {
			styles: styles
		}).wraps(this.element);
		this.element.store('wrapper', this.wrapper).setStyle('margin', 0);
		this.now = [];
		this.open = true;
	},

	vertical: function(){
		this.margin = 'margin-top';
		this.layout = 'height';
		this.offset = this.element.offsetHeight;
	},

	horizontal: function(){
		this.margin = 'margin-left';
		this.layout = 'width';
		this.offset = this.element.offsetWidth;
	},

	set: function(now){
		this.element.setStyle(this.margin, now[0]);
		this.wrapper.setStyle(this.layout, now[1]);
		return this;
	},

	compute: function(from, to, delta){
		return [0, 1].map(function(i){
			return Fx.compute(from[i], to[i], delta);
		});
	},

	start: function(how, mode){
		if (!this.check(how, mode)) return this;
		this[mode || this.options.mode]();
		var margin = this.element.getStyle(this.margin).toInt();
		var layout = this.wrapper.getStyle(this.layout).toInt();
		var caseIn = [[margin, layout], [0, this.offset]];
		var caseOut = [[margin, layout], [-this.offset, 0]];
		var start;
		switch (how){
			case 'in': start = caseIn; break;
			case 'out': start = caseOut; break;
			case 'toggle': start = (layout == 0) ? caseIn : caseOut;
		}
		return this.parent(start[0], start[1]);
	},

	slideIn: function(mode){
		return this.start('in', mode);
	},

	slideOut: function(mode){
		return this.start('out', mode);
	},

	hide: function(mode){
		this[mode || this.options.mode]();
		this.open = false;
		return this.set([-this.offset, 0]);
	},

	show: function(mode){
		this[mode || this.options.mode]();
		this.open = true;
		return this.set([0, this.offset]);
	},

	toggle: function(mode){
		return this.start('toggle', mode);
	}

});

Element.Properties.slide = {

	set: function(options){
		var slide = this.retrieve('slide');
		if (slide) slide.cancel();
		return this.eliminate('slide').store('slide:options', $extend({link: 'cancel'}, options));
	},

	get: function(options){
		if (options || !this.retrieve('slide')){
			if (options || !this.retrieve('slide:options')) this.set('slide', options);
			this.store('slide', new Fx.Slide(this, this.retrieve('slide:options')));
		}
		return this.retrieve('slide');
	}

};

Element.implement({

	slide: function(how, mode){
		how = how || 'toggle';
		var slide = this.get('slide'), toggle;
		switch (how){
			case 'hide': slide.hide(mode); break;
			case 'show': slide.show(mode); break;
			case 'toggle':
				var flag = this.retrieve('slide:flag', slide.open);
				slide[flag ? 'slideOut' : 'slideIn'](mode);
				this.store('slide:flag', !flag);
				toggle = true;
			break;
			default: slide.start(how, mode);
		}
		if (!toggle) this.eliminate('slide:flag');
		return this;
	}

});


/*
---

script: Date.English.US.js

description: Date messages for US English.

license: MIT-style license

authors:
- Aaron Newton

requires:
- /Lang
- /Date

provides: [Date.English.US]

...
*/

MooTools.lang.set('en-US', 'Date', {

	months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
	days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
	//culture's date order: MM/DD/YYYY
	dateOrder: ['month', 'date', 'year'],
	shortDate: '%m/%d/%Y',
	shortTime: '%I:%M%p',
	AM: 'AM',
	PM: 'PM',

	/* Date.Extras */
	ordinal: function(dayOfMonth){
		//1st, 2nd, 3rd, etc.
		return (dayOfMonth > 3 && dayOfMonth < 21) ? 'th' : ['th', 'st', 'nd', 'rd', 'th'][Math.min(dayOfMonth % 10, 4)];
	},

	lessThanMinuteAgo: 'less than a minute ago',
	minuteAgo: 'about a minute ago',
	minutesAgo: '{delta} minutes ago',
	hourAgo: 'about an hour ago',
	hoursAgo: 'about {delta} hours ago',
	dayAgo: '1 day ago',
	daysAgo: '{delta} days ago',
	weekAgo: '1 week ago',
	weeksAgo: '{delta} weeks ago',
	monthAgo: '1 month ago',
	monthsAgo: '{delta} months ago',
	yearAgo: '1 year ago',
	yearsAgo: '{delta} years ago',
	lessThanMinuteUntil: 'less than a minute from now',
	minuteUntil: 'about a minute from now',
	minutesUntil: '{delta} minutes from now',
	hourUntil: 'about an hour from now',
	hoursUntil: 'about {delta} hours from now',
	dayUntil: '1 day from now',
	daysUntil: '{delta} days from now',
	weekUntil: '1 week from now',
	weeksUntil: '{delta} weeks from now',
	monthUntil: '1 month from now',
	monthsUntil: '{delta} months from now',
	yearUntil: '1 year from now',
	yearsUntil: '{delta} years from now'

});
