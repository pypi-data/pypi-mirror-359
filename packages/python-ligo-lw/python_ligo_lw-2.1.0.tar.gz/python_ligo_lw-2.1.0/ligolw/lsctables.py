# Copyright (C) 2006--2022,2024--2025  Kipp Cannon
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#


"""
LSC Table definitions.

See the LDAS CVS repository at
http://www.ldas-sw.ligo.caltech.edu/cgi-bin/cvsweb.cgi/ldas/dbms/db2/sql
for more information.
"""


import cmath
import functools
import itertools
import math
import numpy
import operator
import os
import socket
import time


try:
	from ligo import segments
except ImportError:
	# try Duncan and Leo's forked version
	import igwn_segments as segments
import lal
from lal import LIGOTimeGPS
from .version import __author__, __date__, __version__
import ligolw


# NOTE:  some table definitions below make the comment that they are using
# indexes where a primary key constraint would be more appropirate.  in
# those cases, the ID column in question refers to IDs in other tables
# (typically the process table) and they cannot be declared to be primary
# keys, even if they would be unique, because sqlite does not allow primary
# key values to be modified.  the values might need to be changed after the
# table to which they refer is populated and its rows have had their IDs
# reassigned to avoid conflicts with pre-existing data in the database.
# that problem can potentially be fixed by populating tables in the correct
# order, but because calling code can declare its own custom tables it's
# not clear that such a solution would be robust or even guaranteed to
# always be possible.  another solution might be to re-assign all IDs in
# all tables in RAM before inserting any rows into the database, but that
# creates a scaling limitation wherein each document individually must be
# small enough to be held in in memory in its entirety, which is not
# currently a limitation the code has.  I think, in practice, documents
# that are too large to hold in memory are also too large to work with
# conveniently so it's unlikely there are any existing use cases where
# imposing that limit would be a problem.  in the meantime, we use indexes
# in these cases instead of primary keys.


#
# =============================================================================
#
#                            Convenience Functions
#
# =============================================================================
#


def HasNonLSCTables(elem):
	"""
	Return a tuple of the names of the tables in the document tree
	below element that are not LSC tables.
	"""
	return tuple(t.Name for t in elem.getElementsByTagName(ligolw.Table.tagName) if t.Name not in ligolw.Table.TableByName)


class instrumentsproperty(object):
	def __init__(self, name):
		self.name = name

	@staticmethod
	def get(instruments):
		"""
		Parse the values stored in the "ifos" and "instruments"
		columns found in many tables.  This function is mostly for
		internal use by the .instruments properties of the
		corresponding row classes.

		If the input is None, then the output is None.  Otherwise,
		the input is split on ",", the resulting strings stripped
		of leading and trailing whitespace, and the sequence of
		non-zero length strings that remain is returned as a set
		(orderless sequence, with unique elements).

		NOTE:  in the past, many tools relied on the convention
		that instrument names be exactly 2 characters long, and so
		sets of instruments were represented by simply
		concatenating the names as there was no ambiguity in how to
		split the result back into a collection of names.  For a
		while, some tools encoded sets of instrument names by
		delimiting them with a "+" character.  This decoder used to
		support all of these encodings, including the modern
		","-delimited encoding, by using a complex heuristic set of
		rules to auto-select the correct decode algorithm.  Because
		this operation is performend an enormous number of times
		when processing typical documents, this eventually proved
		to be a significant performance burden.  For this reason,
		this code now only supports the ","-delimited encoding.
		For over a decade, the corresponding encoder in this
		library has only generated documents using the
		","-delimited encoding, so there should no longer be any
		documents in active use that rely on one of the older
		encodings.  However, if you find yourself trying to read a
		very old document be aware that instrument name sets stored
		in the document might not be decoded the way the original
		tool that wrote the document intended, and you should be
		aware of the possible need to do some format translation.
		There will be no warning or error message:  documents using
		obsolete encodings will appear to be valid documents, the
		strings will simply be mistaken for unusual instrument
		names, as shown below in some examples.

		Example:

		>>> assert instrumentsproperty.get(None) is None
		>>> assert instrumentsproperty.get("") == set([])
		>>> assert instrumentsproperty.get("  ,  ,,") == set([])
		>>> assert instrumentsproperty.get("H1") == set(['H1'])
		>>> assert instrumentsproperty.get("H1,") == set(['H1'])
		>>> assert instrumentsproperty.get("H1,L1") == set(['H1', 'L1'])
		>>> assert instrumentsproperty.get("H1L1") == set(['H1L1'])
		>>> assert instrumentsproperty.get("H1+L1") == set(['H1+L1'])
		"""
		if instruments is None:
			return None
		instruments = set(instrument.strip() for instrument in instruments.split(","))
		instruments.discard("")
		return instruments

	@staticmethod
	def set(instruments):
		"""
		Convert an iterable of instrument names into a value
		suitable for storage in the "ifos" or "instruments" columns
		found in many tables.  This function is mostly for internal
		use by the .instruments properties of the corresponding row
		classes.  The input must be None or an iterable of zero or
		more instrument names, none of which may be zero-length,
		contain whitespace, or contain "," characters.  The output
		is a single string containing the unique instrument names
		concatenated using "," as a delimiter.  instruments will
		only be iterated over once and so can be a generator
		expression.

		NOTE:  for performance reasons, because of the large number
		of times this operation is performed when processing a
		typical document, very little error checking is performed.
		If any of the instrument names fail to meet the criteria
		listed above, that fact will typically go unnoticed.  The
		document that results will be decodable, under no
		circumstances will an unreadable document be generated, but
		what form the decoded instruments string takes is
		undefined.

		Example:

		>>> print(instrumentsproperty.set(None))
		None
		>>> assert instrumentsproperty.set(()) == ''
		>>> assert instrumentsproperty.set(("H1",)) == 'H1'
		>>> assert instrumentsproperty.set(("H1","H1","H1")) == 'H1'
		>>> assert instrumentsproperty.set(("H1","L1")) == 'H1,L1'
		>>> assert instrumentsproperty.set(("SWIFT",)) == 'SWIFT'
		>>> assert instrumentsproperty.set(("H1L1",)) == 'H1L1'
		"""
		return None if instruments is None else ",".join(sorted(set(instruments)))

	def __get__(self, obj, cls = None):
		return self.get(getattr(obj, self.name))

	def __set__(self, obj, instruments):
		setattr(obj, self.name, self.set(instruments))


class gpsproperty(object):
	"""
	Descriptor used internally to implement LIGOTimeGPS-valued
	properties using pairs of integer attributes on row objects, one
	for the integer seconds part of the GPS time and one for the
	integer nanoseconds part.

	Non-LIGOTimeGPS values are converted to LIGOTimeGPS before encoding
	them into the integer attributes.  None is allowed as a special
	case, which is encoded by setting both column attributes to None.

	For the purpose of representing the boundaries of unbounded
	segments (open-ended time intervals), +inf and -inf are also
	allowed, and will be encoded into and decoded out of the integer
	attributes.  To do so, a non-standard encoding is used that makes
	use of denormalized GPS times, that is times whose nanosecond
	component has a magnitude greater than 999999999.  Two such values
	are reserved for +/- infinity.  To guard against the need for
	additional special encodings in the future, this descriptor
	reserves all denormalized values and will not allow calling code to
	set GPS times to those values.  Calling code must provide
	normalized GPS times, times with nanosecond components whose
	magnitudes are not greater than 999999999.  When decoded, the
	values reported are segments.PosInfinity or segments.NegInfinity.
	"""
	def __init__(self, s_name, ns_name):
		self.s_name = s_name
		self.get_s = operator.attrgetter(s_name)
		self.ns_name = ns_name
		self.get_ns = operator.attrgetter(ns_name)

	posinf = 0x7FFFFFFF, 0xFFFFFFFF
	neginf = 0xFFFFFFFF, 0xFFFFFFFF
	infs = posinf, neginf

	def __get__(self, obj, cls = None):
		s = self.get_s(obj)
		ns = self.get_ns(obj)
		if s is None and ns is None:
			return None
		if ns == 0xFFFFFFFF:
			if (s, ns) == self.posinf:
				return segments.PosInfinity
			elif (s, ns) == self.neginf:
				return segments.NegInfinity
			raise ValueError("unrecognized denormalized number LIGOTimeGPS(%d,%d)" % (s, ns))
		return LIGOTimeGPS(s, ns)

	def __set__(self, obj, gps):
		if gps is None:
			s = ns = None
		elif isinstance(gps, segments.infinity) or math.isinf(gps):
			if gps > 0:
				s, ns = self.posinf
			elif gps < 0:
				s, ns = self.neginf
			else:
				raise ValueError(gps)
		else:
			try:
				s = gps.gpsSeconds
				ns = gps.gpsNanoSeconds
			except AttributeError:
				# try converting and going again
				return self.__set__(obj, LIGOTimeGPS(gps))
			if abs(ns) > 999999999:
				raise ValueError("denormalized LIGOTimeGPS not allowed: LIGOTimeGPS(%d, %d)" % (s, ns))
		setattr(obj, self.s_name, s)
		setattr(obj, self.ns_name, ns)


class gpsproperty_with_gmst(gpsproperty):
	"""
	Variant of the gpsproperty descriptor, adding support for a third
	"GMST" column.  When assigning a time to the GPS-valued descriptor,
	after the pair of integer attributes are set to the encoded form of
	the GPS time, the value is retrieved and the GMST column is set to
	the Greenwhich mean sidereal time corresponding to that GPS time.
	Note that the conversion to sidereal time is performed after
	encoding the GPS time into the integer seconds and nanoseconds
	attributes, so the sidereal time will reflect any rounding that has
	occured as a result of that encoding.  If the GPS time is set to
	None or +inf or -inf, the sidereal time is set to that value as
	well.
	"""
	def __init__(self, s_name, ns_name, gmst_name):
		super(gpsproperty_with_gmst, self).__init__(s_name, ns_name)
		self.gmst_name = gmst_name

	def __set__(self, obj, gps):
		super(gpsproperty_with_gmst, self).__set__(obj, gps)
		if gps is None:
			setattr(obj, self.gmst_name, None)
		else:
			# re-retrieve the value in case it required type
			# conversion
			gps = self.__get__(obj)
			if not isinstance(gps, segments.infinity):
				setattr(obj, self.gmst_name, lal.GreenwichMeanSiderealTime(gps))
			elif gps > 0:
				setattr(obj, self.gmst_name, float("+inf"))
			elif gps < 0:
				setattr(obj, self.gmst_name, float("-inf"))
			else:
				# this should be impossible
				raise ValueError(gps)


class segmentproperty(object):
	"""
	Descriptor used internally to expose pairs of GPS-valued properties
	as segment-valued properties.  A segment may be set to None, which
	is encoded by setting both GPS-valued properties to None.  Likewise
	if both GPS-valued properties are set to None then the value
	reported by this descriptor is None, not (None, None).

	See the documentation for gpsproperty for more information on the
	encodings it uses for special values and the limitations they
	create.
	"""
	def __init__(self, start_name, stop_name):
		self.start = start_name
		self.stop = stop_name

	def __get__(self, obj, cls = None):
		start = getattr(obj, self.start)
		stop = getattr(obj, self.stop)
		if start is None and stop is None:
			return None
		return segments.segment(start, stop)

	def __set__(self, obj, seg):
		if seg is None:
			start = stop = None
		else:
			start, stop = seg
		setattr(obj, self.start, start)
		setattr(obj, self.stop, stop)


