#
# Load and handle CSV Files.
#
# author: Remo Giermann
# created: 2012/02/07
#

def load(fp, delim=';', remove='"\n', keys=0, charset=None):
	"""
	Generate dictionary from an open file 'fp'.

	Arguments:
	 delim   delimiter between data fields
	 remove  an iterable of characters to remove from data
	 keys    row index or list of strings to use as 
	         field captions/dictionary keys
	 charset charset to decode from.
	"""

	csv = list(fp)
	for r in remove:
		csv = map(lambda s: s.replace(r, ""), csv)
	
	if charset:
		csv = map(lambda s: s.decode(charset), csv)

	csv = map(lambda s: s.split(delim), csv)

	if hasattr(keys, "__iter__"):
		captions = keys[:]
	elif type(keys) == int:
		captions = csv[keys]
		csv = csv[:keys]+csv[keys+1:]
	
	csv = [[(captions[i], row[i]) for i in range(len(captions))] for row in csv]
	return map(dict, csv)

def dump(ds, fp=None, delim=";", fieldnames=True, quotes='"'):
	"""
	Dump a list of dicts 'ds'.

	Arguments:
	 fp          File to write to or, if None, return string
	 delim       Delimiter between fields
	 fieldnames  write fieldnames as first line
	 quotes      Quotes to use for values, if any
	"""
	enquote    = lambda s:  quotes+s+quotes
	fieldnames = lambda: ds[0].keys()
	values     = lambda: [d.values() for d in ds] 
	
	text  = [fieldnames()]
	text += values()

	text = [map(enquote, s) for s in text]
	text = [delim.join(line)+'\n' for line in text]
	
	if fp is not None:
		fp.writelines(text)
	else:
		return text

def apply(ds, column, func, *args, **kwargs):
	""" Apply a function to 'column' of dataset. """
	map(lambda d: d.update({column: func(d[column], *args, **kwargs)}), ds)

def delete(ds, column):
	""" Remove a column from data set. """
	map(lambda d: d.pop(column), ds)

def append(ds, column, default=''):
	""" Add a column to data set. """
	map(lambda d: d.update({column: default}), ds)

def dumpjson(*args, **kwargs):
	import json
	return json.dump(*args, **kwargs)

def loadjson(*args, **kwargs):
	import json
	return json.load(*args, **kwargs)

def dumpyaml(*args, **kwargs):
	import yaml
	return yaml.dump(*args, **kwargs)

def loadyaml(*args, **kwargs):
	import yaml
	return yaml.load(*args, **kwargs)
