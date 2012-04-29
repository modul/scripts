#
# pluto
#
# Some datetime plotting utilities.
#
# author: Remo Giermann
# created: 2012/01/03
#


import matplotlib.pyplot as plt
from matplotlib.pyplot import show,\
     NullFormatter, FormatStrFormatter, \
     FixedFormatter, NullLocator, \
     AutoLocator
from matplotlib.dates import date2num, num2date, \
     DateFormatter, WeekdayLocator, \
     MonthLocator, DayLocator, \
     HourLocator, MinuteLocator, \
     AutoDateFormatter, AutoDateLocator, \
     MO, TU, WE, TH, FR, SA, SU
from scipy import linspace
from scipy.interpolate import interp1d
from datetime import datetime, timedelta


DATE_FORMAT = "%y/%m/%d"
DATETIME_FORMAT = "%y/%m/%d %H:%M"

now   = datetime.now
today = now
yesterday = lambda: today() - timedelta(days=1)
tomorrow  = lambda: today() + timedelta(days=1)

def argslist(arg, *args):
	"""
	returns a combined list of arguments.
	'arg' might be a sequence.

	>>> argslist(0)
	[0]
	>>> argslist([0, 1], 2, [3])
	[0, 1, 2, [3]]
	"""
	if type(arg) in (list, tuple):
		arg = list(arg)
		arg.extend(args)
		return arg
	if len(args) > 0:
		args = list(args)
		args.insert(0, arg)
		return args
	return [arg]

def to_seconds(delta):
	""" timedelta(...) -> int seconds """
	return delta.seconds + delta.days*24*60*60

def to_minutes(delta):
	""" timedelta(...) -> float minutes """
	return to_seconds(delta)/60.

def to_hours(delta):
	""" timedelta(...) -> float hours """
	return to_minutes(delta)/60.

def to_days(delta):
	""" timedelta(...) -> float days """
	return to_hours(delta)/24.

def hours(n):
	""" returns timedelta(hours=n) instance """
	return timedelta(hours=n)

def days(n):
	""" returns timedelta(days=n) instance """
	return timedelta(days=n)

def settime(date=None, hour=0, minute=0, second=0):
	"""
	resets the time spec of a datetime object 'date'.
	defaults to today 00:00:00 hours.
	"""
	date = date or today()
	return datetime(date.year, date.month, date.day, hour, minute, second)

def fixtime(n=0, hour=0, minute=0, second=0):
	"""
	returns a function that resets the time spec of
	its argument number 'n'.
	"""
	def fix(arg, *args):
		d = argslist(arg, *args)[n]
		return settime(d, hour, minute, second)
	return fix

def centered(date=None, margin=hours(12)):
	"""
	returns two dates, centered around 'date' (today if None).
	"""
	date = date or settime(today(), hour=12, minute=0)
	return date-margin, date+margin

def distance(seq):
	return max(seq)-min(seq)

def timeofday(date):
	"""
	returns the decimal time of day from 'date'
	"""
	return date.hour + date.minute/60.

def first(arg, *args):
	"""
	returns the first of n values or a sequence.
	"""
	return argslist(arg, *args)[0]

def last(arg, *args):
	"""
	returns the last of n values or a sequence.
	"""
	return argslist(arg, *args)[-1]

def average(arg, *args):
	"""
	returns the average of n values or a sequence.
	"""
	args = argslist(arg, *args)
	return min(args) + distance(args)/2

def median(arg, *args):
	"""
	returns the median of n values or a sequence.
	"""
	data = sorted(seq)
	n = len(data)
	m = n/2
	if n%2 == 0:
		return average(data[m-1], data[m])
	else:
		return data[m]

def matchyear(seq, date):
	"""
	returns datetime objects from 'seq'
	for which 'date' matches up to the year.
	"""
	match = lambda d: d.year == date.year
	return filter(match, seq)

def matchmonth(seq, date):
	"""
	returns datetime objects from 'seq'
	for which 'date' matches up to the month.
	"""
	match = lambda d: d.month == date.month
	return filter(match, matchyear(seq, date))

def matchday(seq, date):
	"""
	returns datetime objects from 'seq'
	for which 'date' matches up to the day.
	"""
	match = lambda d: d.day == date.day
	return filter(match, matchmonth(seq, date))

def matchhour(seq, date):
	"""
	returns datetime objects from 'seq'
	for which 'date' matches up to the hour.
	"""
	match = lambda d: d.hour == date.hour
	return filter(match, matchday(seq, date))

def pick(seq, start, end):
	"""
	pick a chunk of data from 'seq'
	which is between 'start' and 'end'.
	"""
	match = lambda d: d >= start and d <= end
	return filter(match, seq)