#
# =============================================================================
#
#                                process:table
#
# =============================================================================
#


ProcessID = ligolw.Column.next_id.type("process_id")


class ProcessTable(ligolw.Table):
	tableName = "process"
	validcolumns = {
		"program": "lstring",
		"version": "lstring",
		"cvs_repository": "lstring",
		"cvs_entry_time": "int_4s",
		"comment": "lstring",
		"is_online": "int_4s",
		"node": "lstring",
		"username": "lstring",
		"unix_procid": "int_4s",
		"start_time": "int_4s",
		"end_time": "int_4s",
		"jobid": "int_4s",
		"domain": "lstring",
		"ifos": "lstring",
		"process_id": "int_8s"
	}
	constraints = "PRIMARY KEY (process_id)"
	next_id = ProcessID(0)

	def get_ids_by_program(self, program):
		"""
		Return a set containing the process IDs from rows whose
		program string equals the given program.
		"""
		return set(row.process_id for row in self if row.program == program)

	@staticmethod
	def get_username():
		"""
		Utility to help retrieve a sensible value for the current
		username.  First the environment variable LOGNAME is tried,
		if that is not set the environment variable USERNAME is
		tried, if that is not set the password database is
		consulted (only on Unix systems, if the import of the pwd
		module succeeds), finally if that fails KeyError is raised.
		"""
		try:
			return os.environ["LOGNAME"]
		except KeyError:
			pass
		try:
			return os.environ["USERNAME"]
		except KeyError:
			pass
		try:
			import pwd
			return pwd.getpwuid(os.getuid())[0]
		except (ImportError, KeyError):
			raise KeyError


class Process(ligolw.Table.RowType):
	"""
	NOTE:  for some historical reason, this table records start and end
	times as integer-valued quantities, only.  GPS time-valued
	quantities are emulated for convenience, but only the integer part
	is stored.  Truncation to an integer occurs when assigning a start
	or end time to the row.

	Example:

	>>> x = Process()
	>>> x.instruments = ("H1", "L1")
	>>> assert x.ifos == 'H1,L1'
	>>> assert x.instruments == set(['H1', 'L1'])
	>>> # truncates to integers
	>>> x.start = 10.5
	>>> x.start
	LIGOTimeGPS(10, 0)
	>>> x.end = 20.5
	>>> x.end
	LIGOTimeGPS(20, 0)
	>>> x.segment
	segment(LIGOTimeGPS(10, 0), LIGOTimeGPS(20, 0))
	>>> # None is supported for start and end times
	>>> x.start = x.end = None
	>>> print(x.segment)
	None
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, ProcessTable.validcolumns))

	@property
	def start_time_ns(self):
		return None if self.start_time is None else 0
	@start_time_ns.setter
	def start_time_ns(self, val):
		pass

	@property
	def end_time_ns(self):
		return None if self.end_time is None else 0
	@end_time_ns.setter
	def end_time_ns(self, val):
		pass

	instruments = instrumentsproperty("ifos")
	start = gpsproperty("start_time", "start_time_ns")
	end = gpsproperty("end_time", "end_time_ns")
	segment = segmentproperty("start", "end")

	@classmethod
	def initialized(cls, program = None, version = None, cvs_repository = None, cvs_entry_time = None, comment = None, is_online = False, jobid = 0, domain = None, instruments = None, process_id = None):
		"""
		Create a new Process object and initialize its attributes
		to sensible defaults.  If not None, program, version,
		cvs_repository, comment, and domain should all be strings.
		If cvs_entry_time is not None, it must be a string in the
		format "YYYY-MM-DD HH:MM:SS".  is_online should be boolean,
		jobid an integer.  If not None, instruments must be an
		iterable (set, tuple, etc.) of instrument names (strings).

		In addition, .node is set to the current hostname,
		.unix_procid is set to the current process ID, .username is
		set to the current user's name, .start is set to the
		current GPS time.

		NOTE:  if the process_id keyword argument is None (the
		default), then the process_id attribute is not set, it is
		left uninitialized rather than setting it to None.  It must
		be initialized before the row object can be written to a
		file, and so in this way the calling code is required to
		provide a proper value for it.

		Example:

		>>> process = Process.initialized()
		"""
		self = cls(
			program = program,
			version = version,
			cvs_repository = cvs_repository,
			cvs_entry_time = lal.UTCToGPS(time.strptime(cvs_entry_time, "%Y-%m-%d %H:%M:%S +0000")) if cvs_entry_time is not None else None,
			comment = comment,
			is_online = int(is_online),
			node = socket.gethostname(),
			unix_procid = os.getpid(),
			start = lal.UTCToGPS(time.gmtime()),
			end = None,
			jobid = jobid,
			domain = domain,
			instruments = instruments
		)
		try:
			self.username = ProcessTable.get_username()
		except KeyError:
			self.username = None
		if process_id is not None:
			self.process_id = process_id
		return self

	def set_end_time_now(self):
		"""
		Set .end to the current GPS time.
		"""
		self.end = lal.UTCToGPS(time.gmtime())


ProcessTable.RowType = Process


#
# =============================================================================
#
#                             process_params:table
#
# =============================================================================
#


class ProcessParamsTable(ligolw.Table):
	tableName = "process_params"
	validcolumns = {
		"program": "lstring",
		"process:process_id": "int_8s",
		"param": "lstring",
		"type": "lstring",
		"value": "lstring"
	}
	# NOTE:  must use index instead of primary key
	#constraints = "PRIMARY KEY (process_id, param)"
	how_to_index = {
		"pp_pip_index": ("process_id", "param"),
	}

	def append(self, row):
		if row.type is not None and row.type not in ligolw.types.Types:
			raise ligolw.ElementError("unrecognized type '%s' for process %d param '%s'" % (row.type, row.process_id, row.param))
		super(ProcessParamsTable, self).append(row)


class ProcessParams(ligolw.Table.RowType):
	"""
	Example:

	>>> x = ProcessParams()
	>>> x.pyvalue = "test"
	>>> print(x.type)
	lstring
	>>> print(x.value)
	test
	>>> print(x.pyvalue)
	test
	>>> x.pyvalue = 6.
	>>> print(x.type)
	real_8
	>>> assert x.value == '6'
	>>> print(x.pyvalue)
	6.0
	>>> x.pyvalue = None
	>>> print(x.type)
	None
	>>> print(x.value)
	None
	>>> print(x.pyvalue)
	None
	>>> x.pyvalue = True
	>>> print(x.type)
	int_4s
	>>> assert x.value == '1'
	>>> x.pyvalue
	1
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, ProcessParamsTable.validcolumns))

	@property
	def pyvalue(self):
		if self.value is None:
			return None
		try:
			parsefunc = ligolw.types.ToPyType[self.type]
		except KeyError:
			raise ValueError("invalid type '%s'" % self.type)
		return parsefunc(self.value)

	@pyvalue.setter
	def pyvalue(self, value):
		if value is None:
			self.type = self.value = None
		else:
			try:
				self.type = ligolw.types.FromPyType[type(value)]
			except KeyError:
				raise ValueError("type not supported: %s" % repr(type(value)))
			# the column has type lstring, so the table I/O
			# code will put quotes around the values when
			# encoding to XML.  we have to *not* put quotes
			# around things that are string-valued or the
			# quotes will get encoded into the values appearing
			# in the table and end up being included in the
			# string value when read back.  that's why there's
			# a special case for string types.  see the comment
			# in types.py about why, for performance reasons,
			# ToPyType is not the inverse of FormatFunc
			self.value = value if self.type in ligolw.types.StringTypes else ligolw.types.FormatFunc[self.type](value)


ProcessParamsTable.RowType = ProcessParams


#
# =============================================================================
#
#                             search_summary:table
#
# =============================================================================
#


class SearchSummaryTable(ligolw.Table):
	tableName = "search_summary"
	validcolumns = {
		"process:process_id": "int_8s",
		"shared_object": "lstring",
		"lalwrapper_cvs_tag": "lstring",
		"lal_cvs_tag": "lstring",
		"comment": "lstring",
		"ifos": "lstring",
		"in_start_time": "int_4s",
		"in_start_time_ns": "int_4s",
		"in_end_time": "int_4s",
		"in_end_time_ns": "int_4s",
		"out_start_time": "int_4s",
		"out_start_time_ns": "int_4s",
		"out_end_time": "int_4s",
		"out_end_time_ns": "int_4s",
		"nevents": "int_4s",
		"nnodes": "int_4s"
	}
	how_to_index = {
		"ss_pi_index": ("process_id",),
	}

	def get_in_segmentlistdict(self, process_ids = None):
		"""
		Return a segmentlistdict mapping instrument to in segment
		list.  If process_ids is a sequence of process IDs, then
		only rows with matching IDs are included otherwise all rows
		are included.

		NOTE:  the result is not coalesced, each segmentlist
		contains the segments listed for that instrument as they
		appeared in the table.
		"""
		seglists = segments.segmentlistdict()
		for row in self:
			ifos = row.instruments or (None,)
			if process_ids is None or row.process_id in process_ids:
				seglists.extend(dict((ifo, segments.segmentlist([row.in_segment])) for ifo in ifos))
		return seglists

	def get_out_segmentlistdict(self, process_ids = None):
		"""
		Return a segmentlistdict mapping instrument to out segment
		list.  If process_ids is a sequence of process IDs, then
		only rows with matching IDs are included otherwise all rows
		are included.

		NOTE:  the result is not coalesced, each segmentlist
		contains the segments listed for that instrument as they
		appeared in the table.
		"""
		seglists = segments.segmentlistdict()
		for row in self:
			ifos = row.instruments or (None,)
			if process_ids is None or row.process_id in process_ids:
				seglists.extend(dict((ifo, segments.segmentlist([row.out_segment])) for ifo in ifos))
		return seglists


