#!/usr/bin/env python3


import matplotlib
matplotlib.use("Agg")
from matplotlib import figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy
import sys

import ligolw
import ligolw.utils
ligolw.logger.setLevel(ligolw.logging.INFO)

xmldoc = ligolw.utils.load_filename("ligo_lw_test_01.xml")
ligolw.utils.write_filename(xmldoc, "/dev/null")

t, = xmldoc.getElementsByTagName(ligolw.Time.tagName)
print("%s: %s" % (t.Name, t.pcdata), file=sys.stderr)

for n, a in enumerate(xmldoc.getElementsByTagName(ligolw.Array.tagName)):
	print("found %s array '%s'" % ("x".join(map(str, a.array.shape)), a.Name), file=sys.stderr)
	fig = figure.Figure()
	FigureCanvas(fig)
	axes = fig.gca()
	axes.loglog()
	axes.grid(True)
	for i in range(1, a.array.shape[0]):
		axes.plot(numpy.fabs(a.array[0]), numpy.fabs(a.array[i]))
	axes.set_title(a.Name)
	print("saving as 'ligo_lw_test_01_%d.png' ..." % n, file=sys.stderr)
	fig.savefig("ligo_lw_test_01_%d.png" % n)
	print("done.", file=sys.stderr)

	# try turning it back into XML
	ligolw.Array.build(a.Name, a.array)
