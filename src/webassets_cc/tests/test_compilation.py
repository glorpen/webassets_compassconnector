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
        self.env.cache = False
        self.env.manifest = False
        
        self.env.append_path(res+"assets", "/")
        self.env.append_path(res+"vendor", "/vendors")
        
        self.env.append_path(res, None)
        
        self.env.config["compass_bin"] = "/home/arkus/.gem/ruby/1.9.1/bin/compass"
        self.env.config["vendor_path"] = "vendor"
        
        #logging.basicConfig(level=logging.DEBUG)
        
    def get_bundle_output(self, test_name):
        f = StringIO()
        js = Bundle('scss/%s.scss' % test_name, filters=CompassConnectorFilter, output='%s.css' % test_name)
        self.env.register(test_name, js)
        js.build(output=f)
        
        return f.getvalue()

    def test_simple(self):
        o = self.get_bundle_output("test_simple")
        self.assertIn("color: red;", o)
    
    def test_simple_import(self):
        o = self.get_bundle_output("test_simple_imports")
        self.assertIn("color: red;", o)
        self.assertIn("(style.css)", o)
        self.assertIn("(/style.css)", o)

    def test_fonts(self):
        o = self.get_bundle_output("test_fonts")
        
        self.assertIn("vendor-inline-font: url('data:font/truetype;base64,AAE", o)
        self.assertIn("app-inline-font: url('data:font/truetype;base64,AAE", o)
        
        self.assertIn("url('/this.eot?#iefix')", o)
        self.assertIn("src: url('/fonts/empty.ttf');", o)
        self.assertIn("src: url('/vendors/fonts/vendor_empty.ttf');", o)
    
    def test_images(self):
        o = self.get_bundle_output("test_images")
        
        self.assertIn("vendor-image-url: url('/vendors/images/vendor_1x1.png?", o)
        self.assertIn("app-image-url: url('/images/image.png?", o)
        self.assertIn("width-app: 10px;", o)
        self.assertIn("width-vendor: 10px;", o)
        self.assertIn("image-inline: url('data:image/png;base64,iVB", o)
        self.assertIn("vendor-generated-image-busted: url('/media-prefix/generated-images/1x1.png?", o)
        self.assertIn("vendor-generated-image: url('/media-prefix/generated-images/1x1.png');", o)
        self.assertIn("generated-image-busted: url('/media-prefix/generated-images/1x1.png?", o)
        self.assertIn("generated-image: url('/media-prefix/generated-images/1x1.png');", o)
        
    def test_sprites(self):
        o = self.get_bundle_output("test_sprites")
        
        self.assertIn("background: url('/media-prefix/generated-images/sprites/something-", o)
        self.assertIn("background: url('/media-prefix/generated-images/vendor-something-", o)

    def test_zurb(self):
        self.env.config["compass_plugins"] = {"zurb-foundation":"<99"}
        o = self.get_bundle_output("test_zurb")
        self.assertIn("body", o)