class SearchSummary(ligolw.Table.RowType):
	"""
	Example:

	>>> x = SearchSummary()
	>>> x.instruments = ("H1", "L1")
	>>> print(x.ifos)
	H1,L1
	>>> assert x.instruments == set(['H1', 'L1'])
	>>> x.in_start = x.out_start = LIGOTimeGPS(0)
	>>> x.in_end = x.out_end = LIGOTimeGPS(10)
	>>> x.in_segment
	segment(LIGOTimeGPS(0, 0), LIGOTimeGPS(10, 0))
	>>> x.out_segment
	segment(LIGOTimeGPS(0, 0), LIGOTimeGPS(10, 0))
	>>> x.in_segment = x.out_segment = None
	>>> print(x.in_segment)
	None
	>>> print(x.out_segment)
	None
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SearchSummaryTable.validcolumns))

	instruments = instrumentsproperty("ifos")

	in_start = gpsproperty("in_start_time", "in_start_time_ns")
	in_end = gpsproperty("in_end_time", "in_end_time_ns")
	out_start = gpsproperty("out_start_time", "out_start_time_ns")
	out_end = gpsproperty("out_end_time", "out_end_time_ns")

	in_segment = segmentproperty("in_start", "in_end")
	out_segment = segmentproperty("out_start", "out_end")

	@classmethod
	def initialized(cls, process, shared_object = "standalone", lalwrapper_cvs_tag = "", lal_cvs_tag = "", comment = None, ifos = None, inseg = None, outseg = None, nevents = 0, nnodes = 1):
		"""
		Create and return a sensibly initialized row for the
		search_summary table.  process is an initialized row for
		the process table.
		"""
		return cls(
			process_id = process.process_id,
			shared_object = shared_object,
			lalwrapper_cvs_tag = lalwrapper_cvs_tag,
			lal_cvs_tag = lal_cvs_tag,
			comment = comment or process.comment,
			instruments = ifos if ifos is not None else process.instruments,
			in_segment = inseg,
			out_segment = outseg,
			nevents = nevents,
			nnodes = nnodes
		)


SearchSummaryTable.RowType = SearchSummary


#
# =============================================================================
#
#                               sngl_burst:table
#
# =============================================================================
#


SnglBurstID = ligolw.Column.next_id.type("event_id")


class SnglBurstTable(ligolw.Table):
	tableName = "sngl_burst"
	validcolumns = {
		"process:process_id": "int_8s",
		"filter:filter_id": "int_8s",
		"ifo": "lstring",
		"search": "lstring",
		"channel": "lstring",
		"start_time": "int_4s",
		"start_time_ns": "int_4s",
		"stop_time": "int_4s",
		"stop_time_ns": "int_4s",
		"duration": "real_4",
		"flow": "real_4",
		"fhigh": "real_4",
		"central_freq": "real_4",
		"bandwidth": "real_4",
		"amplitude": "real_4",
		"snr": "real_4",
		"confidence": "real_4",
		"chisq": "real_8",
		"chisq_dof": "real_8",
		"tfvolume": "real_4",
		"hrss": "real_4",
		"time_lag": "real_4",
		"peak_time": "int_4s",
		"peak_time_ns": "int_4s",
		"peak_frequency": "real_4",
		"peak_strain": "real_4",
		"peak_time_error": "real_4",
		"peak_frequency_error": "real_4",
		"peak_strain_error": "real_4",
		"ms_start_time": "int_4s",
		"ms_start_time_ns": "int_4s",
		"ms_stop_time": "int_4s",
		"ms_stop_time_ns": "int_4s",
		"ms_duration": "real_4",
		"ms_flow": "real_4",
		"ms_fhigh": "real_4",
		"ms_bandwidth": "real_4",
		"ms_hrss": "real_4",
		"ms_snr": "real_4",
		"ms_confidence": "real_4",
		"param_one_name": "lstring",
		"param_one_value": "real_8",
		"param_two_name": "lstring",
		"param_two_value": "real_8",
		"param_three_name": "lstring",
		"param_three_value": "real_8",
		"event_id": "int_8s"
	}
	constraints = "PRIMARY KEY (event_id)"
	next_id = SnglBurstID(0)


class SnglBurst(ligolw.Table.RowType):
	__slots__ = tuple(map(ligolw.Column.ColumnName, SnglBurstTable.validcolumns))

	#
	# Tile properties
	#

	start = gpsproperty("start_time", "start_time_ns")
	stop = gpsproperty("stop_time", "stop_time_ns")
	peak = gpsproperty("peak_time", "peak_time_ns")

	@property
	def period(self):
		start = self.start
		try:
			stop = self.stop
		except AttributeError:
			stop = None
		# special case:  use duration if stop is not recorded
		if start is not None and stop is None and self.duration is not None:
			stop = start + self.duration
		if start is None and stop is None:
			return None
		return segments.segment(start, stop)

	@period.setter
	def period(self, seg):
		if seg is None:
			self.start = self.stop = self.duration = None
		else:
			self.start, self.stop = seg
			self.duration = float(abs(seg))

	@property
	def band(self):
		if self.central_freq is None and self.bandwidth is None:
			return None
		return segments.segment(self.central_freq - self.bandwidth / 2., self.central_freq + self.bandwidth / 2.)

	@band.setter
	def band(self, seg):
		if seg is None:
			try:
				self.flow = self.fhigh = None
			except AttributeError:
				# not in LAL C version
				pass
			self.central_freq = self.bandwidth = None
		else:
			try:
				self.flow, self.fhigh = seg
			except AttributeError:
				# not in LAL C version
				pass
			self.central_freq = sum(seg) / 2.
			self.bandwidth = abs(seg)

	#
	# "Most significant pixel" properties
	#

	ms_start = gpsproperty("ms_start_time", "ms_start_time_ns")
	ms_stop = gpsproperty("ms_stop_time", "ms_stop_time_ns")
	ms_peak = gpsproperty("ms_peak_time", "ms_peak_time_ns")

	@property
	def ms_period(self):
		start = self.ms_start
		stop = self.ms_stop
		# special case:  use duration if stop is not recorded
		if start is not None and stop is None and self.ms_duration is not None:
			stop = start + self.ms_duration
		if start is None and stop is None:
			return None
		return segments.segment(start, stop)

	@ms_period.setter
	def ms_period(self, seg):
		if seg is None:
			self.ms_start = self.ms_stop = self.ms_duration = None
		else:
			self.ms_start, self.ms_stop = seg
			self.ms_duration = float(abs(seg))

	@property
	def ms_band(self):
		if self.ms_flow is None and self.ms_bandwidth is None:
			return None
		return segments.segment(self.ms_flow, self.ms_flow + self.ms_bandwidth)

	@ms_band.setter
	def ms_band(self, seg):
		if seg is None:
			self.ms_bandwidth = self.ms_flow = self.ms_fhigh = None
		else:
			self.ms_flow, self.ms_fhigh = seg
			self.ms_bandwidth = abs(seg)


SnglBurstTable.RowType = SnglBurst


#
# =============================================================================
#
#                             sngl_inspiral:table
#
# =============================================================================
#


SnglInspiralID = ligolw.Column.next_id.type("event_id")


class SnglInspiralTable(ligolw.Table):
	tableName = "sngl_inspiral"
	validcolumns = {
		"process:process_id": "int_8s",
		"ifo": "lstring",
		"search": "lstring",
		"channel": "lstring",
		"end_time": "int_4s",
		"end_time_ns": "int_4s",
		"end_time_gmst": "real_8",
		"impulse_time": "int_4s",
		"impulse_time_ns": "int_4s",
		"template_duration": "real_8",
		"event_duration": "real_8",
		"amplitude": "real_4",
		"eff_distance": "real_4",
		"coa_phase": "real_4",
		"mass1": "real_4",
		"mass2": "real_4",
		"mchirp": "real_4",
		"mtotal": "real_4",
		"eta": "real_4",
		"kappa": "real_4",
		"chi": "real_4",
		"tau0": "real_4",
		"tau2": "real_4",
		"tau3": "real_4",
		"tau4": "real_4",
		"tau5": "real_4",
		"ttotal": "real_4",
		"psi0": "real_4",
		"psi3": "real_4",
		"alpha": "real_4",
		"alpha1": "real_4",
		"alpha2": "real_4",
		"alpha3": "real_4",
		"alpha4": "real_4",
		"alpha5": "real_4",
		"alpha6": "real_4",
		"beta": "real_4",
		"f_final": "real_4",
		"snr": "real_4",
		"chisq": "real_4",
		"chisq_dof": "int_4s",
		"bank_chisq": "real_4",
		"bank_chisq_dof": "int_4s",
		"cont_chisq": "real_4",
		"cont_chisq_dof": "int_4s",
		"sigmasq": "real_8",
		"rsqveto_duration": "real_4",
		"Gamma0": "real_4",
		"Gamma1": "real_4",
		"Gamma2": "real_4",
		"Gamma3": "real_4",
		"Gamma4": "real_4",
		"Gamma5": "real_4",
		"Gamma6": "real_4",
		"Gamma7": "real_4",
		"Gamma8": "real_4",
		"Gamma9": "real_4",
		"spin1x": "real_4",
		"spin1y": "real_4",
		"spin1z": "real_4",
		"spin2x": "real_4",
		"spin2y": "real_4",
		"spin2z": "real_4",
		"event_id": "int_8s"
	}
	constraints = "PRIMARY KEY (event_id)"
	next_id = SnglInspiralID(0)


class SnglInspiral(ligolw.Table.RowType):
	__slots__ = tuple(map(ligolw.Column.ColumnName, SnglInspiralTable.validcolumns))

	@staticmethod
	def chirp_distance(dist, mchirp, ref_mass=1.4):
		return dist * (2.**(-1./5) * ref_mass / mchirp)**(5./6)

	#
	# Properties
	#

	end = gpsproperty_with_gmst("end_time", "end_time_ns", "end_time_gmst")

	@property
	def spin1(self):
		if self.spin1x is None and self.spin1y is None and self.spin1z is None:
			return None
		return numpy.array((self.spin1x, self.spin1y, self.spin1z), dtype = "double")

	@spin1.setter
	def spin1(self, spin):
		if spin is None:
			self.spin1x = self.spin1y = self.spin1z = None
		else:
			self.spin1x, self.spin1y, self.spin1z = spin

	@property
	def spin2(self):
		if self.spin2x is None and self.spin2y is None and self.spin2z is None:
			return None
		return numpy.array((self.spin2x, self.spin2y, self.spin2z), dtype = "double")

	@spin2.setter
	def spin2(self, spin):
		if spin is None:
			self.spin2x = self.spin2y = self.spin2z = None
		else:
			self.spin2x, self.spin2y, self.spin2z = spin

	#
	# simulate tempate_id column
	# FIXME:  add a proper column for this
	#

	@property
	def template_id(self):
		return int(self.Gamma0)

	@template_id.setter
	def template_id(self, template_id):
		self.Gamma0 = float(template_id)

	#
	# Methods
	#

	# FIXME: how are two inspiral events defined to be the same?
	def __eq__(self, other):
		return self.ifo == other.ifo and self.end == other.end and self.mass1 == other.mass1 and self.mass2 == other.mass2 and self.spin1 == other.spin1 and self.spin2 == other.spin2 and self.search == other.search


SnglInspiralTable.RowType = SnglInspiral


#
# =============================================================================
#
#                             coinc_inspiral:table
#
# =============================================================================
#


class CoincInspiralTable(ligolw.Table):
	tableName = "coinc_inspiral"
	validcolumns = {
		"coinc_event:coinc_event_id": "int_8s",
		"ifos": "lstring",
		"end_time": "int_4s",
		"end_time_ns": "int_4s",
		"mass": "real_8",
		"mchirp": "real_8",
		"minimum_duration": "real_8",
		"snr": "real_8",
		"false_alarm_rate": "real_8",
		"combined_far": "real_8"
	}
	# NOTE:  must use index instead of primary key
	#constraints = "PRIMARY KEY (coinc_event_id)"
	how_to_index = {
		"ci_cei_index": ("coinc_event_id",)
	}


class CoincInspiral(ligolw.Table.RowType):
	"""
	Example:

	>>> x = CoincInspiral()
	>>> x.instruments = ("H1", "L1")
	>>> print(x.ifos)
	H1,L1
	>>> assert x.instruments == set(['H1', 'L1'])
	>>> x.end = LIGOTimeGPS(10)
	>>> x.end
	LIGOTimeGPS(10, 0)
	>>> x.end = None
	>>> print(x.end)
	None
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, CoincInspiralTable.validcolumns))

	instruments = instrumentsproperty("ifos")

	end = gpsproperty("end_time", "end_time_ns")


