#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: Arkadiusz Dzięgiel
"""

from os.path import dirname,realpath,exists,join
import os, sys, re, base64, hashlib, json
import subprocess
import time
import types
import logging

class Handler(object):
    
    INITIAL_FILE = "python::stdin.%s"
    
    initial_scss = INITIAL_FILE % "scss"
    initial_css = INITIAL_FILE % "css"
    
    vendor_path = "vendor" # prefix webasset vendor dir
    vendor_dirs = {
        "font": "fonts",
        "image": "images",
    }
    generated_dir = "generated-images"
    
    api_version = 2
    
    def __init__(self, env, in_, out, plugins=[]):
        
        self.env = env
        self.plugins = plugins
        
        self.logger = logging.getLogger(__name__)
        
        self.input = in_.getvalue().encode()
        self.output = out
        
        self.deps = set()
    
    def get_configuration(self):
        c = {
            "environment" : ":development",
            "line_comments": True,
            "output_style" : ":expanded", #nested, expanded, compact, compressed
            
            "generated_images_path" : "/",
            "css_path" : "/dev/null",
            "sass_path" : "/dev/null",
            "plugins" : self.plugins
        }
        return c
    
    def file_to_dict(self, filepath, data, mtime=None):
        return {"mtime":mtime if mtime else os.path.getmtime(filepath), "data": base64.encodebytes(data).decode(), "hash": hashlib.md5(filepath.encode()).hexdigest(), "ext": os.path.splitext(filepath)[1][1:]}
    
    def get_path(self, path, is_vendor, type_=None):
        
        if type_ == "generated_image":
            return self.env.resolver.resolve_output_to_path("/".join([self.generated_dir, path]), None)
        else:
            filepath = "/".join([self.vendor_path, self.vendor_dirs[type_], path]) if is_vendor else path
            try:
                ret = self.env.resolver.search_for_source(filepath)
                return ret[0] if isinstance(ret, list) else ret
            except OSError:
                return None
    
    def filepath_to_dict(self, filepath, is_vendor=False, type_=None):
        filepath = self.get_path(filepath, is_vendor, type_)
        self.deps.add(filepath)
        
        self.logger.debug("Trying path %s", filepath)
        
        if filepath is None or not os.path.exists(filepath):
            return None
        with open(filepath,"rb") as file:
            return self.file_to_dict(filepath, file.read())
    
    def get_file(self, path, type_, mode):
        if path == self.initial_scss:
            return self.file_to_dict(self.initial_scss, self.input, time.time())
        if path == self.initial_css:
            return None
        
        return self.filepath_to_dict(path, mode == "vendor", type_)
    
    def put_file(self, path, type_, data, mode):
        if not isinstance(data, bytes):
            data = data.encode()
        data = base64.decodebytes(data)
        
        if path == self.initial_css:
            self.output.write(data.decode())
        else:
            p = self.get_path(path, mode=="vendor", type_)
            self.logger.info("Writting to file %s", p)
            os.makedirs(dirname(p), 0o777, True)
            with open(p, "wb") as f:
                f.write(data)
    
    def get_url(self, path, type_, mode):
        is_vendor = mode == "vendor"
        
        parts = path.split("?",1)
        p = self.get_path(parts[0], is_vendor, type_)
        if p is None:
            raise Exception("Source %s not found" % parts[0]);
        
        parts[0] = self.env.resolver.resolve_source_to_url(p, None)
        return "?".join(parts)
        
    def find_sprites_matching(self, path, mode):
        if mode == "vendor":
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

        with subprocess.Popen(command,
            cwd = self.env.directory,
            stdout = subprocess.PIPE,
            stdin = subprocess.PIPE,
            env = {
                "HOME": os.environ["HOME"]
            }) as proc:
            
            self.run(proc)