def around(seq, date, margin=days(1)):
	"""
	pick a chunk of data from 'seq'
	which is centered around 'date'.
	"""
	return pick(seq, *centered(date, margin))

def interdates(seq, win=2):
	"""
	calculates dates in between for 'seq'.
	"""
	x = map(date2num, seq)
	xn = linspace(x[0], x[-1], len(x)*win)
	return map(num2date, xn)

def intervalues(x, y, win=2, kind='cubic'):
	"""
	interpolates x (dates) and y values.
	"""
	xnum = map(date2num, x)
	xnew = interdates(x, win)
	yfun = interp1d(xnum, y, kind=kind)
	return xnew, yfun(map(date2num, xnew))

def buckets(seq, filt=matchday):
	"""
	sorts data from 'seq' into seperate lists
	using 'filt' to match similar data.

	helper functions for 'filt':
	 matchhour, matchday, matchmonth, matchyear
	"""
	if len(seq) == 0:
		return [[]]
	
	data = sorted(seq)
	slots = [filt(data, data[0])]
	
	if len(data) == 1:
		return slots

	for datum in data[1:]:
		if datum not in slots[-1]:
			slots.append(filt(data, datum))
	return slots

def count(seq, by=matchday, which=average):
	"""
	organizes the sequence of dates using the filter
	'by' and counts occurrences. 
	'which' chooses the correlating date for the count.

	helper functions for 'by':
	 matchhour, matchday, matchmonth, matchyear
	
	helper functions for 'which':
	 median, average, first, last
	"""
	c = buckets(seq, by)
	return ([which(data) for data in c], [len(data) for data in c])

def meantime(seq, conv=to_minutes, which=average, interval=1, offset=0):
	"""
	calculates the meantime between consecutive dates in 'seq'.
	the function 'which' picks a date out of two to correlate
	the time. 'conv' converts a timedelta object to a number.

	'interval' controls which items to compare.
	interval=1 measures time between each item, interval=2
	between pairs, interval=4 between each second pair, etc.

	'offset' can be used to start calculating later in
	the sequence. skips first n values.

	helper functions for 'which':
	 average, first, last

	helper functions for 'conv':
	 to_seconds, to_minutes, to_hours, to_days
	"""
	date = []
	dur = []
	if len(seq) == 1:
		return ([seq[0]], [0])
	for i in range(offset+1, len(seq), interval):
		one, two = seq[i-1], seq[i]
		date.append(which(one, two))
		dur.append(conv(two-one))
	return (date, dur)

def duration(seq, conv=to_minutes, which=average, offset=0):
	"""
	calculates the duration between	pairs of dates in 'seq'.
	this is a shortcut to 
	 meantime(seq, conv, which, offset=offset, interval=2)
	
	helper functions for 'which':
	 average, first, last

	helper functions for 'conv':
	 to_seconds, to_minutes, to_hours, to_days
	"""
	return meantime(seq, conv, which, offset=offset, interval=2)

def combined(what, seq, filt=matchday, xreduce=average, yreduce=average, **kwargs):
	"""
	'what' is applied to the whole dataset 'seq'
	(passing **kwargs), which should return two lists 
	x and y.
	x gets sorted using 'filt' into separate lists from 
	which each gets reduced to a single value using the 
	function 'xreduce'.
	corresponding values from the y get reduced by applying
	'yreduce' and two sequences are returned.

	helper functions for 'filt':
	 matchhour, matchday, matchmonth, matchyear
	
	helper functions for 'which':
	 average, median, first, last
	"""
	x, y = what(seq, **kwargs)
	slots = buckets(x, filt)
	xnew = [xreduce(date) for date in slots]
	ynew = [yreduce([y[x.index(datum)] for datum in slot]) for slot in slots]
	return xnew, ynew

def separately(what, seq, filt=matchday, xreduce=average, yreduce=average, **kwargs):
	"""
	'seq' is first sorted into separate lists using
	'filt'. the function 'what' is applied (passing **kwargs)
	to each of the lists. This should return 2 lists x and y 
	which are reduced using the functions 'xreduce' and 
	'yreduce' and the two resulting sequences are returned.

	This is for instance useful for calculating 
	the meantime separately per day.
	Data is first organized in daily buckets, meantime()
	gets applied separately and the result gets averaged.

	Calculating the meantime on the whole dataset
	and later reducing it to averages per day would
	give a slightly different result (which could be
	wanted, though).
	"""
	data = buckets(seq, filt=filt)
	results = map(lambda x: what(x, **kwargs), data)
	x = [xreduce(r[0]) for r in results]
	y = [yreduce(r[1]) for r in results]
	return x, y
	