CoincInspiralTable.RowType = CoincInspiral


#
# =============================================================================
#
#                             sngl_ringdown:table
#
# =============================================================================
#


SnglRingdownID = ligolw.Column.next_id.type("event_id")


class SnglRingdownTable(ligolw.Table):
	tableName = "sngl_ringdown"
	validcolumns = {
		"process:process_id": "int_8s",
		"ifo": "lstring",
		"channel": "lstring",
		"start_time": "int_4s",
		"start_time_ns": "int_4s",
		"start_time_gmst": "real_8",
		"frequency": "real_4",
		"quality": "real_4",
		"phase": "real_4",
		"mass": "real_4",
		"spin": "real_4",
		"epsilon": "real_4",
		"num_clust_trigs": "int_4s",
		"ds2_H1H2": "real_4",
		"ds2_H1L1": "real_4",
		"ds2_H1V1": "real_4",
		"ds2_H2L1": "real_4",
		"ds2_H2V1": "real_4",
		"ds2_L1V1": "real_4",
		"amplitude": "real_4",
		"snr": "real_4",
		"eff_dist": "real_4",
		"sigma_sq": "real_8",
		"event_id": "int_8s"
	}
	constraints = "PRIMARY KEY (event_id)"
	next_id = SnglRingdownID(0)


class SnglRingdown(ligolw.Table.RowType):
	__slots__ = tuple(map(ligolw.Column.ColumnName, SnglRingdownTable.validcolumns))

	start = gpsproperty_with_gmst("start_time", "start_time_ns", "start_time_gmst")


SnglRingdownTable.RowType = SnglRingdown


#
# =============================================================================
#
#                             coinc_ringdown:table
#
# =============================================================================
#


class CoincRingdownTable(ligolw.Table):
	tableName = "coinc_ringdown"
	validcolumns = {
		"coinc_event:coinc_event_id": "int_8s",
		"ifos": "lstring",
		"start_time": "int_4s",
		"start_time_ns": "int_4s",
		"frequency": "real_8",
		"quality": "real_8",
		"mass": "real_8",
		"spin": "real_8",
		"snr": "real_8",
		"choppedl_snr": "real_8",
		"snr_sq": "real_8",
		"eff_coh_snr": "real_8",
		"null_stat": "real_8",
		"kappa": "real_8",
		"snr_ratio": "real_8",
		"false_alarm_rate": "real_8",
		"combined_far": "real_8"
	}
	# NOTE:  must use index instead of primary key
	# constraints = "PRIMARY KEY (coinc_event_id)"
	how_to_index = {
		"cr_cei_index": ("coinc_event_id",)
	}


class CoincRingdown(ligolw.Table.RowType):
	__slots__ = tuple(map(ligolw.Column.ColumnName, CoincRingdownTable.validcolumns))

	instruments = instrumentsproperty("ifos")

	start = gpsproperty("start_time", "start_time_ns")


CoincRingdownTable.RowType = CoincRingdown


#
# =============================================================================
#
#                              sim_inspiral:table
#
# =============================================================================
#


SimInspiralID = ligolw.Column.next_id.type("simulation_id")


class SimInspiralTable(ligolw.Table):
	tableName = "sim_inspiral"
	validcolumns = {
		"process:process_id": "int_8s",
		"waveform": "lstring",
		"geocent_end_time": "int_4s",
		"geocent_end_time_ns": "int_4s",
		"h_end_time": "int_4s",
		"h_end_time_ns": "int_4s",
		"l_end_time": "int_4s",
		"l_end_time_ns": "int_4s",
		"g_end_time": "int_4s",
		"g_end_time_ns": "int_4s",
		"t_end_time": "int_4s",
		"t_end_time_ns": "int_4s",
		"v_end_time": "int_4s",
		"v_end_time_ns": "int_4s",
		"end_time_gmst": "real_8",
		"source": "lstring",
		"mass1": "real_4",
		"mass2": "real_4",
		"mchirp": "real_4",
		"eta": "real_4",
		"distance": "real_4",
		"longitude": "real_4",
		"latitude": "real_4",
		"inclination": "real_4",
		"coa_phase": "real_4",
		"polarization": "real_4",
		"psi0": "real_4",
		"psi3": "real_4",
		"alpha": "real_4",
		"alpha1": "real_4",
		"alpha2": "real_4",
		"alpha3": "real_4",
		"alpha4": "real_4",
		"alpha5": "real_4",
		"alpha6": "real_4",
		"beta": "real_4",
		"spin1x": "real_4",
		"spin1y": "real_4",
		"spin1z": "real_4",
		"spin2x": "real_4",
		"spin2y": "real_4",
		"spin2z": "real_4",
		"theta0": "real_4",
		"phi0": "real_4",
		"f_lower": "real_4",
		"f_final": "real_4",
		"eff_dist_h": "real_4",
		"eff_dist_l": "real_4",
		"eff_dist_g": "real_4",
		"eff_dist_t": "real_4",
		"eff_dist_v": "real_4",
		"numrel_mode_min": "int_4s",
		"numrel_mode_max": "int_4s",
		"numrel_data": "lstring",
		"amp_order": "int_4s",
		"taper": "lstring",
		"bandpass": "int_4s",
		"simulation_id": "int_8s"
	}
	constraints = "PRIMARY KEY (simulation_id)"
	next_id = SimInspiralID(0)


