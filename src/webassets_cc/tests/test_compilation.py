# -*- coding: utf-8 -*-
'''
Created on 18-06-2013

@author: Arkadiusz Dzięgiel
'''

from webassets import Environment, Bundle
from webassets_cc.filter import CompassConnectorFilter
from os.path import dirname
import unittest
from io import StringIO
import logging

class TestCompilation(unittest.TestCase):
    
    def setUp(self):
        res = dirname(__file__)+'/resources/'
        self.env = Environment(dirname(__file__)+"/out", '/media-prefix')
        
        self.env.append_path(res+"assets", "assets")
        self.env.append_path(res+"vendor", "vendors")
        self.env.append_path(res, None)
        
        self.env.config["compass_bin"] = "/home/arkus/.gem/ruby/1.9.1/bin/compass"
        self.env.config["vendor_path"] = res+"vendor"
        self.env.config["vendor_prefix"] = "vendors"
        
        logging.basicConfig(level=logging.DEBUG)
        
    def get_bundle_output(self, test_name):
        f = StringIO()
        js = Bundle('scss/%s.scss' % test_name, filters=CompassConnectorFilter, output='%s.css' % test_name)
        self.env.register(test_name, js)
        js.build(output=f)
        
        return f.getvalue()
    
    def test_simple(self):
        o = self.get_bundle_output("test_simple")
        self.assertIn("color: red;", o)
