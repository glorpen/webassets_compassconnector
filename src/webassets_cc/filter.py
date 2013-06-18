# -*- coding: utf-8 -*-
'''
Created on 11-05-2013

@author: Arkadiusz Dzięgiel
'''

from webassets.filter import Filter, option
from webassets.exceptions import FilterError
from webassets_cc import connector

class CompassConnectorFilter(Filter):
	name = 'compassconnector'
	max_debug_level = None

	options = {
		'compass': ('binary', 'COMPASS_BIN'),
		'plugins': option('COMPASS_PLUGINS', type=list),
		'config': 'COMPASS_CONFIG',
	}
	
	depends = None
	
	def find_dependencies(self):
		return self.depends
	
	def output(self, _in, out, **kwargs):
		h = connector.Handler(self.env, _in, out, self.plugins if self.plugins else {})
		if not self.compass:
			raise FilterError("Compass bin path is not set")
		h.start(self.compass)
		
		self.depends = h.deps
