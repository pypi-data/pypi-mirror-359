#!/usr/bin/env python3

import doctest
import sys
import ligolw.utils

if __name__ == '__main__':
	failures = doctest.testmod(ligolw.utils)[0]
	sys.exit(bool(failures))
