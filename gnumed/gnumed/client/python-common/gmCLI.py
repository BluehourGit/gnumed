"""GnuMed command line options handling.

All command line argument handling should go through this module.

Theory of operation:
--------------------
Upon startup the command line is parsed for any option
arguments. Those are assumed to start with at least one "-".
Any arguments not starting with a "-" are considered
non-option arguments. Option arguments are then stored in
the module level global dictionary _cli_args{}.

Your module should import gmCLI and query for existence of
one-letter arguments like this:

if gmGLI.has_arg("-v"):
	do_something_verbosely()
else:
	be_rather_quiet()

If you want to access the value for a long option you should
first check for it's existence and then access the value:

if gmCLI.has_arg("--foo"):
	print gmCLI.arg["--foo"]
else:
	print "no argument --foo specified"

Remember that even though a long argument exists it may not
have a value, e.g. the value might amount to an empty string.

Limitations:
------------
1) Aggregated short arguments are not supported, eg you CANNOT say
    my-script -fo
   instead of
    my-script -f -o
   In fact, "-fo" will be truncated to "-f"
2) Values on short arguments are not supported. Use long
   style arguments for that, e.g.:
    my-script --foo=bar

@license: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmCLI.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, getopt, string
import gmLog

_log = gmLog.gmDefLog
_cli_args = {}

# define global shortcuts
has_arg = _cli_args.has_key
arg = _cli_args
######################################################################
def _preparse_cmdline():
	"""Parse command line for given options.

	- this is needed to tell getopt which options to get
	- ALL logging in here is lData level noise
	"""
	_log.Log(gmLog.lData, "unparsed command line is >>%s<<" % string.join(sys.argv))

	opts = []
	short_opt_names = ""
	long_opt_names = []
	for arg in sys.argv[1:]:
		# is this an option ?
		if arg[0:1] == "-":
			# yes it is
			# strip trailing values (=...)
			val_pos = string.find(arg, "=")
			if val_pos != -1:
				# but keep "=" so getopt will retrieve the value
				opt = arg[:val_pos+1]
			else:
				opt = arg
			# strip leading slashes
			if arg[1:2] != "-":
				opt = opt[1:2]
				short_opt_names = short_opt_names + opt
				# short option ("-opt") - may only be two characters long ...
				# therefore truncate if necessary
				# FIXME: what about short options with values ("t:") ?
				opts.append("-%s" % opt)
				# but log a warning
				if len(arg) > 2:
					_log.Log(gmLog.lWarn, 'Unable to handle aggregated short arguments. Had to truncate "short" option "%s" to "-%s".' % (arg, opt))
			else:
				# long option ("--opt")
				opt = opt[2:]
				long_opt_names.append(opt)
				opts.append(arg)
		else:
			# nope (so maybe a filename)
			_log.Log(gmLog.lInfo, 'argument <%s> does not seem to be an option argument since it does not start with a "-"' % arg)

	return short_opt_names, long_opt_names, opts
#---------------------------------------------------------------------
def _parse_opts(short_names, long_names, arg_list):
	"""Break down preparsed command line into option-value pairs.
	"""
	opts = []
	args = []
	try:
		(opts, args) = getopt.getopt(arg_list, short_names, long_names)
	except getopt.GetoptError:
		_log.Log(gmLog.lWarn, "problem parsing command line")
		exc = sys.exc_info()
		_log.LogException("Non-fatal exception caught:", exc, fatal=0)

	for opt in opts:
		_cli_args[opt[0]] = opt[1]

	_log.Log(gmLog.lData, "command line arguments: %s" % str(_cli_args))
######################################################################
# Main
#=====================================================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	_ = lambda x:x
	print "testing gmCLI"
	print "============="
	print "You gave me the following arguments on the command line:"
	(shorts, longs, opts) = _preparse_cmdline()
	print "short options:", shorts
	print "long  options:", longs
	_parse_opts(shorts, longs, opts)
	print "This yields the following command line arguments dictionary:"
	print _cli_args
	if has_arg("--help") or has_arg("-h") or has_arg("-?"):
		print "You requested help. Wise you."
		print __doc__
	else:
		print "You might wanna try --help, -h, or -?"

	print "======================================================================"
	print __doc__
	print "======================================================================"

else:
	(shorts, longs, opts) = _preparse_cmdline()
	_parse_opts(shorts, longs, opts)

#=====================================================================
# $Log: gmCLI.py,v $
# Revision 1.8  2002-11-18 09:41:25  ncq
# - removed magic #! interpreter incantation line to make Debian happy
#
# Revision 1.7  2002/11/17 20:09:10  ncq
# - always display __doc__ when called standalone
#
# Revision 1.6  2002/09/30 10:58:27  ncq
# - consistently spell GnuMed
#
# Revision 1.5  2002/09/26 13:20:02  ncq
# - log version
#
# Revision 1.4  2002/09/08 15:57:42  ncq
# - added log cvs keyword
#
