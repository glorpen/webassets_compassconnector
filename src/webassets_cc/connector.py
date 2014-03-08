#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: Arkadiusz Dzięgiel
"""

from os.path import dirname
import os, re, base64, hashlib, json
import subprocess
import time
import types
import logging

try:
    base64_encode = base64.encodebytes
    base64_decode = base64.decodebytes
except:
    base64_encode = base64.encodestring
    base64_decode = base64.decodestring
    

class Handler(object):
    
    TYPE_GENERATED_IMAGE = 'generated_image'
    
    MODE_ABSOLUTE = 'absolute'
    MODE_APP = 'app'
    MODE_VENDOR = 'vendor'
    
    INITIAL_FILE = "python::stdin.%s"
    
    initial_scss = INITIAL_FILE % "scss"
    initial_css = INITIAL_FILE % "css"
    
    vendor_path = "vendor" # prefix webasset vendor dir
    vendor_dirs = {
        "font": "fonts",
        "image": "images",
    }
    generated_dir = "generated-images"
    
    api_version = 4
    
    def __init__(self, env, in_, out, plugins=[], imports=[], source=None):
        
        self.env = env
        self.plugins = plugins
        self.imports = imports
        
        self.logger = logging.getLogger(__name__)
        
        self.input = in_.getvalue().encode()
        self.output = out
        self.source = source
        
        self.deps = set()
    
    def get_configuration(self):
        c = {
            "environment" : ":development",
            "line_comments": True,
            "output_style" : ":expanded", #nested, expanded, compact, compressed
            
            "generated_images_path" : "/",
            "css_path" : "/dev/null",
            "sass_path" : "/dev/null",
            "plugins" : self.plugins,
            "imports" : self.imports
        }
        return c
    
    def file_to_dict(self, filepath, data, mtime=None):
        return {"mtime":mtime if mtime else os.path.getmtime(filepath), "data": base64_encode(data).decode(), "hash": hashlib.md5(filepath.encode()).hexdigest(), "ext": os.path.splitext(filepath)[1][1:]}
    
    def get_path(self, path, mode, type_=None):
        
        if mode == self.MODE_ABSOLUTE:
            raise ValueError("Resolving url absolute paths is not supported")
        
        if type_ == self.TYPE_GENERATED_IMAGE:
            return self.env.resolver.resolve_output_to_path("/".join([self.generated_dir, path]), self.source)
        else:
            filepath = "/".join([self.vendor_path, self.vendor_dirs[type_], path]) if mode == self.MODE_VENDOR else path
            try:
                ret = self.env.resolver.search_for_source(filepath)
                return ret[0] if isinstance(ret, list) else ret
            except OSError:
                return None
    
    def filepath_to_dict(self, filepath, mode, type_=None):
        filepath = self.get_path(filepath, mode, type_)
        
        self.logger.debug("Trying path %s", filepath)
        
        if filepath is None or not os.path.exists(filepath):
            return None
        
        self.deps.add(filepath)
        with open(filepath,"rb") as file:
            return self.file_to_dict(filepath, file.read())
    
    def get_file(self, path, type_, mode):
        if path == self.initial_scss:
            return self.file_to_dict(self.initial_scss, self.input, time.time())
        if path == self.initial_css:
            return None
        
        return self.filepath_to_dict(path, mode, type_)
    
    def put_file(self, path, type_, data, mode):
        if not isinstance(data, bytes):
            data = data.encode()
        data = base64_decode(data)
        
        if path == self.initial_css:
            self.output.write(data.decode())
        else:
            p = self.get_path(path, mode, type_)
            self.logger.info("Writting to file %s", p)
            os.makedirs(dirname(p), 0o777, True)
            with open(p, "wb") as f:
                f.write(data)
    
    def get_url(self, path, type_, mode):
        
        if mode == self.MODE_ABSOLUTE:
            return path
        
        parts = path.split("?",1)
        p = self.get_path(parts[0], mode, type_)
        if p is None:
            raise Exception("Source %s not found" % parts[0]);
        
        parts[0] = self.env.resolver.resolve_source_to_url(p, self.source)
        return "?".join(parts)
        
    def find_sprites_matching(self, path, mode):
        if mode == self.MODE_VENDOR:
            path = "/".join([self.vendor_path, self.vendor_dirs["image"], path])
        
        r = re.compile(r'^.*?('+path.replace("*", ".*")+')$')
        return ["@"+r.match(p).group(1) for p in self.env.resolver.search_for_source(path.lstrip("/"))]
    
    def run(self, proc):
        decoder = json.JSONDecoder()
        encoder = json.JSONEncoder()
        bracet = re.compile(br'^(\x1b\x5b[0-9]{1,2}m?)?({.*)$')
        while True:
            line = proc.stdout.readline()
            if not line: break
            
            m = bracet.match(line)
            if m:
                d = decoder.decode(m.group(2).decode())
                
                self.logger.debug("running %s with: %s", d["method"], ", ".join([(a if len(a)<40 else a[0:20]+"...") for a in d["args"]]))
                
                m = getattr(self, d["method"])
                ret = m(*d["args"]) if isinstance(m, types.MethodType) else m
                    
                self.logger.debug("return %s", ret)
                proc.stdin.write(encoder.encode(ret).encode() + b"\n")
                proc.stdin.flush()
            else:
                self.logger.info(line.decode().strip())

    def start(self, compass_bin):
        command = [compass_bin,'compile','--trace','-r','compass-connector']
        for i in self.plugins:
            command.extend(("-r", i))
        command.append("@%s" % (self.INITIAL_FILE % "scss"))

        proc = subprocess.Popen(command,
            cwd = self.env.directory,
            stdout = subprocess.PIPE,
            stdin = subprocess.PIPE,
            env = {
                "HOME": os.environ["HOME"]
            })
            
        self.run(proc)
        proc.wait()
