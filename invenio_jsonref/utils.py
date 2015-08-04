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

from werkzeug.routing import Map, Rule
from jsonref import JsonLoader, JsonRef

from werkzeug.exceptions import NotFound
import urlparse
from invenio_jsonref.registry import json_loaders


class JsonLoaderManager():
    ref_keyword = '$ref'
    url_rules = []
    url_map = None

    def __init__(self):
        if not self.url_rules:
            self._create_url_map()

    def _create_url_map(self):
        for jsonloader in json_loaders:
            assert hasattr(jsonloader, 'url_map')

            paths, hostnames = zip(*jsonloader.url_map)
            url_tuples = zip(paths, [jsonloader.resolve for _ in range(len(paths))], hostnames)
            url_rules = [Rule(path, endpoint=method, host=host) for path, method, host in url_tuples]
            JsonLoaderManager.url_rules += url_rules

        JsonLoaderManager.url_map = Map(JsonLoaderManager.url_rules)

    def get_remote_json(self, uri, **kwargs):
        splitted_url = urlparse.urlsplit(uri)
        scheme = splitted_url.scheme
        endpoint, args = self.url_map.bind(splitted_url.hostname).match(splitted_url.path)
        return endpoint(int(splitted_url.path.split('/')[2]))


class JsonProxy(JsonLoader):
    def __init__(self, *args, **kwargs):
        super(JsonProxy, self).__init__(*args, **kwargs)

    def get_remote_json(self, uri, **kwargs):
        json_manager = JsonLoaderManager()
        try:
            return json_manager.get_remote_json(uri, **kwargs)
        except NotFound, e:
            return super(JsonProxy, self).get_remote_json(uri, **kwargs)

    def create_references(self, data_structure):
        if isinstance(data_structure, dict) or isinstance(data_structure, list):
            referenced_data_structure = JsonRef.replace_refs(data_structure, loader=self)
            return referenced_data_structure
        return data_structure
