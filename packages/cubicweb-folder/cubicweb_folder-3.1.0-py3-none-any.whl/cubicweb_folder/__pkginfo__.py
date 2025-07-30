# pylint: disable-msg=W0622
"""cubicweb-classification-folder packaging information"""

modname = 'cubicweb_folder'
distname = "cubicweb-folder"

numversion = (3, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname
description = "folder component for the CubicWeb framework"
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
           ]

__depends__ = {
    'cubicweb': ">=4.5.2,<6.0.0",
    'cubicweb-web': ">=1.0.0,<2.0.0",
}

__recommends__ = {}
