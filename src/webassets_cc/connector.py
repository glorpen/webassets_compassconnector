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

re_schema = re.compile(r'^(([a-z0-9]+://)|(//))')
re_app = re.compile(r'^@.*$')

def resolve_url(fun):
    def decorator(self, *args, **kwargs):
        ret = fun(self, *args, **kwargs)
        
        if not re_schema.match(ret) is None:
            return ret
        
        rel_path = ret.lstrip("/@")
        parts = rel_path.split("?",1)
        #parts[0] could be asset spec
        p = self.env.resolver.search_for_source(parts[0])
        p = realpath(p[0] if isinstance(p, list) else p)
        url = self.env.resolver.resolve_source_to_url(p, parts[0])
        parts[0] = url
        return "?".join(parts)
        
    return decorator

class Handler(object):
    
    INITIAL_FILE = "python::stdin.%s"
    
    initial_scss = INITIAL_FILE % "scss"
    initial_css = INITIAL_FILE % "css"
    
    vendor_path = None # /disk/path/to/dir/
    vendor_prefix = "/vendors" #http:// ....
    
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
    
    def filepath_to_dict(self, filepath):
        filepath = os.path.realpath(filepath)
        if not exists(filepath):
            return None
        
        self.deps.add(filepath)
        
        with open(filepath,"rb") as file:
            return self.file_to_dict(filepath, file.read())
    
    def get_file(self, path, type_, mode):
        if path == self.initial_scss:
            return self.file_to_dict(self.initial_scss, self.input, time.time())
        if path == self.initial_css:
            return None
        
        raise NotImplementedError()
    
    def put_file(self, path, type_, data, mode):
        data = base64.decodebytes(data.encode()).decode()
        
        if path == self.initial_css:
            self.output.write(data)
        else:
            raise NotImplementedError()
    
    """
    def get_url(self, path, type_, mode):
        return self.env.resolver.resolve_source_to_url(self.env.resolver.search_for_source(path))
    
    def get_file(self, path, type_, vendor):
        path = path.lstrip("/@")
        
        if type_ == "out_stylesheet": return None #input is from stdin
        
        if type_ in ("generated_image",):
            f = join(self.get_generated_images_root(), path)
        else:
            if vendor:
                f = self.env.resolver.search_for_source(self.vendors_path.lstrip("/")+"/"+type_+"s/"+path)
            else:
                f = self.env.resolver.search_for_source(path)
        
        f = f[0] if isinstance(f, list) else f
        
        return self.file_to_dict(f)
    
    def put_file(self, path, type_, data):
        
        if type_  == "sprite":
            p = join(self.get_generated_images_root(), path.lstrip("/"))
        elif type_  == "css":
            self.output.write(base64.decodebytes(data.encode()).decode())
            return True
        else:
            raise NotImplementedError(path, type_)
        
        os.makedirs(dirname(p), 0o777, True)
        with open(p,"wb") as f:
            f.write(base64.decodebytes(data.encode()))
        return True
    """
    def find_sprites_matching(self, path):
        r = re.compile(r'^.*?('+path.replace("*", ".*")+')$')
        return [r.match(p).group(1) for p in self.env.resolver.search_for_source(path.lstrip("/"))]
    
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