class SimInspiral(ligolw.Table.RowType):
	"""
	Example:

	>>> x = SimInspiral()
	>>> x.ra_dec = 0., 0.
	>>> x.ra_dec
	(0.0, 0.0)
	>>> x.ra_dec = None
	>>> print(x.ra_dec)
	None
	>>> x.time_geocent = None
	>>> print(x.time_geocent)
	None
	>>> print(x.end_time_gmst)
	None
	>>> x.time_geocent = LIGOTimeGPS(6e8)
	>>> print(x.time_geocent)
	600000000
	>>> print(round(x.end_time_gmst, 8))
	-2238.39417156
	>>> x.distance = 100e6
	>>> x.ra_dec = 0., 0.
	>>> x.inclination = 0.
	>>> x.coa_phase = 0.
	>>> x.polarization = 0.
	>>> x.snr_geometry_factors(("H1",))
	{'H1': (0.490467233277456-0.4671010853697789j)}
	>>> # NOTE:  complex, abs() is traditional value
	>>> x.effective_distances(("H1",))
	{'H1': (106915812.12292896+101822279.85362741j)}
	>>> x.expected_snrs({"H1": 150e6})
	{'H1': (5.885606799329472-5.605213024437346j)}
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SimInspiralTable.validcolumns))

	time_geocent = gpsproperty_with_gmst("geocent_end_time", "geocent_end_time_ns", "end_time_gmst")

	@property
	def ra_dec(self):
		if self.longitude is None and self.latitude is None:
			return None
		return self.longitude, self.latitude

	@ra_dec.setter
	def ra_dec(self, radec):
		if radec is None:
			self.longitude = self.latitude = None
		else:
			self.longitude, self.latitude = radec

	@property
	def spin1(self):
		if self.spin1x is None and self.spin1y is None and self.spin1z is None:
			return None
		return numpy.array((self.spin1x, self.spin1y, self.spin1z), dtype = "double")

	@spin1.setter
	def spin1(self, spin):
		if spin is None:
			self.spin1x, self.spin1y, self.spin1z = None, None, None
		else:
			self.spin1x, self.spin1y, self.spin1z = spin

	@property
	def spin2(self):
		if self.spin2x is None and self.spin2y is None and self.spin2z is None:
			return None
		return numpy.array((self.spin2x, self.spin2y, self.spin2z), dtype = "double")

	@spin2.setter
	def spin2(self, spin):
		if spin is None:
			self.spin2x, self.spin2y, self.spin2z = None, None, None
		else:
			self.spin2x, self.spin2y, self.spin2z = spin

	def time_at_instrument(self, instrument, offsetvector = None):
		"""
		Return the "time" of the injection, delay corrected for the
		displacement from the geocentre to the given instrument.
		If offsetvector is not None then it must be a dictionary
		mapping instrument names to time offsets in seconds and
		must contain at least at entry for instrument.  The
		corresponding time offset will be subtracted from the
		injection time at the geocentre.

		NOTE:  this method does not account for the rotation of the
		Earth that occurs during the transit of the plane wave from
		the detector to the geocentre.  That is, it is assumed the
		Earth is in the same orientation with respect to the
		celestial sphere when the wave passes through the detector
		as when it passes through the geocentre.  The Earth rotates
		by about 1.5 urad during the 21 ms it takes light to travel
		the radius of the Earth, which corresponds to 10 m of
		displacement at the equator, or 33 light-ns.  Therefore,
		the failure to do a proper retarded time calculation here
		results in errors as large as 33 ns.  This is insignificant
		in present applications, but be aware that this
		approximation is being made if the return value is used in
		other contexts.
		"""
		t_geocent = self.time_geocent
		# the offset is subtracted from the time of the injection.
		# injections are done this way so that when the triggers
		# that result from an injection have the offset vector
		# added to their times (as is the convention for time
		# slides) the triggers will form a coinc
		if offsetvector is not None:
			t_geocent -= offsetvector[instrument]
		ra, dec = self.ra_dec
		return t_geocent + lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix[instrument].location, ra, dec, t_geocent)

	def snr_geometry_factors(self, instruments):
		"""
		Compute and return a dictionary of the ratios of the
		source's physical distance to its effective distance for
		each of the given instruments.  NOTE that the quantity
		returned is complex, where the magnitude of the value is
		that ratio and the phase is such that the expected complex
		SNR in a detector is given by

		rho_{0} = 8 * (D_horizon / D) * snr_geometry_factor,

		where D_horizon is the detector's horizon distance for this
		waveform (computed from the detector's noise spectral
		density), and D is the source's physical distance.  The
		geometry factor (what this method computes) depends on the
		direction to the source with respect to the antenna beam,
		the inclination of the source's orbital plane, the wave
		frame's polarization, and the phase of the waveform at the
		time of coalescence.  The combination

		D / geometry factor

		is called the effective distance.  See Equation (4.3) of
		arXiv:0705.1514.

		See also .effective_distances(), .expected_snrs().
		"""
		cosi = math.cos(self.inclination)
		cos2i = cosi**2.
		# don't rely on self.gmst to be set properly
		gmst = lal.GreenwichMeanSiderealTime(self.time_geocent)
		snr_geometry_factors = {}
		for instrument in instruments:
			fp, fc = lal.ComputeDetAMResponse(
				lal.cached_detector_by_prefix[instrument].response,
				self.longitude, self.latitude,
				self.polarization,
				gmst
			)
			snr_geometry_factors[instrument] = complex(
				-fc * cosi, fp * (1. + cos2i) / 2.
			) * cmath.exp(-2.j * self.coa_phase)
		return snr_geometry_factors

	def effective_distances(self, instruments):
		"""
		Compute and return a dictionary of the effective distances
		for this injection for the given instruments.  The
		effective distance is the distance at which an optimally
		oriented and positioned source would be seen with the same
		SNR as that with which this source will be seen in the
		given instrument.  Effective distance is related to the
		physical distance, D, by the geometry factor

		D_effective = D / (geometry factor).

		NOTE that in this implementation the quantity returned is
		complex such that the expected complex SNR in a detector is

		rho_{0} = 8 * D_horizon / D_effective

		Traditionally the effective distance is a scalar and does
		not convey information about the phase of the
		signal-to-noise ratio.  That quantity is the absolute value
		of the quantity computed by this method.  The extension to
		complex values is done here to facilitate the use of this
		code in applications where the expected complex SNR is
		required.

		See also .snr_geometry_factors(), .expected_snrs().
		"""
		return {instrument: self.distance / snr_geometry_factor for instrument, snr_geometry_factor in self.snr_geometry_factors(instruments).items()}

	def expected_snrs(self, horizon_distances):
		"""
		Compute and return a dictionary of the expected complex
		SNRs for this injection in the given instruments.
		horizon_distances is a dictionary giving the horizon
		distance for each of the detectors for which an expected
		SNR is to be computed.  The expected SNR in a detector is

		rho_{0} = 8 * D_horizon / D_effective.

		See also .effective_distances().
		"""
		return {instrument: 8. * horizon_distances[instrument] / effective_distance for instrument, effective_distance in self.effective_distances(horizon_distances).items()}


SimInspiralTable.RowType = SimInspiral


#
# =============================================================================
#
#                               sim_burst:table
#
# =============================================================================
#


SimBurstID = ligolw.Column.next_id.type("simulation_id")


class SimBurstTable(ligolw.Table):
	tableName = "sim_burst"
	validcolumns = {
		"process:process_id": "int_8s",
		"waveform": "lstring",
		"ra": "real_8",
		"dec": "real_8",
		"psi": "real_8",
		"time_geocent_gps": "int_4s",
		"time_geocent_gps_ns": "int_4s",
		"time_geocent_gmst": "real_8",
		"duration": "real_8",
		"frequency": "real_8",
		"bandwidth": "real_8",
		"q": "real_8",
		"pol_ellipse_angle": "real_8",
		"pol_ellipse_e": "real_8",
		"amplitude": "real_8",
		"hrss": "real_8",
		"egw_over_rsquared": "real_8",
		"waveform_number": "int_8u",
		"time_slide:time_slide_id": "int_8s",
		"simulation_id": "int_8s"
	}
	constraints = "PRIMARY KEY (simulation_id)"
	next_id = SimBurstID(0)


class SimBurst(ligolw.Table.RowType):
	"""
	Example:

	>>> x = SimBurst()
	>>> x.ra_dec = 0., 0.
	>>> x.ra_dec
	(0.0, 0.0)
	>>> x.ra_dec = None
	>>> print(x.ra_dec)
	None
	>>> x.time_geocent = None
	>>> print(x.time_geocent)
	None
	>>> print(x.time_geocent_gmst)
	None
	>>> x.time_geocent = LIGOTimeGPS(6e8)
	>>> print(x.time_geocent)
	600000000
	>>> print(round(x.time_geocent_gmst, 8))
	-2238.39417156
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SimBurstTable.validcolumns))

	time_geocent = gpsproperty_with_gmst("time_geocent_gps", "time_geocent_gps_ns", "time_geocent_gmst")

	@property
	def ra_dec(self):
		if self.ra is None and self.dec is None:
			return None
		return self.ra, self.dec

	@ra_dec.setter
	def ra_dec(self, radec):
		if radec is None:
			self.ra = self.dec = None
		else:
			self.ra, self.dec = radec

	def time_at_instrument(self, instrument, offsetvector = None):
		"""
		Return the "time" of the injection, delay corrected for the
		displacement from the geocentre to the given instrument.
		If offsetvector is not None then it must be a dictionary
		mapping instrument names to time offsets in seconds and
		must contain at least at entry for instrument.  The
		corresponding time offset will be subtracted from the
		injection time at the geocentre.

		NOTE:  this method does not account for the rotation of the
		Earth that occurs during the transit of the plane wave from
		the detector to the geocentre.  That is, it is assumed the
		Earth is in the same orientation with respect to the
		celestial sphere when the wave passes through the detector
		as when it passes through the geocentre.  The Earth rotates
		by about 1.5 urad during the 21 ms it takes light to travel
		the radius of the Earth, which corresponds to 10 m of
		displacement at the equator, or 33 light-ns.  Therefore,
		the failure to do a proper retarded time calculation here
		results in errors as large as 33 ns.  This is insignificant
		for burst searches, but be aware that this approximation is
		being made if the return value is used in other contexts.
		"""
		t_geocent = self.time_geocent
		# the offset is subtracted from the time of the injection.
		# injections are done this way so that when the triggers
		# that result from an injection have the offset vector
		# added to their times (as is the convention for time
		# slides) the triggers will form a coinc
		if offsetvector is not None:
			t_geocent -= offsetvector[instrument]
		ra, dec = self.ra_dec
		return t_geocent + lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix[instrument].location, ra, dec, t_geocent)


SimBurstTable.RowType = SimBurst


#
# =============================================================================
#
#                              sim_ringdown:table
#
# =============================================================================
#


SimRingdownID = ligolw.Column.next_id.type("simulation_id")


class SimRingdownTable(ligolw.Table):
	tableName = "sim_ringdown"
	validcolumns = {
		"process:process_id": "int_8s",
		"waveform": "lstring",
		"coordinates": "lstring",
		"geocent_start_time": "int_4s",
		"geocent_start_time_ns": "int_4s",
		"h_start_time": "int_4s",
		"h_start_time_ns": "int_4s",
		"l_start_time": "int_4s",
		"l_start_time_ns": "int_4s",
		"v_start_time": "int_4s",
		"v_start_time_ns": "int_4s",
		"start_time_gmst": "real_8",
		"longitude": "real_4",
		"latitude": "real_4",
		"distance": "real_4",
		"inclination": "real_4",
		"polarization": "real_4",
		"frequency": "real_4",
		"quality": "real_4",
		"phase": "real_4",
		"mass": "real_4",
		"spin": "real_4",
		"epsilon": "real_4",
		"amplitude": "real_4",
		"eff_dist_h": "real_4",
		"eff_dist_l": "real_4",
		"eff_dist_v": "real_4",
		"hrss": "real_4",
		"hrss_h": "real_4",
		"hrss_l": "real_4",
		"hrss_v": "real_4",
		"simulation_id": "int_8s"
	}
	constraints = "PRIMARY KEY (simulation_id)"
	next_id = SimRingdownID(0)


class SimRingdown(ligolw.Table.RowType):
	__slots__ = tuple(map(ligolw.Column.ColumnName, SimRingdownTable.validcolumns))

	geocent_start = gpsproperty_with_gmst("geocent_start_time", "geocent_start_time_ns", "start_time_gmst")

	@property
	def ra_dec(self):
		if self.longitude is None and self.latitude is None:
			return None
		return self.longitude, self.latitude

	@ra_dec.setter
	def ra_dec(self, radec):
		if radec is None:
			self.longitude = self.latitude = None
		else:
			self.longitude, self.latitude = radec

	def time_at_instrument(self, instrument, offsetvector = None):
		"""
		Return the start time of the injection, delay corrected for
		the displacement from the geocentre to the given
		instrument.  If offsetvector is not None then it must be a
		dictionary mapping instrument names to time offsets in
		seconds and must contain at least at entry for instrument.
		The corresponding time offset will be subtracted from the
		injection time at the geocentre.

		NOTE:  this method does not account for the rotation of the
		Earth that occurs during the transit of the plane wave from
		the detector to the geocentre.  That is, it is assumed the
		Earth is in the same orientation with respect to the
		celestial sphere when the wave passes through the detector
		as when it passes through the geocentre.  The Earth rotates
		by about 1.5 urad during the 21 ms it takes light to travel
		the radius of the Earth, which corresponds to 10 m of
		displacement at the equator, or 33 light-ns.  Therefore,
		the failure to do a proper retarded time calculation here
		results in errors as large as 33 ns.  This is insignificant
		for ring-down searches, but be aware that this
		approximation is being made if the return value is used in
		other contexts.
		"""
		t_geocent = self.geocent_start
		# the offset is subtracted from the time of the injection.
		# injections are done this way so that when the triggers
		# that result from an injection have the offset vector
		# added to their times (as is the convention for time
		# slides) the triggers will form a coinc
		if offsetvector is not None:
			t_geocent -= offsetvector[instrument]
		ra, dec = self.ra_dec
		return t_geocent + lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix[instrument].location, ra, dec, t_geocent)


SimRingdownTable.RowType = SimRingdown


#
# =============================================================================
#
#                         sim_cbc: new injection table
#
# =============================================================================
#


SimCBCID = ligolw.Column.next_id.type("cbc_sim_id")


