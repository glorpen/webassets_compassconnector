==========================
Webassets CompassConnector
==========================

Seamless integration with Compass for Python3 apps.

For full blown experience you have to use webassets with patches from https://github.com/miracle2k/webassets/pull/240 and https://github.com/miracle2k/webassets/pull/241 .
Especially if you're using Python3.3. Alternatively you can install webassets fork from https://github.com/glorpen/webassets (branch ``mymaster``).

Using unpatched version can result in bad dependency traacking (parent asset may not compile even if child has changed).

What problems is it solving?
============================

- adds load_path namespace for compass files - so you can do cross app imports or use assets from other packages
- you don't need already installed assets - connector uses files for you packages 
- assets recompiling/updating when any of its dependencies are modified - be it another import, inlined font file or just ``width: image-width(@path/myimage.png);``

How to install
==============

- firstly you need to install ruby connector gem:

.. sourcecode:: bash

   gem install compass-connector

- then install filter:

.. sourcecode:: bash

   pip install webassets_compassconnector

Virtual Paths
=============

There are three kind of "paths":

- app, starts with an ``@`` and may look like ``@public/images/asset.png``
- vendor: a relative path, should be used only by compass plugins (eg. zurb-foundation, blueprint)
- absolute path: starts with ``/``, ``http://`` etc. and will NOT be changed by connector

Some examples:

.. sourcecode:: css

   @import "@package/scss/settings"; /* will resolve to eg. .../package/scss/_settings.scss */
   @import "foundation"; /* will include foundation scss from your compass instalation */
   
   width: image-size("@package/public/images/my.png");
   background-image: image-url("@package/public/images/my.png"); // will generate url with prefixes given by Webassets
   @import "@package/sprites/*.png"; // will import sprites located in package/sprites/ (generated url will be with applied Webasset prefixes)


Usage
=====

Standalone example:

.. sourcecode:: python

   from webassets import Environment, Bundle
   from webassets_cc.filter import CompassConnectorFilter
   
   env = Environment("/some/path/out", '/media-prefix')
   
   env.config["compass_bin"] = "/path/to/compass/bin"
   env.config["vendor_path"] = "vendor" #it is relative path prepended in vendor urls 
   
   env.append_path("/some/path/assets", "/")
   env.append_path("/some/path/vendors", "/vendors")
   
   scss = Bundle('scss/my.scss', filters=CompassConnectorFilter, output='my.css')
   
With Webassets, Pyramid and Jinja2:

.. sourcecode:: python

   config = Configurator()
   config.include('pyramid_jinja2')
   
   config.add_settings({"webassets.base_dir": join(root_dir, "cache", "assets"),"webassets.base_url":"/static"})
   config.include('pyramid_webassets')
   
   config.add_route('show', '/')
   config.add_static_view(name='static', path=join(root_dir, "cache", "assets"))
   
   scss = Bundle('package:resources/assets/app.scss', filters=CompassConnectorFilter, output='app.css')
   config.add_webasset('styles', scss)
   
   config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
   assets_env = config.get_webassets_env()
   assets_env.config["compass_bin"] = "/home/user/.gem/ruby/1.9.1/bin/compass"
   assets_env.config["compass_plugins"] = {"zurb-foundation":">4"}
   config.get_jinja2_environment().assets_environment = assets_env
