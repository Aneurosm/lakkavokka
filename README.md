
**Lakkavokka** is a JOSM plugin for digitizing indexed color
images in a controlled manner. This tool is useful for semi-automated imports in
ML/AI mapping pipelines.

Usage
=====

The following steps requires you have JSOM ext_tools plugin installed.

0. Make sure you have Python >3.8 and Pip installed:

```
$ python3 --version
Python 3.8.10

$ python3 -m pip --version
pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)
```

1. Install Lakkavokka:

```
python3 -m pip install lakkavokka
```

2. Setup external script in JOSM

Use `Lakkavokka` as a name and
`lakkavokka --lat {lat} --lon {lon} --zoom 16 --source /path/to/tiles/{zoom}/{x}/{y}.png`
as a command line.

Now, you can open your area in JOSM, enable Lakkavokka tool and click on the map.
Lakkavokka will load the area around the clicked point and build a way nearest
to the point. It doesn't matter if you click inside or outside the colored area.
If the area is small enough, the way will be automatically closed. Otherwise,
you can combine those line to the multipolygon later.


Command line options
--------------------
`--source` TMS tiles source, can be either a file path template
or URL template. Variables {zoom}, {x}, and {y} will be automatically
substituted to tile coordinates

`--buffer` number of tiles around the clicked point to be loaded. Increasing
this value will significantly increase required RAM and calculation time.
You can adjust this setting according to your data. Most useful values are
from 1 (default) to 3.

`--simplify-factor` simplification factor for the resulting geometry.
You should adjust this setting according to your data if you're getting
too many points or too coarse geometry.


`--tags` comma-separated list of tags to be added to generated ways. It's a
good idea to add `source` tag to indicate other mappers that is an automated or
semi-automated load of data.

`--lat` and `--lon` latitude and longitude of a clicked point

`--zoom` zoom of tiles will be processed. It may be different from
the zoom level in JOSM but it should always match the best zoom of tiles.

Example workflow
----------------

1. Download data/8323903.tar.gz from this repository. This file contains
forest overlay for a random rural area in Bashkortostan republic, Russia.
2. Extract this file somewhere
3. Enter the 8323903 directory and run `python3 -m http.server 9000` you
could skip this step and point `--source` parameter to the directory itself,
but it is more convenient to be able to see the data in JOSM
4. Open JOSM and add image layer, type TMS, URL `tms[16,16]:http://localhost:9000/{z}/{x}/{y}.png`
5. Download area around `https://www.openstreetmap.org/#map=14/52.3410/57.8839` in JOSM and enable recently added layer
6. Setup lakkavokka as described earlier. If you're using http.server you can omit `--source` parameter.
