# Copyright (C) 2007--2025  Kipp Cannon
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
This module provides an implementation of the Table element that uses a
database engine for storage.  On top of that it then re-implements a number
of the tables from the ligolw.lsctables module to provide versions of their
methods that work against the SQL database.

NOTE:  this is not an object-relational mapper.  This module's function is
to facilitate bi-directional format conversion between XML format files and
SQLite database files, and the merging of LIGO Light-Weight XML style
databases into single database files.  Some basic object-relational mapper
features have been implemented where it was found to be trivial to do so,
in case they come in handy, but applications that wish to interact with the
contents of an SQLite database file must, for the most part, do so using
SQL code.  To be clear, an example of what this means:  appending a row
object to an SQL-backed Table object inserts a new row into the SQL table
with the object's attributes providing the values for the columns, however
the link between the row object and the contents of the databse ends there.
If, subsequently, the attributes of that row object in the Python calling
code are modified, that has no effect on the contents of the database.
"""


import itertools
import operator
import os
import re
import shutil
import sqlite3
import sys
import tempfile


from .version import __author__, __date__, __version__
import ligolw


#
# =============================================================================
#
#                                  Connection
#
# =============================================================================
#


def connection_db_type(connection):
	"""
	A totally broken attempt to determine what type of database a
	connection object is attached to.  Don't use this.

	The input is a DB API 2.0 compliant connection object, the return
	value is one of the strings "sqlite3" or "mysql".  Raises TypeError
	when the database type cannot be determined.
	"""
	if "sqlite" in repr(connection):
		return "sqlite"
	if "mysql" in repr(connection):
		return "mysql"
	raise TypeError(connection)


#
# work with database file in scratch space
#


class workingcopy(object):
	"""
	Manage a working copy of an sqlite database file.  This is used
	when a large enough number of manipulations are being performed on
	a database file that the total network I/O would be higher than
	that of copying the entire file to a local disk, doing the
	manipulations locally, then copying the file back.  It is also
	useful in unburdening a file server when large numbers of read-only
	operations are being performed on the same file by many different
	machines.
	"""

	def __init__(self, filename, tmp_path = None, replace_file = False, discard = False):
		"""
		filename:  the name of the sqlite database file.

		tmp_path:  the directory to use for the working copy.  If
		None (the default), the system's default location for
		temporary files is used.  If set to the special value
		"_CONDOR_SCRATCH_DIR" then the value of the environment
		variable with that name will be used (to use a directory
		literally named _CONDOR_SCRATCH_DIR set tmp_path to
		"./_CONDOR_SCRATCH_DIR").

		replace_file:  if True, filename is truncated in place
		before manipulation;  if False (the default), the file is
		not modified before use.  This is used when the original
		file, if present, is meant to be replaced with a newly
		constructed file created in the local scratch space and
		copied over top of the original file when finished.
		Truncating the original file is necessary in this scenario
		to ensure that a malfunction or crash does not leave behind
		the unmodified original, as that could subsequently be
		mistaken for valid output.

		discard:  if True the working copy is simply deleted
		instead of being copied back to the original location;  if
		False (the default) the working copy overwrites the
		original.  This is used to improve read-only operations,
		when it is not necessary to pay the I/O cost of moving an
		unmodified file a second time.  The .discard attribute can
		be set at any time while the context manager is in use,
		before the .__exit__() method is invoked, so that a program
		that normally overwrites the file can choose to skip that
		operation if it decides that no modifications were made.

		NOTES:

		- When replace_file mode is enabled, failures that prevent
		  the original file from being trucated are ignored.  The
		  inability to truncate the file is considered non-fatal.
		  If, additionally, some failure later prevents the working
		  copy from being returned and over-writting the original
		  then the original is left in place.  Setting replace_file
		  to True is not a guarantee that old output from a
		  previous program is removed.

		- If the operation to copy the file to the working path
		  fails then a working copy is not used, the original file
		  is used in place.  If the failure that prevents copying
		  the file to the working path is potentially transient,
		  for example "permission denied" or "no space on device",
		  the code sleeps for a brief period of time and then tries
		  again.  Only after the potentially transient failure
		  persists for several attempts is the working copy
		  abandoned and the original copy used instead.

		- When the working copy is moved back to the original
		  location, if a file with the same name but ending in
		  -journal is present in the working directory then it is
		  deleted.

		- The name of the working copy can be obtained by
		  converting the workingcopy object to a string.
		"""
		self.filename = filename
		self.tmp_path = tmp_path if tmp_path != "_CONDOR_SCRATCH_DIR" else os.getenv("_CONDOR_SCRATCH_DIR")
		self.replace_file = replace_file
		self.discard = discard


	@staticmethod
	def truncate(filename):
		"""
		Truncate a file to 0 size, ignoring all errors.  This is
		used internally to implement the "replace_file" feature.
		"""
		ligolw.logger.info("'%s' exists, truncating ..." % filename)
		try:
			fd = os.open(filename, os.O_WRONLY | os.O_TRUNC)
		except Exception as e:
			ligolw.logger.info("cannot truncate '%s': %s" % (filename, str(e)))
			return
		os.close(fd)
		ligolw.logger.info("... truncating done.")


	@staticmethod
	def cpy(srcname, dstname, attempts = 5):
		"""
		Copy a file to a destination preserving permission if
		possible.  If the operation fails for a non-fatal reason
		then several attempts are made with a pause between each.
		The return value is dstname if the operation was successful
		or srcname if a non-fatal failure caused the operation to
		terminate.  Fatal failures raise an exeption.
		"""
		ligolw.logger.info("copying '%s' to '%s' ..." % (srcname, dstname))
		for i in itertools.count(1):
			try:
				shutil.copy2(srcname, dstname)
				# if we get here it worked
				break
			except IOError as e:
				# anything other than permission-denied or
				# out-of-space is a real error
				import errno
				import time
				if e.errno not in (errno.EPERM, errno.ENOSPC):
					raise
				# if we've run out of attempts, fall back
				# to the original file
				if i > 4:
					ligolw.logger.info("warning: attempt %d: %s: working with original file '%s'" % (i, errno.errorcode[e.errno], srcname))
					return srcname
				# otherwise sleep and try again
				ligolw.logger.info("warning: attempt %d: %s: sleeping and trying again ..." % (i, errno.errorcode[e.errno]))
				time.sleep(10)
		ligolw.logger.info("... copying done.")
		try:
			# try to preserve permission bits.  according to
			# the documentation, copy() and copy2() are
			# supposed preserve them, but I observe that they
			# don't.  maybe they don't preserve them if the
			# destination file already exists?
			shutil.copystat(srcname, dstname)
		except Exception as e:
			ligolw.logger.info("warning: ignoring failure to copy permission bits from '%s' to '%s': %s" % (srcname, dstname, str(e)))
		return dstname


	def __enter__(self):
		database_exists = os.access(self.filename, os.F_OK)

		if self.tmp_path is not None:
			# create the remporary file and retain a reference
			# to prevent its removal.  for suffix, can't use
			# splitext() because it only keeps the last bit,
			# e.g. won't give ".xml.gz" but just ".gz"

			self.temporary_file = tempfile.NamedTemporaryFile(suffix = ".".join(os.path.split(self.filename)[-1].split(".")[1:]), dir = self.tmp_path)
			self.target = self.temporary_file.name
			ligolw.logger.info("using '%s' as workspace for '%s'" % (self.target, self.filename))

			# mkstemp() ignores umask, creates all files
			# accessible only by owner;  we should respect
			# umask.  note that os.umask() sets it, too, so we
			# have to set it back after we know what it is.

			umsk = os.umask(0)
			os.umask(umsk)
			os.chmod(self.target, 0o666 & ~umsk)

			if database_exists:
				# if the file is being replaced then
				# truncate the database so that if this job
				# fails the user won't think the database
				# file is valid, otherwise copy the
				# existing database to the work space for
				# modification
				if self.replace_file:
					self.truncate(self.filename)
				elif self.cpy(self.filename, self.target) == self.filename:
					# non-fatal errors have caused us
					# to fall-back to the file in its
					# original location
					self.target = self.filename
					del self.temporary_file
		else:
			self.target = self.filename
			if database_exists and self.replace_file:
				self.truncate(self.target)

		return self


	def __str__(self):
		return self.target


	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Restore the working copy to its original location if that's
		not where it already is.

		During the move operation, this function traps the signals
		used by HTCondor to evict jobs.  This reduces the risk of
		corrupting a document by the job terminating part-way
		through the restoration of the file to its original
		location.  When the move operation is concluded, the
		original signal handlers are restored and if any signals
		were trapped they are resent to the current process in
		order.  Typically this will result in the signal handlers
		installed by the install_signal_trap() function being
		invoked, meaning any other scratch files that might be in
		use will be lost and the current process is terminated.
		"""
		# when removed, must also delete a -journal partner, ignore
		# all errors

		try:
			os.unlink("%s-journal" % self)
		except:
			pass

		# restore the file to its original location

		if self.target != self.filename:
			with ligolw.utils.SignalsTrap():
				if not self.discard:
					# move back to original location

					ligolw.logger.info("moving '%s' to '%s' ..." % (self.target, self.filename))
					shutil.move(self.target, self.filename)
					ligolw.logger.info("... moving done.")

					# next we will trigger the
					# temporary file removal.  because
					# we've just deleted that file,
					# this will produce an annoying but
					# harmless message about an ignored
					# OSError.  so silence the warning
					# we create a dummy file for the
					# TemporaryFile to delete.  ignore
					# any errors that occur when trying
					# to make the dummy file.  FIXME:
					# this is stupid, find a better way
					# to shut TemporaryFile up

					try:
						open(self.target, "w").close()
					except:
						pass

				# remove reference to
				# tempfile.TemporaryFile object.  this
				# triggers the removal of the file.

				del self.temporary_file

			ligolw.logger.info("working copy '%s' discarded" % self.target)
		# if an exception terminated the code block, re-raise the
		# exception

		return False


	def set_temp_store_directory(self, connection):
		"""
		Sets sqlite's temp_store_directory to the value of
		self.tmp_path, but only does so if .tmp_path is not None
		(indicating that a scratch directory has been set for the
		working copy) and if the working copy's filename differs
		from the original copy's filename.  If the two filenames
		are the same, that indicates that something prevented a
		working copy from being placed in the scratch directory,
		which typically means it's not available for use, either
		due to a permissions problem or that it's full.
		"""
		if self.tmp_path is None or self.target == self.filename:
			ligolw.logger.info("scratch space not in use:  sqlite temp_store_directory not changed")
			return
		ligolw.logger.info("setting sqlite temp_store_directory to '%s'" % self.tmp_path)
		cursor = connection.cursor()
		cursor.execute("PRAGMA temp_store_directory = '%s'" % self.tmp_path)
		cursor.close()


