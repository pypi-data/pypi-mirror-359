#!/usr/bin/env python3

import sys
import ligolw
import ligolw.utils
import numpy
import os
import time


# make text mode lossless otherwise the test won't pass with random data

ligolw.types.FormatFunc.update({
	"real_8": "%.17g".__mod__,
	"double": "%.17g".__mod__
})


def test_io_iteration_order(orig, mode):
	filename = "big_array_%s.xml.gz" % mode
	print("mode = \"%s\":" % mode)

	xmldoc = ligolw.Document()
	xmldoc.appendChild(ligolw.LIGO_LW()).appendChild(ligolw.Array.build("test", orig, mode = mode))

	start_write = time.perf_counter()
	ligolw.utils.write_filename(xmldoc, filename, with_mv = False)
	end_write = time.perf_counter()
	print("\twriting took %g s" % (end_write - start_write))
	print("\tcompressed file size is %d bytes" % os.path.getsize(filename))

	start_read = time.perf_counter()
	recov = ligolw.Array.get_array(ligolw.utils.load_filename(filename), "test").array
	end_read = time.perf_counter()
	print("\treading took %g s" % (end_read - start_read))

	if not (recov == orig).all():
		raise ValueError("arrays are not the same")

	os.remove(filename)

if __name__ == '__main__':
	array = numpy.random.random((250, 250, 250))
	print("using %s array of random double precision floats ..." % "x".join("%d" % i for i in array.shape))

	failures = False
	try:
		test_io_iteration_order(array, "text")
		test_io_iteration_order(array, "b64le")
		test_io_iteration_order(array, "b64be")
	except ValueError as e:
		print(e, file = sys.stderr)
		failures |= True
	sys.exit(bool(failures))
