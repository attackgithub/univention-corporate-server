#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Univention App Center
#  univention-app module for uninstalling an app
#  (docker version)
#
# Copyright 2015-2017 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.
#

from univention.appcenter.actions import Abort
from univention.appcenter.actions.remove import Remove
from univention.appcenter.actions.docker_base import DockerActionMixin


class Remove(Remove, DockerActionMixin):

	def setup_parser(self, parser):
		super(Remove, self).setup_parser(parser)
		parser.add_argument('--do-not-backup', action='store_false', dest='backup', help='For docker apps, do not save a backup container')

	def _do_it(self, app, args):
		self._unregister_host(app, args)
		self.percentage = 5
		super(Remove, self)._do_it(app, args)

	def _remove_app(self, app, args):
		if not app.docker:
			super(Remove, self)._remove_app(app, args)
		else:
			self._remove_docker_container(app, args)

	def _remove_docker_container(self, app, args):
		if args.backup:
			if self._backup_container(app, backup_data='move') is False:
				raise Abort('Could not backup container!')
		docker = self._get_docker(app)
		if docker.container:
			docker.stop()
			docker.rm()