#
# =============================================================================
#
#                                  ID Mapping
#
# =============================================================================
#


class idmapper(object):
	"""
	Create and manage the _idmap_ table in an sqlite database.  This
	table has columns "table_name", "old", and "new" mapping old IDs to
	new IDs for each table.  The (table_name, old) column pair is a
	primary key (is indexed and must contain unique entries).  The
	table is created as a temporary table, so it will be automatically
	dropped when the database connection is closed.

	This class is for internal use, it forms part of the code used to
	re-map row IDs when merging multiple documents.
	"""
	def __init__(self, connection):
		self.connection = connection
		self.cursor = self.connection.cursor()
		try:
			self.cursor.execute("CREATE TEMPORARY TABLE _idmap_ (table_name TEXT NOT NULL, old INTEGER NOT NULL, new INTEGER NOT NULL, PRIMARY KEY (table_name, old))")
		except sqlite3.OperationalError:
			# assume table already exists
			pass
		self.sync()

	def reset(self):
		"""
		Erase the contents of the _idmap_ table, but leave the
		table in place.
		"""
		self.cursor.execute("DELETE FROM _idmap_")

	def sync(self):
		"""
		Iterate over the tables in the database, ensure that there
		exists a custom DBTable class for each, and synchronize
		that table's ID generator to the ID values in the database.
		"""
		xmldoc = get_xml(self.connection)
		for tbl in xmldoc.getElementsByTagName(DBTable.tagName):
			tbl.sync_next_id()
		xmldoc.unlink()

	@staticmethod
	def get_new(cursor, table_name, old, tbl):
		"""
		From the old ID, obtain a replacement ID by either grabbing
		it from the _idmap_ table if one has already been assigned
		to the old ID, or by using the current value of the Table
		instance's next_id class attribute.  In the latter case,
		the new ID is recorded in the _idmap_ table, and the class
		attribute incremented by 1.
		"""
		cursor.execute("SELECT new FROM _idmap_ WHERE table_name == ? AND old == ?", (table_name, old))
		new = cursor.fetchone()
		if new is not None:
			# a new ID has already been created for this old ID
			return new[0]
		# this ID was not found in _idmap_ table, assign a new ID and
		# record it
		new = tbl.get_next_id()
		cursor.execute("INSERT INTO _idmap_ VALUES (?, ?, ?)", (table_name, old, new))
		return new

	def update_ids(self, xmldoc):
		# NOTE:  it's critical that the xmldoc object be retrieved
		# *before* the rows whose IDs need to be updated (by
		# calling this method) are inserted.  the xml retrieval
		# resets the "last max row ID" values inside the table
		# objects, so if retrieval of the xmldoc is deferred until
		# after the rows are inserted, nothing will get updated.
		# therefore, the xmldoc must be retrieved by the calling
		# code, held while the rows are inserted, and then that
		# xmldoc object must be passed to this method, even though
		# it might seem like this method could simply reconstruct
		# the xmldoc itself from the connection.
		table_elems = xmldoc.getElementsByTagName(ligolw.Table.tagName)
		for i, tbl in enumerate(table_elems):
			ligolw.logger.info("updating IDs: %d%% (%s)" % (100.0 * i / len(table_elems), tbl.Name))
			tbl.applyKeyMapping()
		ligolw.logger.info("updating IDs: 100%")
		# reset for next document
		self.reset()


