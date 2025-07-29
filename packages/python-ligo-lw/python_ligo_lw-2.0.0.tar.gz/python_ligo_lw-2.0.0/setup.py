from setuptools import setup, Extension


__version__ = "2.0.0"
__date__ = "2025-04-25"


def macroreplace(filenames, substs):
	"""
	Autoconf-style macro replacement
	"""
	for filename in filenames:
		if not filename.endswith(".in"):
			raise ValueError("\"%s\" must end in \".in\"" % filename)
	for pattern in substs:
		if not pattern.startswith("@") or not pattern.endswith("@"):
			raise ValueError("bad pattern \"%s\"" % pattern)
	for filename in filenames:
		with open(filename[:-3], "w") as outfile:
			for line in open(filename, "r"):
				for pattern, value in substs.items():
					line = line.replace(pattern, value)
				outfile.write(line)


macroreplace([
	"ligolw/version.py.in",
	"python-ligo-lw.spec.in",
], {
	"@VERSION@": __version__,
	"@DATE@": __date__,
})


setup(
	name = "python-ligo-lw",
	version = __version__,
	author = "Kipp Cannon",
	author_email = "kipp@g.ecc.u-tokyo.ac.jp",
	description = "Python LIGO Light-Weight XML I/O Library",
	long_description = "The LIGO Light-Weight XML format is used by gravitational-wave detection pipelines and associated tool sets.  This package provides a Python I/O library for reading, writing, and interacting with documents in this format.",
	url = "https://git.ligo.org/kipp.cannon/python-ligo-lw",
	license = "GPL",
	packages = [
		"ligolw",
		"ligolw.utils",
	],
	ext_modules = [
		Extension(
			"ligolw.tokenizer",
			[
				"ligolw/tokenizer.c",
				"ligolw/tokenizer.Tokenizer.c",
				"ligolw/tokenizer.RowBuilder.c",
				"ligolw/tokenizer.RowDumper.c",
			],
			include_dirs = ["ligolw"]
		),
	],
	scripts = [
		"bin/ligolw_add",
		"bin/ligolw_cut",
		"bin/ligolw_no_ilwdchar",
		"bin/ligolw_print",
		"bin/ligolw_run_sqlite",
		"bin/ligolw_segments",
		"bin/ligolw_sqlite",
	],
	classifiers = [
		"Development Status :: 6 - Mature",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		"Natural Language :: English",
		"Operating System :: POSIX",
		"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Astronomy",
		"Topic :: Scientific/Engineering :: Physics",
		"Topic :: Software Development :: Libraries",
		"Topic :: Text Processing :: Markup :: XML",
	],
)
