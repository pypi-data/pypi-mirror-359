# Copyright (C) 2006-2014,2016-2018,2020--2022,2024--2025  Kipp Cannon
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
Add (merge) LIGO LW XML files containing LSC tables.
"""


import os
import sys
import urllib.parse


from .. import __author__, __date__, __version__
import ligolw
from . import load_url


#
# =============================================================================
#
#                             I/O File Management
#
# =============================================================================
#


def url2path(url):
	"""
	If url identifies a file on the local host, return the path to the
	file otherwise raise ValueError.
	"""
	scheme, host, path, nul, nul, nul = urllib.parse.urlparse(url)
	if scheme.lower() in ("", "file") and host.lower() in ("", "localhost"):
		return path
	raise ValueError(url)


def delete_with_exceptions(urls, preserves):
	"""
	Attempt to delete all files identified by the URLs in urls except
	any that are the same as the files in the preserves list.
	"""
	for path in map(url2path, urls):
		if any(os.path.samefile(path, preserve) for preserve in preserves):
			continue
		ligolw.logger.info("removing \"%s\" ..." % path)
		try:
			os.remove(path)
		except:
			ligolw.logger.info("... removing failed (ignoring error).")
		else:
			ligolw.logger.info("... removing done.")


#
# =============================================================================
#
#                                Document Merge
#
# =============================================================================
#


def merge_ligolws(elem):
	"""
	Merge all LIGO_LW elements that are immediate children of elem by
	appending their children to the first, and unlinking all but the
	first.

	NOTE:  the attributes of the LIGO_LW elements are assumed to be
	meaningless.  No check is performed to ensure the elements being
	deleted had the same attributes as the one that remains.
	"""
	ligolw.logger.info("merge top-level LIGO_LW's ...")
	ligolws = [child for child in elem.childNodes if child.tagName == ligolw.LIGO_LW.tagName]
	if ligolws:
		dest = ligolws.pop(0)
		for src in ligolws:
			# copy children
			for elem in src.childNodes:
				dest.appendChild(elem)
			# unlink from parent
			if src.parentNode is not None:
				src.parentNode.removeChild(src)
	ligolw.logger.info("... merge top-level LIGO_LW's done.")
	return elem


def merge_compatible_tables(elem):
	"""
	Below the given element, find all Tables whose structure is
	described in lsctables, and merge compatible ones of like type.
	That is, merge all SnglBurstTables that have the same columns into
	a single table, etc..
	"""
	ligolw.logger.info("merging tables ...")
	for name in ligolw.Table.TableByName.keys():
		tables = ligolw.Table.getTablesByName(elem, name)
		if tables:
			dest = tables.pop(0)
			ligolw.logger.info("%s" % dest.Name)
			for src in tables:
				if src.Name != dest.Name:
					# src and dest have different names
					continue
				# src and dest have the same names
				if dest.compare_columns(src):
					# but they have different columns
					raise ValueError("document contains %s tables with incompatible columns" % dest.Name)
				# and the have the same columns
				# copy src rows to dest
				for row in src:
					dest.append(row)
				# unlink src from parent
				if src.parentNode is not None:
					src.parentNode.removeChild(src)
				src.unlink()
	ligolw.logger.info("... merging tables done.")
	return elem


#
# =============================================================================
#
#                                 Library API
#
# =============================================================================
#


def ligolw_add(xmldoc, urls, non_lsc_tables_ok = False, remove_input = False, preserves = [], **kwargs):
	"""
	A LIGO Light-Weight XML document add algorithm.  Loads a sequence
	of documents into memory and merges them into a single LIGO_LW
	block, merging compatible tables and reassigning row IDs so that
	there are no collisions.

	urls is a list of URLs (or filenames) to load, xmldoc
	is the XML document tree to which they should be added.  If
	non_lsc_tables_ok is False (the default) then the code will refuse
	to process documents found to contain tables not recognized by the
	name-->class mapping in ligolw.Table.TableByName.  If remove_input
	is True then any local files in the urls list are deleted after the
	merge is complete, with the exception of any documents listed in
	the preserves list.  If remove_input is False (the default) then
	the input documents are left in place.  All remaining keyword
	arguments are passed to ligolw.utils.load_url().

	NOTE:  only Table elements are merged.  No other data that it might
	make sense to combine is processed.  The name of this utility was
	chosen at a time when, due to the lack of an I/O library for
	handling documents in this format, documents used for astrophysical
	data analysis were restricted to tabular data only.  Merging tables
	was all there was to merging documents.  The more complete document
	handling capabilities, even of this library itself, came later.

	NOTE:  this process assumes the attributes of LIGO_LW elements (the
	Name and Type) are meaningless.  The attributes of the first LIGO_LW
	element are preserved.
	"""
	# Input
	for n, url in enumerate(urls, 1):
		ligolw.logger.info("inserting %d/%d '%s' ..." % (n, len(urls), url))
		load_url(url, xmldoc = xmldoc, **kwargs)
		ligolw.logger.info("... inserting '%s' done" % url)

	# ID reassignment
	if not non_lsc_tables_ok and ligolw.lsctables.HasNonLSCTables(xmldoc):
		raise ValueError("non-LSC tables found (%s).  Use --non-lsc-tables-ok to force" % ". ".join(ligolw.lsctables.HasNonLSCTables(xmldoc)))
	xmldoc.reassign_table_row_ids()

	# Document merge
	merge_ligolws(xmldoc)
	merge_compatible_tables(xmldoc)

	# Remove input documents, preserving any requested
	if remove_input:
		delete_with_exceptions(urls, preserves)

	return xmldoc