#
# =============================================================================
#
#                             Database Information
#
# =============================================================================
#


#
# SQL parsing
#


_sql_create_table_pattern = re.compile(r"CREATE\s+TABLE\s+(?P<name>\w+)\s*\((?P<coldefs>.*)\)", re.IGNORECASE)
_sql_coldef_pattern = re.compile(r"\s*(?P<name>\w+)\s+(?P<type>\w+)[^,]*")


#
# Database info extraction utils
#


def get_table_names(connection):
	"""
	Return a list of the table names in the database.
	"""
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM sqlite_master WHERE type == 'table'")
	return [name for (name,) in cursor]


def get_xml(connection, table_names = None):
	"""
	Construct an XML element tree wrapping around the contents of the
	database.  On success the return value is a ligolw.LIGO_LW element
	containing the tables as children.  Arguments are a connection to
	to a database, and an optional list of table names to extract from
	the database.  If table_names is None (the default), then
	get_table_names() is used to obtain the list of tables to extract.

	NOTE:  as explained above the return value is not an XML document,
	not a ligolw.Document instance, but a ligolw.LIGO_LW element
	instance.  For example, to write the document to disk in XML
	format, append the return value as a child node of a
	ligolw.Document object then pass that to the desired file writing
	routine.
	"""
	ligo_lw = ligolw.LIGO_LW()

	if table_names is None:
		table_names = get_table_names(connection)

	for table_name in table_names:
		# build the table document tree.  copied from
		# ligolw.Table.new()
		try:
			cls = DBTable.TableByName[table_name]
		except KeyError:
			cls = DBTable
		table_elem = cls(ligolw.AttributesImpl({"Name": "%s:table" % table_name}), connection = connection)
		destrip = {}
		if table_elem.validcolumns is not None:
			for name in table_elem.validcolumns:
				destrip[ligolw.Column.ColumnName(name)] = name
		for column_name, column_type in table_elem.get_column_info():
			if table_elem.validcolumns is not None:
				try:
					column_name = destrip[column_name]
				except KeyError:
					raise ValueError("invalid column")
				# use the pre-defined column type
				column_type = table_elem.validcolumns[column_name]
			else:
				# guess the column type
				column_type = ligolw.types.FromSQLiteType[column_type]
			table_elem.appendChild(ligolw.Column(ligolw.AttributesImpl({"Name": column_name, "Type": column_type})))
		table_elem._end_of_columns()
		table_elem.appendChild(table_elem.Stream(ligolw.AttributesImpl({"Name": "%s:table" % table_name})))
		ligo_lw.appendChild(table_elem)
	return ligo_lw


