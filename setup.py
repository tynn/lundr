#	This file is part of lundr.
#
#	Copyright (c) 2014 Christian Schmitz <tynn.dev@gmail.com>
#
#	lundr is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	lundr is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with lundr. If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from distutils.command.install import install
import sys
sys.dont_write_bytecode = True
try :
	from importlib.machinery import SourceFileLoader
	lundr = SourceFileLoader('lundr', 'lundr').load_module()
except ImportError :
	import imp
	lundr = imp.load_source('lundr', 'lundr')

_noegg = lambda (key, _) :  key != 'install_egg_info'
class install_noegg (install) :
	sub_commands = list(filter(_noegg, install.sub_commands))

setup(
	name = 'lundr',
	version = lundr.__version__,
	author = lundr.__author__,
	author_email = lundr.__author_email__,
	license = 'GPLv3+',
	description = lundr.__doc__,
	long_description = lundr.__doc__,
	url = lundr.__url__,
	platforms = ['Linux'],
	scripts = ['lundr'],
	data_files = [('share/applications', ['lundr.desktop'])],
	cmdclass = {'install': install_noegg},
)

