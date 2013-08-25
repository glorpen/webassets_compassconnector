# -*- coding: utf-8 -*-
'''
Created on 11-05-2013

@author: Arkadiusz Dzięgiel
'''

from webassets.filter import Filter, option
from webassets.exceptions import FilterError
from webassets_cc import connector

try:
    from webassets.utils import hash_func
except ImportError:
    from webassets.cache import make_md5 as hash_func

class CompassConnectorFilter(Filter):
    name = 'compassconnector'
    max_debug_level = None

    options = {
        'compass': ('binary', 'COMPASS_BIN'),
        'plugins': option('COMPASS_PLUGINS', type=list),
        'vendor_path': ('relative path', 'VENDOR_PATH'),
    }
    
    depends = None
    
    def find_dependencies(self):
        return self.depends

    def unique(self):
        hash_func(self.plugins)

    def input(self, in_, out, **kwargs):
        h = connector.Handler(self.env, in_, out, self.plugins if self.plugins else {}, kwargs["source"])
        h.vendor_path = self.vendor_path
        if not self.compass:
            raise FilterError("Compass bin path is not set")
        h.start(self.compass)
        
        self.depends = h.deps