#
# =============================================================================
#
#                            DBTable Element Class
#
# =============================================================================
#


class DBTable(ligolw.Table):
	"""
	A version of the Table class using an SQL database for storage.
	Many of the features of the Table class are not available here, but
	instead the user can use SQL to query the table's contents.

	The constraints attribute can be set to a text string that will be
	added to the table's CREATE statement where constraints go.  For
	example you might wish to set this to "PRIMARY KEY (event_id)" for
	a table with an event_id column.

	Note:  because the table is stored in an SQL database, the use of
	this class imposes the restriction that table names be unique
	within a document.

	Also note that at the present time there is really only proper
	support for the pre-defined tables in the ligolw.lsctables module.
	It is possible to load unrecognized tables into a database from
	LIGO Light Weight XML files, but without developer intervention
	there is no way to indicate the constraints that should be imposed
	on the columns, for example which columns should be used as primary
	keys and so on.  This can result in poor query performance.  It is
	also possible to extract a database' contents to a LIGO Light
	Weight XML file even when the database contains unrecognized
	tables, but without developer intervention the column types will be
	guessed using a generic mapping of SQL types to LIGO Light Weight
	types.

	Each instance of this class must be connected to a database.  The
	(Python DBAPI 2.0 compatible) connection object is passed to the
	class via the connection parameter at instance creation time.

	Example:

	>>> import sqlite3
	>>> connection = sqlite3.connection()
	>>> tbl = dbtables.DBTable(ligolw.AttributesImpl({"Name": "process:table"}), connection = connection)

	A custom content handler must be created in order to pass the
	connection keyword argument to the DBTable class when instances are
	created, since the default content handler does not do this.  See
	the use_in() function defined in this module for information on how
	to create such a content handler

	If a custom ligolw.Table subclass is defined in ligolw.lsctables
	whose name matches the name of the DBTable being constructed, the
	lsctables class is added to the list of parent classes.  This
	allows the lsctables class' methods to be used with the DBTable
	instances but not all of the methods will necessarily work with the
	database-backed version of the class.  Your mileage may vary.
	"""

	#
	# Table name ---> table type mapping.
	#


	TableByName = {}


	def __new__(cls, *args, **kwargs):
		# NOTE:  in what follows cls.TableByName is the look-up
		# table defined above, for this class, whereas
		# ligolw.Table.TableByName is the parent class' version.

		# have we previously constructed a custom table-specific
		# class for this?
		attrs, = args
		name = cls.TableName(attrs["Name"])
		if name in cls.TableByName:
			# construct instance of new table-specific class
			# using the parent class' parent class'
			# constructor.  the parent class' own constructor
			# would recognize the table name, and override the
			# class, turning it into whatever its own look-up
			# table says it should be.  do not pass additional
			# keyword arguments to the parent class.
			new = super(ligolw.Table, ligolw.Table).__new__(cls.TableByName[name], *args)
			# because new is not an instance of cls, python
			# will not automatically call .__init__().
			# therefore we must do it ourselves.  now we pass
			# the kwargs, which contain the database connection
			# information.
			new.__init__(*args, **kwargs)
			return new

		# there is no custom database-backed class for this table.
		# does the parent class' look-up table provde a class for
		# this table that can provide us with the metadata needed
		# to create a custom table-specific class on the fly?
		if name not in ligolw.Table.TableByName:
			# no.  fall back to the default constructor.  do
			# not pass additional keyword arguments to the
			# parent class.  because we are returning an
			# instance of cls, python will call .__init__() for
			# us, so we don't need to
			return super().__new__(cls, *args)

		# construct custom database-backed subclass on the fly.
		# the class from lsctables is added as a parent class to
		# allow methods from that class to be used with this class,
		# however there is no guarantee that all parent class
		# methods will be appropriate for use with the
		# database-backed object.
		lsccls = ligolw.Table.TableByName[name]
		class CustomDBTable(cls, lsccls):
			tableName = lsccls.tableName
			validcolumns = lsccls.validcolumns
			loadcolumns = lsccls.loadcolumns
			constraints = lsccls.constraints
			next_id = lsccls.next_id
			RowType = lsccls.RowType
			how_to_index = lsccls.how_to_index

		# save for re-use (required for ID remapping across
		# multiple documents in ligolw_sqlite)
		cls.TableByName[name] = CustomDBTable

		# construct instance of new table-specific class using the
		# parent class' parent class' constructor.  the parent
		# class' own constructor would recognize the table name,
		# and override the class, turning it into whatever its own
		# look-up table says it should be.
		new = super(ligolw.Table, ligolw.Table).__new__(CustomDBTable, *args)
		# because new is not an instance of cls, python will not
		# automatically call .__init__().  therefore we must do it
		# ourselves.  now we pass the kwargs, which contain the
		# database connection information.
		new.__init__(*args, **kwargs)
		return new

	def __init__(self, *args, **kwargs):
		# chain to parent class
		ligolw.Table.__init__(self, *args)

		# retrieve connection object from kwargs
		self.connection = kwargs.pop("connection")

		# pre-allocate a cursor for internal queries
		self.cursor = self.connection.cursor()

	def copy(self, *args, **kwargs):
		"""
		This method is not implemented.  See ligolw.Table for more
		information.
		"""
		raise NotImplementedError

	def _end_of_columns(self):
		# chain to parent class
		ligolw.Table._end_of_columns(self)
		# dbcolumnnames and types have the "not loaded" columns
		# removed
		if self.loadcolumns is not None:
			self.dbcolumnnames = [name for name in self.columnnames if name in self.loadcolumns]
			self.dbcolumntypes = [name for i, name in enumerate(self.columntypes) if self.columnnames[i] in self.loadcolumns]
		else:
			self.dbcolumnnames = self.columnnames
			self.dbcolumntypes = self.columntypes

		# create the table
		ToSQLType = {
			"sqlite": ligolw.types.ToSQLiteType,
			"mysql": ligolw.types.ToMySQLType
		}[connection_db_type(self.connection)]
		try:
			statement = "CREATE TABLE IF NOT EXISTS " + self.Name + " (" + ", ".join(map(lambda n, t: "%s %s" % (n, ToSQLType[t]), self.dbcolumnnames, self.dbcolumntypes))
		except KeyError as e:
			raise ValueError("column type '%s' not supported" % str(e))
		if self.constraints is not None:
			statement += ", " + self.constraints
		statement += ")"
		self.cursor.execute(statement)

		# row ID where remapping is to start
		self.remap_first_rowid = None

		# construct the SQL to be used to insert new rows
		params = {
			"sqlite": ",".join("?" * len(self.dbcolumnnames)),
			"mysql": ",".join(["%s"] * len(self.dbcolumnnames))
		}[connection_db_type(self.connection)]
		self.append_statement = "INSERT INTO %s (%s) VALUES (%s)" % (self.Name, ",".join(self.dbcolumnnames), params)
		self.append_attrgetter = operator.attrgetter(*self.dbcolumnnames)

	def get_column_info(self):
		"""
		Return an in order list of (name, type) tuples describing
		the columns in this table.
		"""
		self.cursor.execute("SELECT sql FROM sqlite_master WHERE type == 'table' AND name == ?", (self.Name,))
		statement, = self.cursor.fetchone()
		coldefs = re.match(_sql_create_table_pattern, statement).groupdict()["coldefs"]
		return [(coldef.groupdict()["name"], coldef.groupdict()["type"]) for coldef in re.finditer(_sql_coldef_pattern, coldefs) if coldef.groupdict()["name"].upper() not in ("PRIMARY", "UNIQUE", "CHECK")]

	def sync_next_id(self):
		if self.next_id is not None:
			maxid = self.cursor.execute("SELECT MAX(%s) FROM %s" % (self.next_id.column_name, self.Name)).fetchone()[0]
			if maxid is not None:
				# type conversion not needed for
				# .set_next_id(), but needed so we can do
				# arithmetic on the thing
				maxid = type(self.next_id)(maxid) + 1
				if maxid > self.next_id:
					self.set_next_id(maxid)
		return self.next_id

	def maxrowid(self):
		self.cursor.execute("SELECT MAX(ROWID) FROM %s" % self.Name)
		return self.cursor.fetchone()[0]

	def __len__(self):
		self.cursor.execute("SELECT COUNT(*) FROM %s" % self.Name)
		return self.cursor.fetchone()[0]

	def __iter__(self):
		cursor = self.connection.cursor()
		cursor.execute("SELECT * FROM %s ORDER BY rowid ASC" % self.Name)
		for values in cursor:
			yield self.row_from_cols(values)

	def __reversed__(self):
		cursor = self.connection.cursor()
		cursor.execute("SELECT * FROM %s ORDER BY rowid DESC" % self.Name)
		for values in cursor:
			yield self.row_from_cols(values)

	def _append(self, row):
		"""
		Standard .append() method.  This method is intended for
		internal use only.
		"""
		self.cursor.execute(self.append_statement, self.append_attrgetter(row))

	def _remapping_append(self, row):
		"""
		Version of the .append() method that performs on the fly
		row ID reassignment, and so also performs the function of
		the updateKeyMapping() method.  SQLite does not permit the
		PRIMARY KEY of a row to be modified, so it needs to be done
		prior to insertion.  This method is intended for internal
		use only.
		"""
		if self.next_id is not None:
			# assign (and record) a new ID before inserting the
			# row to avoid collisions with existing rows
			setattr(row, self.next_id.column_name, idmapper.get_new(self.cursor, self.Name, getattr(row, self.next_id.column_name), self))
		self._append(row)
		if self.remap_first_rowid is None:
			self.remap_first_rowid = self.maxrowid()
			assert self.remap_first_rowid is not None

	append = _append

	def row_from_cols(self, values):
		"""
		Given an iterable of values in the order of columns in the
		database, construct and return a row object.  This is a
		convenience function for turning the results of database
		queries into Python objects.
		"""
		return self.RowType(**dict(zip(self.dbcolumnnames, values)))

	def unlink(self):
		# chain to parent class
		ligolw.Table.unlink(self)
		self.cursor.close()
		self.cursor = None
		self.connection = None

	def applyKeyMapping(self):
		"""
		Used as the second half of the key reassignment algorithm.
		Loops over each row in the table, replacing references to
		old row keys with the new values from the _idmap_ table.
		"""
		if self.remap_first_rowid is None:
			# no rows have been added since we processed this
			# table last
			return
		assignments = []
		for colname in self.dbcolumnnames:
			column = self.getColumnByName(colname)
			try:
				table_name = column.table_name
			except ValueError:
				# if we get here the column's name does not
				# have a table name component, so by
				# convention it cannot contain IDs pointing
				# to other tables
				continue
			# make sure it's not our own ID column (by
			# convention this should not be possible, but it
			# doesn't hurt to check)
			if self.next_id is not None and colname == self.next_id.column_name:
				continue
			assignments.append("%s = (SELECT new FROM _idmap_ WHERE _idmap_.table_name == \"%s\" AND _idmap_.old == %s)" % (colname, table_name, colname))
		assignments = ", ".join(assignments)
		if assignments:
			# SQLite documentation says ROWID is monotonically
			# increasing starting at 1 for the first row unless
			# it ever wraps around, then it is randomly
			# assigned.  ROWID is a 64 bit integer, so the only
			# way it will wrap is if somebody sets it to a very
			# high number manually.  This library does not do
			# that, so I don't bother checking.
			self.cursor.execute("UPDATE %s SET %s WHERE ROWID >= %d" % (self.Name, assignments, self.remap_first_rowid))
		self.remap_first_rowid = None