def baseplot(x, y, fmt='b.',
	 figure=None, subplot=111, grid=True,
	 sharex=None, sharey=None,
	 xmajloc=AutoDateLocator(), xminloc=AutoDateLocator(), 
	 xmajfmt=None, xminfmt=NullFormatter(), 
         fmtxdata=DateFormatter("%F"), fmtydata=None,
	 fill_between={"facecolor": "blue", "alpha": 0.08},
	 **kwargs
	 ):
	"""
	prepares and sets options to plot dates,
	returns matplotlib.figure and matplotlib.axes

	Arguments
	---------
	x             x data (sequence of datetime objects)
	y             y data

	fmt           plot format as understood by matplotlib.plot()
	              default: "b."
	figure        passed to matplotlib.figure, default: None
	subplot       passed to matplotlib.subplot, default: 111
	grid          boolean, turns grid on/off
	sharex        matplotlib.axes object to share x axis with (None)
	sharey        matplotlib.axes object to share y axis with (None)
	
	xmajloc       matplotlib Locator instance to set as 
	              x axis major locator, default: AutoDateLocator
	
	xminloc       matplotlib Locator instance to set as
	              x axis minor locator, default: AutoDateLocator
	
	xmajfmt       matplotlib Formatter or similar to set as
	              x axis major formatter, default: None (->AutoDateFormatter)
	
	xminfmt       matplotlib Formatter or similar to set as
		      x axis minor formatter, default: NullFormatter
	
	fmtxdata      matplotlib Formatter or similar to set as
		      x coordinates formatter, default: DateFormatter(%F)
	
	fmtydata      matplotlib Formatter or similar to set as
	              y coordinates formatter
	
	fill_between  dictionary passed as keyword arguments 
	              to matplotlib.axes.fill_between,
		      default: {"facecolor": "blue", "alpha": 0.08}

	----------------------------------------------
	Any other keyword argument is passed on 
	to matplotlib.pyplot.plot_date().
	----------------------------------------------
	"""

	fig = plt.figure(figure)
	ax = fig.add_subplot(subplot, sharex=sharex, sharey=sharey)
	ax.plot_date(x, y, fmt, **kwargs)

	if len(filter(lambda x: type(x) == int, y)) == len(y):
		ax.set_ylim([0, max(y)+1])
		fmtydata = fmtydata or FormatStrFormatter("%i")
	else:
		ax.set_ylim([0, max(y)+max(y)/10.])
		fmtydata = fmtydata or FormatStrFormatter("%.1f")

	ax.set_xlim(([x[0], x[-1]]))
	ax.grid(grid)

	formatter = AutoDateFormatter(xmajloc)
	formatterscale = {100000 : '%Y',
			  360.0  : '%b %y',
			  90.0   : '%b',
			  29.0   : '%b %d',
			   1/24. : '%H:%M',
			  }
	formatter.scaled = formatterscale
	xmajfmt = xmajfmt or formatter

	ax.xaxis.set_major_locator(xmajloc)
	ax.xaxis.set_minor_locator(xminloc)
	ax.xaxis.set_major_formatter(xmajfmt)
	ax.xaxis.set_minor_formatter(xminfmt)
	ax.fmt_xdata = fmtxdata
	ax.fmt_ydata = fmtydata

	if fill_between and len(fill_between) > 0:
		ax.fill_between(x, y, **fill_between)

	fig.autofmt_xdate()

	return fig, ax

