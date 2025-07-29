#
# assorted python code for testing bits of the database interface
#


import sqlite3
import sys


import ligolw
import ligolw.dbtables

ligolw.set_verbose(True)

database_filename = sys.argv[1]


with ligolw.dbtables.workingcopy(database_filename, tmp_path = "/tmp", discard = True) as target:
	connection = sqlite3.connect(str(target))
	target.set_temp_store_directory(connection)
	xmldoc = ligolw.dbtables.get_xml(connection)

	# test .row_from_cols()

	for row in ligolw.lsctables.ProcessTable.get_table(xmldoc):
		print(row.program, row.version, row.start, row.username)