#
# =============================================================================
#
#                                  LSC Tables
#
# =============================================================================
#


class CoincMapTable(DBTable):
	tableName = ligolw.lsctables.CoincMapTable.tableName
	validcolumns = ligolw.lsctables.CoincMapTable.validcolumns
	constraints = ligolw.lsctables.CoincMapTable.constraints
	next_id = ligolw.lsctables.CoincMapTable.next_id
	RowType = ligolw.lsctables.CoincMapTable.RowType
	how_to_index = ligolw.lsctables.CoincMapTable.how_to_index

	def applyKeyMapping(self):
		if self.remap_first_rowid is not None:
			self.cursor.execute("UPDATE coinc_event_map SET event_id = (SELECT new FROM _idmap_ WHERE _idmap_.table_name == coinc_event_map.table_name AND old == event_id), coinc_event_id = (SELECT new FROM _idmap_ WHERE _idmap_.table_name == 'coinc_event' AND old == coinc_event_id) WHERE ROWID >= ?", (self.remap_first_rowid,))
			self.remap_first_rowid = None


class TimeSlideTable(DBTable):
	tableName = ligolw.lsctables.TimeSlideTable.tableName
	validcolumns = ligolw.lsctables.TimeSlideTable.validcolumns
	constraints = ligolw.lsctables.TimeSlideTable.constraints
	next_id = ligolw.lsctables.TimeSlideTable.next_id
	RowType = ligolw.lsctables.TimeSlideTable.RowType
	how_to_index = ligolw.lsctables.TimeSlideTable.how_to_index

	def as_dict(self):
		"""
		Return a dictionary mapping time slide IDs to offset
		dictionaries.
		"""
		# import is done here to reduce risk of a cyclic
		# dependency.  at the time of writing there is not one, but
		# we can help prevent it in the future by putting this
		# here.
		from lalburst import offsetvector
		return dict((time_slide_id, offsetvector.offsetvector((instrument, offset) for time_slide_id, instrument, offset in values)) for time_slide_id, values in itertools.groupby(self.cursor.execute("SELECT time_slide_id, instrument, offset FROM time_slide ORDER BY time_slide_id"), lambda time_slide_id_instrument_offset: time_slide_id_instrument_offset[0]))

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
			raise KeyError(offsetdict)
		if len(ids) == 1:
			# found one
			return ids[0]
		# offset vector not found in table
		if create_new is None:
			# and that's not OK
			raise KeyError(offsetdict)
		# that's OK, create new vector
		time_slide_id = self.get_next_id()
		for instrument, offset in offsetdict.items():
			row = self.RowType()
			row.process_id = create_new.process_id
			row.time_slide_id = time_slide_id
			row.instrument = instrument
			row.offset = offset
			self.append(row)

		# return new ID
		return time_slide_id