def plot(x, y, 
	 title="{start} -- {end}", tfmt="%e %b %y", 
	 xlabel='', ylabel="Value",
	 **kwargs):
	"""
	Plots date-based data nicely by setting arguments for baseplot()
	and adding some labels.

	Arguments
	---------
	x   sequence holding datetime objects
	y   correlating values

	title   string to set as title
	        '{start}' and '{end}' can be used and 
		will be replaced with the start and end
		date found in 'x'

	tfmt    date format string to convert {start}, {end}
	        in 'title'; if 'tfmt' is a string, the format
		is used for both dates; 'tfmt' might also
		be a 2-item tuple to give different format
		strings for {start} and {end} resp.
	
	xlabel  string to set as x-axis label
	ylabel  string to set as y-axis label

	------------------------------------------------------
	Any other keyword argument is passed on to baseplot().
	------------------------------------------------------
	"""
	if len(x) <= 2:
		print "not enough data to plot"
		return
	start, end = x[0], x[-1]
	span = end-start

	if start == end:
		print "insufficient differing data to plot"
		return

	kwds = {"xmajloc": AutoDateLocator()}

	if span.days < 3:
		kwds = {"xminloc":  HourLocator(),
		       "fmtxdata": DateFormatter("%a %H:%M")
		       }
		tfmt = "%a, %e %b %y"
		title = "{start}"
		start = median(x)

	elif span.days <= 5:
		kwds = {"xmajfmt": DateFormatter("%a %e"),
			"xminloc": HourLocator(),
			"fmtxdata": DateFormatter("%F, %a %Hh"),
		       }

	elif span.days <= 30:
		kwds = {"xminloc": HourLocator(byhour=[0,6,12,18]),
		        "fmtxdata": DateFormatter("%F, %a %Hh"),
		       }

	elif span.days <= 60:
		kwds = {"xminloc": DayLocator(),
			"fmtxdata": DateFormatter("%F, %a")
		       }

	elif span.days <= 300:
		kwds = {"xminloc": WeekdayLocator(byweekday=MO)}

	elif span.days <= 450:
		kwds = {"xminloc": WeekdayLocator(byweekday=MO)}
		tfmt = "%Y"
		title = "{start}"
		start = median(x)

	else:
		kwds = {"xminloc": MonthLocator()}
		tfmt = "%Y"
		title = "{start} - {end}"

	kwds.update(kwargs)
	fig, ax = baseplot(x, y, **kwds)

	if type(tfmt) == str:
		s = start.strftime(tfmt)
		e = end.strftime(tfmt)
	elif type(tfmt) in (list, tuple) and len(tfmt) > 1:
		s = start.strftime(tfmt[0])
		e = start.strftime(tfmt[1])
	else:
		s = start
		e = start

	plt.title(title.format(start=s, end=e))
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)

	return fig, ax

def interpolated(x, y, win=5, kind='cubic', interpfmt='b-', **kwargs):
	"""
	plots (x, y) data points and an interpolated line on top.

	'win' and 'kind' are options to intervalues().
	'interpfmt' is the plotting format string for the 
	interpolation. **kwargs is passed to plot()
	where 'fmt' is only applied to the data plot
	and 'fill_between' only to the interpolated line.
	"""
	fillbetween = kwargs.pop("fill_between", {"facecolor": "blue", "alpha": 0.1})
	pointfmt    = kwargs.pop("fmt", "b.")
	figure      = kwargs.pop("figure", "Interpolated")
	subplot     = kwargs.pop("subplot", 111)

	pointkwds = {"figure": figure, 
		    "subplot": subplot, 
		    "fmt": pointfmt,
		    "fill_between": None
		    }

	interkwds = {"fmt": interpfmt,
		    "fill_between": fillbetween
	 	    }

	kwargs.update(pointkwds)
	fa = plot(x, y, **kwargs)
	kwargs.update(interkwds)
	plot(*intervalues(x, y, win=win, kind=kind), **kwargs)
	return fa

def read(filename, start=None, end=None, fmt=DATETIME_FORMAT):
	"""
	reads dates from 'filename' and returns 
	datetime objects ranging from 'start' to 'end'.
	"""
	dates = list(open(filename))
	dates = [x for x in dates if not x.isspace()]
	dates = map(lambda x: x.strip(), dates)
	dates = map(lambda x: datetime.strptime(x, fmt), dates)
	dates.sort()

	start = start or dates[0]
	end   = end or dates[-1]

	data = pick(dates, start, end)

	if len(data) <= 2:
		print "no data between", start, "and", end
		return ([], [])
	elif data[0] > start or data[-1] < end:
		rstart, rend = data[0], data[-1]
		diff = (rend-rstart) - (end-start)
		if abs(diff.days) > 2:
			diff = "{d:+.1f}d".format(d=to_days(diff))
		else:
			diff = "{d:+.1f}h".format(d=to_hours(diff))
		msg = "insufficient data, shrunk to {s} ... {e} ({d})"
		print msg.format(s=rstart, e=rend, d=diff)
	else:
		print "read", len(data), "fnords"

	return data

def write(seq, filename, mode='w', fmt=DATETIME_FORMAT, lineend='\n'):
	"""
	converts datetime objects from 'seq' using 'fmt'
	and writes them to 'filename'.
	"""
	fd = open(filename, mode)
	dates = [datetime.strftime(x, fmt) + lineend for x in seq]
	fd.writelines(dates)
	fd.close()

def prind(x, y=None, unit='', fmt="{date} {value: 1.1f}{unit}"): 
	"""
	prints dates ('x') and values ('y'), if any.
	"""
	if y is None:
		for date in x:
			print date
	elif type(y) in (tuple, list):
		if len(y) == len(x):
			for i in range(len(x)):
				print fmt.format(date=x[i], value=y[i], unit=unit)
		else:
			print "list lengths don't match."

