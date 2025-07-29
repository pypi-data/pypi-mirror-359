# Copyright (C) 2006--2019,2021--2022,2024--2025  Kipp Cannon
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


"""
DOM-like library for handling LIGO Light Weight XML files.  For more
information on the Python DOM specification and SAX document content
handlers, please refer to the Python standard library reference and the
documentation it links to.

This module provides class definitions corresponding to the elements that
can be found in a LIGO Light Weight XML file.  It also provides a class
representing an entire LIGO Light Weight XML document, a ContentHandler
class for use with SAX2 parsers, and a convenience function for
constructing a parser.

Here is a brief tutorial for a common use case:  load a LIGO Light-Weight
XML document containing tabular data complying with the LSC table
definitions, access rows in the tables including the use of ID-based cross
references, modify the contents of a table, and finally write the document
back to disk.  Please see the documentation for the modules, classes,
functions, and methods shown below for more information.

Example:

>>> # import modules
>>> import ligolw
>>> # enable verbosity throughout library
>>> ligolw.logger.setLevel(ligolw.logging.INFO)
>>> 
>>> # load a document.  several compressed file formats are recognized
>>> filename = "inspiral_event_id_test_in1.xml.gz"
>>> xmldoc = ligolw.utils.load_filename(filename)
>>> 
>>> # retrieve the process and sngl_inspiral tables.  these are list-like
>>> # objects of rows.  the row objects' attributes are the column names
>>> process_table = ligolw.lsctables.ProcessTable.get_table(xmldoc)
>>> sngl_inspiral_table = ligolw.lsctables.SnglInspiralTable.get_table(xmldoc)
>>> 
>>> # fix the mtotal column in the sngl_inspiral table
>>> for row in sngl_inspiral_table:
...	row.mtotal = row.mass1 + row.mass2
...
>>> # construct a look-up table mapping process_id to row in process table
>>> index = dict((row.process_id, row) for row in process_table)
>>> 
>>> # for each trigger in the sngl_inspiral table, print the name of the user
>>> # who ran the job that produced it, the computer on which the job ran, and
>>> # the GPS end time of the trigger
>>> for row in sngl_inspiral_table:
...	process = index[row.process_id]
...	print("%s@%s: %s s" % (process.username, process.node, str(row.end)))
...
inspiralbns@node120: 600000000.926757812 s
inspiralbns@node120: 600000000.919189453 s
inspiralbns@node120: 600000000.926757812 s
inspiralbns@node120: 600000000.924072265 s
>>> # write document.  the file is automatically compressed because its name
>>> # ends with .gz, and several other compression formats are also supported
>>> ligolw.utils.write_filename(xmldoc, filename)	# doctest: +SKIP

Version 2 Notes:

The LIGO Light-Weight XML document foramt does not have a formal
specification, instead it is mostly defined by active implementations.
Those implementations have differed in incompatible ways in the past, and
might still do so today.  Historically, this library made an effort to be
as flexible as posisble with regard to the document content to allow
documents compatible with all other I/O libraries to be read and written.
The only true requirement imposed by this library was that documents were
required to be valid XML and comply with the DTD (when that was supplied).
Aspects of the file format outside the scope of XML itself, for example how
to encode a choice of units in a Dim element, did not necessarily have a
strict specification imposed, but as a consequence high-level features
could not be implemented because it wasn't possible to ensure input
documents would comply with the necessary format assumptions.  To implement
more convenient high-level support for the document contents, for example
to cause this libray to treat Table elements as containing tabular data
instead of blocks of text, calling codes were required to explicitly enable
additional parsing rules by constructing a suitable content handler object
(the object responsible for translating XML components to the corresponding
Python objects).  This required numerous module imports and cryptic symbol
declarations, often for reasons that weren't clear to users of the library.
Over time the number of users of this file format has dwindled, and since
the user community that remains works exclusively with documents that
comply with the high-level format assumptions of this library, the
motivation has evaporated for continuing to inconvenience those remaining
users with the cryptic imports and configuration boilerplate required to
support other hypothetical users working with non-compliant documents.
Therefore, starting with version 2.0 that flexibility was removed.  All
documents processed with this library are now required to comply with the
file format defined by this library.  Removing the flexibility increases
document loading speed, and makes calling codes simpler, and less sensitive
to future API changes.
"""


from .version import __author__, __date__, __version__


__all__ = [
	"dbtables",
	"lsctables",
	"tokenizer",
	"types",
	"utils"
]


#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#


import base64
import copy
import datetime
import dateutil.parser
from functools import reduce
import itertools
import logging
import numpy
import re
import sys
from tqdm import tqdm
from xml import sax
from xml.sax.xmlreader import AttributesImpl
# the xmlescape() call replaces things like "<" with "&lt;" so that the
# string will not confuse an XML parser when the file is read.  this needs
# to be done explicitly as the last thing done to any string that might
# contain such characters before it is sent to the output stream.  turning
# "&lt;" back into "<" during file reading is handled by the .characters()
# method of the content handler, e.g., ContentHandler, so there is almost
# nowhere in this library where something special is needed to handle that.
# FIXME:  I might have overlooked the handling of XML excape codes in
# attribute values.  we never apply xmlescape() to them when writing and
# because parsing attribute values is handled entirely internally within
# the SAX library, I don't know if it has applied the un-escape
# transformation or not.
from xml.sax.saxutils import escape as xmlescape
from xml.sax.saxutils import unescape as xmlunescape
import yaml


from . import tokenizer
# NOTE:  not a good idea to import something as a name that conflicts with
# part of the standard library, but after decades of use there's been no
# need to use the native types module in this code, so this is thought to
# be reasonable.  doing this allows calling code to access the local types
# module via this module's own namespace, avoiding additional imports in
# calling code and making that code easier to read.
from . import types
# NOTE:  the lsctables module is imported at the end of this module
# NOTE:  the utils subpackage is imported at the end of this module


#
# =============================================================================
#
#                        Logging Facility for Verbosity
#
# =============================================================================
#


#
# Logger instance shared by all code in this library
#


logger = logging.getLogger(__name__)


#
# set format.  set default verbosity level = errors only.
#


logger_handler = logging.StreamHandler()
logger.addHandler(logger_handler)

def set_verbose(enabled, application = "ligolw"):
	"""
	Enable or disable verbosity throughout the ligolw library.  If
	enabled is True, the library-wide logger instance is set to log at
	INFO level, otherwise it is set to log at ERROR level.  The
	optional keyword argument application sets the name of the
	application in the logging messages (default = "ligolw").  It is
	recommended that this be set to the name of the program run by the
	user so that the origin of the messages is clear.

	Example:

	>>> set_verbose(True, application = "my_program")
	"""
	logger_handler.setFormatter(logging.Formatter("%s: %%(asctime)s: %%(message)s" % application))
	logger.setLevel(logging.INFO if enabled else logging.ERROR)

set_verbose(False)


#
# =============================================================================
#
#                         Document Header, and Indent
#
# =============================================================================
#


NameSpace = "http://ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt"