#
# =============================================================================
#
#                                Table Metadata
#
# =============================================================================
#


def build_indexes(connection):
	"""
	Using the how_to_index annotations in the table class definitions,
	construct a set of indexes for the database at the given
	connection.
	"""
	cursor = connection.cursor()
	for table_name in get_table_names(connection):
		# FIXME:  figure out how to do this extensibly
		if table_name in DBTable.TableByName:
			how_to_index = DBTable.TableByName[table_name].how_to_index
		elif table_name in ligolw.Table.TableByName:
			how_to_index = ligolw.Table.TableByName[table_name].how_to_index
		else:
			continue
		if how_to_index is not None:
			ligolw.logger.info("indexing %s table ..." % table_name)
			for index_name, cols in how_to_index.items():
				cursor.execute("CREATE INDEX IF NOT EXISTS %s ON %s (%s)" % (index_name, table_name, ",".join(cols)))
	connection.commit()


#
# =============================================================================
#
#                                Table Metadata
#
# =============================================================================
#


#
# add the pre-defined custom tables to the name-to-class mapping
#


DBTable.TableByName.update({
	CoincMapTable.tableName: CoincMapTable,
	TimeSlideTable.tableName: TimeSlideTable
})


#
# =============================================================================
#
#                               Content Handler
#
# =============================================================================
#