class SimCBCTable(ligolw.Table):
	tableName = "sim_cbc"
	validcolumns = {
		"geocent_end_time": "int_4s",
		"geocent_end_time_ns": "int_4s",
		"cbc_model": "lstring",
		"coa_phase": "real_8",
		"d_lum": "real_8",
		"dec": "real_8",
		"f22_ref_spin": "real_8",
		"f22_start": "real_8",
		"inclination": "real_8",
		"mass1_det": "real_8",
		"mass2_det": "real_8",
		"polarization": "real_8",
		"ra": "real_8",
		"spin1x": "real_8",
		"spin1y": "real_8",
		"spin1z": "real_8",
		"spin2x": "real_8",
		"spin2y": "real_8",
		"spin2z": "real_8",
		"ampinterpol": "int_4s",
		"convention": "int_4s",
		"eobchoosenumoranalhamder": "int_4s",
		"eobellmaxfornyquistcheck": "int_4s",
		"expansionorder": "int_4s",
		"finalspinmod": "int_4s",
		"getideo": "int_4s",
		"gmtideo": "int_4s",
		"insampfitsversion": "int_4s",
		"insamphmversion": "int_4s",
		"insampversion": "int_4s",
		"insphasehmversion": "int_4s",
		"insphaseversion": "int_4s",
		"inspiralversion": "int_4s",
		"intampfitsversion": "int_4s",
		"intamphmversion": "int_4s",
		"intampversion": "int_4s",
		"intphasehmversion": "int_4s",
		"intphaseversion": "int_4s",
		"liv_a_sign": "real_8",
		"mbandprecversion": "int_4s",
		"mergerversion": "int_4s",
		"modearray": "lstring",
		"modearrayjframe": "lstring",
		"modesl0frame": "int_4s",
		"phaseref21": "real_8",
		"precmodes": "int_4s",
		"precthresholdmband": "real_8",
		"precversion": "int_4s",
		"rdampfitsversion": "int_4s",
		"rdamphmversion": "int_4s",
		"rdampversion": "int_4s",
		"rdphasehmversion": "int_4s",
		"rdphaseversion": "int_4s",
		"thresholdmband": "real_8",
		"tidalhexadecapolarlambda1": "real_8",
		"tidalhexadecapolarlambda2": "real_8",
		"tidaloctupolarfmode1": "real_8",
		"tidaloctupolarfmode2": "real_8",
		"tidaloctupolarlambda1": "real_8",
		"tidaloctupolarlambda2": "real_8",
		"tidalquadrupolarfmode1": "real_8",
		"tidalquadrupolarfmode2": "real_8",
		"transprecessionmethod": "int_4s",
		"twistphenomhm": "int_4s",
		"usemodes": "int_4s",
		"alphappe": "real_8",
		"alphappe0": "real_8",
		"alphappe1": "real_8",
		"alphappe2": "real_8",
		"alphappe3": "real_8",
		"alphappe4": "real_8",
		"alphappe5": "real_8",
		"alphappe6": "real_8",
		"alphappe7": "real_8",
		"ampo": "int_4s",
		"axis": "int_4s",
		"betappe": "real_8",
		"betappe0": "real_8",
		"betappe1": "real_8",
		"betappe2": "real_8",
		"betappe3": "real_8",
		"betappe4": "real_8",
		"betappe5": "real_8",
		"betappe6": "real_8",
		"betappe7": "real_8",
		"cbc_sim_id": "int_8s",
		"dquadmon1": "real_8",
		"dquadmon2": "real_8",
		"dalpha1": "real_8",
		"dalpha2": "real_8",
		"dalpha3": "real_8",
		"dalpha4": "real_8",
		"dalpha5": "real_8",
		"dbeta1": "real_8",
		"dbeta2": "real_8",
		"dbeta3": "real_8",
		"dchi0": "real_8",
		"dchi1": "real_8",
		"dchi2": "real_8",
		"dchi3": "real_8",
		"dchi4": "real_8",
		"dchi5": "real_8",
		"dchi5l": "real_8",
		"dchi6": "real_8",
		"dchi6l": "real_8",
		"dchi7": "real_8",
		"dsigma1": "real_8",
		"dsigma2": "real_8",
		"dsigma3": "real_8",
		"dsigma4": "real_8",
		"dxi1": "real_8",
		"dxi2": "real_8",
		"dxi3": "real_8",
		"dxi4": "real_8",
		"dxi5": "real_8",
		"dxi6": "real_8",
		"ecco": "int_4s",
		"eccentricity": "real_8",
		"f_ecc": "real_8",
		"fend": "real_8",
		"lambda1": "real_8",
		"lambda2": "real_8",
		"liv": "int_4s",
		"log10lambda_eff": "real_8",
		"longascnodes": "real_8",
		"lscorr": "int_4s",
		"meanperano": "real_8",
		"modes": "int_4s",
		"nltidesa1": "real_8",
		"nltidesa2": "real_8",
		"nltidesf1": "real_8",
		"nltidesf2": "real_8",
		"nltidesn1": "real_8",
		"nltidesn2": "real_8",
		"nongr_alpha": "real_8",
		"numreldata": "lstring",
		"phaseo": "int_4s",
		"phi1": "real_8",
		"phi2": "real_8",
		"phi3": "real_8",
		"phi4": "real_8",
		"redshift": "real_8",
		"sideband": "int_4s",
		"spino": "int_4s",
		"tideo": "int_4s",
		"time_slide:time_slide_id": "int_8s",
		"process:process_id": "int_8s",
		"h_snr": "real_8",
		"l_snr": "real_8",
		"v_snr": "real_8",
		"k_snr": "real_8",
	}
	constraints = "PRIMARY KEY (cbc_sim_id)"
	next_id = SimCBCID(0)


class SimCBC(ligolw.Table.RowType):
	"""
	Example:

	>>> x = SimCBC()
	>>> x.ra_dec = 0., 0.
	>>> x.ra_dec
	(0.0, 0.0)
	>>> x.ra_dec = None
	>>> print(x.ra_dec)
	None
	>>> x.time_geocent = None
	>>> print(x.time_geocent)
	None
	>>> x.time_geocent = LIGOTimeGPS(6e8)
	>>> print(x.time_geocent)
	600000000
	>>> x.d_lum = 100e6
	>>> x.ra_dec = 0., 0.
	>>> x.inclination = 0.
	>>> x.coa_phase = 0.
	>>> x.polarization = 0.
	>>> x.snr_geometry_factors(("H1",))
	{'H1': (0.490467233277456-0.4671010853697789j)}
	>>> # NOTE:  complex, abs() is traditional value
	>>> x.effective_distances(("H1",))
	{'H1': (106915812.12292896+101822279.85362741j)}
	>>> x.expected_snrs({"H1": 150e6})
	{'H1': (5.885606799329472-5.605213024437346j)}
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SimCBCTable.validcolumns))

	time_geocent = gpsproperty("geocent_end_time", "geocent_end_time_ns")

	@property
	def ra_dec(self):
		if self.ra is None and self.dec is None:
			return None
		return self.ra, self.dec

	@ra_dec.setter
	def ra_dec(self, radec):
		if radec is None:
			self.ra = self.dec = None
		else:
			self.ra, self.dec = radec

	@property
	def spin1(self):
		if self.spin1x is None and self.spin1y is None and self.spin1z is None:
			return None
		return numpy.array((self.spin1x, self.spin1y, self.spin1z), dtype = "double")

	@spin1.setter
	def spin1(self, spin):
		if spin is None:
			self.spin1x, self.spin1y, self.spin1z = None, None, None
		else:
			self.spin1x, self.spin1y, self.spin1z = spin

	@property
	def spin2(self):
		if self.spin2x is None and self.spin2y is None and self.spin2z is None:
			return None
		return numpy.array((self.spin2x, self.spin2y, self.spin2z), dtype = "double")

	@spin2.setter
	def spin2(self, spin):
		if spin is None:
			self.spin2x, self.spin2y, self.spin2z = None, None, None
		else:
			self.spin2x, self.spin2y, self.spin2z = spin

	def time_at_instrument(self, instrument, offsetvector = None):
		"""
		Return the "time" of the injection, delay corrected for the
		displacement from the geocentre to the given instrument.
		If offsetvector is not None then it must be a dictionary
		mapping instrument names to time offsets in seconds and
		must contain at least at entry for instrument.  The
		corresponding time offset will be subtracted from the
		injection time at the geocentre.

		NOTE:  this method does not account for the rotation of the
		Earth that occurs during the transit of the plane wave from
		the detector to the geocentre.  That is, it is assumed the
		Earth is in the same orientation with respect to the
		celestial sphere when the wave passes through the detector
		as when it passes through the geocentre.  The Earth rotates
		by about 1.5 urad during the 21 ms it takes light to travel
		the radius of the Earth, which corresponds to 10 m of
		displacement at the equator, or 33 light-ns.  Therefore,
		the failure to do a proper retarded time calculation here
		results in errors as large as 33 ns.  This is insignificant
		in present applications, but be aware that this
		approximation is being made if the return value is used in
		other contexts.
		"""
		t_geocent = self.time_geocent
		# the offset is subtracted from the time of the injection.
		# injections are done this way so that when the triggers
		# that result from an injection have the offset vector
		# added to their times (as is the convention for time
		# slides) the triggers will form a coinc
		if offsetvector is not None:
			t_geocent -= offsetvector[instrument]
		ra, dec = self.ra_dec
		return t_geocent + lal.TimeDelayFromEarthCenter(lal.cached_detector_by_prefix[instrument].location, ra, dec, t_geocent)

	def snr_geometry_factors(self, instruments):
		"""
		Compute and return a dictionary of the ratios of the
		source's physical distance to its effective distance for
		each of the given instruments.  NOTE that the quantity
		returned is complex, where the magnitude of the value is
		that ratio and the phase is such that the expected complex
		SNR in a detector is given by

		rho_{0} = 8 * (D_horizon / D) * snr_geometry_factor,

		where D_horizon is the detector's horizon distance for this
		waveform (computed from the detector's noise spectral
		density), and D is the source's physical distance.  The
		geometry factor (what this method computes) depends on the
		direction to the source with respect to the antenna beam,
		the inclination of the source's orbital plane, the wave
		frame's polarization, and the phase of the waveform at the
		time of coalescence.  The combination

		D / geometry factor

		is called the effective distance.  See Equation (4.3) of
		arXiv:0705.1514.

		See also .effective_distances(), .expected_snrs().
		"""
		cosi = math.cos(self.inclination)
		cos2i = cosi**2.
		# don't rely on self.gmst to be set properly
		gmst = lal.GreenwichMeanSiderealTime(self.time_geocent)
		snr_geometry_factors = {}
		for instrument in instruments:
			fp, fc = lal.ComputeDetAMResponse(
				lal.cached_detector_by_prefix[instrument].response,
				self.ra, self.dec,
				self.polarization,
				gmst
			)
			snr_geometry_factors[instrument] = complex(
				-fc * cosi, fp * (1. + cos2i) / 2.
			) * cmath.exp(-2.j * self.coa_phase)
		return snr_geometry_factors

	def effective_distances(self, instruments):
		"""
		Compute and return a dictionary of the effective distances
		for this injection for the given instruments.  The
		effective distance is the distance at which an optimally
		oriented and positioned source would be seen with the same
		SNR as that with which this source will be seen in the
		given instrument.  Effective distance is related to the
		physical distance, D, by the geometry factor

		D_effective = D / (geometry factor).

		NOTE that in this implementation the quantity returned is
		complex such that the expected complex SNR in a detector is

		rho_{0} = 8 * D_horizon / D_effective

		Traditionally the effective distance is a scalar and does
		not convey information about the phase of the
		signal-to-noise ratio.  That quantity is the absolute value
		of the quantity computed by this method.  The extension to
		complex values is done here to facilitate the use of this
		code in applications where the expected complex SNR is
		required.

		See also .snr_geometry_factors(), .expected_snrs().
		"""
		return {instrument: self.d_lum / snr_geometry_factor for instrument, snr_geometry_factor in self.snr_geometry_factors(instruments).items()}

	def expected_snrs(self, horizon_distances):
		"""
		Compute and return a dictionary of the expected complex
		SNRs for this injection in the given instruments.
		horizon_distances is a dictionary giving the horizon
		distance for each of the detectors for which an expected
		SNR is to be computed.  The expected SNR in a detector is

		rho_{0} = 8 * D_horizon / D_effective.

		See also .effective_distances().
		"""
		return {instrument: 8. * horizon_distances[instrument] / effective_distance for instrument, effective_distance in self.effective_distances(horizon_distances).items()}


SimCBCTable.RowType = SimCBC


#
# =============================================================================
#
#                                segment:table
#
# =============================================================================
#


SegmentID = ligolw.Column.next_id.type("segment_id")


class SegmentTable(ligolw.Table):
	tableName = "segment"
	validcolumns = {
		"process:process_id": "int_8s",
		"segment_id": "int_8s",
		"start_time": "int_4s",
		"start_time_ns": "int_4s",
		"end_time": "int_4s",
		"end_time_ns": "int_4s",
		"segment_definer:segment_def_id": "int_8s"
	}
	constraints = "PRIMARY KEY (segment_id)"
	next_id = SegmentID(0)


@functools.total_ordering
class Segment(ligolw.Table.RowType):
	"""
	One row in a segment table.  This class emulates enough of the
	behaviour of the ligo.segments.segment class that a
	ligo.segments.segmentlist object containing these Segment objects
	can be manipulated algebraically as usual.  This simplifies
	arithmetic with segment lists stored in XML files, but note that
	when the result of a calculation requires new segments to be
	created, the segmentlist class creates them as
	ligo.segments.segment objects, not these Segment objects.  To
	re-insert them into an XML document a type conversion is required,
	and the missing ID values populated.  See the ligolw.utils.segments
	module for a high-level interface to segment data in XML documents.

	Example:

	>>> x = Segment()
	>>> x.start = LIGOTimeGPS(0)
	>>> x.end = LIGOTimeGPS(10)
	>>> x.segment
	segment(LIGOTimeGPS(0, 0), LIGOTimeGPS(10, 0))
	>>> x.segment = None
	>>> print(x.segment)
	None
	>>> print(x.start)
	None
	>>> # non-LIGOTimeGPS times are converted to LIGOTimeGPS
	>>> x.segment = (20, 30.125)
	>>> x.end
	LIGOTimeGPS(30, 125000000)
	>>> # initialization from a tuple or with arguments
	>>> Segment((20, 30)).segment
	segment(LIGOTimeGPS(20, 0), LIGOTimeGPS(30, 0))
	>>> Segment(20, 30).segment
	segment(LIGOTimeGPS(20, 0), LIGOTimeGPS(30, 0))
	>>> # use as a segment object in segmentlist operations
	>>> try:
	...	from ligo import segments
	... except ImportError:
	...	import igwn_segments as segments
	...
	>>> x = segments.segmentlist([Segment(0, 10), Segment(20, 30)])
	>>> abs(x)
	LIGOTimeGPS(20, 0)
	>>> y = segments.segmentlist([Segment(5, 15), Segment(25, 35)])
	>>> abs(x & y)
	LIGOTimeGPS(10, 0)
	>>> abs(x | y)
	LIGOTimeGPS(30, 0)
	>>> 8.0 in x
	True
	>>> 12 in x
	False
	>>> Segment(2, 3) in x
	True
	>>> Segment(2, 12) in x
	False
	>>> segments.segment(2, 3) in x
	True
	>>> segments.segment(2, 12) in x
	False
	>>> # make sure results are segment table row objects
	>>> segments.segmentlist(map(Segment, x & y))	# doctest: +ELLIPSIS
	[<ligolw.lsctables.Segment object at 0x...>, <ligolw.lsctables.Segment object at 0x...>]

	Unbounded intervals are permitted.  See gpsproperty for information
	on the encoding scheme used internally, and its limitations.

	Example:

	>>> x = Segment()
	>>> # OK
	>>> x.start = -segments.infinity()
	>>> # also OK
	>>> x.start = float("-inf")
	>>> # infinite boundaries always returned as segments.infinity
	>>> # instances
	>>> x.start
	-infinity
	>>> x.end = float("+inf")
	>>> x.segment
	segment(-infinity, infinity)

	See also SegmentDef, SegmentSum, and ligolw.utils.segments.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SegmentTable.validcolumns))

	start = gpsproperty("start_time", "start_time_ns")
	end = gpsproperty("end_time", "end_time_ns")
	segment = segmentproperty("start", "end")

	# emulate a ligo.segments.segment object

	def __abs__(self):
		return abs(self.segment)

	def __lt__(self, other):
		return self.segment < other

	def __eq__(self, other):
		return self.segment == other

	def __contains__(self, other):
		return other in self.segment

	def __getitem__(self, i):
		return self.segment[i]

	def __init__(self, *args, **kwargs):
		if args:
			try:
				# first try unpacking arguments
				self.segment = args
			except ValueError:
				# didn't work, try unpacking 0th argument
				self.segment, = args
		for key, value in kwargs.items():
			setattr(self, key, value)

	def __len__(self):
		return len(self.segment)

	def __nonzero__(self):
		return bool(self.segment)