Header = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE LIGO_LW SYSTEM "%s">""" % NameSpace


Indent = "\t"


#
# =============================================================================
#
#                                Element Class
#
# =============================================================================
#


class ElementError(Exception):
	"""
	Base class for exceptions generated by elements.
	"""
	pass


class attributeproxy(property):
	"""
	Expose an XML attribute of an Element subclass as Python instance
	attribute with support for an optional default value.

	The .getAttribute() and .setAttribute() methods of the instance to
	which this is attached are used to retrieve and set the string
	attribute value, respectively.

	When retrieving a value, the function given via the dec keyword
	argument will be used to convert the string into a native Python
	object (the default is to leave the string value as a string).
	When setting a value, the function given via the enc keyword
	argument will be used to convert a native Python object to a
	string.

	When retrieving a value, if .getAttribute() raises KeyError then
	AttributeError is raised unless a default value is provided in
	which case it is returned instead.

	If doc is provided it will be used as the documentation string,
	otherwise a default documentation string will be constructed
	identifying the attribute's name and explaining the default value
	if one is set.

	NOTE:  If an XML document is parsed and an element is encountered
	that does not have a value set for an attribute whose corresponding
	attributeproxy has a default value defined, then Python codes will
	be told the default value.  Therefore, the default value given here
	must match what the XML DTD says the default value is for that
	attribute even if a different default would be more convenient.
	Likewise, attributes for which the DTD does not define a default
	must not have a default defined here, even if it would be
	convenient to do so.  These conditions must both be met to not
	create a discrepancy between the behaviour of Python codes relying
	on this I/O library and other interfaces to the same document.

	NOTE:  To improve performance the decoded value is cached, and
	reused, and the cached value is only discarded when a new value is
	assigned to the attribute or the attribute value is deleted *via
	this proxy*.  Direct manipulation of the underlying string value by
	other means will not be reflected in the cached value.  Therefore,
	do not mix direct manipulation of the string value with
	manipulation via the attributeproxy mechanism, or else the
	behaviour is undefined.  Merely retrieving the underlying string
	value with .getAttribute() is safe.  The cached value is stored in
	an instance attribute named ._XXX_cached where XXX is the
	attributeproxy's name, but this is for internal use only.

	NOTE:  Each of an XML element's attributes *must* have a
	corresponding attributeproxy instance in the class definition for
	that element.  The Element class' .validattributes() class method
	uses the set of attributeproxy instances to define the set of valid
	attributes for an Element object.

	Example:

	>>> class Test(Element):
	...	Scale = attributeproxy("Scale", enc = "%.17g".__mod__, dec = float, default = 1.0, doc = "This is the scale (default = 1).")
	...
	>>> x = Test()
	>>> # have not set value, default will be returned
	>>> x.Scale
	1.0
	>>> x.Scale = 16
	>>> x.Scale
	16.0
	>>> # default can be retrieved via the .default attribute of the
	>>> # class attribute
	>>> Test.Scale.default
	1.0
	>>> # default is read-only
	>>> Test.Scale.default = 2.
	Traceback (most recent call last):
	    ...
	AttributeError: property 'default' of 'attributeproxy' object has no setter
	>>> # internally, value is stored as a string (for XML)
	>>> x.getAttribute("Scale")
	'16'
	>>> # deleting an attribute restores the default value if defined
	>>> del x.Scale
	>>> x.Scale
	1.0
	>>> # assigning the default value to an attribute removes it from the XML
	>>> # element's tags to save on I/O
	>>> x.Scale = 16
	>>> x.getAttribute("Scale")
	'16'
	>>> x.Scale = 1
	>>> x.getAttribute("Scale")
	Traceback (most recent call last):
	    ...
	KeyError: 'Scale'
	>>> x.Scale
	1.0
	"""
	def __init__(self, name, enc = str, dec = str, default = None, doc = None):
		# define get/set/del implementations, relying on Python's
		# closure mechanism to remember values for name, default,
		# etc.
		cached = "_%s_cached" % name
		def getter(self):
			try:
				return getattr(self, cached)
			except AttributeError:
				pass
			try:
				val = self.getAttribute(name)
			except KeyError:
				if default is not None:
					setattr(self, cached, default)
					return default
				raise AttributeError("attribute '%s' is not set" % name)
			val = dec(val)
			setattr(self, cached, val)
			return val
		def setter(self, value):
			try:
				delattr(self, cached)
			except AttributeError:
				pass
			if default is not None and value == default:
				self.removeAttribute(name)
			else:
				self.setAttribute(name, enc(value))
		def deleter(self):
			try:
				delattr(self, cached)
			except AttributeError:
				pass
			self.removeAttribute(name)
		# construct a default documentation string if needed
		if doc is None:
			doc = "The \"%s\" attribute." % name
			if default is not None:
				doc += "  Default is \"%s\" if not set." % str(default)
		# initialize the property object
		super(attributeproxy, self).__init__(getter, (setter if enc is not None else None), (deleter if enc is not None else None), doc)
		# documentation is not inherited, need to set it explicitly
		self.__doc__ = doc
		# record default attribute.  if no value is supplied,
		# AttributeError will be raised on attempts to retrieve it
		if default is not None:
			self._default = default
		# NOTE:  the XML DTD standard allows attributes to be
		# flagged as #REQUIRED.  no element attributes defined in
		# the LIGO Light-Weight XML DTD are #REQUIRED so we don't
		# implement any feature to enforce that here.

	@property
	def default(self):
		"""
		Default value.  AttributeError is raised if no default
		value is set.
		"""
		return self._default


class Element(object):
	"""
	Base class for all element types.  This class is inspired by the
	class of the same name in the Python standard library's xml.dom
	package.  One important distinction is that the standard DOM
	element is used to represent the structure of a document at a much
	finer level of detail than here.  For example, in the case of the
	standard DOM element, each XML attribute is its own element being a
	child node of its tag, while here they are simply stored as
	attributes of the tag element itself.

	Despite the differences, the documentation for the xml.dom package,
	particularly that of the Element class and it's parent, the Node
	class, is useful as supplementary material in understanding how to
	use this class.
	"""
	# XML tag names are case sensitive:  compare with ==, !=, etc.
	tagName = None
	validchildren = frozenset()

	@classmethod
	def validattributes(cls):
		"""
		Return a set of the names of the attributeproxy instances
		in this Element's class definition.  These are the names of
		the attributes that may appear in the XML document.  Some
		are required, some are optional.
		"""
		return frozenset(name for name in dir(cls) if isinstance(getattr(cls, name), attributeproxy))

	def __init__(self, attrs = None):
		"""
		Construct an element.  The argument is a
		sax.xmlreader.AttributesImpl object used to set the element
		attributes.  The AttributesImpl class is a dictionary-like
		thing, but the additional features of an AttributesImpl may
		be required.  See the xml.sax documentation for more
		information.
		"""
		self.parentNode = None
		if attrs is None:
			self.attributes = AttributesImpl({})
		elif set(attrs.keys()) <= self.validattributes():
			# calling code may reuse attrs object so make a
			# copy.  NOTE:  *our* calling code, here, creates a
			# copy, itself, as part of the namespace halding
			# logic, so this is a waste of time, but just in
			# case this code gets used elsewhere it doesn't
			# hurt to do the right thing.
			self.attributes = attrs.copy()
		else:
			raise ElementError("%s element: invalid attribute(s) %s" % (self.tagName, ", ".join("'%s'" % key for key in set(attrs.keys()) - self.validattributes())))
		self.childNodes = []
		self.pcdata = None

	def start_tag(self, indent):
		"""
		Generate the string for the element's start tag.
		"""
		return "%s<%s%s>" % (indent, self.tagName, "".join(" %s=\"%s\"" % keyvalue for keyvalue in self.attributes.items()))

	def end_tag(self, indent):
		"""
		Generate the string for the element's end tag.
		"""
		return "%s</%s>" % (indent, self.tagName)

	def appendChild(self, child):
		"""
		Add a child to this element.  The child's parentNode
		attribute is updated, too.
		"""
		self.childNodes.append(child)
		child.parentNode = self
		self._verifyChildren(len(self.childNodes) - 1)
		return child

	def insertBefore(self, newchild, refchild):
		"""
		Insert a new child node before an existing child.  It must
		be the case that refchild is a child of this node;  if not,
		ValueError is raised.  newchild is returned.
		"""
		# .index() would use compare-by-value, we want
		# compare-by-id because we want to find the exact object,
		# not something equivalent to it.
		for i, childNode in enumerate(self.childNodes):
			if childNode is refchild:
				self.childNodes.insert(i, newchild)
				newchild.parentNode = self
				self._verifyChildren(i)
				return newchild
		raise ValueError(refchild)

	def removeChild(self, child):
		"""
		Remove a child from this element.  The child element is
		returned, and it's .parentNode attribute is set to None.
		If the child will not be used anymore, one should call its
		unlink() method to promote garbage collection.
		"""
		# .index() would use compare-by-value, we want
		# compare-by-id because we want to find the exact object,
		# not something equivalent to it.
		for i, childNode in enumerate(self.childNodes):
			if childNode is child:
				del self.childNodes[i]
				child.parentNode = None
				return child
		raise ValueError(child)

	def unlink(self):
		"""
		Break all parent/child element references within the
		document tree rooted on this element.  By eliminating the
		cyclic object references, garbage collection is made easier
		and the memory is more likely to be freed on a short time
		scale.  Specifically, this element's .parentNode is set to
		None, its .childNodes list is emptied, and .unlink() is
		invoked recursively on those children.
		"""
		self.parentNode = None
		while self.childNodes:
			self.childNodes.pop().unlink()

	def replaceChild(self, newchild, oldchild):
		"""
		Replace an existing node with a new node.  It must be the
		case that oldchild is a child of this node;  if not,
		ValueError is raised. newchild is returned.
		"""
		# .index() would use compare-by-value, we want
		# compare-by-id because we want to find the exact object,
		# not something equivalent to it.
		for i, childNode in enumerate(self.childNodes):
			if childNode is oldchild:
				childNode.parentNode = None
				self.childNodes[i] = newchild
				newchild.parentNode = self
				self._verifyChildren(i)
				return newchild
		raise ValueError(oldchild)

	def getElements(self, func = None):
		"""
		Perform an in-order traversal of the tree starting with
		this Element and return a list of those for which
		func(element) is True.  If func is None (the default), then
		all Elements are included in the result.

		If func() evaluates to True for the root element, so it is
		included in the list, it is guaranteed to be in the 0th
		position.  If a calling code wishes only to walk the child
		elements, it can test the 0th element's identity for a
		match with the root element and exclude it.
		"""
		return sum((elem.getElements(func) for elem in self.childNodes), ([self] if func is None or func(self) else []))

	def getElementsByTagName(self, tagName):
		return self.getElements(lambda e: e.tagName == tagName)

	def getChildrenByAttributes(self, attrs):
		"""
		Iterate over the immediate children of this Element and
		return a list of those whose attributes match attrs.  attrs
		is a dictionary-like object with a .items() method
		returning attribute/value pairs.  For each attribute, the
		child Element's value for the attribute is retrieved and
		compared to the value.  If all such comparisons show
		equality then the child Element is a match.

		NOTE:  If the child Element has additional attributes not
		included in attrs, their values are ignored.  If a child
		Element does not have a value set explicitly for a given
		attribute but that attribute has a default value which
		matches, then that is a match.
		"""
		l = []
		attrs = tuple(attrs.items())
		for c in self.childNodes:
			try:
				if all(c.getAttribute(name) == value for name, value in attrs):
					l.append(c)
			except KeyError:
				pass
		return l

	def hasAttribute(self, attrname):
		"""
		Return True if his Element has an explicit value set for an
		attribute name attrname.  Return False otherwise.  If there
		is a default value for an attribute with the given name but
		no explicit value is set the return value is False.
		"""
		return attrname in self.attributes

	def getAttribute(self, attrname):
		"""
		Return the string value of the attribute named attrname.
		This is the text that will appear in the XML document, not
		the Python value it represents.  NOTE:  If no explicit
		value is set for that attribute then KeyError is raised
		even if a default value is defined for that attribute.  To
		access the values of attributes as Python values,
		respecting their default values if they have them, access
		them via their attributeproxy instances.
		"""
		return self.attributes[attrname]

	def setAttribute(self, attrname, value):
		"""
		Set the string value of the attribute named attrname.  This
		is the text that will appear in the XML document, not the
		Python value it represents.

		NOTE:  Invoking this method breaks the internal value
		chaching mechanism of the attributeproxy instance
		corresponding to the modified attribute.  Do not use this
		method unless you know what you're doing.  Normally an
		attribute value is modified by assigning a native Python
		value to the corresponding attributeproxy instance.
		"""
		# cafeful:  this digs inside an AttributesImpl object and
		# modifies its internal data.  probably not a good idea,
		# but I don't know how else to edit an attribute because
		# the stupid things don't export a method to do it.
		self.attributes._attrs[attrname] = str(value)

	def removeAttribute(self, attrname):
		"""
		Remove an explicit value for an attribute.  This removes
		the text that would be written to the XML document, if the
		attribute has a default value defined for it then it
		is still considered to have that value.

		NOTE:  Invoking this method breaks the internal value
		caching mechanism of the attributeproxy instance
		corresponding to the modified attribute.  Do not use this
		method unless you know what you're doing.  Normally an
		attribute value is removed by performing a del operation
		on the corresponding attributeproxy instance.
		"""
		# cafeful:  this digs inside an AttributesImpl object and
		# modifies its internal data.  probably not a good idea,
		# but I don't know how else to edit an attribute because
		# the stupid things don't export a method to do it.
		try:
			del self.attributes._attrs[attrname]
		except KeyError:
			pass

	def appendData(self, content):
		"""
		Append text to the Element's ,pcdata.  This is called
		repeatedly by the ContentHandler class to append blocks of
		text data to the Element during document parsing.  Usually
		subclasses for Element types with potentially large volumes
		of text content will override this to implement parsing
		rules.  The default implementation appends the content
		string to the .pcdata attribute, or assigns the value to
		.pcdata if it is None.

		NOTE:  At the time of writing, the operation of repeatedly
		appending to a Python string scales very poorly.  In the
		event that one wishes to literally do that --- not parse
		the text into Python objects but append it into one giant
		string --- it is still recommended that an override be
		provided that collects the strings in a list and joins them
		in a single operation in the .endElement() handler.  What
		is here is only appropriate for text that is expected to be
		short.
		"""
		if self.pcdata is not None:
			self.pcdata += content
		else:
			self.pcdata = content

	def _verifyChildren(self, i):
		"""
		Method used internally by some elements to verify that
		their children are from the allowed set and in the correct
		order following modifications to their child list.  i is
		the index of the child that has just changed.
		"""
		pass

	def endElement(self):
		"""
		Method invoked by document parser when it encounters the
		end-of-element event.
		"""
		pass

	def write(self, fileobj = sys.stdout, indent = ""):
		"""
		Recursively write an element and it's children to a file.
		This is a default implementation that writes the start tag,
		the child elements, the .pcdata text, and the end tag in
		that order, with some indenting.  Typically subclasses will
		override this.
		"""
		fileobj.write(self.start_tag(indent))
		fileobj.write("\n")
		for c in self.childNodes:
			if c.tagName not in self.validchildren:
				raise ElementError("invalid child %s for %s" % (c.tagName, self.tagName))
			c.write(fileobj, indent + Indent)
		if self.pcdata is not None:
			fileobj.write(xmlescape(self.pcdata))
			fileobj.write("\n")
		fileobj.write(self.end_tag(indent))
		fileobj.write("\n")


class EmptyElement(Element):
	"""
	Parent class for Elements that cannot contain text.
	"""
	def appendData(self, content):
		"""
		The content is discarded, but TypeError is raised if
		content is anything other than whitespace.
		"""
		if not content.isspace():
			raise TypeError("%s does not hold text" % type(self))


#
# =============================================================================
#
#                         Name Attribute Manipulation
#
# =============================================================================
#


class LLWNameAttr(str):
	"""
	Baseclass to hide pattern-matching of various element names.
	Subclasses must provide a .dec_pattern compiled regular expression
	defining a group "Name" that identifies the meaningful portion of
	the string, and a .enc_pattern that gives a format string to be
	used with "%" to reconstrct the full string.

	This is intended to be used to provide the enc() and dec()
	functions for an attributeproxy instance.

	Example:

	>>> import re
	>>> class Test(Element):
	...	class TestName(LLWNameAttr):
	...		dec_pattern = re.compile(r"(?P<Name>[a-zA-Z0-9_]+):test\\Z")
	...		enc_pattern = "%s:test"
	...
	...	Name = attributeproxy("Name", enc = TestName.enc, dec = TestName)
	...
	>>> x = Test()
	>>> x.Name = "blah"
	>>> # internally, suffix has been appended
	>>> print(x.getAttribute("Name"))
	blah:test
	>>> # but attributeproxy reports original value
	>>> print(x.Name)
	blah
	>>> # only lower-case Latin letters, numerals, and '_' are allowed
	>>> x.Name = "Hello-world"
	Traceback (most recent call last):
	    ...
	ValueError: invalid Name 'Hello-world'
	"""

	# default = no-op(ish)
	enc_pattern = "%s"

	def __new__(cls, name):
		try:
			name = cls.dec_pattern.search(name).group("Name")
		except AttributeError:
			pass
		return name

	@classmethod
	def enc(cls, name):
		s = cls.enc_pattern % name
		# confirm invertiblity
		if cls(s) != name:
			raise ValueError("invalid Name '%s'" % name)
		return s


#
# =============================================================================
#
#                        LIGO Light Weight XML Elements
#
# =============================================================================
#


class LIGO_LW(EmptyElement):
	"""
	LIGO_LW element.
	"""
	tagName = "LIGO_LW"
	validchildren = frozenset(["LIGO_LW", "Comment", "Param", "Table", "Array", "Stream", "IGWDFrame", "AdcData", "AdcInterval", "Time", "Detector"])

	Name = attributeproxy("Name")
	Type = attributeproxy("Type")

	@classmethod
	def get_ligo_lw(cls, xmldoc, name = None, unique = True):
		"""
		Scan xmldoc for a LIGO_LW element with .Name name.  If name
		is None (default), then all LIGO_LW elements are considered
		to match.  If unique == True (the default), then ValueError
		is raised if not exactly 1 such element is found, or if
		exactly 1 such element is found then it is returned.
		Otherwise, if unique != True then the return value is a
		possibly empty sequence of matching elements.

		LIGO_LW elements are used to group collections of elements
		together into complex data structures.  For example, a
		dictionary of power spectral densities (PSDs) for a set of
		instruments is encoded as a LIGO_LW block containing
		several frequency series objects, one for each instrument,
		each of which is encoded as a LIGO_LW block containing an
		Array, a Time, an optional Comment and so on.  The process
		of decoding complex objects out of the XML tree therefore
		starts with a scan for the LIGO_LW element containing the
		object.  This class method is meant to simplify that
		operation in calling code, providing consistent error
		handling and improving code readability.
		"""
		elems = xmldoc.getElementsByTagName(cls.tagName)
		if name is not None:
			elems = [elem for elem in elems if elem.hasAttribute("Name") and elem.Name == name]
		if not unique:
			return elems
		if len(elems) != 1:
			raise ValueError("document tree at '%s' must contain exactly one '%s' element%s" % (repr(xmldoc), cls.tagName, (" named %s" % name if name is not None else "")))
		return elems[0]

	def reassign_table_row_ids(self):
		"""
		Recurses over all Table elements within this LIGO_LW elem
		whose .next_id attributes are not None, and uses the
		.get_next_id() method of each of those Tables to generate
		new IDs and assign them to the rows.  The modifications are
		recorded, and finally all ID attributes in all rows of all
		tables are updated to fix cross references to the modified
		IDs.

		This method is not normally used outside of this library.
		This method is used by the
		Document.reassign_table_row_ids() function to assign new
		IDs to rows when merging documents as part of the
		ligolw_add document merge algorithm, in order to make sure
		there are no ID collisions in the final document.

		Example:

		>>> import ligolw
		>>> xmldoc = ligolw.Document()
		>>> xmldoc.appendChild(ligolw.LIGO_LW()).appendChild(ligolw.lsctables.SnglInspiralTable.new())
		[]
		>>> xmldoc.childNodes[-1].reassign_table_row_ids()
		"""
		mapping = {}
		for tbl in self.getElementsByTagName(Table.tagName):
			if tbl.next_id is not None:
				tbl.updateKeyMapping(mapping)
		for tbl in self.getElementsByTagName(Table.tagName):
			tbl.applyKeyMapping(mapping)


class Comment(Element):
	"""
	Comment element.
	"""
	tagName = "Comment"

	def __init__(self, attrs = None, txt = None):
		"""
		Create a new Comment object.  If txt is None (the default)
		then the Comment's .pcdata (the text of the Comment) is set
		to None, otherwise txt is converted to a string and .pcdata
		is set equal to it.

		Example:

		>>> elem = Comment()
		>>> elem.write(sys.stdout)
		<Comment></Comment>
		>>> elem = Comment(txt = "hello world")
		>>> elem.write(sys.stdout)
		<Comment>hello world</Comment>
		"""
		super(Comment, self).__init__(attrs = attrs)
		if txt is not None:
			self.pcdata = str(txt)

	def write(self, fileobj = sys.stdout, indent = ""):
		fileobj.write(self.start_tag(indent))
		if self.pcdata is not None:
			fileobj.write(xmlescape(self.pcdata))
		fileobj.write(self.end_tag(""))
		fileobj.write("\n")


class Param(Element):
	"""
	Param element.  The value is stored in the pcdata attribute as the
	native Python type rather than as a string.

	NOTE:  For historical reasons Params that are string type do not
	have their text value quoted, which means it is not, in general,
	possible to indicate the start and stop of the string, for example
	if a string starts or stops with whitespace it becomes confused
	with whitespace added to the XML document for aesthetic purposes.
	This is a problem for string valued only, all other python types
	are encoded and decoded without additional complications.  When
	parsing a string-valued Param, the leading and trailing whitespace
	is stripped.  In additional to resulting in the loss of any leading
	or trailing whitespace that was intended to be part of the stored
	value, this creates an ambiguity between a null-valued Param
	(encoded as zero-length element text) and a true zero-length
	string-valued Param.  The parser interprets a zero-length string
	(prior to whitespace removal) as None.  If the string is not
	zero-length then leading and trailing whitespace is stripped and
	the result becomes the string value.  This allows None values,
	zero-length string values (stored as short purely whitespace
	strings), and string values without leading and trailing whitespace
	to be encoded losslessly.  Strings with leading and trailing
	whitespace cannot be stored, they will be mangled.  If this is a
	problem for you, please convince the collaborations to switch to
	quoted strings in Param elements ([cough] good luck).

	NOTE:  A non-standard extension is supported.  If the Type
	attribute is "yaml" then the text is interpreted as a yaml stream
	and parsed with Python's yaml interpreter into whatever object it
	becomes.  This can be used to work around the whitespace problems
	with strings, and also allow more complex objects to be encoded,
	but DO NOT ABUSE THIS FEATURE.  Do not stuff things into
	yaml-valued Param elements because you're too lazy to encode them
	properly.
	"""
	tagName = "Param"
	validchildren = frozenset(["Comment"])

	DataUnit = attributeproxy("DataUnit")
	class ParamName(LLWNameAttr):
		dec_pattern = re.compile(r"(?P<Name>[a-zA-Z0-9_]+)(:param)?\Z")
	Name = attributeproxy("Name", enc = ParamName.enc, dec = ParamName)
	Scale = attributeproxy("Scale", enc = types.FormatFunc["real_8"], dec = types.ToPyType["real_8"])
	Start = attributeproxy("Start")
	Type = attributeproxy("Type", default = "lstring")
	Unit = attributeproxy("Unit")

	def endElement(self):
		# convert .pcdata from string to native Python type
		if not self.pcdata:
			# zero-length Param --> None, regardless of Type.
			# it should already be None in this case, if there
			# was no text loaded from the XML, but we reset to
			# None just in case
			self.pcdata = None
		elif self.Type == "yaml":
			# yaml-encoded stream
			self.pcdata = yaml.load(self.pcdata)
		else:
			# strip leading and trailing whitespace then use
			# ToPyType mapping to decode the result.
			self.pcdata = types.ToPyType[self.Type](self.pcdata.strip())

	def write(self, fileobj = sys.stdout, indent = ""):
		fileobj.write(self.start_tag(indent))
		for c in self.childNodes:
			if c.tagName not in self.validchildren:
				raise ElementError("invalid child %s for %s" % (c.tagName, self.tagName))
			c.write(fileobj, indent + Indent)
		if self.pcdata is not None:
			if self.Type == "yaml":
				fileobj.write(xmlescape(yaml.dump(self.pcdata).strip()))
			else:
				# we have to strip quote characters from
				# string formats.  if the result is a
				# zero-length string it will get parsed as
				# None when the document is loaded, but on
				# this code path we know that .pcdata is
				# not None, we know it's a zero-length
				# string, so as a hack we replace
				# zero-length strings here with a bit of
				# whitespace.  whitespace is stripped from
				# strings during parsing so this will turn
				# .pcdata back into a zero-length string.
				# any other purely whitespace string will
				# be lost, converted to a zero-length
				# string when the document is loaded.
				#
				# None --> zero-length Param
				# zero-length string --> whitespace Param
				# whitespace string --> whitespace Param
				#
				# NOTE:  the degeneracy in the last two.
				# FIXME:  should a warning be emitted for
				# the last case?  Maybe an error?
				fileobj.write(xmlescape(types.FormatFunc[self.Type](self.pcdata).strip("\"") or " "))
		fileobj.write(self.end_tag("") + "\n")

	@property
	def value(self):
		"""
		Synonym of .pcdata.  Makes calling code easier to
		understand.  In the parent class .pcdata is text only.
		Here it has been translated into a native Python type, but
		it's not obvious in calling code that that is what has
		happened so it can be unclear when reading calling codes if
		one should be expecting a string or a native value.  Using
		this synonym can clarify the meaning.
		"""
		return self.pcdata

	@value.setter
	def value(self, value):
		self.pcdata = value

	@classmethod
	def build(cls, name, Type, value, start = None, scale = None, unit = None, dataunit = None, comment = None):
		"""
		Construct a LIGO Light Weight XML Param document subtree.

		name, Type and value are required.  The Param element is
		created with its .Name attribute set to name, its .Type
		attribute set to Type and its .value set to value.  The
		only check done to ensure that Type is the appropriate type
		for the data being stored is the encoding process that
		occurs when the document is written to XML.  The remaining
		arguments are optional, and are used to set the values of
		the optional attributes of the Parame element, with the
		exception of comment.  If comment is not None, it is used
		as the text for a Comment element which is added as a child
		node of the Param element.

		See also .from_pyvalue().
		"""
		# FIXME: document keyword arguments.  I have no idea how
		# most of the attributes should be encoded, I don't even
		# know what they're supposed to be.
		elem = cls()
		elem.Name = name
		elem.Type = Type
		elem.pcdata = value
		if dataunit is not None:
			elem.DataUnit = dataunit
		if scale is not None:
			elem.Scale = scale
		if start is not None:
			elem.Start = start
		if unit is not None:
			elem.Unit = unit
		if comment is not None:
			elem.appendChild(Comment(txt = comment))
		return elem

	@classmethod
	def from_pyvalue(cls, name, value, **kwargs):
		"""
		Convenience wrapper for .build() that constructs a Param
		element from an instance of a Python builtin type by
		selecting the Type from the FromPyType look-up table.  See
		.build() for a description of the valid keyword arguments.

		Examples:

		>>> import sys
		>>> # float with/without units
		>>> Param.from_pyvalue("length", 3.0, unit = "m").write(sys.stdout)
		<Param Name="length" Type="real_8" Unit="m">3</Param>
		>>> Param.from_pyvalue("example", 3.0).write(sys.stdout)
		<Param Name="example" Type="real_8">3</Param>
		>>> # string
		>>> Param.from_pyvalue("example", "test").write(sys.stdout)
		<Param Name="example">test</Param>
		>>> # short string (non-empty data = not NULL)
		>>> Param.from_pyvalue("example", "").write(sys.stdout)
		<Param Name="example"> </Param>
		>>> # None (empty data = NULL)
		>>> Param.from_pyvalue("example", None).write(sys.stdout)
		<Param Name="example" Type="None"></Param>

		Note that any type of Param may be NULL-valued.  These
		examples demonstrate the use of the automatic encoding
		helper function, which translates None into a None-typed
		Param because it doesn't know what else it might be, but,
		for example, a float-typed Param may also be set to None.
		"""
		if value is not None:
			return cls.build(name, types.FromPyType[type(value)], value, **kwargs)
		return cls.build(name, None, None, **kwargs)

	@classmethod
	def getParamsByName(cls, elem, name):
		"""
		Return a list of Param elements with Name name under elem
		using an in-order tree traversal.

		See also .get_param().
		"""
		name = cls.ParamName(name)
		return elem.getElements(lambda e: (e.tagName == cls.tagName) and (e.Name == name))

	@classmethod
	def get_param(cls, xmldoc, name = None):
		"""
		Use .getParamsByName() to search xmldoc's tree for a Param
		named name.  Raises ValueError if not exactly 1 such Param
		is found.  If name is None (default), then the .paramName
		attribute of this class is used.  The Param class does not
		provide a .paramName attribute, but sub-classes may do so.

		See also .getParamsByName().
		"""
		if name is None:
			name = cls.paramName
		elems = Param.getParamsByName(xmldoc, name)
		if len(elems) != 1:
			raise ValueError("document must contain exactly one %s Param" % cls.ParamName(name))
		return elems[0]


class Stream(Element):
	"""
	Stream element.

	See section V of LIGO-T990023 for more information about the Stream
	element.  Very little of the feature set described there is
	supported.  In particular, only the "Local" Type is supported
	(inline data).  Note that XML's ability to indicate that some
	components of the document are to be retrieved from remote sources
	and then fed into the document parsing code is a security
	vulnerability unless those sources can be trusted.

	Examples:

	>>> s = Stream(AttributesImpl({"Encoding": "base64,LittleEndian"}))
	>>> sorted(s.Encoding)
	['LittleEndian', 'base64']
	>>> s.mode
	'b64le'
	>>> s.mode = "text"
	>>> s.Encoding
	{'Text'}
	>>> s.mode = "b64le"
	>>> sorted(s.Encoding)
	['LittleEndian', 'base64']
	>>> # delimiter may only be 1 character.  space is allowed, not tab
	>>> s = Stream(AttributesImpl({"Delimiter": ","}))
	>>> s = Stream(AttributesImpl({"Delimiter": ",:"}))
	Traceback (most recent call last):
	    ...
	ligolw.ElementError: invalid Delimiter for Stream: ',:'
	>>> s = Stream(AttributesImpl({"Delimiter": " "}))
	>>> s = Stream(AttributesImpl({"Delimiter": "\t"}))	# doctest: +NORMALIZE_WHITESPACE
	Traceback (most recent call last):
	    ...
	ligolw.ElementError: invalid Delimiter for Stream: '\t'
	"""
	tagName = "Stream"

	Content = attributeproxy("Content")
	Delimiter = attributeproxy("Delimiter", default = ",")
	Encoding = attributeproxy("Encoding", enc = (lambda x: ",".join(sorted(x))), dec = (lambda s: set(map(str.strip, s.strip().split(",")) if s.strip() else ("Text",))), default = set(("Text",)))
	Name = attributeproxy("Name")
	Type = attributeproxy("Type", default = "Local")

	def __init__(self, *args):
		super(Stream, self).__init__(*args)

		#
		# validate attributes
		#

		# see LIGO-T990023 section V.B
		if self.Type not in ("Local", "Remote"):
			raise ElementError("invalid Type for Stream: '%s'" % self.Type)
		# see LIGO-T990023 section V.D
		if hasattr(self, "Content") and self.Content not in ("Typed", "Raw", "MIME"):
			raise ElementError("invalid Content for Stream: '%s'" % self.Content)
		# see LIGO-T990023 section V.E
		if not self.Encoding <= set(("Text", "Binary", "uuencode", "base64", "BigEndian", "LittleEndian", "Delimiter")):
			raise ElementError("invalid Encoding for Stream: '%s'" % self.getAttribute("Encoding"))

		#
		# now impose our own limitations
		#

		if self.Type != "Local":
			raise ElementError("Type '%s' for Stream not supported" % self.Type)
		# NOTE:  the various specifications for LIGO Light-Weight
		# XML one can find floating around imply or sometimes
		# explicitly state that delimited text Stream elements may
		# specify multiple delimiter characters.  the algorithm is:
		# combine the characters with newline and tab to comprise a
		# set, any of which will then be recognized as a field
		# separator but that a sequence of consecutive whitespace
		# delimiters, specifically, will be interpreted as a single
		# delimiter instead of a sequence of null-value fields.
		# old versions of this library worked this way, they
		# allowed multiple delimiter characters to be in use
		# simultaneously, with the special case that sequential
		# whitespace was not interpeted as multiple delimiters,
		# however it was *slow*.  a lot of conditional logic was
		# applied to every character.  it was a significant
		# performance improvement to assume that only a single
		# delimiter character is ever in use, and that a sequence
		# of consecutive delimiters is unconditionally interpreted
		# as a sequence of null fields.  all known example
		# documents were consistent with this interpretation.  for
		# example, if using "," as the delimiter the specification
		# means it would be allowed to omit the comma at the end of
		# a line and rely on the newline character to be the
		# delimiter.  however, no documents do this:  when
		# comma-delimited they all include a "," at the end of each
		# line if the next line contains more field values, meaning
		# whitespace can be ignored and the "," alone relied on to
		# delimit fields.  also, documents that use the space
		# character as the delimiter never use it for indenting of
		# lines, they always use tabs for this.  no examples were
		# found of multiple non-whitespace delimiters being used
		# simultaneously in the same Stream, nor of whitespace
		# characters other than space being used for a delimiter.
		# recognizing this, the decision was made by DASWG to limit
		# the delimiter to a single character, the only allowed
		# whitespace delimiter is the space character (tabs are
		# used everywhere for indenting), and to require exactly 1
		# delimiter between all fields.  I don't remember when, and
		# I don't remember where the decision was recorded.  this
		# project's own revision history might have that
		# information somewhere.  in any case, this is a
		# significant departure from the parsing rules one might
		# believe are being applied if some of the specification
		# documents are consulted
		if len(self.Delimiter) > 1 or (self.Delimiter.isspace() and self.Delimiter != " "):
			raise ElementError("invalid Delimiter for Stream: '%s'" % self.Delimiter)

	# look-up table mapping .Encoding to encoding scheme
	encodings = {
		frozenset(("Delimiter",)):		"text",
		frozenset(("Text",)):			"text",
		frozenset(("Text", "Delimiter")):	"text",
		frozenset(("base64", "BigEndian")):	"b64be",
		frozenset(("base64", "LittleEndian")):	"b64le",
	}

	@property
	def mode(self):
		"""
		Interprets the Type and Encoding attributes to determine
		the format of the Stream element's contents, evaluating to
		one of "text", "b64be", "b64le", to indicate that the
		Stream contains delimited text, base64 encoded big-endian
		data, or base64-encoded little-endian data, respectively.

		When base64-encoded, the assumption is that the Stream
		contains a uniformly-typed array in C element order with no
		padding.  The data type and the number of dimensions are
		obtained from elsewhere, namely the parent Array and
		sibling Dim elements.

		Raises ElementError if Type and Encoding do not indicate
		one of the three supported encodings.

		Assigning one of the three possible values sets the Type
		and Encoding attributes as necessary.  When assigning a
		value, "b64" is also recognized, in which case the native
		endianness of the machine will be used to select the
		Encoding.

		When assigning a mode, if a mode other than delimited text
		is selected then the Delimiter attribute is removed.  If,
		subsequently, the mode is set back to delimted text the
		Delimiter attribute must be set manually to restore its
		value or else the default delimiter character will be used.
		"""
		if self.Type != "Local":
			raise ElementError("only Type=\"Local\" is supported")
		try:
			return self.encodings[frozenset(self.Encoding)]
		except KeyError:
			raise ElementError("Encoding=\"%s\" not supported" % self.getAttribute("Encoding"))

	@mode.setter
	def mode(self, val):
		# set Type by removing the attribute:  default is "Local"
		del self.Type
		# set Encoding.  if the encoding isn't delimited text then
		# remove the Delimiter attribute
		if val == "text":
			# since Type is "Local" (the only value we support)
			# "Text" is the default, so this statement causes
			# Encoding to be removed from the attribute list.
			# we could just do that for simplicity, but we set
			# the value to Text to avoid a bug being introduced
			# in the future if this ever isn't taken to be the
			# default.
			self.Encoding = set(("Text",))
		elif val == "b64be" or val == "b64" and sys.byteorder == "big":
			self.Encoding = set(("base64", "BigEndian"))
			del self.Delimiter
		elif val == "b64le" or val == "b64" and sys.byteorder == "little":
			self.Encoding = set(("base64", "LittleEndian"))
			del self.Delimiter
		else:
			raise ValueError(mode)


class Table(EmptyElement, list):
	"""
	Table element that knows about its columns and a provides a
	list-like interface to its rows.

	Customization
	=============

	In some cases, applications will want to define custom sub-classes
	of the Table element tailored to their specific use case.  The
	lsctables module provides many examples.  The following is a quick
	summary of how to do this.

	When defining a sub-class, a number of class attributes can be
	defined and used to convey metadata about the custom Table to other
	code in the library.  All are optional, but in some cases failing
	to set them will defeat the purpose of creating a special
	sub-class.  For example, typically you will want to specify the
	columns and their types, and indicate which column, if there is
	one, carries the IDs for rows in this table.  The special class
	attributes are given below.

	Special Attributes
	------------------

	.tableName:  The name of the table.  This is optional, but failing
	to set it makes the sub-class indistinguishable from the stock
	Table element to most of the code in this library.

	.validcolumns:  Dictionary of column name-->type mappings defining
	the set of columns that instances of this Table may have, and what
	their types are.  When loading a document, if a column is
	encountered that is not in this dictionary or its type does not
	match what is specified an error will be reported.  Column names
	must be lower case, and obey the normal rules for C or Python
	variables:  no spaces, no hyphens, and they cannot start with a
	numeral.  The recognized types can be found in the types module.
	NOTE:  the names of columns that contain the IDs of rows in other
	tables must be named in the form "<table_name>:<column_name>",
	i.e., the other table's name, a colon, then the column in that
	other table containing that table's IDs.  For example, a column
	that contains process IDs referring to rows in the process table
	must be named "process:process_id".  Failure to ensure this will
	break the ligolw_add algorithm for reassigning IDs to prevent
	collisions.

	.loadcolumns:  Set of names of columns to be loaded, or None.  If
	not None, only columns whose names are in the set will be loaded,
	the rest will be skipped.  Can be used to reduce memory use.
	Typically a subclass will leave this set to None (inherited from
	the parent class) so that all columns in an XML file are loaded.
	The value may be modified by an application at runtime before
	loading a document.

	.constraints:  Text to be included as constraints in the SQL
	statement used to construct the Table.

	.how_to_index:  Dictionary mapping SQL index name to an iterable of
	column names over which to construct that index.

	.next_id:  The next ID to assign to a row in this Table.  IDs are
	integer-like objects that have a .column_name attribute set to the
	name of the column for which each is an ID.  Typically the
	Column.next_id metaclass is used to create a new custom class for
	this purpose, then the .next_id attribute is initialized to the 0
	instance of that new class.  NOTE:  when doing this, the
	column_name used to initialize the new class must be set to the
	name of the column that will hold the IDs.  Failing to ensure this
	will break the ligolw_add algorithm for merging documents and
	re-assigning IDs to prevent collisions.

	.RowType:  This attribute provides the class that will be used to
	store rows for this Table.  A default implementation is provided
	which will initialize attributes from keyword arguments, and
	supports pickling, but if any special handling of the data stored
	in the Table's columns is required then a custom class will be
	needed.  Typically the class defined here will be sub-classed.  The
	lsctables module provides helper code to implement a variety of
	properties, for example sets of instrument names or GPS times
	broken out into integer and nanosecond parts.

	Document Parsing
	----------------

	Once a new Table class is defined, the .TableByName class attribute
	in this class should be updated.  The .TableByName attribute is a
	dictionary mapping table names to corresponding Python classes.
	This mapping is used when parsing XML documents, when extracting
	the contents of SQL databases and any other place the conversion
	from a name to a class definition is required.  Once the mapping is
	updated, when reading XML documents, Table elements whose names
	match the custom definition will be converted to instances of that
	class.  Tables whose names are not recognized are loaded as
	instances of this generic class.

	Example:

	>>> class MyCustomTable(Table):
	...	tableName = "my_custom_table"
	...	validcolumns = {
	...		"process:process_id": "int_8s",
	...		"snr": "real_8",
	...		"event_id": "int_8s"
	...	}
	...	next_id = Column.next_id.type("event_id")(0)
	...	class RowType(Table.RowType):
	...		pass
	...
	>>> Table.TableByName[MyCustomTable.tableName] = MyCustomTable

	The .TableByName dictionary is initialized at import time to point
	to the table definitions in the lsctables module.  Tables whose
	names match those in that module are parsed into instances of those
	classes, not this class.  Users who need to work with documents
	containing one or more tables matching those names but whose
	structures are incompatible with the definitions in lsctables must
	remove those names from .TableByName to disable the format checks,
	and cause those tables to be parsed as generic Table objects.
	"""
	tagName = "Table"
	validchildren = frozenset(["Comment", "Column", "Stream"])

	class TableName(LLWNameAttr):
		dec_pattern = re.compile(r"\A(?:[a-z0-9_]+:(?!table))*(?P<Name>[a-z0-9_]+)(:table)?\Z")
		# FIXME:  remove :... when enough time has passed that
		# versions of the library for which the suffix is optional
		# are sufficiently widely deployed
		enc_pattern = "%s:table"

	Name = attributeproxy("Name", enc = TableName.enc, dec = TableName)
	Type = attributeproxy("Type")

	validcolumns = None
	loadcolumns = None
	constraints = None
	how_to_index = None
	next_id = None

	class Stream(Stream):
		"""
		Stream element for use inside Tables.  This element knows
		how to parse the character stream into row objects that it
		appends into the list-like parent element, and knows how to
		turn the parent's rows back into a character stream.  Only
		delimited text encoding is supported.

		See the parent class for more information.

		NOTE:  For tabluar data, only delimited text encoding is
		supported.
		"""
		#
		# select the RowBuilder class to use when parsing tables.
		# this is here so that in the event calling code wishes to
		# do something with parsed tokens other than populate the
		# attributes of row objects with them, it's possible to
		# provide a custom hook for taht here.  the ability to
		# override the RowBuilder is not used in this library.
		#

		RowBuilder = tokenizer.RowBuilder

		def __init__(self, *args):
			super(Table.Stream, self).__init__(*args)
			if self.mode != "text":
				raise ElementError("Table Stream must use delimited text encoding")

		def config(self, parentNode):
			# some initialization that requires access to the
			# parentNode, and so cannot be done inside the
			# __init__() function.
			loadcolumns = set(parentNode.columnnames)
			if parentNode.loadcolumns is not None:
				loadcolumns &= parentNode.loadcolumns
			self._tokenizer = tokenizer.Tokenizer(self.Delimiter)
			self._tokenizer.set_types([(pytype if colname in loadcolumns else None) for pytype, colname in zip(parentNode.columnpytypes, parentNode.columnnames)])
			self._rowbuilder = self.RowBuilder(parentNode.RowType, [name for name in parentNode.columnnames if name in loadcolumns])
			return self

		def appendData(self, content):
			# tokenize buffer, pack into row objects, and
			# append to Table
			appendfunc = self.parentNode.append
			for row in self._rowbuilder.append(self._tokenizer.append(content)):
				appendfunc(row)

		def endElement(self):
			# stream tokenizer uses delimiter to identify end
			# of each token, so add a final delimiter to induce
			# the last token to get parsed but only if there's
			# something other than whitespace left in the
			# tokenizer's buffer.  the writing code will have
			# put a final delimiter into the stream if the
			# final token was pure whitespace in order to
			# unambiguously indicate that token's presence
			if not self._tokenizer.data.isspace():
				self.appendData(self.Delimiter)
			# now we're done with these
			del self._tokenizer
			del self._rowbuilder

		def write(self, fileobj = sys.stdout, indent = ""):
			# retrieve the .write() method of the file object
			# to avoid doing the attribute lookup in loops
			w = fileobj.write
			# loop over parent's rows.  This is complicated
			# because we need to not put a delimiter at the end
			# of the last row unless it ends with a null token
			w(self.start_tag(indent))
			rowdumper = tokenizer.RowDumper(self.parentNode.columnnames, [types.FormatFunc[coltype] for coltype in self.parentNode.columntypes], self.Delimiter)
			rowdumper.dump(self.parentNode)
			try:
				line = next(rowdumper)
			except StopIteration:
				# Table is empty
				pass
			else:
				# write first row
				newline = "\n" + indent + Indent
				w(newline)
				w(xmlescape(line))
				# now add delimiter and write the remaining
				# rows
				newline = rowdumper.delimiter + newline
				for line in rowdumper:
					w(newline)
					w(xmlescape(line))
				if rowdumper.tokens and rowdumper.tokens[-1] == "":
					# the last token of the last row
					# was null: add a final delimiter
					# to indicate that a token is
					# present
					w(rowdumper.delimiter)
			w("\n" + self.end_tag(indent) + "\n")

	class RowType(object):
		"""
		Helpful parent class for row objects.  Also used as the
		default row class by Table instances.  Provides an
		.__init__() method that accepts keyword arguments from
		which the object's attributes can be initialized.

		Example:

		>>> x = Table.RowType(a = 0.0, b = "test", c = True)
		>>> x.a
		0.0
		>>> x.b
		'test'
		>>> x.c
		True

		Also provides .__getstate__() and .__setstate__() methods
		to allow row objects to be pickled (otherwise, because they
		all use __slots__ to reduce their memory footprint, they
		aren't pickleable).
		"""
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				setattr(self, key, value)

		def __getstate__(self):
			if not hasattr(self, "__slots__"):
				raise NotImplementedError
			return dict((key, getattr(self, key)) for key in self.__slots__ if hasattr(self, key))

		def __setstate__(self, state):
			self.__init__(**state)

	@property
	def columnnames(self):
		"""
		The stripped (without table prefixes attached) Name
		attributes of the Column elements in this Table, in order.
		These are the names of the attributes that row objects in
		this table possess.
		"""
		return [child.Name for child in self.getElementsByTagName(Column.tagName)]

	@property
	def columnnamesreal(self):
		"""
		The non-stripped (with table prefixes attached) Name
		attributes of the Column elements in this Table, in order.
		These are the Name attributes as they appear in the XML.
		"""
		return [child.getAttribute("Name") for child in self.getElementsByTagName(Column.tagName)]

	@property
	def columntypes(self):
		"""
		The Type attributes of the Column elements in this Table,
		in order.
		"""
		return [child.Type for child in self.getElementsByTagName(Column.tagName)]

	@property
	def columnpytypes(self):
		"""
		The Python types corresponding to the Type attributes of
		the Column elements in this Table, in order.
		"""
		return [types.ToPyType[child.Type] for child in self.getElementsByTagName(Column.tagName)]

	@classmethod
	def CheckElement(cls, elem):
		"""
		Return True if element is a Table element whose Name
		attribute matches the .tableName attribute of this class;
		return False otherwise.  See also .CheckProperties().
		"""
		return cls.CheckProperties(elem.tagName, elem.attributes)

	@classmethod
	def CheckProperties(cls, tagname, attrs):
		"""
		Return True if tagname and attrs are the XML tag name and
		element attributes, respectively, of a Table element whose
		Name attribute matches the .tableName attribute of this
		class;  return False otherwise.  The Table parent class
		does not provide a .tableName attribute, but sub-classes,
		especially those in lsctables.py, do provide a value for
		that attribute.  See also .CheckElement()

		Example:

		>>> import ligolw
		>>> ligolw.lsctables.ProcessTable.CheckProperties("Table", {"Name": "process:table"})
		True
		"""
		return tagname == cls.tagName and cls.TableName(attrs["Name"]) == cls.tableName


	#
	# Table name ---> table type mapping.  Used by .__new__()
	#


	TableByName = {}


	#
	# Constructors
	#


	def __new__(cls, attrs = None):
		"""
		Create a Table instance.  If attrs is None (the default)
		then an instance of this class is created.  If attrs is not
		None then it must be a dictionary-like object with a key
		equal to "Name" (KeyError will be raised otherwise).  If
		the corresponding value is found in the .TableByName
		mapping then an instance of that class is created,
		otherwise, again, an instance of this class is created.
		.__init__() is invoked on the result.
		"""
		if attrs is not None:
			name = Table.TableName(attrs["Name"])
			if name in cls.TableByName:
				new = super().__new__(cls.TableByName[name], attrs)
				# because new is not an instance of cls,
				# python will not automatically call
				# .__init__().  therefore we must do it
				# ourselves.
				new.__init__(attrs)
				return new
		return super().__new__(cls, attrs)


	@classmethod
	def new(cls, columns = None, **kwargs):
		"""
		Construct a pre-defined table using metadata stored as
		class attributes.  The optional columns argument is a
		sequence of the names of the columns the table is to be
		constructed with.  If columns = None (the default), then
		the table is constructed with all valid columns (use
		columns = [] to create a table with no columns).

		NOTE:  this method can only be used with subclasses that
		provide the metadata required to create the Column
		elements.

		NOTE:  this method cannot be used with documents stored in
		databases.

		Example:

		>>> import ligolw
		>>> import sys
		>>> tbl = ligolw.lsctables.ProcessTable.new(["process_id", "start_time", "end_time", "comment"])
		>>> tbl.write(sys.stdout)	# doctest: +NORMALIZE_WHITESPACE
		<Table Name="process:table">
			<Column Name="process_id" Type="int_8s"/>
			<Column Name="start_time" Type="int_4s"/>
			<Column Name="end_time" Type="int_4s"/>
			<Column Name="comment" Type="lstring"/>
			<Stream Name="process:table">
			</Stream>
		</Table>
		"""
		new = cls(AttributesImpl({"Name": cls.TableName.enc(cls.tableName)}), **kwargs)
		for name in columns if columns is not None else sorted(new.validcolumns):
			new.appendColumn(name)
		new._end_of_columns()
		new.appendChild(new.Stream(AttributesImpl({"Name": new.getAttribute("Name")})))
		return new

	def copy(self):
		"""
		Construct and return a new Table document subtree whose
		structure is the same as this Table, that is it has the
		same Columns etc..  The rows are not copied.  Note that a
		fair amount of metadata is shared between the original and
		new Tables.  In particular, a copy of the Table object
		itself is created (but with no rows), and copies of the
		child nodes are created.  All other object references are
		shared between the two instances.  In many (most?) cases
		this is consistent with the configuration that would be
		seen if both tables were constructed with .new() from the
		same class.
		"""
		new = copy.copy(self)
		new.childNodes = []	# got reference to original list
		for elem in self.childNodes:
			new.appendChild(copy.copy(elem))
		del new[:]
		new._end_of_columns()
		return new

	@classmethod
	def ensure_exists(cls, xmldoc, create_new = True, columns = None):
		"""
		A wrapper around .get_table() and .new() that adds the
		table to the element tree if one is not found.  This only
		works with subclasses that provide the required metadata.
		Raises ValueError if not exactly 1 matching table is found,
		unless 0 are found and create_new is True (the default), in
		which case a new Table element is appended to the top-level
		LIGO_LW element, and that new Table object returned.  When
		creating a new Table element, the names of the columns to
		include can be passed via the columns parameter, otherwise
		if columns is None the default columns will be created (all
		of them).
		"""
		try:
			# return existing table if present
			return cls.get_table(xmldoc)
		except ValueError:
			# not exactly 1 table found.  check that there
			# isn't more than 1, and if there are 0 check that
			# we've been asked to create a new one, otherwise
			# re-raise the exception with its original error
			# message.  note that .get_table() has already
			# walked the document tree, and we're repeating
			# that operation here, but this code path should
			# never be followed more than once for a given
			# document, so this isn't a performance-critical
			# path.
			if not create_new or len(cls.getTablesByName(xmldoc, cls.tableName)) > 1:
				raise
		return xmldoc.ensure_llw_at_toplevel().childNodes[0].appendChild(cls.new(columns = columns))


	#
	# Table retrieval
	#


	@classmethod
	def getTablesByName(cls, elem, name):
		"""
		Return a list of Table elements named name under elem.  See
		also .get_table().
		"""
		name = cls.TableName(name)
		return elem.getElements(lambda e: (e.tagName == cls.tagName) and (e.Name == name))

	@classmethod
	def get_table(cls, xmldoc, name = None):
		"""
		Scan xmldoc for a Table element named name.  Raises
		ValueError if not exactly 1 such Table is found.  If name
		is None (default), then the .tableName attribute of this
		class is used.  The Table class does not provide a
		.tableName attribute, but sub-classes, for example those in
		lsctables.py, do provide a value for that attribute.

		Example:

		>>> import ligolw
		>>> xmldoc = ligolw.Document()
		>>> xmldoc.appendChild(ligolw.LIGO_LW()).appendChild(ligolw.lsctables.SnglInspiralTable.new())
		[]
		>>> # find Table
		>>> sngl_inspiral_table = ligolw.lsctables.SnglInspiralTable.get_table(xmldoc)

		See also .getTablesByName().
		"""
		if name is None:
			name = cls.tableName
		elems = cls.getTablesByName(xmldoc, name)
		if len(elems) != 1:
			raise ValueError("document must contain exactly one %s Table" % cls.TableName(name))
		return elems[0]


	#
	# Column access
	#


	def getColumnByName(self, name):
		"""
		Retrieve and return the Column child element named name.
		The comparison is done using the stripped names.  Raises
		KeyError if this Table has no Column by that name.

		Example:

		>>> import ligolw
		>>> tbl = ligolw.lsctables.SnglInspiralTable.new()
		>>> col = tbl.getColumnByName("mass1")
		"""
		try:
			col, = Column.getColumnsByName(self, name)
		except ValueError:
			# did not find exactly 1 matching child
			raise KeyError(name)
		return col

	def appendColumn(self, name):
		"""
		Append a Column element named "name" to the Table.  Returns
		the new child.  Raises ValueError if the Table already has
		a Column by that name, and KeyError if the validcolumns
		attribute of this Table does not contain an entry for a
		Column by that name.

		Example:

		>>> import ligolw
		>>> tbl = ligolw.lsctables.ProcessParamsTable.new([])
		>>> col = tbl.appendColumn("param")
		>>> print(col.getAttribute("Name"))
		param
		>>> print(col.Name)
		param
		>>> col = tbl.appendColumn("process:process_id")
		>>> print(col.getAttribute("Name"))
		process:process_id
		>>> print(col.Name)
		process_id
		"""
		try:
			self.getColumnByName(name)
			# if we get here the Table already has that Column
			raise ValueError("duplicate Column '%s'" % name)
		except KeyError:
			pass
		if name in self.validcolumns:
			coltype = self.validcolumns[name]
		elif Column.ColumnName(name) in self.validcolumns:
			coltype = self.validcolumns[Column.ColumnName(name)]
		else:
			raise ElementError("invalid Column '%s' for Table '%s'" % (name, self.Name))
		column = Column(AttributesImpl({"Name": "%s" % name, "Type": coltype}))
		streams = self.getElementsByTagName(Stream.tagName)
		if streams:
			self.insertBefore(column, streams[0])
		else:
			self.appendChild(column)
		return column

	def compare_columns(self, other):
		"""
		Return False if the Table other has the same Columns (same
		names and types, ignoring order) according to LIGO LW name
		conventions as this Table.  Return True otherwise.

		NOTE:  type synonyms are considered to be distinct from
		each other for the purposes of this test, for example
		"real_8" are "double" Columns are considered to have
		different types.  This behaviour might change in the
		future.
		"""
		return {(col.Name, col.Type) for col in self.getElementsByTagName(Column.tagName)} != {(col.Name, col.Type) for col in other.getElementsByTagName(Column.tagName)}


	#
	# Row access
	#


	def appendRow(self, *args, **kwargs):
		"""
		Create and append a new row to this Table, then return it

		All positional and keyword arguments are passed to the RowType
		constructor for this Table.
		"""
		row = self.RowType(*args, **kwargs)
		self.append(row)
		return row


	#
	# Element methods
	#


	def _verifyChildren(self, i):
		"""
		Used for validation during parsing.  For internal use only.
		"""
		# first confirm the number and order of children
		ncomment = 0
		ncolumn = 0
		nstream = 0
		for child in self.childNodes:
			if child.tagName == Comment.tagName:
				if ncomment:
					raise ElementError("only one Comment allowed in Table")
				if ncolumn or nstream:
					raise ElementError("Comment must come before Column(s) and Stream in Table")
				ncomment += 1
			elif child.tagName == Column.tagName:
				if nstream:
					raise ElementError("Column(s) must come before Stream in Table")
				ncolumn += 1
			else:
				if nstream:
					raise ElementError("only one Stream allowed in Table")
				nstream += 1

		# check consistency rules for Column and Stream children
		child = self.childNodes[i]
		if child.tagName == Column.tagName:
			if self.validcolumns is not None:
				if child.Name in self.validcolumns:
					expected_type = self.validcolumns[child.Name]
				elif child.getAttribute("Name") in self.validcolumns:
					expected_type = self.validcolumns[child.getAttribute("Name")]
				else:
					raise ElementError("invalid Column '%s' for Table '%s'" % (child.Name, self.Name))
				if expected_type != child.Type:
					raise ElementError("invalid type '%s' for Column '%s' in Table '%s', expected type '%s'" % (child.Type, child.Name, self.Name, expected_type))
			try:
				types.ToPyType[child.Type]
			except KeyError:
				raise ElementError("unrecognized Type '%s' for Column '%s' in Table '%s'" % (child.Type, child.Name, self.Name))
			# since this is called after each child is
			# appeneded, the first failure occurs on the
			# offending child, so the error message reports the
			# current child as the offender
			# FIXME:  this is O(n^2 log n) in the number of
			# Columns.  think about a better way
			if len(set(self.columnnames)) != len(self.columnnames):
				raise ElementError("duplicate Column '%s' in Table '%s'" % (child.Name, self.Name))
		elif child.tagName == Stream.tagName:
			# require agreement of non-stripped strings
			if child.getAttribute("Name") != self.getAttribute("Name"):
				raise ElementError("Stream Name '%s' does not match Table Name '%s'" % (child.getAttribute("Name"), self.getAttribute("Name")))

	def _end_of_columns(self):
		"""
		Called during parsing to indicate that the last Column
		child element has been added.  Subclasses can override this
		to perform any special action that should occur following
		the addition of the last Column element.
		"""
		pass

	def unlink(self):
		"""
		In addition to the action of the .unlink() method of the
		parent class, this Table object is emptied of its row
		objects.
		"""
		super(Table, self).unlink()
		del self[:]

	def endElement(self):
		# Table elements are allowed to contain 0 Stream children,
		# but _end_of_columns() hook must be called regardless, so
		# we do that here if needed.
		if self.childNodes[-1].tagName != Stream.tagName:
			self._end_of_columns()


	#
	# Row ID manipulation
	#


	@classmethod
	def get_next_id(cls):
		"""
		Returns the current value of the .next_id class attribute,
		and increments the next_id class attribute by 1.  Raises
		ValueError if the Table does not have an ID generator
		associated with it.
		"""
		# = None if no ID generator
		next_id = cls.next_id
		cls.next_id += 1
		return next_id

	@classmethod
	def set_next_id(cls, next_id):
		"""
		Sets the value of the .next_id class attribute.  This is a
		convenience function to ensure the numeric ID is converted
		to the correct type and to prevent accidentally assigning a
		value to an instance attribute instead of the class
		attribute.
		"""
		cls.next_id = type(cls.next_id)(next_id)

	@classmethod
	def reset_next_id(cls):
		"""
		If the current value of the next_id class attribute is not
		None then set it to 0, otherwise it is left unmodified.

		Example:

		>>> for cls in Table.TableByName.values(): cls.reset_next_id()
		"""
		if cls.next_id is not None:
			cls.set_next_id(0)

	@classmethod
	def reset_next_ids(cls, classes = None):
		"""
		classes is an iterable of Table subclasses or None.  If
		None (the default) then the values of the TableByName
		dictionary are used.  The .reset_next_id() method is called
		on each class in the sequence, reseting the .next_id
		attributes of those classes for which it is not None to 0.
		This has the effect of reseting the ID generators, and is
		useful in applications that process multiple documents and
		add new rows to tables in those documents.  Calling this
		function between documents prevents new row IDs from
		growing continuously from document to document.  There is
		no need to do this, it's purpose is merely aesthetic, but
		it can be confusing to open a document and find process ID
		300 in the process table and wonder what happened to the
		other 299 processes.
		"""
		for cls in (cls.TableByName.values() if classes is None else classes):
			cls.reset_next_id()

	def sync_next_id(self):
		"""
		If the Table's .next_id attribute is None, then this method
		is a no-op.  Otherwise, this method determines the
		highest-numbered ID used by this Table's rows, and sets the
		Table's class' .next_id attribute to 1 + that value, or, if
		the .next_id attribute is already set to a value greater
		than that, then it is left unmodified.  The return value is
		the final value of .next_id (which may be None).

		Note that Tables of the same name typically share a common
		.next_id attribute (.next_id is a class attribute, not an
		instance attribute, and Table elements of the same name are
		typically instances of the same class).  Sharing the
		.next_id attribute means that IDs can be generated that are
		unique across all identically-named Tables in the document.
		Running .sync_next_id() on all the Tables in a document
		that are of the same type will have the effect of setting
		.next_id to a value higher than any ID used in any of those
		Tables, guaranteeing that IDs assigned after that are
		globally unique within the document.

		Example:

		>>> import ligolw
		>>> tbl = ligolw.lsctables.ProcessTable.new()
		>>> print(tbl.sync_next_id())
		0
		"""
		if self.next_id is not None:
			if len(self):
				n = max(self.getColumnByName(self.next_id.column_name)) + 1
			else:
				n = 0
			if n > self.next_id:
				self.set_next_id(n)
		return self.next_id

	def updateKeyMapping(self, mapping):
		"""
		Used as the first half of the row key reassignment
		algorithm.  Accepts a dictionary mapping old key --> new
		key.  Iterates over the rows in this Table, using the
		.next_id attribute to assign a new ID to each row,
		recording the changes in the mapping.  Returns the mapping.
		Raises ValueError if the Table's next_id attribute is None.
		"""
		if self.next_id is None:
			raise ValueError(self)
		try:
			column = self.getColumnByName(self.next_id.column_name)
		except KeyError:
			# Table is missing its ID Column, this is a no-op
			return mapping
		table_name = self.Name
		for i, old in enumerate(column):
			if old is None:
				raise ValueError("null row ID encountered in Table '%s', row %d" % (self.Name, i))
			key = table_name, old
			if key in mapping:
				column[i] = mapping[key]
			else:
				column[i] = mapping[key] = self.get_next_id()
		return mapping

	def applyKeyMapping(self, mapping):
		"""
		Used as the second half of the key reassignment algorithm.
		Loops over each row in the Table, replacing references to
		old row keys with the new values from the mapping.
		"""
		for colname in self.columnnames:
			column = self.getColumnByName(colname)
			try:
				table_name = column.table_name
			except ValueError:
				# if we get here the Column's name does not
				# have a Table name component, so by
				# convention it cannot contain IDs pointing
				# to other Tables
				continue
			# make sure it's not our own ID Column (by
			# convention this should not be possible, but it
			# doesn't hurt to check)
			if self.next_id is not None and colname == self.next_id.column_name:
				continue
			# replace IDs with new values from mapping
			for i, old in enumerate(column):
				try:
					column[i] = mapping[table_name, old]
				except KeyError:
					pass


class Column(EmptyElement):
	"""
	Column element.  Provides list-like access to the values in a
	column.

	Example:

	>>> from xml.sax.xmlreader import AttributesImpl
	>>> import sys
	>>> tbl = Table(AttributesImpl({"Name": "test"}))
	>>> col = tbl.appendChild(Column(AttributesImpl({"Name": "test:snr", "Type": "real_8"})))
	>>> tbl.appendChild(tbl.Stream(AttributesImpl({"Name": "test"})))	# doctest: +ELLIPSIS
	<ligolw.Table.Stream object at ...>
	>>> print(col.Name)
	snr
	>>> print(col.Type)
	real_8
	>>> print(col.table_name)
	test
	>>> # append 3 rows (with nothing in them)
	>>> tbl.appendRow()	# doctest: +ELLIPSIS
	<ligolw.Table.RowType object at ...>
	>>> tbl.appendRow()	# doctest: +ELLIPSIS
	<ligolw.Table.RowType object at ...>
	>>> tbl.appendRow()	# doctest: +ELLIPSIS
	<ligolw.Table.RowType object at ...>
	>>> # assign values to the rows, in order, in this column
	>>> col[:] = [8.0, 10.0, 12.0]
	>>> col[:]
	[8.0, 10.0, 12.0]
	>>> col.asarray()	# doctest: +NORMALIZE_WHITESPACE
	array([ 8., 10., 12.])
	>>> tbl.write(sys.stdout)	# doctest: +NORMALIZE_WHITESPACE
	<Table Name="test">
		<Column Name="test:snr" Type="real_8"/>
		<Stream Name="test">
			8,
			10,
			12
		</Stream>
	</Table>
	>>> col.index(10)
	1
	>>> 12 in col
	True
	>>> col[0] = 9.
	>>> col[1] = 9.
	>>> col[2] = 9.
	>>> tbl.write(sys.stdout)		# doctest: +NORMALIZE_WHITESPACE
	<Table Name="test">
		<Column Name="test:snr" Type="real_8"/>
		<Stream Name="test">
			9,
			9,
			9
		</Stream>
	</Table>
	>>> col.count(9)
	3

	NOTE:  the .Name attribute returns the stripped "Name" attribute of
	the element, e.g. with the table name prefix removed, but when
	assigning to the .Name attribute the value provided is stored
	without modification, i.e. there is no attempt to reattach the
	table's name to the string.  The calling code is responsible for
	doing the correct manipulations.  Therefore, the assignment
	operation below

	>>> print(col.Name)
	snr
	>>> print(col.getAttribute("Name"))
	test:snr
	>>> col.Name = col.Name
	>>> print(col.Name)
	snr
	>>> print(col.getAttribute("Name"))
	snr

	does not preserve the value of the "Name" attribute (though it does
	preserve the stripped form reported by the .Name property).  This
	asymmetry is necessary because the correct table name string to
	reattach to the attribute's value cannot always be known, e.g., if
	the Column object is not part of an XML tree and does not have a
	parent node.
	"""
	tagName = "Column"
	# FIXME: the pattern should be
	#
	# r"(?:\A[a-z0-9_]+:|\A)(?P<FullName>(?:[a-z0-9_]+:|\A)(?P<Name>[a-z0-9_]+))\Z"
	#
	# but people are putting upper case letters in names!!!!!  Someone
	# is going to get the beats.  There is a reason for requiring names
	# to be all lower case:  SQL table and column names are case
	# insensitive, therefore (i) when converting a document to SQL the
	# columns "Rho" and "rho" would become indistinguishable and so it
	# would be impossible to convert a document with columns having
	# names like this into an SQL database;  and (ii) even if that
	# degeneracy is not encountered the case cannot be preserved and so
	# when converting back to XML the correct capitalization is lost.
	# Requiring names to be all lower-case creates the same
	# degeneracies in XML representations that exist in SQL
	# representations ensuring compatibility and defines the correct
	# case to restore the names to when converting to XML.  Other rules
	# can be imagined that would work as well, this is the one that got
	# chosen.
	class ColumnName(LLWNameAttr):
		dec_pattern = re.compile(r"(?:\A\w+:|\A)(?P<FullName>(?:(?P<Table>\w+):|\A)(?P<Name>\w+))\Z")

		@classmethod
		def table_name(cls, name):
			"""
			When columns contain IDs that reference rows in
			other tables, the name of the table being
			referenced is prepended to the column name with a
			colon delimiter.  This function extracts that part
			of the column name.  Raises ValueError if the
			column's name does not contain a table name prefix.

			Example:

			>>> Column.ColumnName.table_name("process:process_id")
			'process'
			>>> Column.ColumnName.table_name("process_id")
			Traceback (most recent call last):
			    ...
			ValueError: table name not found in 'process_id'
			"""
			table_name = cls.dec_pattern.match(name).group("Table")
			if table_name is None:
				raise ValueError("table name not found in '%s'" % name)
			return table_name

	Name = attributeproxy("Name", enc = ColumnName.enc, dec = ColumnName)
	Type = attributeproxy("Type")
	Unit = attributeproxy("Unit")

	@property
	def table_name(self):
		return self.ColumnName.table_name(self.getAttribute("Name"))

	def start_tag(self, indent):
		"""
		Generate the string for the element's start tag.
		"""
		return "%s<%s%s/>" % (indent, self.tagName, "".join(" %s=\"%s\"" % keyvalue for keyvalue in self.attributes.items()))

	def end_tag(self, indent):
		"""
		Generate the string for the element's end tag.
		"""
		return ""

	def write(self, fileobj = sys.stdout, indent = ""):
		"""
		Recursively write an element and it's children to a file.
		"""
		fileobj.write(self.start_tag(indent))
		fileobj.write("\n")

	def __len__(self):
		"""
		The number of values in this column.
		"""
		return len(self.parentNode)

	def __getitem__(self, i):
		"""
		Retrieve the value in this column in row i.
		"""
		if isinstance(i, slice):
			return [getattr(r, self.Name) for r in self.parentNode[i]]
		else:
			return getattr(self.parentNode[i], self.Name)

	def __setitem__(self, i, value):
		"""
		Set the value in this column in row i.  i may be a slice.

		NOTE:  Unlike normal Python lists, the length of the Column
		cannot be changed as it is tied to the number of rows in
		the Table.  Therefore, if i is a slice, value should be an
		iterable with exactly the correct number of items.  No
		check is performed to ensure that this is true:  if value
		contains too many items the extras will be ignored, and if
		value contains too few items only as many rows will be
		updated as there are items.
		"""
		if isinstance(i, slice):
			for r, val in zip(self.parentNode[i], value):
				setattr(r, self.Name, val)
		else:
			setattr(self.parentNode[i], self.Name, value)

	def __delitem__(self, *args):
		raise NotImplementedError

	def __iter__(self):
		"""
		Return an iterator object for iterating over values in this
		column.
		"""
		for row in self.parentNode:
			yield getattr(row, self.Name)

	def count(self, value):
		"""
		Return the number of rows with this column equal to value.
		"""
		return sum(x == value for x in self)

	def index(self, value):
		"""
		Return the smallest index of the row(s) with this column
		equal to value.
		"""
		for i, x in enumerate(self):
			if x == value:
				return i
		raise ValueError(value)

	def __contains__(self, value):
		"""
		Returns True or False if there is or is not, respectively,
		a row containing val in this column.
		"""
		return value in iter(self)

	def asarray(self):
		"""
		Construct a numpy array from this column.  Note that this
		creates a copy of the data, so modifications made to the
		array will *not* be recorded in the original document.
		"""
		try:
			dtype = types.ToNumPyType[self.Type]
		except KeyError as e:
			raise TypeError("cannot determine numpy dtype for Column '%s': %s" % (self.getAttribute("Name"), e))
		return numpy.fromiter(self, dtype = dtype)

	@classmethod
	def getColumnsByName(cls, elem, name):
		"""
		Return a list of Column elements named name under elem.
		"""
		name = cls.ColumnName(name)
		return elem.getElements(lambda e: (e.tagName == cls.tagName) and (e.Name == name))

	class next_id(int):
		"""
		Type for .next_id attributes of tables with int_8s ID
		columns.  This class is not normally instantiated, itself,
		instead the .type() class method is used to create a new,
		custom, class derived from this class, which is then
		instantiated to create an ID object.
		"""
		column_name = None

		def __add__(self, other):
			"""
			Override .__add__() to ensure that incrementing an
			ID yields a new object of the same type (and so
			that carries the correct .column_name class
			attribute).

			NOTE:  no other arithmetic operations are
			customized, and they will return standard Python
			types.

			Example:

			>>> x = Column.next_id.type("event_id")(0)
			>>> x
			0
			>>> x.column_name
			'event_id'
			>>> y = x + 1
			>>> y
			1
			>>> y.column_name
			'event_id'
			"""
			return type(self)(super(Column.next_id, self).__add__(other))

		@classmethod
		def type(cls, column_name):
			"""
			Create a new sub-class derived from this class and
			whose .column_name class attribute is set to
			column_name.

			Example:

			>>> MyCustomID = Column.next_id.type("event_id")
			>>> MyCustomID.column_name
			'event_id'
			>>> x = MyCustomID(0)
			>>> x
			0
			>>> x.column_name
			'event_id'
			>>> y = x + 1
			>>> y
			1
			>>> y.column_name
			'event_id'
			>>> z = y - x
			>>> z
			1
			>>> z.column_name
			Traceback (most recent call last):
			    ...
			AttributeError: 'int' object has no attribute 'column_name'
			"""
			return type(str("next_%s" % column_name), (cls,), {"column_name": column_name})


class Array(EmptyElement):
	"""
	Array element.  During parsing, the character data contained within
	the Stream element is parsed into a numpy array object.  The array
	has the dimensions and type described by the Array and Dim element
	metadata.  When the document is written, the Stream element
	serializes the numpy array back into character data.  The array is
	stored as an attribute of the Array element.

	Examples:

	>>> import numpy
	>>> x = numpy.mgrid[0:5,0:3][0]
	>>> x
	array([[0, 0, 0],
	       [1, 1, 1],
	       [2, 2, 2],
	       [3, 3, 3],
	       [4, 4, 4]])
	>>> x.shape
	(5, 3)
	>>> elem = Array.build("test", x, ["dim0", "dim1"])
	>>> elem.shape
	(5, 3)
	>>> import sys
	>>> elem.write(sys.stdout)	# doctest: +NORMALIZE_WHITESPACE
	<Array Type="int_8s" Name="test:array">
		<Dim Name="dim1">3</Dim>
		<Dim Name="dim0">5</Dim>
		<Stream Delimiter=" ">
			0 1 2 3 4
			0 1 2 3 4
			0 1 2 3 4
		</Stream>
	</Array>
	>>> # change the Array shape.  the internal array is changed, too
	>>> elem.shape = 15
	>>> elem.write(sys.stdout)	# doctest: +NORMALIZE_WHITESPACE
	<Array Type="int_8s" Name="test:array">
		<Dim Name="dim0">15</Dim>
		<Stream Delimiter=" ">
			0 0 0 1 1 1 2 2 2 3 3 3 4 4 4
		</Stream>
	</Array>
	>>> # replace the internal array with one with a different number
	>>> # of dimensions.  assign to .array first, then fix .shape
	>>> elem.array = numpy.mgrid[0:4,0:3,0:2][0]
	>>> elem.shape = elem.array.shape
	>>> elem.write(sys.stdout)	# doctest: +NORMALIZE_WHITESPACE
	<Array Type="int_8s" Name="test:array">
		<Dim>2</Dim>
		<Dim>3</Dim>
		<Dim Name="dim0">4</Dim>
		<Stream Delimiter=" ">
			0 1 2 3
			0 1 2 3
			0 1 2 3
			0 1 2 3
			0 1 2 3
			0 1 2 3
		</Stream>
	</Array>
	"""
	tagName = "Array"
	validchildren = frozenset(["Dim", "Stream"])

	class ArrayName(LLWNameAttr):
		dec_pattern = re.compile(r"(?P<Name>[a-zA-Z0-9_]+)(:array)?\Z")
		# FIXME:  remove :... when enough time has passed that
		# versions of the library for which the suffix is optional
		# are sufficiently widely deployed
		enc_pattern = "%s:array"

	Name = attributeproxy("Name", enc = ArrayName.enc, dec = ArrayName)
	Type = attributeproxy("Type")
	Unit = attributeproxy("Unit")

	class Stream(Stream):
		"""
		Stream element for use inside Arrays.  This element knows
		how to parse the character stream into the parent's array
		attribute, and knows how to turn the parent's array
		attribute back into a character stream.  Delimited text
		streams as well as base64 encoded, little-endian and
		big-endian, packed, C-order, arrays are supported.
		"""

		def __init__(self, *args):
			super(Array.Stream, self).__init__(*args)
			if self.mode == "text":
				self._tokenizer = tokenizer.Tokenizer(self.Delimiter)
				self.appendData = self._text_appendData
			elif self.mode in ("b64be", "b64le"):
				self._buffs = []
				self.appendData = self._b64_appendData
			else:
				# impossible to get here
				raise RuntimeError()

		def config(self, parentNode):
			# some initialization that can only be done once
			# parentNode has been set.
			parentNode.array = numpy.zeros(parentNode.shape, types.ToNumPyType[parentNode.Type])
			if self.mode == "text":
				self._array_view = parentNode.array.T.flat
				self._tokenizer.set_types([types.ToPyType[parentNode.Type]])
			else:
				self._array_view = parentNode.array.flat
			self._index = 0
			return self

		def _b64_appendData(self, content):
			self._buffs.append(content)

		def _text_appendData(self, content):
			# tokenize buffer, and assign to array
			tokens = tuple(self._tokenizer.append(content))
			next_index = self._index + len(tokens)
			self._array_view[self._index : next_index] = tokens
			self._index = next_index

		def endElement(self):
			if self.mode == "text":
				# stream tokenizer uses delimiter to
				# identify end of each token, so add a
				# final delimiter to induce the last token
				# to get parsed.
				self.appendData(self.Delimiter)
				if self._index != len(self._array_view):
					raise ValueError("length of Stream (%d elements) does not match array size (%d elements)" % (self._index, len(self._array_view)))
				# now we're done with these
				del self._tokenizer
				del self._index
			elif self.mode in ("b64be", "b64le"):
				self._array_view[:] = numpy.frombuffer(base64.b64decode("".join(self._buffs)), dtype = self.parentNode.array.dtype.newbyteorder("<" if self.mode == "b64le" else ">"))
				# now we're done with these
				del self._buffs
			else:
				# impossible to get here
				raise RuntimeError()
			# now we're done with these
			del self._array_view

		def write(self, fileobj = sys.stdout, indent = ""):
			# avoid symbol and attribute look-ups in inner loop
			w = fileobj.write
			w(self.start_tag(indent))

			array = self.parentNode.array
			if array is None or not array.size:
				pass
			elif self.mode == "text":
				# avoid symbol and attribute look-ups in
				# inner loop.  we use self.parentNode.shape
				# to retrieve the array's shape, rather
				# than just asking the array, to induce a
				# sanity check that the Dim elements are
				# correct for the array
				linelen = self.parentNode.shape[0]
				lines = array.size // linelen
				tokens = iter(map(types.FormatFunc[self.parentNode.Type], array.T.flat))
				islice = itertools.islice
				join = self.Delimiter.join

				newline = "\n" + indent + Indent
				w(newline)
				w(xmlescape(join(islice(tokens, linelen))))
				newline = self.Delimiter + newline
				for i in range(lines - 1):
					w(newline)
					w(xmlescape(join(islice(tokens, linelen))))
			elif self.mode == "b64be":
				if not array.flags.carray:
					raise ValueError("base64 encoded arrays must be aligned contiguous C order arrays")
				w("\n")
				if sys.byteorder == "little":
					array = array.byteswap()
				w(base64.b64encode(array.tobytes()).decode("ascii"))
			elif self.mode == "b64le":
				if not array.flags.carray:
					raise ValueError("base64 encoded arrays must be aligned contiguous C order arrays")
				w("\n")
				if sys.byteorder == "big":
					array = array.byteswap()
				w(base64.b64encode(array.tobytes()).decode("ascii"))
			else:
				# impossible to get here
				raise RuntimeError()
			w("\n" + self.end_tag(indent) + "\n")

	def __init__(self, *args):
		"""
		Initialize a new Array element.
		"""
		super(Array, self).__init__(*args)
		self.array = None

	@property
	def shape(self):
		"""
		The Array's dimensions.  If the shape described by the Dim
		child elements is not consistent with the shape of the
		internal array object then ValueError is raised.

		When assigning to this property, the internal array object
		is adjusted as well, and an error will be raised if the
		re-shape is not allowed (see numpy documentation for the
		rules).  If the number of dimensions is being changed, and
		the Array object requires additional Dim child elements to
		be added, they are created with higher ranks than the
		existing dimensions, with no Name attributes assigned;
		likewise if Dim elements need to be removed, the highest
		rank dimensions are removed first.  NOTE: Dim elements are
		stored in reverse order, so the highest rank dimension
		corresponds to the first Dim element in the XML tree.

		NOTE:  the shape of the internal numpy array and the shape
		described by the Dim child elements are only weakly related
		to one another.  There are some sanity checks watching out
		for inconsistencies, for example when retrieving the value
		of this property, or when writing the XML tree to a file,
		but in general there is no mechanism preventing
		sufficiently quirky code from getting the .array attribute
		out of sync with the Dim child elements.  Calling code
		should ensure it contains its own safety checks where
		needed.
		"""
		shape = tuple(c.n for c in self.getElementsByTagName(Dim.tagName))[::-1]
		if self.array is not None and self.array.shape != shape:
			raise ValueError("shape of Dim children not consistent with shape of .array:  %s != %s" % (str(shape), str(self.array.shape)))
		return shape

	@shape.setter
	def shape(self, shape):
		# adjust the internal array.  this has the side effect of
		# testing that the new shape is permitted
		if self.array is not None:
			self.array.shape = shape

		# make sure we have the correct number of Dim elements.
		# Dim elements are in the reverse order relative to the
		# entries in shape, so we remove extra ones or add extra
		# ones at the start of the list to preseve the metadata of
		# the lower-indexed dimensions
		dims = self.getElementsByTagName(Dim.tagName)
		try:
			len(shape)
		except TypeError:
			shape = (shape,)
		while len(dims) > len(shape):
			self.removeChild(dims.pop(0)).unlink()
		while len(dims) < len(shape):
			if dims:
				# prepend new Dim elements
				dim = self.insertBefore(Dim(), dims[0])
			elif self.childNodes:
				# there are no Dim children, only other
				# allowed child is a single Stream, and
				# Dim children must come before it
				assert len(self.childNodes) == 1 and self.childNodes[-1].tagName == Stream.tagName, "invalid children"
				dim = self.insertBefore(Dim(), self.childNodes[-1])
			else:
				dim = self.appendChild(Dim())
			dims.insert(0, dim)

		# set the dimension sizes of the Dim elements
		for dim, n in zip(dims, reversed(shape)):
			dim.n = n

	@classmethod
	def build(cls, name, array, dim_names = None, mode = None):
		"""
		Construct a LIGO Light Weight XML Array document subtree
		from a numpy array object.

		Example:

		>>> import numpy, sys
		>>> a = numpy.arange(12, dtype = "double")
		>>> a.shape = (4, 3)
		>>> Array.build("test", a).write(sys.stdout)	# doctest: +NORMALIZE_WHITESPACE
		<Array Type="real_8" Name="test:array">
			<Dim>3</Dim>
			<Dim>4</Dim>
			<Stream Delimiter=" ">
				0 3 6 9
				1 4 7 10
				2 5 8 11
			</Stream>
		</Array>
		"""
		# Type must be set for .__init__();  easier to set Name
		# afterwards to take advantage of encoding handled by
		# attribute proxy
		self = cls(AttributesImpl({"Type": types.FromNumPyType[str(array.dtype)]}))
		self.array = array
		self.Name = name
		self.shape = array.shape
		if dim_names is not None:
			if len(dim_names) != len(array.shape):
				raise ValueError("dim_names must be same length as number of dimensions")
			for child, name in zip(self.getElementsByTagName(Dim.tagName), reversed(dim_names)):
				child.Name = name
		stream = self.appendChild(self.Stream(AttributesImpl({"Delimiter": " "})))
		# set the Stream encoding if something other than the
		# default is desired.
		if mode is not None:
			stream.mode = mode
		# done
		return self

	@classmethod
	def getArraysByName(cls, elem, name):
		"""
		Return a list of arrays with name name under elem.

		See also .get_array().
		"""
		name = cls.ArrayName(name)
		return elem.getElements(lambda e: (e.tagName == cls.tagName) and (e.Name == name))

	@classmethod
	def get_array(cls, xmldoc, name = None):
		"""
		Scan xmldoc for an array named name.  Raises ValueError if
		not exactly 1 such array is found.  If name is None
		(default), then the .arrayName attribute of this class is
		used.  The Array class does not provide a .arrayName
		attribute, but sub-classes could choose to do so.

		See also .getArraysByName().
		"""
		if name is None:
			name = cls.arrayName
		elems = cls.getArraysByName(xmldoc, name)
		if len(elems) != 1:
			raise ValueError("document must contain exactly one %s array" % cls.ArrayName(name))
		return elems[0]

	#
	# Element methods
	#

	def _verifyChildren(self, i):
		nstream = 0
		for child in self.childNodes:
			if child.tagName == Dim.tagName:
				if nstream:
					raise ElementError("Dim(s) must come before Stream in Array")
			else:
				if nstream:
					raise ElementError("only one Stream allowed in Array")
				nstream += 1

	def unlink(self):
		"""
		Break internal references within the document tree rooted
		on this element to promote garbage collection.
		"""
		super(Array, self).unlink()
		self.array = None


class Dim(Element):
	"""
	Dim element.
	"""
	tagName = "Dim"

	Name = attributeproxy("Name")
	Scale = attributeproxy("Scale", enc = types.FormatFunc["real_8"], dec = types.ToPyType["real_8"])
	Start = attributeproxy("Start", enc = types.FormatFunc["real_8"], dec = types.ToPyType["real_8"])
	Unit = attributeproxy("Unit")

	@property
	def n(self):
		return types.ToPyType["int_8s"](self.pcdata) if self.pcdata is not None else None

	@n.setter
	def n(self, val):
		self.pcdata = types.FormatFunc["int_8s"](val) if val is not None else None

	@n.deleter
	def n(self):
		self.pcdata = None

	def write(self, fileobj = sys.stdout, indent = ""):
		fileobj.write(self.start_tag(indent))
		if self.pcdata is not None:
			fileobj.write(xmlescape(self.pcdata))
		fileobj.write(self.end_tag(""))
		fileobj.write("\n")


class IGWDFrame(EmptyElement):
	"""
	IGWDFrame element.
	"""
	tagName = "IGWDFrame"
	validchildren = frozenset(["Comment", "Param", "Time", "Detector", "AdcData", "LIGO_LW", "Stream", "Array", "IGWDFrame"])

	Name = attributeproxy("Name")


class Detector(EmptyElement):
	"""
	Detector element.
	"""
	tagName = "Detector"
	validchildren = frozenset(["Comment", "Param", "LIGO_LW"])

	Name = attributeproxy("Name")


class AdcData(EmptyElement):
	"""
	AdcData element.
	"""
	tagName = "AdcData"
	validchildren = frozenset(["AdcData", "Comment", "Param", "Time", "LIGO_LW", "Array"])

	Name = attributeproxy("Name")


class AdcInterval(EmptyElement):
	"""
	AdcInterval element.
	"""
	tagName = "AdcInterval"
	validchildren = frozenset(["AdcData", "Comment", "Time"])

	DeltaT = attributeproxy("DeltaT", enc = types.FormatFunc["real_8"], dec = types.ToPyType["real_8"])
	Name = attributeproxy("Name")
	StartTime = attributeproxy("StartTime")


class Time(Element):
	"""
	Time element.  The .pcdata attribute contains the time value as its native Python type.  The value is converted to and and from text by the writing and reading code using routines specific to each format.

	For writing:

	Type="ISO-8601":
		.pcdata must have a .isoformat() method whose return value
		can be cast to a string with str().
	Type="GPS":
		.pcdata must convert itself to a string with str().
	Type="Unix":
		.pcdata must be a floating point number or other object
		that can be printed using the %g format.
	all others:
		.pcdata must convert itself to a string with str().

	For reading:

	Type="ISO-8601":
		.pcdata set to result of applying dateutil.parser.parse()
		to the text.
	Type="GPS":
		.pcdata set to result of applying lal.LIGOTimeGPS() to the
		text, meaning the XML document contains the count of atomic
		seconds since the GPS epoch, stated to nanosecond
		precision, and .pcdata will be a lal.LIGOTimeGPS object
		representing that time.  NOTE:  this is not compatible with
		LIGO-T000067 which states that a GPS time is represented by
		the integer count of nanoseconds since the GPS epoch.
	Type="Unix":
		.pcdata set to the result of applying float() to the text.
	all others:
		.pcdata set to the text contained in the XML.
	"""
	tagName = "Time"

	Name = attributeproxy("Name")
	Type = attributeproxy("Type", default = "ISO-8601")

	def __init__(self, *args):
		super(Time, self).__init__(*args)
		if self.Type not in types.TimeTypes:
			raise ElementError("invalid Type for Time: '%s'" % self.Type)

	def endElement(self):
		if self.Type == "ISO-8601":
			self.pcdata = dateutil.parser.parse(self.pcdata)
		elif self.Type == "GPS":
			from lal import LIGOTimeGPS
			self.pcdata = LIGOTimeGPS(self.pcdata)
		elif self.Type == "Unix":
			self.pcdata = float(self.pcdata)
		else:
			# unsupported time type.  not impossible that
			# calling code has overridden TimeTypes set in
			# ligolw.types;  just accept it as a string
			pass

	def write(self, fileobj = sys.stdout, indent = ""):
		fileobj.write(self.start_tag(indent))
		if self.pcdata is not None:
			if self.Type == "ISO-8601":
				fileobj.write(xmlescape(str(self.pcdata.isoformat())))
			elif self.Type == "GPS":
				fileobj.write(xmlescape(str(self.pcdata)))
			elif self.Type == "Unix":
				fileobj.write(xmlescape("%.16g" % self.pcdata))
			else:
				# unsupported time type.  not impossible.
				# assume correct thing to do is cast to
				# string and let calling code figure out
				# how to ensure that does the correct
				# thing.
				fileobj.write(xmlescape(str(self.pcdata)))
		fileobj.write(self.end_tag(""))
		fileobj.write("\n")

	@classmethod
	def now(cls, Name = None):
		"""
		Instantiate a Time element initialized to the current UTC
		time in the default format (ISO-8601).  The Name attribute
		will be set to the value of the Name parameter if given.
		"""
		self = cls()
		if Name is not None:
			self.Name = Name
		self.pcdata = datetime.datetime.utcnow()
		return self

	@classmethod
	def from_gps(cls, gps, Name = None):
		"""
		Instantiate a Time element initialized to the value of the
		given GPS time.  The Name attribute will be set to the
		value of the Name parameter if given.

		Note:  the new Time element holds a reference to the GPS
		time, not a copy of it.  Subsequent modification of the GPS
		time object will be reflected in what gets written to disk.
		"""
		self = cls(AttributesImpl({"Type": "GPS"}))
		if Name is not None:
			self.Name = Name
		self.pcdata = gps
		return self


class Document(EmptyElement):
	"""
	Description of a LIGO LW file.
	"""
	tagName = "Document"
	validchildren = frozenset(["LIGO_LW"])

	def ensure_llw_at_toplevel(self, fix = False):
		"""
		Make sure the 0th top-level element is a LIGO_LW element.
		Used in a variety of places for sanity checking document
		structure before starting other operations.  If the 0th
		top-level element is not a LIGO_LW element, then if fix is
		False (the default) ValueError is raised, otherwise a new
		LIGO_LW element is inserted at position 0.  Returns self on
		success.

		NOTE:  the outermost LIGO_LW element groups the LIGO
		Light-Weight XML data together into a single XML element,
		making it more straight-forward to combine it with other
		data from different namespaces within the same document.
		Other than this the top-level LIGO_LW element plays no role
		in the document structure, but it has lazily become common
		practice for decoding algorithms to look for it at position
		0 in the top-level elements of the document, and then
		search within it for the data they seek.  Many programs
		will break if that's not where it is.

		With that in mind, be aware that setting fix=True does not
		cause a document that was broken to now be fixed.  It is
		permitted for the LIGO Light-Weight document contents to be
		found grouped in a LIGO_LW element elsewhere in the tree,
		and placing a second outermost LIGO_LW element somewhere
		else in the document is likely to create confusion in
		decoders, creating a broken document from one that was
		valid.
		"""
		if not self.childNodes:
			if not fix:
				raise ValueError("empty document (must have %s element at top level)" % LIGO_LW.tagName)
			self.childNodes.appendChild(LIGO_LW())

		elem = self.childNodes[0]

		if elem.tagName != LIGO_LW.tagName:
			if not fix:
				raise ValueError("expected %s element in position 0 at top level of document, found %s" % (LIGO_LW.tagName, elem.tagName))
			elem = self.insertBefore(LIGO_LW(), elem)

		return self

	def register_process(self, program, paramdict, **kwargs):
		"""
		Ensure the document has sensible process and process_params
		tables, synchronize the process table's ID generator, add a
		new row to the table for the current process, and add rows
		to the process_params table describing the options in
		paramdict.  program is the name of the program.  paramdict
		is expected to be the .__dict__ contents of an
		optparse.OptionParser options object, or the equivalent.
		Any keyword arguments are passed to
		lsctables.Process.initialized(), see that method for more
		information.  The new process row object is returned.

		The document tree must have a LIGO_LW element at the top
		level.  ValueError is raised if this condition is not met.

		Example

		>>> xmldoc = Document()
		>>> xmldoc.appendChild(LIGO_LW())	# doctest: +ELLIPSIS
		<ligolw.LIGO_LW object at ...>
		>>> process = xmldoc.register_process("program_name", {"verbose": True})
		"""
		# retrieve the process table and process_params table, or
		# add them if missing
		proctable = lsctables.ProcessTable.ensure_exists(self)
		paramtable = lsctables.ProcessParamsTable.ensure_exists(self)

		# add an entry to the process table
		proctable.sync_next_id()
		process = proctable.RowType.initialized(program = program, process_id = proctable.get_next_id(), **kwargs)
		proctable.append(process)

		# add entries to the process_params table
		for name, values in paramdict.items():
			# change the name back to the form it had on the command
			# line
			name = "--%s" % name.replace("_", "-")

			# skip options that aren't set;  ensure values is something
			# that can be iterated over even if there is only one value
			if values is None:
				continue
			elif values is True or values is False:
				# boolen options have no value recorded
				values = [None]
			elif not isinstance(values, list):
				values = [values]

			for value in values:
				paramtable.appendRow(
					program = process.program,
					process_id = process.process_id,
					param = name,
					pyvalue = value
				)
		return process

	def includes_process(self, program):
		"""
		Return True if the process table includes one or more
		entries for a program named program.
		"""
		return program in lsctables.ProcessTable.get_table(self).getColumnByName("program")

	def get_process_params(self, program, param, require_unique_program = True):
		"""
		Return a list of the values stored in the process_params
		table for params named param for the program(s) named
		program.  The values are returned as Python native types,
		not as the strings appearing in the XML document.  There
		must be at least one program with the requested name, or
		else ValueError is raised.  If require_unique_program is
		True (default), then the document must contain exactly one
		program with the requested name or ValueError is raised.
		If require_unique_program is not True then the return value
		contains all matching parameter values for all matching
		programs.
		"""
		process_ids = lsctables.ProcessTable.get_table(self).get_ids_by_program(program)
		if len(process_ids) < 1:
			raise ValueError("process table must contain at least one program named '%s'" % program)
		elif require_unique_program and len(process_ids) != 1:
			raise ValueError("process table must contain exactly one program named '%s'" % program)
		return [row.pyvalue for row in lsctables.ProcessParamsTable.get_table(self) if (row.process_id in process_ids) and (row.param == param)]

	def append_search_summary(self, process, **kwargs):
		"""
		Append search summary information associated with the given
		process to the search summary table in self.  Returns the
		newly-created search_summary table row.  Any keyword
		arguments are passed to the .initialized() method of the
		SearchSummary row type.
		"""
		tbl = lsctables.SearchSummaryTable.ensure_exists(self)
		row = tbl.RowType.initialized(process, **kwargs)
		tbl.append(row)
		return row

	def segmentlistdict_fromsearchsummary_in(self, program = None):
		"""
		Convenience wrapper for a common case usage of the
		segmentlistdict class:  searches the process table in self
		for occurances of a program named program, then scans the
		search summary table for matching process IDs and
		constructs a segmentlistdict object from the in segments in
		those rows.

		Note:  the segmentlists in the segmentlistdict are not
		necessarily coalesced, they contain the segments as they
		appear in the search_summary table.
		"""
		return lsctables.SearchSummaryTable.get_table(self).get_in_segmentlistdict(program and lsctables.ProcessTable.get_table(self).get_ids_by_program(program))

	def segmentlistdict_fromsearchsummary_out(self, program = None):
		"""
		Convenience wrapper for a common case usage of the
		segmentlistdict class:  searches the process table in self
		for occurances of a program named program, then scans the
		search summary table for matching process IDs and
		constructs a segmentlistdict object from the out segments
		in those rows.

		Note:  the segmentlists in the segmentlistdict are not
		necessarily coalesced, they contain the segments as they
		appear in the search_summary table.
		"""
		return lsctables.SearchSummaryTable.get_table(self).get_out_segmentlistdict(program and lsctables.ProcessTable.get_table(self).get_ids_by_program(program))

	def get_time_slide_id(self, offsetvector, create_new = None, superset_ok = False, nonunique_ok = False):
		"""
		Return the time_slide_id corresponding to the offset vector
		described by time_slide, a dictionary of instrument/offset
		pairs.

		Example:

		>>> xmldoc.get_time_slide_id({"H1": 0, "L1": 0})	# doctest: +SKIP
		10

		This function is a wrapper around the .get_time_slide_id()
		method of the ligolw.lsctables.TimeSlideTable class.  See
		the documentation for that class for the meaning of the
		create_new, superset_ok and nonunique_ok keyword arguments.

		This function requires the document to contain exactly one
		time_slide table.  If the document does not contain exactly
		one time_slide table then ValueError is raised, unless the
		optional create_new argument is not None.  In that case a
		new table is created.  This effect of the create_new
		argument is in addition to the effects described by the
		TimeSlideTable class.
		"""
		tbl = lsctables.TimeSlideTable.ensure_exists(self, create_new = create_new)
		tbl.sync_next_id()
		return tbl.get_time_slide_id(offsetvector, create_new = create_new, superset_ok = superset_ok, nonunique_ok = nonunique_ok)

	def get_coinc_def_id(self, search, search_coinc_type, create_new = True, description = ""):
		"""
		Wrapper for the get_coinc_def_id() method of the
		CoincDefiner table class in ligolw.lsctables.  This
		wrapper will optionally create a new coinc_definer table in
		the document if one does not already exist.
		"""
		tbl = lsctables.CoincDefTable.ensure_exists(self, create_new = create_new)
		tbl.sync_next_id()
		return tbl.get_coinc_def_id(search, search_coinc_type, create_new = create_new, description = description)

	def reassign_table_row_ids(self):
		"""
		Iterate over all top-level LIGO_LW elements and run
		.reassign_table_row_ids() on each of them individually.
		This has the effect of assigning new globally unique IDs to
		all rows in all LSC tables in this Document so that there
		are no collisions when the LIGO_LW elements are merged and
		when the Table elements within them are merged.

		This operation assumes that table row IDs are initially
		unique only within each top-level LIGO_LW block, and that
		there are no cross-references from the contents of one such
		block to another.  This operation uses the .get_next_id()
		methods of all Table elements in the LIGO_LW blocks to
		yield IDs suitable for usee in the final document.

		This function is used by ligolw_add to implement its
		document merge algorithm.

		NOTE:  If there are fewer than 2 top-level LIGO_LW blocks,
		this is a no-op.
		"""
		# construct a fresh old --> new mapping within each LIGO_LW
		# block.  if there are less than 2 LIGO_LW blocks, revert
		# to an identity transform (no-op).
		elems = [elem for elem in self.childNodes if elem.tagName == LIGO_LW.tagName]
		if len(elems) < 2:
			return
		for elem in tqdm(elems, desc = 'reassign row IDs', disable = logger.getEffectiveLevel() > logging.INFO):
			elem.reassign_table_row_ids()

	def write(self, fileobj = sys.stdout, xsl_file = None):
		"""
		Write the document.  The document is written to the file
		object fileobj.  If xsl_file is not None then an
		xml-stylesheet entry to the document header with the href
		attribute set equal to the value of xsl_file.
		"""
		fileobj.write(Header)
		fileobj.write("\n")
		if xsl_file is not None:
			fileobj.write('<?xml-stylesheet type="text/xsl" href="%s" ?>\n' % xsl_file)
		for c in self.childNodes:
			if c.tagName not in self.validchildren:
				raise ElementError("invalid child %s for %s" % (c.tagName, self.tagName))
			c.write(fileobj)


#
# =============================================================================
#
#                             SAX Content Handler
#
# =============================================================================
#


class ContentHandler(sax.handler.ContentHandler, object):
	"""
	ContentHandler class for parsing LIGO Light Weight documents with a
	SAX2-compliant parser.

	Example:

	>>> # initialize empty Document tree into which parsed XML tree
	>>> # will be inserted
	>>> xmldoc = Document()
	>>> # create handler instance attached to Document object
	>>> handler = ContentHandler(xmldoc)
	>>> # open file and parse
	>>> make_parser(handler).parse(open("demo.xml"))
	>>> # write XML (default to stdout)
	>>> xmldoc.write()

	NOTE:  this example is for illustration only.  Most users will wish
	to use the .load_*() functions in the ligolw.utils subpackage to
	load documents, and the .write_*() functions to write documents.
	Those functions provide additional features such as support for
	gzip'ed documents, MD5 hash computation, and HTCondor eviction
	trapping to avoid writing broken documents to disk.

	See also:  PartialContentHandler, FilteringContentHandler.
	"""

	def __init__(self, document, start_handlers = {}):
		"""
		Initialize the handler by pointing it to the Document object
		into which the parsed file will be loaded.
		"""
		self.current = self.document = document

		self._startElementHandlers = {
			(None, AdcData.tagName): self.startAdcData,
			(None, AdcInterval.tagName): self.startAdcInterval,
			(None, Array.tagName): self.startArray,
			(None, Column.tagName): self.startColumn,
			(None, Comment.tagName): self.startComment,
			(None, Detector.tagName): self.startDetector,
			(None, Dim.tagName): self.startDim,
			(None, IGWDFrame.tagName): self.startIGWDFrame,
			(None, LIGO_LW.tagName): self.startLIGO_LW,
			(None, Param.tagName): self.startParam,
			(None, Stream.tagName): self.startStream,
			(None, Table.tagName): self.startTable,
			(None, Time.tagName): self.startTime,
		}
		self._startElementHandlers.update(start_handlers)

	def startAdcData(self, parent, attrs):
		return AdcData(attrs)

	def startAdcInterval(self, parent, attrs):
		return AdcInterval(attrs)

	def startArray(self, parent, attrs):
		return Array(attrs)

	def startColumn(self, parent, attrs):
		return Column(attrs)

	def startComment(self, parent, attrs):
		return Comment(attrs)

	def startDetector(self, parent, attrs):
		return Detector(attrs)

	def startDim(self, parent, attrs):
		return Dim(attrs)

	def startIGWDFrame(self, parent, attrs):
		return IGWDFrame(attrs)

	def startLIGO_LW(self, parent, attrs):
		return LIGO_LW(attrs)

	def startParam(self, parent, attrs):
		return Param(attrs)

	def startStream(self, parent, attrs):
		if parent.tagName == Table.tagName:
			parent._end_of_columns()
			return parent.Stream(attrs).config(parent)
		elif parent.tagName == Array.tagName:
			return parent.Stream(attrs).config(parent)
		return Stream(attrs)

	def startTable(self, parent, attrs):
		return Table(attrs)

	def startTime(self, parent, attrs):
		return Time(attrs)

	def startElementNS(self, uri_localname, qname, attrs):
		try:
			start_handler = self._startElementHandlers[uri_localname]
		except KeyError:
			uri, localname = uri_localname
			raise ElementError("unknown element %s for namespace %s" % (localname, uri or NameSpace))
		attrs = AttributesImpl(dict((attrs.getQNameByName(name), value) for name, value in attrs.items()))
		try:
			self.current = self.current.appendChild(start_handler(self.current, attrs))
		except Exception as e:
			raise type(e)("line %d: %s" % (self._locator.getLineNumber(), str(e)))

	def endElementNS(self, uri_localname, qname):
		try:
			self.current.endElement()
		except Exception as e:
			raise type(e)("line %d: %s" % (self._locator.getLineNumber(), str(e)))
		self.current = self.current.parentNode

	def characters(self, content):
		try:
			# FIXME:  this unescape logic will fail if a
			# boundary between two text blocks occurs within an
			# escaped character sequence.  I don't know why
			# this hasn't been a problem for us yet, we've been
			# running this code this way for years.  maybe the
			# underlying loader watches for that and doesn't
			# chunk the text within escaped characters?  maybe
			# escaped characters are very rare in our
			# documents.
			self.current.appendData(xmlunescape(content))
		except Exception as e:
			raise type(e)("line %d: %s" % (self._locator.getLineNumber(), str(e)))


class PartialContentHandler(ContentHandler):
	"""
	LIGO LW content handler object that loads only those parts of the
	document matching some criteria.  Useful, for example, when one
	wishes to read only a single table from a file.

	Example:

	>>> import ligolw
	>>> def contenthandler(document):
	...	return PartialContentHandler(document, lambda name, attrs: name == Table.tagName)
	...
	>>> xmldoc = ligolw.utils.load_filename("demo.xml", contenthandler = contenthandler)

	This parses "demo.xml" and returns an XML tree containing only the
	Table elements and their children.
	"""
	def __init__(self, document, element_filter):
		"""
		Only those elements for which element_filter(name, attrs)
		evaluates to True, and the children of those elements, will
		be loaded.
		"""
		super(PartialContentHandler, self).__init__(document)
		self.element_filter = element_filter
		self.depth = 0

	def startElementNS(self, uri_localname, qname, attrs):
		uri, localname = uri_localname
		filter_attrs = AttributesImpl(dict((attrs.getQNameByName(name), value) for name, value in attrs.items()))
		if self.depth > 0 or self.element_filter(localname, filter_attrs):
			super(PartialContentHandler, self).startElementNS(uri_localname, qname, attrs)
			self.depth += 1

	def endElementNS(self, *args):
		if self.depth > 0:
			self.depth -= 1
			super(PartialContentHandler, self).endElementNS(*args)

	def characters(self, content):
		if self.depth > 0:
			super(PartialContentHandler, self).characters(content)


class FilteringContentHandler(ContentHandler):
	"""
	LIGO LW content handler that loads everything but those parts of a
	document that match some criteria.  Useful, for example, when one
	wishes to read everything except a single table from a file.

	Example:

	>>> import ligolw
	>>> def contenthandler(document):
	...	return FilteringContentHandler(document, lambda name, attrs: name != Table.tagName)
	...
	>>> xmldoc = ligolw.utils.load_filename("demo.xml", contenthandler = contenthandler)

	This parses "demo.xml" and returns an XML tree with all the Table
	elements and their children removed.
	"""
	def __init__(self, document, element_filter):
		"""
		Those elements for which element_filter(name, attrs)
		evaluates to False, and the children of those elements,
		will not be loaded.
		"""
		super(FilteringContentHandler, self).__init__(document)
		self.element_filter = element_filter
		self.depth = 0

	def startElementNS(self, uri_localname, qname, attrs):
		uri, localname = uri_localname
		filter_attrs = AttributesImpl(dict((attrs.getQNameByName(name), value) for name, value in attrs.items()))
		if self.depth == 0 and self.element_filter(localname, filter_attrs):
			super(FilteringContentHandler, self).startElementNS(uri_localname, qname, attrs)
		else:
			self.depth += 1

	def endElementNS(self, *args):
		if self.depth == 0:
			super(FilteringContentHandler, self).endElementNS(*args)
		else:
			self.depth -= 1

	def characters(self, content):
		if self.depth == 0:
			super(FilteringContentHandler, self).characters(content)


#
# =============================================================================
#
#                            Convenience Functions
#
# =============================================================================
#


def make_parser(handler):
	"""
	Convenience function to construct a document parser with namespaces
	enabled and validation disabled.  Document validation is a nice
	feature, but enabling validation can require the LIGO LW DTD to be
	downloaded from the LDAS document server if the DTD is not included
	inline in the XML.  This requires a working connection to the
	internet and the server to be up.
	"""
	parser = sax.make_parser()
	parser.setContentHandler(handler)
	# turn on namespace mode:  .startElementNS() and .endElementNS()
	# will be the ContentHandler methods called to start and end
	# elements, not .startElement() and .endElement()
	parser.setFeature(sax.handler.feature_namespaces, True)
	# don't validate document structure against the DTD (= bad, but for
	# practical reasons it's often necessary to disable this)
	parser.setFeature(sax.handler.feature_validation, False)
	# don't try to retrieve anything else external
	parser.setFeature(sax.handler.feature_external_ges, False)
	parser.setFeature(sax.handler.feature_external_pes, False)
	return parser


#
# =============================================================================
#
#                     Finally, Import lsctables and utils
#
# =============================================================================
#


#
# the lsctables module imports this module, and it and the utils subpackage
# references symbols defined here.  I don't know if this used to work in
# the past, but experiments show that it works now:  importing lsctables at
# the end of this module results in no cyclic references.
#


from . import lsctables
from . import utils
