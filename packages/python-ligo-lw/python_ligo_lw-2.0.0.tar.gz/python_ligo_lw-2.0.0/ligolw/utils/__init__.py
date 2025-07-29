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
Library of utility code for LIGO Light Weight XML applications.
"""


import bz2
import codecs
import contextlib
import gzip
import lzma
import os
import signal
import stat
import sys
import urllib.parse
import urllib.request


from .. import __author__, __date__, __version__
import ligolw


__all__ = [
	"sort_files_by_size",
	"local_path_from_url",
	"load_fileobj",
	"load_filename",
	"load_url",
	"write_fileobj",
	"write_filename",
	"write_url"
]


#
# =============================================================================
#
#                             Named File Utilities
#
# =============================================================================
#


def sort_files_by_size(filenames, reverse = False):
	"""
	Return a list of the filenames sorted in order from smallest file
	to largest file (or largest to smallest if reverse is set to True).
	If a filename in the list is None (used by many ligolw based codes
	to indicate stdin), its size is treated as 0.  The filenames may be
	any sequence, including generator expressions.
	"""
	if reverse:
		ligolw.logger.info("sorting files from largest to smallest ...")
	else:
		ligolw.logger.info("sorting files from smallest to largest ...")
	return sorted(filenames, key = (lambda filename: os.stat(filename)[stat.ST_SIZE] if filename is not None else 0), reverse = reverse)


def local_path_from_url(url):
	"""
	For URLs that point to locations in the local filesystem, extract
	and return the filesystem path of the object to which they point.
	As a special case pass-through, if the URL is None, the return
	value is None.  Raises ValueError if the URL is not None and does
	not point to a local file.

	Example:

	>>> print(local_path_from_url(None))
	None
	>>> local_path_from_url("file:///home/me/somefile.xml.gz")
	'/home/me/somefile.xml.gz'
	"""
	if url is None:
		return None
	scheme, host, path = urllib.parse.urlparse(url)[:3]
	if scheme.lower() not in ("", "file") or host.lower() not in ("", "localhost"):
		raise ValueError("%s is not a local file" % repr(url))
	return path


#
# =============================================================================
#
#                           Context Manager Helpers
#
# =============================================================================
#


class RewindableInputFile(object):
	# The GzipFile class in Python's standard library is, in my
	# opinion, somewhat weak.  Instead of relying on the return values
	# from the file object's .read() method, GzipFile checks for EOF
	# using calls to .seek().  Furthermore, it uses .seek() instead of
	# buffering data internally as required.  This makes GzipFile
	# gratuitously unable to work with pipes, urlfile objects, and
	# anything else that does not support seeking.  To hack around
	# this, this class provides the buffering needed by GzipFile.  It
	# also does proper EOF checking, and uses the results to emulate
	# the results of GzipFile's .seek() games.
	#
	# By wrapping your file object in this class before passing it to
	# GzipFile, you can use GzipFile to read from non-seekable files.
	#
	# How GzipFile checks for EOF == call .tell() to get current
	# position, seek to end of file with .seek(0, 2), call .tell()
	# again and check if the number has changed from before, if it has
	# then we weren't at EOF so call .seek() with original position and
	# keep going.  ?!

	def __init__(self, fileobj, buffer_size = 1024):
		# the real source of data
		self.fileobj = fileobj
		# where the application thinks it is in the file.  this is
		# used to fake .tell() because file objects that don't
		# support seeking, like stdin, report IOError, and the
		# things returned by urllib don't have a .tell() method at
		# all.
		self.pos = 0
		# how many octets of the internal buffer to return before
		# getting more data
		self.reuse = 0
		# the internal buffer
		self.buf = b" " * buffer_size
		# flag indicating a .seek()-based EOF test is in progress
		self.gzip_hack_pretend_to_be_at_eof = False
		# avoid attribute look-ups
		try:
			self._next = self.fileobj.next
		except AttributeError:
			self.next = lambda *args, **kwargs: fileobj.next(*args, **kwargs)
		self._read = self.fileobj.read
		self.close = self.fileobj.close

	def __iter__(self):
		return self

	def next(self):
		if self.gzip_hack_pretend_to_be_at_eof:
			return b""
		if self.reuse:
			buf = self.buf[-self.reuse:]
			self.reuse = 0
		else:
			buf = self._next()
			self.buf = (self.buf + buf)[-len(self.buf):]
		self.pos += len(buf)
		return buf

	def read(self, size = None):
		if self.gzip_hack_pretend_to_be_at_eof:
			return b""
		if self.reuse:
			if self.reuse < 0:
				buf = self._read(size - self.reuse)
				self.buf = (self.buf + buf)[-len(self.buf):]
				buf = buf[-self.reuse:]
				self.reuse = 0
			# size is None --> condition is False
			elif 0 <= size < self.reuse:
				buf = self.buf[-self.reuse:-self.reuse + size]
				self.reuse -= size
			else:
				buf = self.buf[-self.reuse:]
				self.reuse = 0
				# size is None --> condition is False
				if len(buf) < size:
					buf += self.read(size - len(buf))
		else:
			buf = self._read(size)
			self.buf = (self.buf + buf)[-len(self.buf):]
		self.pos += len(buf)
		return buf

	def seek(self, offset, whence = os.SEEK_SET):
		self.gzip_hack_pretend_to_be_at_eof = False
		if whence == os.SEEK_SET:
			if offset >= 0 and 0 <= self.pos + self.reuse - offset < len(self.buf):
				self.reuse += self.pos - offset
				self.pos = offset
			else:
				raise IOError("seek out of range")
		elif whence == os.SEEK_CUR:
			if self.reuse - len(self.buf) <= offset:
				self.reuse -= offset
				self.pos += offset
			else:
				raise IOError("seek out of range")
		elif whence == os.SEEK_END:
			if offset == 0:
				self.gzip_hack_pretend_to_be_at_eof = True
			else:
				raise IOError("seek out of range")

	def tell(self):
		if self.gzip_hack_pretend_to_be_at_eof:
			# check to see if we are at EOF by seeing if we can
			# read 1 character.  save it in the internal buffer
			# to not loose it.
			c = self._read(1)
			self.buf = (self.buf + c)[-len(self.buf):]
			self.reuse += len(c)
			if c:
				# this will not return the same answer as
				# when GzipFile called it before seeking to
				# EOF
				return self.pos + 1
		return self.pos

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.close()
		return False


class NoCloseFlushWrapper(object):
	"""
	File-like wrapper around a file object that intercepts .close()
	method calls and replaces them with .flush().  Can be used as a
	context manager.  .next(), .read(), .write(), .tell() and .flush()
	are all passed through to the wrapped file object.

	This is useful when writing data to a file object inside a function
	using some kind of encoder.  It is convenient to use context
	managers for error handling and clean-up but the file object should
	not be closed when finished because the calling code expects to
	have control returned to it with the file still open.  In some
	cases there is no way to prevent an encoder from .close()ing a file
	when it exits and cleans up, and this wrapper can be useful as a
	work-around.
	"""
	def __init__(self, fileobj):
		self.fileobj = fileobj
		# avoid attribute look-ups
		try:
			self.next = self.fileobj.next
		except AttributeError:
			# replace our .next() method with something that
			# will raise a more meaningful exception if
			# attempted
			self.next = lambda *args, **kwargs: fileobj.next(*args, **kwargs)
		try:
			self.read = self.fileobj.read
		except AttributeError:
			# replace our .read() method with something that
			# will raise a more meaningful exception if
			# attempted
			self.read = lambda *args, **kwargs: fileobj.read(*args, **kwargs)
		try:
			self.write = self.fileobj.write
		except AttributeError:
			# replace our .write() method with something that
			# will raise a more meaningful exception if
			# attempted
			self.write = lambda *args, **kwargs: fileobj.write(*args, **kwargs)
		try:
			self.tell = self.fileobj.tell
		except AttributeError:
			self.tell = lambda *args, **kwargs: fileobj.tell(*args, **kwargs)
		try:
			self.flush = self.fileobj.flush
		except AttributeError:
			self.flush = lambda *args, **kwargs: fileobj.flush(*args, **kwargs)

	def __iter__(self):
		return self

	def close(self):
		self.flush()

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.close()
		return False


class SignalsTrap(object):
	"""
	Context manager that defers signals (by default SIGTERM and
	SIGTSTP) for the lifetime of the context manager object.  On entry,
	the context manager replaces the signal handlers for the requested
	signals with a version that records the occurance of the given
	signals.  On exit, the original signal handlers are restored, and
	any signals that were received during the interveneing time are
	resent to the current process in the order received.

	This is useful to help prevent HTCondor from evicting or
	terminating a job while it is in the process of writing a file.
	The default signals are the signals used by HTCondor for these
	purposes.  If a file write operation is wrapped in this context
	manager, the eviction or job termination will occur after the file
	is closed.  If the write process takes too long, HTCondor will
	eventually lose patience and SIGKILL the process, but the grace
	period is configurable, and admins can adjust it to be the length
	of time they are willing to let a process try to finish writing a
	file before it's forced off the cluster.

	trap_signals may be an empty sequenced or None, in which case no
	modification of signal handling is performed.  Repeats of signal
	numbers in trap_signals are ignored.

	NOTE:  the signal.signal() system call cannot be invoked from
	threads, so code that uses this context manager to protect against
	eviction, and that might be called from inside a thread, must
	arrange for trap_signals to be set to None or an empty sequence to
	disable this code.
	"""
	default_signals = (signal.SIGTERM, signal.SIGTSTP)

	def __init__(self, trap_signals = default_signals):
		self.trap_signals = trap_signals

	def handler(self, signum, frame):
		self.deferred_signals.append(signum)

	def __enter__(self):
		self.oldhandlers = {}
		self.deferred_signals = []
		if self.trap_signals is not None:
			for sig in set(self.trap_signals):
				self.oldhandlers[sig] = signal.getsignal(sig)
				signal.signal(sig, self.handler)
		return self

	def __exit__(self, *args):
		# restore original handlers
		while self.oldhandlers:
			signal.signal(*self.oldhandlers.popitem())
		# send ourselves the trapped signals in order
		while self.deferred_signals:
			os.kill(os.getpid(), self.deferred_signals.pop(0))
		return False


class tildefile(object):
	"""
	Context manager wrapper around open() for use when writing to named
	files.  Provides a form of protection against failures that occur
	during the write process when overwriting an existing document.
	Modifies the filename passed to open() to include a trailing "~"
	(tilde) character.  Data is written to that file.  When the context
	manager exits, the file is closed and renamed to the original name
	without the "~" suffix.  In this way, the original file is only
	overwritten when the write operation completes successfully.

	NOTE:  if another file exists whose name differs from the target
	file only by the addition of a tilde character at the end, it will
	be silently overwritten.  Do not use this in contexts where
	filenames may take that form.

	NOTE:  if an IOError exception occurs when opening the file with a
	"~" suffix appended, then this code attempts, instead, to write to
	the original filename.  If that succeeds, then failures that occur
	during the write process will leave the target file corrupted.
	This has been found to result in a lower net failure rate, but that
	assessment might change in the future, so do not rely on this
	behaviour.
	"""
	def __init__(self, filename):
		if not filename:
			raise ValueError(filename)
		self.filename = filename

	def __enter__(self):
		try:
			self.tildefilename = self.filename + "~"
			self.fobj = open(self.tildefilename, "wb")
		except IOError:
			self.tildefilename = None
			self.fobj = open(self.filename, "wb")
		return self.fobj

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.fobj.close()
		del self.fobj

		#
		# only rename the "~" version to the final destination if
		# no exception has occurred.
		#

		if exc_type is None and self.tildefilename is not None:
			os.rename(self.tildefilename, self.filename)

		return False


#
# =============================================================================
#
#                                 Input/Output
#
# =============================================================================
#


def load_fileobj(fileobj, compress = None, xmldoc = None, contenthandler = ligolw.ContentHandler):
	"""
	Parse the contents of the file object fileobj, and return the
	contents as a LIGO Light Weight document tree.  The file object
	does not need to be seekable.  The file object must be in binary
	mode.

	The compress parameter selects the decompression algorithm to use.
	Valid values are:  "auto" to automatically deduce the decompression
	scheme from the file format;  one of "bz2", "gz", or "xz" to force
	bzip2, gzip, or lzma/xz decompression, respectively;  False to
	disable decompression;  or None to select the default behaviour
	(which is "auto").

	If the optional xmldoc argument is provided and not None, the
	parsed XML tree will be appended to that document, otherwise a new
	document will be created.  The return value is the xmldoc argument
	or the root of the newly created XML tree.

	Example:

	>>> from io import BytesIO
	>>> f = BytesIO(b'<?xml version="1.0" encoding="utf-8" ?><!DOCTYPE LIGO_LW SYSTEM "http://ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt"><LIGO_LW><Table Name="demo:table"><Column Name="name" Type="lstring"/><Column Name="value" Type="real_8"/><Stream Name="demo:table" Type="Local" Delimiter=",">"mass",0.5,"velocity",34</Stream></Table></LIGO_LW>')
	>>> xmldoc = load_fileobj(f)

	The contenthandler argument specifies the SAX content handler to
	use when parsing the document.  See the ligolw package
	documentation for an explanation of a typical document parsing
	scenario and the content handler it uses.  See
	ligolw.PartialContentHandler and ligolw.FilteringContentHandler for
	examples of custom content handlers used to load subsets of
	documents into memory.
	"""
	if compress is None:
		# select default behaviour
		compress = "auto"

	if compress == "auto":
		# set keyword argument automatically from file format
		fileobj = RewindableInputFile(fileobj)
		magic = fileobj.read(6)
		fileobj.seek(0, os.SEEK_SET)
		if magic[:3] == b"\x42\x5A\x68":
			compress = "bz2"
		elif magic[:2] == b"\x1F\x8B":
			compress = "gz"
		elif magic[:6] == b"\xFD\x37\x7A\x58\x5A\x00":
			compress = "xz"
		elif magic[:4] == b"\x28\xB5\x2F\xFD":
			# NOTE:  only format detection is provided.  this
			# compression format is not supported.  will
			# trigger the unrecognized keyword arg exception
			# below
			compress = "zst"
		else:
			# format not recognized, assume not compressed
			compress = False

	#
	# select stream decoder
	#

	if compress == False:
		# pass-through
		pass
	elif compress == "bz2":
		# bzip2 decompression
		fileobj = bz2.BZ2File(fileobj, mode = "rb")
	elif compress == "gz":
		# gzip decompression
		fileobj = gzip.GzipFile(mode = "rb", fileobj = fileobj if type(fileobj) == RewindableInputFile else RewindableInputFile(fileobj))
	elif compress == "xz":
		# xz/lzma decompression
		fileobj = lzma.LZMAFile(fileobj, mode = "rb")
	else:
		# oops
		raise ValueError("unrecognized compress \"%s\"" % compress)

	#
	# parse stream into XML tree and return it
	#

	if xmldoc is None:
		xmldoc = ligolw.Document()

	ligolw.make_parser(contenthandler(xmldoc)).parse(fileobj)
	return xmldoc


def load_filename(filename, **kwargs):
	"""
	Parse the contents of the file identified by filename, and return
	the contents as a LIGO Light Weight document tree.  stdin is parsed
	if filename is None.  All keyword arguments are passed to
	load_fileobj(), see that function for more information.

	Example:

	>>> ligolw.logger.setLevel(ligolw.logging.INFO)
	>>> xmldoc = load_filename("demo.xml")
	"""
	ligolw.logger.info("reading %s ..." % (("'%s'" % filename) if filename is not None else "stdin"))
	if filename is None:
		return load_fileobj(sys.stdin.buffer, **kwargs)
	with open(filename, "rb") as fileobj:
		xmldoc = load_fileobj(fileobj, **kwargs)
	ligolw.logger.info("... reading %s done." % (("'%s'" % filename) if filename is not None else "stdin"))
	return xmldoc


def load_url(url, **kwargs):
	"""
	Parse the contents of file at the given URL and return the contents
	as a LIGO Light Weight document tree.  Any source from which
	Python's urllib library can read data is acceptable.  stdin is
	parsed if url is None.  When url is not a local file,
	urllib.request.urlopen() is used to access it, and if the keyword
	arguments timeout and/or context is set then those arguments are
	passed to urlopen().  All other keyword arguments are passed to
	load_fileobj(), see that function for more information.

	Example:

	>>> from os import getcwd
	>>> ligolw.logger.setLevel(ligolw.logging.INFO)
	>>> xmldoc = load_url("file://localhost/%s/demo.xml" % getcwd())
	"""
	# separate urlopen()'s kwargs from load_fileobj()'s
	urlopen_kwargs = dict((kwarg, kwargs.pop(kwarg)) for kwarg in ("context", "timeout") if kwarg in kwargs)
	try:
		# also accepts None as a valid local file
		filename = local_path_from_url(url)
	except ValueError:
		# not a local file
		ligolw.logger.info("reading %s ..." % (("'%s'" % url) if url is not None else "stdin"))
		with contextlib.closing(urllib.request.urlopen(url, **urlopen_kwargs)) as fileobj:
			xmldoc = load_fileobj(fileobj, **kwargs)
		ligolw.logger.info("... reading %s done." % (("'%s'" % url) if url is not None else "stdin"))
		return xmldoc
	# handle local files, and also None (stdin)
	return load_filename(filename, **kwargs)


def write_fileobj(xmldoc, fileobj, compress = None, compresslevel = 3, **kwargs):
	"""
	Writes the LIGO Light Weight document tree rooted at xmldoc to the
	given file object.  Internally, the .write() method of the xmldoc
	object is invoked and any additional keyword arguments are passed
	to that method.  The file object need not be seekable.  The file
	object must be in binary mode.

	The compress parameter selects the file compression format to use.
	Valid values are:  False to disable compression;  one of "bz2",
	"gz", or "xz" to select bzip2, gzip, or lzma compression,
	respectively;  or None to select the default behaviour (which is to
	disable compression).  When bzip2 or gzip compression is selected,
	the compresslevel parameter sets the compression level (the default
	is 3).

	Example:

	>>> xmldoc = load_filename("demo.xml")
	>>> write_fileobj(xmldoc, open("/dev/null","wb"))
	"""
	if compress is None:
		# select default behaviour
		compress = False

	with NoCloseFlushWrapper(fileobj) as fileobj:
		#
		# select stream encoder
		#

		if compress == False:
			# no compression
			pass
		elif compress == "bz2":
			fileobj = bz2.BZ2File(fileobj, mode = "wb", compresslevel = compresslevel)
		elif compress == "gz":
			fileobj = gzip.GzipFile(mode = "wb", fileobj = fileobj, compresslevel = compresslevel)
		elif compress == "xz":
			fileobj = lzma.LZMAFile(fileobj, mode = "wb", format = lzma.FORMAT_XZ)
		else:
			# oops
			raise ValueError("unrecognized compress \"%s\"" % compress)

		#
		# write file
		#

		with codecs.getwriter("utf_8")(fileobj) as fileobj:
			xmldoc.write(fileobj, **kwargs)


def write_filename(xmldoc, filename, compress = None, with_mv = True, trap_signals = SignalsTrap.default_signals, **kwargs):
	"""
	Writes the LIGO Light Weight document tree rooted at xmldoc to the
	file name filename.  If filename is None the file is written to
	stdout, otherwise it is written to the named file.

	The compress keyword argument selects the compression format to
	use.  Recognized values are:  "auto" to automatically select the
	format based on filename;  None to select the default behaviour
	(which is "auto");  or any of the compression format values
	recognized by write_fileobj().  When "auto" is the mode selected,
	then if the filename ends in ".bz2", ".gz", or ".xz" then the
	corresponding compression format is selected, othewrise if the
	filename does not match a recognized pattern or if filename is None
	(writing to stdout) then compression is disabled.

	If with_mv is True and filename is not None the filename has a "~"
	appended to it and the file is written to that name then moved to
	the requested name once the write has completed successfully.

	Internally, write_fileobj() is used to perform the write.  All
	additional keyword arguments are passed to write_fileobj().

	This function traps the signals in the trap_signals iterable during
	the write process (see SignalsTrap for the default signals), and it
	does this by temporarily installing its own signal handlers in
	place of the current handlers.  This is done to prevent HTCondor
	eviction during the write process.  When the file write is
	concluded the original signal handlers are restored.  Then, if
	signals were trapped during the write process, the signals are
	resent to the current process in the order in which they were
	received.  The signal.signal() system call cannot be invoked from
	threads, and trap_signals must be set to None or an empty sequence
	if this function is used from a thread.

	Example:

	>>> # write file
	>>> write_filename(xmldoc, "demo.xml")	# doctest: +SKIP
	>>> # write gzip-compressed file (auto-select format)
	>>> write_filename(xmldoc, "demo.xml.gz")	# doctest: +SKIP
	>>> # force compression off
	>>> write_filename(xmldoc, "demo.xml.gz", compress = False)	# doctest: +SKIP
	"""
	#
	# select format
	#

	if compress is None:
		# select default behaviour
		compress = "auto"
	if compress == "auto":
		if filename is None:
			# writing to stdout:  no filename = cannot deduce
			# compression format = turn compression off
			compress = False
		elif filename.endswith(".bz2"):
			compress = "bz2"
		elif filename.endswith(".gz"):
			compress = "gz"
		elif filename.endswith(".xz"):
			compress = "xz"
		elif filename.endswith(".zst"):
			# NOTE:  this format is not supported.  this will
			# trigger the unrecognized keyword arg exception in
			# write_fileobj()
			compress = "zst"
		else:
			# filename scheme not recognized, disable
			# compression
			compress = False

	ligolw.logger.info("writing %s ..." % (("'%s'" % filename) if filename is not None else "stdout"))
	with SignalsTrap(trap_signals):
		if filename is None:
			write_fileobj(xmldoc, sys.stdout.buffer, compress = compress, **kwargs)
		else:
			binary_open = lambda filename: open(filename, "wb")
			with (binary_open if not with_mv else tildefile)(filename) as fileobj:
				write_fileobj(xmldoc, fileobj, compress = compress, **kwargs)
	ligolw.logger.info("... writing %s done." % (("'%s'" % filename) if filename is not None else "stdout"))


def write_url(xmldoc, url, **kwargs):
	"""
	Writes the LIGO Light Weight document tree rooted at xmldoc to the
	URL name url.

	NOTE:  only URLs that point to local files can be written to at
	this time.  Internally, write_filename() is used to perform the
	write.  All additional keyword arguments are passed to that
	function.  The implementation might change in the future,
	especially if support for other types of URLs is ever added.

	Example:

	>>> write_url(xmldoc, "file:///data.xml")	# doctest: +SKIP
	>>> write_url(xmldoc, "file:///data.xml.gz", compress = 'gz')	# doctest: +SKIP
	"""
	return write_filename(xmldoc, local_path_from_url(url), **kwargs)
