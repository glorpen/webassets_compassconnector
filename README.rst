==========================
Webassets CompassConnector
==========================

Seamless integration with Compass for Python apps.

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

- app: looks like ``@public/images/asset.png``
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