#
# Override portions of a ligolw.ContentHandler class
#


class ContentHandler(ligolw.ContentHandler):
	"""
	A sub-class of ligolw.ContentHandler using the DBTable class
	defined in this module when parsing XML documents and encountering
	Table elements.  Instances of this ContentHandler class must have
	an attribute named .connection.  No specific mechanism is provided
	for initializing this attribute, it is left as an exercise for the
	calling code to arrange for it to be set properly before the
	ContentHandler is used to parse a document.

	When a document is parsed, the value of the .connection attribute
	will be passed to the DBTable class' .__init__() method as each
	table object is created, and thus sets the database connection for
	all table objects in the document.

	NOTE:  Because the ContentHandler class is instantiated deep within
	the I/O code, immediately prior to its use, it is necessary to set
	the .connection attribute on the class itself, as a class
	attribute.  There is no way to set the attribute on the instance of
	the class that is used to load the document.  Because a
	ContentHandler is only used to load an XML document, and it's
	highly unusual to load multiple documents simultaneously, the need
	to set the attribute on the class itself is usually not a
	limitation.  However, if multiple XML streams are to be loaded into
	distinct databases simultaneously then it will be necessary to
	create per-database subclasses of this class so that each can have
	its own .connection class attribute set.

	Example:

	>>> import sqlite
	>>> class MyContentHandler(ContentHandler):
	...	connection = sqlite3.connection()
	... 
	>>> ligolw.utils.load_url("demo.xml", contenthandler = MyContentHandler)
	"""
	def startTable(self, parent, attrs):
		return DBTable(attrs, connection = self.connection)


def use_in(ContentHandler):
	"""
	Decorator to modify a ContentHandler class definition to cause it
	to use the DBTable class defined in this module when parsing XML
	documents.  Instances of the ContentHandler class must have an
	attribute named .connection.  See ContentHandler in this module for
	more information.

	In the example below, the .__init__() method of a custom
	ContentHandler is used to set the .connection attribute on a newly
	created instance of the class, while the use_in() decorator is used
	to ensure the other customizations required to use the
	ContentHandler to load a document into an sqlite database have been
	made.

	Example:

	>>> import sqlite3
	>>> import ligolw
	>>> @use_in
	... class MyContentHandler(ligolw.ContentHandler):
	...	def __init__(self, *args):
	...		super(MyContentHandler, self).__init__(*args)
	...		self.connection = sqlite3.connection()
	... 
	>>> 
	"""
	def startTable(self, parent, attrs):
		return DBTable(attrs, connection = self.connection)
	ContentHandler.startTable = startTable
	return ContentHandler
