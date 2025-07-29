#!/usr/bin/env python3

import ligolw
import ligolw.utils

while 1:
	ligolw.utils.load_filename("ligo_lw_test_01.xml", verbose = True).unlink()
