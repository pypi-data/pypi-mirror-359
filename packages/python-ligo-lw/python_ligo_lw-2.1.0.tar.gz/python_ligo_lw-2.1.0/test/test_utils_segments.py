#!/usr/bin/env python3

import doctest
import sys
from ligolw.utils import segments as ligolw_segments

if __name__ == '__main__':
	failures = doctest.testmod(ligolw_segments)[0]
	sys.exit(bool(failures))
