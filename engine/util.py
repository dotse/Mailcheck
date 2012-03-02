
import traceback
import cStringIO


def traceback_as_str(limit=20):
	f = cStringIO.StringIO()
	traceback.print_exc(limit=limit, file=f)
	s = str(f.getvalue())
	f.close()
	return unicode(s, 'iso-8859-1')
