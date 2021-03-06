# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


import urlparse

from flask import current_app

site_hostname = urlparse.urlsplit(current_app.config['CFG_SITE_URL']).netloc
site_secure_hostname = urlparse.urlsplit(current_app.config['CFG_SITE_SECURE_URL']).netloc

url_map = [
    ('/record/<id>', site_hostname)
]

if site_hostname != site_secure_hostname:
    url_map += ('/record/<id>', site_secure_hostname)


class LocalRecordJsonLoader():
    __url_map__ = url_map

    def get_remote_json(self, uri):
        from invenio_records.api import get_record

        splitted_url = urlparse.urlsplit(uri)
        recid = int(splitted_url.path.split('/')[2])
        return get_record(recid).dumps()


loader = LocalRecordJsonLoader