SegmentTable.RowType = Segment


#
# =============================================================================
#
#                            segment_definer:table
#
# =============================================================================
#


SegmentDefID = ligolw.Column.next_id.type("segment_def_id")


class SegmentDefTable(ligolw.Table):
	tableName = "segment_definer"
	validcolumns = {
		"process:process_id": "int_8s",
		"segment_def_id": "int_8s",
		"ifos": "lstring",
		"name": "lstring",
		"version": "int_4s",
		"comment": "lstring",
		"insertion_time": "int_4s"
	}
	constraints = "PRIMARY KEY (segment_def_id)"
	next_id = SegmentDefID(0)


class SegmentDef(ligolw.Table.RowType):
	"""
	One row of the segment_definer table.  Stores the metadata
	describing a segment list.

	Segment lists define the time intervals for which a condition is
	true, and the XML encoding provides a tri-state definition:  times
	when a condition is true, times when it is false, and times when
	the state of the condition is not known.  The intervals within
	which the state of the condition is known to be true or false are
	recorded in the segment_summary table, and for the times when the
	state is known the times when it is true are recorded in the
	segment table.  It is not an error for the segment table to contain
	segments (indicating a true state) outside of the intervals for
	which the segment_summary says the state is known, but they will be
	ignored.  See ligo.utils.segments for a high-level interface to the
	segment information in an XML document.  Note, in particular, the
	definitions given there for the interpretation of the state of the
	condition and the rules of ternary logic to be used with segment
	lists.

	Example:

	>>> x = SegmentDef()
	>>> x.instruments = ("H1", "L1")
	>>> print(x.ifos)
	H1,L1
	>>> assert x.instruments == set(['H1', 'L1'])

	See also Segment, SegmentSum, and ligolw.utils.segments.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SegmentDefTable.validcolumns))

	instruments = instrumentsproperty("ifos")


SegmentDefTable.RowType = SegmentDef


#
# =============================================================================
#
#                            segment_summary:table
#
# =============================================================================
#


SegmentSumID = ligolw.Column.next_id.type("segment_sum_id")


class SegmentSumTable(ligolw.Table):
	tableName = "segment_summary"
	validcolumns = {
		"process:process_id": "int_8s",
		"segment_sum_id": "int_8s",
		"start_time": "int_4s",
		"start_time_ns": "int_4s",
		"end_time": "int_4s",
		"end_time_ns": "int_4s",
		"comment": "lstring",
		"segment_definer:segment_def_id": "int_8s"
	}
	constraints = "PRIMARY KEY (segment_sum_id)"
	next_id = SegmentSumID(0)

	def get(self, segment_def_id = None):
		"""
		Return a segmentlist object describing the times spanned by
		the segments carrying the given segment_def_id.  If
		segment_def_id is None then all segments are returned.

		NOTE:  the result is not coalesced, the segmentlist
		contains the segments as they appear in the table.

		NOTE:  the result is a copy of the contents of the table.
		Modifications of the object returned by this method have no
		effect on the original data in the table.  To manipulate
		the segment lists in an XML document see
		ligolw.utils.segments.
		"""
		if segment_def_id is None:
			return segments.segmentlist(row.segment for row in self)
		return segments.segmentlist(row.segment for row in self if row.segment_def_id == segment_def_id)


class SegmentSum(Segment):
	"""
	One row of a segment_summary table.  Represents an interval of time
	for which the state of the condition represented by a segment list
	is known to be true or false.

	See also SegmentDef, Segment, and ligolw.utils.segments.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, SegmentSumTable.validcolumns))

	start = gpsproperty("start_time", "start_time_ns")
	end = gpsproperty("end_time", "end_time_ns")
	segment = segmentproperty("start", "end")


SegmentSumTable.RowType = SegmentSum


#
# =============================================================================
#
#                               time_slide:table
#
# =============================================================================
#


TimeSlideID = ligolw.Column.next_id.type("time_slide_id")


class TimeSlideTable(ligolw.Table):
	tableName = "time_slide"
	validcolumns = {
		"process:process_id": "int_8s",
		"time_slide_id": "int_8s",
		"instrument": "lstring",
		"offset": "real_8"
	}
	constraints = "PRIMARY KEY (time_slide_id, instrument)"
	next_id = TimeSlideID(0)

	def as_dict(self):
		"""
		Return a dictionary mapping time slide IDs to offset
		dictionaries.

		NOTE:  very little checking is done, e.g., for repeated
		instruments for a given ID (which could suggest an ID
		collision).
		"""
		# import is done here to reduce risk of a cyclic
		# dependency.  at the time of writing there is not one, but
		# we can help prevent it in the future by putting this
		# here.
		from lalburst.offsetvector import offsetvector
		return dict((time_slide_id, offsetvector((row.instrument, row.offset) for row in rows)) for time_slide_id, rows in itertools.groupby(sorted(self, key = lambda row: row.time_slide_id), lambda row: row.time_slide_id))

	def append_offsetvector(self, offsetvect, process):
		"""
		Append rows describing an instrument --> offset mapping to
		this table.  offsetvect is a dictionary mapping instrument
		to offset.  process should be the row in the process table
		on which the new time_slide table rows will be blamed (or
		any object with a process_id attribute).  The return value
		is the time_slide_id assigned to the new rows.
		"""
		time_slide_id = self.get_next_id()
		for instrument, offset in offsetvect.items():
			self.appendRow(
				process_id = process.process_id,
				time_slide_id = time_slide_id,
				instrument = instrument,
				offset = offset
			)
		return time_slide_id

	def get_time_slide_id(self, offsetdict, create_new = None, superset_ok = False, nonunique_ok = False):
		"""
		Return the time_slide_id corresponding to the offset vector
		described by offsetdict, a dictionary of instrument/offset
		pairs.

		If the optional create_new argument is None (the default),
		then the table must contain a matching offset vector.  The
		return value is the ID of that vector.  If the table does
		not contain a matching offset vector then KeyError is
		raised.

		If the optional create_new argument is set to a Process
		object (or any other object with a process_id attribute),
		then if the table does not contain a matching offset vector
		a new one will be added to the table and marked as having
		been created by the given process.  The return value is the
		ID of the (possibly newly created) matching offset vector.

		If the optional superset_ok argument is False (the default)
		then an offset vector in the table is considered to "match"
		the requested offset vector only if they contain the exact
		same set of instruments.  If the superset_ok argument is
		True, then an offset vector in the table is considered to
		match the requested offset vector as long as it provides
		the same offsets for the same instruments as the requested
		vector, even if it provides offsets for other instruments
		as well.

		More than one offset vector in the table might match the
		requested vector.  If the optional nonunique_ok argument is
		False (the default), then KeyError will be raised if more
		than one offset vector in the table is found to match the
		requested vector.  If the optional nonunique_ok is True
		then the return value is the ID of one of the matching
		offset vectors selected at random.
		"""
		# look for matching offset vectors
		if superset_ok:
			ids = [time_slide_id for time_slide_id, slide in self.as_dict().items() if offsetdict == dict((instrument, offset) for instrument, offset in slide.items() if instrument in offsetdict)]
		else:
			ids = [time_slide_id for time_slide_id, slide in self.as_dict().items() if offsetdict == slide]
		if len(ids) > 1:
			# found more than one
			if nonunique_ok:
				# and that's OK
				return ids[0]
			# and that's not OK
			raise KeyError("%s not unique" % repr(offsetdict))
		if len(ids) == 1:
			# found one
			return ids[0]
		# offset vector not found in table
		if create_new is None:
			# and that's not OK
			raise KeyError("%s not found" % repr(offsetdict))
		# that's OK, create new vector, return its ID
		return self.append_offsetvector(offsetdict, create_new)


