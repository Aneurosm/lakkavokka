################################################################################
# Copyright (c) 2021 Miroff
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################
from optparse import OptionParser

from lakkavokka.contours import find_single_contour, prepare_tags
from lakkavokka.global_mercator import GlobalMercator
from lakkavokka.load import loadFromDisk, downloadTile

def get_args():
    usage = "usage: %prog [options] --lat <latitude> --lon <longitude>"
    parser = OptionParser(usage=usage)

    parser.add_option('-b', '--buffer', dest='buffer',
                      default=1, type='int',
                      help='Buffer size arout the click point in tile. --b 1 means that 3x3 tile block will be analyzed')

    parser.add_option('-z', '--zoom', dest='zoom',
                      default=16, type='int',
                      help="Pretrained model zoom level")

    parser.add_option('-s', '--simplify-factor', dest='simplify_tolerance_factor',
                      default=2, type='float',
                      help="Pretrained model zoom level")

    parser.add_option('-t', '--tags', dest='tags',
                      default='', type='str',
                      help="Comma-separated list of tags for the new objects")

    parser.add_option('--source', dest='source',
                      default='http://localhost:9000/{zoom}/{x}/{y}.png', type='str',
                      help="TMS tiles source. Can be either an URL of a path. See README about variable substitution")

    parser.add_option('--lat', dest='lat',
                      type='float',
                      help="Latitude in decimal form (48.1234)")

    parser.add_option('--lon', dest='lon',
                      type='float',
                      help="Longituse in decimal form (35.1234)")

    (options, args) = parser.parse_args()

    if not options.lat or not options.lon:
        parser.print_usage()
        print('--lat and --lon options are required')
        exit(-1)

    return options

def main(argv=None):
    args = get_args()

    zoom = args.zoom
    offset = args.buffer
    tile_size = 256


    tags = prepare_tags(args.tags)

    proj = GlobalMercator()
    mx, my = proj.LatLonToMeters(args.lat, args.lon)
    tx, ty = proj.MetersToTile(mx, my, zoom)
    px, py = proj.MetersToPixels(mx, my, zoom)
    click_x, click_y = int(px - tile_size * (tx - offset)), int(py - tile_size * (ty - offset))
    click_y = tile_size * (2 * offset + 1) - click_y

    if '://' in args.source:
        loadFunc = lambda zoom, x, y: downloadTile(zoom, x, y, args.source)
    else:
        loadFunc = lambda zoom, x, y: loadFromDisk(zoom, x, y, args.source)

    osm = find_single_contour(zoom, tx, ty, click_x, click_y, offset, loadFunc, args.simplify_tolerance_factor, tags)

    print(osm.prettify())
