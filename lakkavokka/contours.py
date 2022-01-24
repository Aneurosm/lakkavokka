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

from shapely.geometry import Point, LineString, box
from shapely.ops import transform, linemerge

import pyproj
import numpy as np
import cv2 as cv
import scipy.interpolate as si

from bs4 import Tag

from lakkavokka.global_mercator import GlobalMercator

tile_size = 256

"""
Remove self-intersections from the LineString
"""
def remove_self_intersaction(ls:LineString) -> LineString:
    assert type(ls) is LineString

    #pass 1
    cache = {}
    for i, p in enumerate(ls.coords[:-1]):
        cache.setdefault(p, []).append(i)

    #pass 2
    coords = []
    i = 0
    while i < len(ls.coords):
        p = ls.coords[i]
        if p in cache:
            max_pos = max(cache[p])
        else:
            max_pos = i

        if max_pos > i:
            i = max_pos + 1
        else:
            i += 1

        coords.append(p)
    return LineString(coords)


"""
Remove contour parts intersecting bbox
"""
def split_contour_inside_bbox(contour, bbox):
    segments = []
    buffer = []
    contour = contour.tolist()
    for x, y in contour + [contour[0]]:
        p = Point(x, y)

        if bbox.contains(p):
            if len(buffer) > 1:
                segments.append(LineString(buffer))
                buffer = []
        else:
            buffer.append(p)

    #Add last buffer
    if len(buffer) > 1:
        segments.append(LineString(buffer))

    #Merge connected segments
    mls = linemerge(segments)
    if type(mls) == LineString:
        return [mls]
    else:
        return mls.geoms

def generateTilesPatch(zoom:int, x:int, y:int, offset:int):
    rows = []

    for yy in range(y - offset, y + offset + 1):
        rows.append(list([(zoom, xx, yy) for xx in range(x - offset, x + offset + 1)]))

    return rows

def load_mask(zoom, x, y, offset, loadFunc):
    tiles = generateTilesPatch(zoom, x, y, offset)

    rows = []
    for row in tiles:
        images = list(map(lambda t: loadFunc(*t), row))
        rows.append(np.concatenate(images, 1))

    return np.concatenate(rows, 0)

def rgb2mask(rgb):
    assert len(rgb.shape) == 3
    height, width, ch = rgb.shape
    assert ch == 3

    binary_mask = (rgb[:,:,0] == 255) & (rgb[:,:,1] == 255) & (rgb[:,:,2] == 0)

    flat = np.reshape(rgb, (height * width, ch))
    colors = np.unique(flat, axis=0)

    mask = np.zeros((width, height), dtype=np.uint8)

    for index, color in enumerate(colors):
        feature_mask = np.where(np.all(rgb == color, axis = 2))
        mask[feature_mask] = index

    return mask

def translate_line_string(zoom, container, id, ls, proj, offset_x, offset_y, width, height, tags):
    cache = {}
    nodes = []
    for px, py in ls.coords:
        py = 0.5 + height - py
        px = 0.5 + px
        px += offset_x
        py += offset_y

        mx, my = proj.PixelsToMeters(px, py, zoom)
        lat, lon = proj.MetersToLatLon(mx, my)

        if (lat, lon) in cache:
            nodes.append(cache[(lat, lon)])
        else:
            nodes.append(id)
            cache[(lat, lon)] = id
            id -= 1
            container.append(Tag(name="node", attrs={
                "id": nodes[-1],
                "lat": lat,
                "lon": lon,
                "version": 1
            }))

    way = Tag(name="way", attrs={
        "id": id,
        "version": 1
    })
    id -= 1

    for k, v in tags.items():
        way.append(Tag(name="tag", attrs={'k': k, 'v': v}))

    for node in nodes:
        way.append(Tag(name="nd", attrs={
            "ref": node
        }))

    container.append(way)
    return id

def find_single_contour(zoom, tx, ty, click_x, click_y, offset, loadFunc, simplify_tolerance_factor=0, tags={}):
    proj = GlobalMercator()

    rgb = load_mask(zoom, tx, (2**zoom - 1) - ty, offset, loadFunc)

    mask = rgb2mask(rgb[:,:,0:3])

    bbox = box(0, 0, mask.shape[0] - 1, mask.shape[1] - 1).boundary

    mask = (mask == mask[click_x, click_y]).astype(np.uint8)

    contours, hierarchy = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)

    regions = map(lambda ix: {
            'idx': ix[0],
            'area': cv.contourArea(ix[1]),
            'dist': cv.pointPolygonTest(ix[1], (click_x, click_y), True)
        }, enumerate(contours))

    regions = filter(lambda cnt: cnt['area'] > 0, regions)

    # Find nearest click point
    regions = sorted(regions, key=lambda r: abs(r['dist']))

    osm = Tag(name='osm', attrs={"version": "0.6"})

    id = -1
    for region in regions:
        contour = np.array(contours[region['idx']])
        contour = np.squeeze(contour, 1)

        line_strings = split_contour_inside_bbox(contour, bbox)
        ls = min(line_strings, key=lambda ls: ls.distance(Point(click_x, click_y)))

        if not ls.is_simple:
            ls = remove_self_intersaction(ls)

        closedWay = ls.is_ring
        contour = np.array(ls.coords)
        if len(contour) <=3:
            continue

        approxination_rate = 5
        tck, u = si.splprep(contour.transpose(), s=approxination_rate)
        splined_contour = si.splev(u, tck)
        contour = np.array(splined_contour).transpose()

        #Preserve topolgy
        if closedWay:
            contour = np.concatenate([contour, [contour[0]]])
        ls = LineString(contour)

        if simplify_tolerance_factor:
            ls = ls.simplify(simplify_tolerance_factor)

        id = translate_line_string(zoom, osm, id, ls, proj, tile_size * (tx - offset), tile_size * (ty - offset), mask.shape[0] - 1, mask.shape[1] - 1, tags)
        break
    return osm

def prepare_tags(tags):
    result = {}
    for pair in tags.split(","):
        if '=' not in pair:
            continue
        k, v = pair.split("=")
        result[k.strip()] = v.strip()
    return result