class TimeSlide(ligolw.Table.RowType):
	"""
	One row of a time_slide table;  mainly an ID, and an instrument,
	offset pair.  The rows that share a common ID together define a
	vector of offsets to be applied to a set of antennas when analyzing
	their data, one offset for each antenna.

	NOTE:  it is an error for more than one row to have the same ID and
	instrument name, however for performance reasons there is very
	little (but some) error checking done to enforce this rule.
	Violating this constraint leads to undefined behaviour.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, TimeSlideTable.validcolumns))


TimeSlideTable.RowType = TimeSlide


#
# =============================================================================
#
#                             coinc_definer:table
#
# =============================================================================
#


CoincDefID = ligolw.Column.next_id.type("coinc_def_id")


class CoincDefTable(ligolw.Table):
	tableName = "coinc_definer"
	validcolumns = {
		"coinc_def_id": "int_8s",
		"search": "lstring",
		"search_coinc_type": "int_4u",
		"description": "lstring"
	}
	constraints = "PRIMARY KEY (coinc_def_id)"
	next_id = CoincDefID(0)
	how_to_index = {
		"cd_ssct_index": ("search", "search_coinc_type")
	}

	def get_coinc_def_id(self, search, search_coinc_type, create_new = True, description = None):
		"""
		Return the coinc_def_id for the row in the table whose
		search string and search_coinc_type integer have the values
		given.  If a matching row is not found, the default
		behaviour is to create a new row and return the ID assigned
		to the new row.  If, instead, create_new is False then
		KeyError is raised when a matching row is not found.  The
		optional description parameter can be used to set the
		description string assigned to the new row if one is
		created, otherwise the new row is left with no description.
		"""
		# look for the ID
		rows = [row for row in self if (row.search, row.search_coinc_type) == (search, search_coinc_type)]
		if len(rows) > 1:
			raise ValueError("(search, search coincidence type) = ('%s', %d) is not unique" % (search, search_coinc_type))
		if len(rows) > 0:
			return rows[0].coinc_def_id

		# coinc type not found in table
		if not create_new:
			raise KeyError((search, search_coinc_type))
		coinc_def_id = self.get_next_id()
		self.appendRow(
			coinc_def_id = coinc_def_id,
			search = search,
			search_coinc_type = search_coinc_type,
			description = description
		)

		# return new ID
		return coinc_def_id


class CoincDef(ligolw.Table.RowType):
	"""
	One row in the coinc_definer table, providing the mapping from
	application-defined coincidence types to database IDs.

	A "coincidence" in this context is an application-defined concept
	in which two things are somehow associated with each other.
	Examples might include two inspiral triggers, one each from a pair
	of detectors, or an inspiral trigger and an inspiral injection, or
	perhaps a burst trigger and a data quality segment.  Any objects
	carrying IDs can participate in a coincidence, and what it means
	for them to be said to be coincident is, in general, known only to
	the application that created the document.

	Usually many coincidences are associated with a given coincidence
	type, for example there will be many examples of sets of inspiral
	triggers from distinct instruments that are coincident with each
	other, or many coincidences between inspiral injections and
	inspiral triggers.

	When processing documents, a typical operation will require all
	coincidences of a given type to be retrieved from the document, for
	example an inspiral<-->inspiral coincidences.  For performance
	reasons it is advantageous to label each coincidence with an ID
	indicating which set of coincidences it belongs to so that all
	members of a set can be retrieved quickly.  A coinc_definer row
	maps the coincidence set's definition to an arbitrarily assigned
	database ID used for this purpose.

	Applications are permitted to define their own coincidence sets,
	more or less arbitrarily.  To do so, an application (meaning a user
	or group of users of this file format, not necessarily one program
	specifically) choses a "search" name for itself.  This choice must
	be co-ordinated so that it is unique across all users of the file
	format.  Having chosen a search name, the application then assigns
	integer search coincidence types, one for each kind of coincidence
	that is to be represented in the database.  Within the application,
	i.e. within that search, the search coincidence types are assigned
	any way the users please, but they must be globally unique within
	that application, and their meanings must be fixed for all time
	(there are over 4 billion allowed values, so simply retiring
	obsolete type values should be fine or the forseeable future).

	The coinc_definer row allows a human-readable description to be
	recorded with the coincidence definition.  This plays no role in
	database queries, the text associated with a given coincidence type
	is free to change over time as people wish, and so when documents
	are merged only the search and search_coinc_type values are
	considered to be the unique definers of coincidence types.  If two
	documents are combined that contain coincidences of the same type
	but for whom the text descriptions differ, and a coincidence type
	de-duplication operation is performed, one of the two will be
	chosen at random and the other discarded.  A corollary is that the
	description cannot be relied upon to disentangle degenerate
	assignment of search, search_coinc_type pairs.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, CoincDefTable.validcolumns))


CoincDefTable.RowType = CoincDef


#
# =============================================================================
#
#                              coinc_event:table
#
# =============================================================================
#


CoincID = ligolw.Column.next_id.type("coinc_event_id")


class CoincTable(ligolw.Table):
	tableName = "coinc_event"
	validcolumns = {
		"process:process_id": "int_8s",
		"coinc_definer:coinc_def_id": "int_8s",
		"coinc_event_id": "int_8s",
		"time_slide:time_slide_id": "int_8s",
		"instruments": "lstring",
		"nevents": "int_4u",
		"likelihood": "real_8"
	}
	constraints = "PRIMARY KEY (coinc_event_id)"
	next_id = CoincID(0)
	how_to_index = {
		"ce_cdi_index": ("coinc_def_id",),
		"ce_tsi_index": ("time_slide_id",)
	}


class Coinc(ligolw.Table.RowType):
	"""
	Each row in the coinc_event table represents a single coincidence.
	For example a pair of inspiral triggers that occur at similar
	times, or an inspiral trigger that occurs at a time near a software
	injection.

	The coinc_event row itself contains almost no information about the
	coincidence.  It provides a unique ID for the coincidence, and it
	carries the IDs of objects in other tables that define the nature
	of the coincidence.  For example, the coinc_def_id identifies the
	set of coincidences of which this is a member, with the description
	of that set found in the coinc_definer table.  The time_slide_id
	points to the vector of time offsets applied to the detectors that
	participated in the coincidence, when that is a meaningful concept
	for a coincidence.

	The objects that participate in the coincidence are encoded in the
	coinc_event_map table, which provides an object ID <--> coinc_event
	ID many-to-many mapping.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, CoincTable.validcolumns))

	insts = instrumentsproperty("instruments")


CoincTable.RowType = Coinc


#
# =============================================================================
#
#                            coinc_event_map:table
#
# =============================================================================
#


class CoincMapTable(ligolw.Table):
	tableName = "coinc_event_map"
	validcolumns = {
		"coinc_event:coinc_event_id": "int_8s",
		"table_name": "char_v",
		"event_id": "int_8s"
	}
	how_to_index = {
		"cem_tn_ei_index": ("table_name", "event_id"),
		"cem_cei_index": ("coinc_event_id",)
	}

	def applyKeyMapping(self, mapping):
		table_column = self.getColumnByName("table_name")
		event_id_column = self.getColumnByName("event_id")
		coinc_event_id_column = self.getColumnByName("coinc_event_id")
		for i, (table_name, old_event_id, old_coinc_event_id) in enumerate(zip(table_column, event_id_column, coinc_event_id_column)):
			try:
				event_id_column[i] = mapping[table_name, old_event_id]
			except KeyError:
				pass
			try:
				coinc_event_id_column[i] = mapping["coinc_event", old_coinc_event_id]
			except KeyError:
				pass


class CoincMap(ligolw.Table.RowType):
	"""
	Link an object to a coincidence.  The (table_name, event_id) pair
	defines the object by specifying its ID and the table in which that
	ID is found, and coinc_event_id the ID of the coincidence.  It is
	unusual in database design for a reference to another object to
	require the table name to be given, but it had to be done.  In
	practice it works well, however, as a rule:

		Queries *must* constrain the table name column.

	Do not omit a table name constraint, the results are undefined.
	Note, also, that the table is indexed on the (table_name, event_id)
	pair so omitting the table name in the query will incur a
	potentially significant performance penalty as the index cannot be
	used.
	"""
	__slots__ = tuple(map(ligolw.Column.ColumnName, CoincMapTable.validcolumns))


CoincMapTable.RowType = CoincMap


#
# =============================================================================
#
#                                Table Metadata
#
# =============================================================================
#


#
# Put our table definitions into the name ---> table type mapping.
#


ligolw.Table.TableByName.update({
	CoincDefTable.tableName: CoincDefTable,
	CoincInspiralTable.tableName: CoincInspiralTable,
	CoincMapTable.tableName: CoincMapTable,
	CoincRingdownTable.tableName: CoincRingdownTable,
	CoincTable.tableName: CoincTable,
	ProcessParamsTable.tableName: ProcessParamsTable,
	ProcessTable.tableName: ProcessTable,
	SearchSummaryTable.tableName: SearchSummaryTable,
	SegmentDefTable.tableName: SegmentDefTable,
	SegmentSumTable.tableName: SegmentSumTable,
	SegmentTable.tableName: SegmentTable,
	SimBurstTable.tableName: SimBurstTable,
	SimInspiralTable.tableName: SimInspiralTable,
	SimRingdownTable.tableName: SimRingdownTable,
	SimCBCTable.tableName: SimCBCTable,
	SnglBurstTable.tableName: SnglBurstTable,
	SnglInspiralTable.tableName: SnglInspiralTable,
	SnglRingdownTable.tableName: SnglRingdownTable,
	TimeSlideTable.tableName: TimeSlideTable
})
