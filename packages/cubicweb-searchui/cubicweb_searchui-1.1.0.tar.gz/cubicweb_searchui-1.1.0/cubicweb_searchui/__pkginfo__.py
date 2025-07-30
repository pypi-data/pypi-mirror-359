# pylint: disable=W0622
"""cubicweb-searchui application packaging information"""

modname = 'searchui'
distname = 'cubicweb-searchui'

numversion = (1, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'

author_email = 'contact@logilab.fr'
description = 'set of ui components to ease data browsing'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': ">=4.5.2,<6.0.0",
    'cubicweb-web': ">=1.0.0,<2.0.0",
    'cubicweb-squareui': ">=2.0.0,<3.0.0"}

__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
