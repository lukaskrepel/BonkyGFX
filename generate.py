import itertools
from typing import Optional, Union

from typeguard import typechecked

import grf

g = grf.NewGRF(
    grfid=b'TODO',
    name='BonkyGFX',
    description='BonkyGFX',
    min_compatible_version=0,
    version=0,
)


def replace_old(first_id, sprites):
    amount = len(sprites)
    g.add(grf.ReplaceOldSprites([(first_id, amount)]))
    g.add(*sprites)


def tmpl_groundtiles(png, y, **kw):
    func = lambda x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=grf.ZOOM_2X, **kw)
    x, z = 0, 2
    return [
        func(1 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(81 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(161 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(241 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),

        func(321 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(399 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(479 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(559 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),

        func(639 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(719 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(799 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(879 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),

        func(959 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(1039 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(1119 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(1197 * z + x * z, z + y * z, 64 * z, 48 * z - 1, xofs=-31 * z, yofs=-16 * z, **kw),

        func(1277 * z + x * z, z + y * z, 64 * z, 16 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func(1357 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func(1437 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
    ]


# Terrain: Single flat tile
def tmpl_flattile_single(png, x, y, **kw):
    func = lambda x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=grf.ZOOM_2X, **kw)
    z = 2
    return [func(1 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0*z, **kw)]


# Normal land
temperate_ground_png = grf.ImageFile('sprites/temperate_groundtiles_32bpp.png', colourkey=(0, 0, 255))
replace_old(3924, tmpl_groundtiles(temperate_ground_png, 144))  # 0% grass
replace_old(3943, tmpl_groundtiles(temperate_ground_png, 96))   # 33% grass
replace_old(3962, tmpl_groundtiles(temperate_ground_png, 48))   # 66% grass
replace_old(3981, tmpl_groundtiles(temperate_ground_png, 0))    # 100% grass

general_concrete_png = grf.ImageFile('sprites/general_concretetiles_32bpp.png', colourkey=(0, 0, 255))
replace_old(1420, tmpl_flattile_single(general_concrete_png, 0, 0))


def tmpl_vehicle_road_8view(png, x, y, **kw):
    # Same spriteset template as in OpenGFX2
    func = lambda x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=grf.ZOOM_4X, **kw)
    z = 1
    return [
        func((1 + 0 + x * 174) * z, (1 + y * 24) * z, 8 * z, 23 * z, xofs=-3 * z, yofs=-15 * z, **kw),
        func((2 + 8 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-10 * z, **kw),
        func((3 + 30 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-15 * z, yofs=-9 * z, **kw),
        func((4 + 61 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-10 * z, **kw),
        func((5 + 83 + x * 174) * z, (1 + y * 24) * z, 8 * z, 23 * z, xofs=-3 * z, yofs=-15 * z, **kw),
        func((6 + 91 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-10 * z, **kw),
        func((7 + 113 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-15 * z, yofs=-9 * z, **kw),
        func((8 + 144 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-10 * z, **kw),
    ]

def replace_rv_generation(file, generation):
    png = grf.ImageFile(file, colourkey=(0, 0, 255))
    # base_graphics spr3284(3284, "../graphics/vehicles/64/road_buses_8bpp.png") { template_vehicle_road_8view(0, 0, 1) } // bus
    o = {1: 0, 2: -192, 3: 192}[generation]
    replace_old(3292 + o, tmpl_vehicle_road_8view(png, 0, 0))  # coal unloaded
    replace_old(3300 + o, tmpl_vehicle_road_8view(png, 0, 1))  # mail
    replace_old(3308 + o, tmpl_vehicle_road_8view(png, 0, 2))  # oil
    replace_old(3316 + o, tmpl_vehicle_road_8view(png, 0, 3))  # livestock
    replace_old(3324 + o, tmpl_vehicle_road_8view(png, 0, 4))  # goods
    replace_old(3332 + o, tmpl_vehicle_road_8view(png, 0, 5))  # food
    replace_old(3340 + o, tmpl_vehicle_road_8view(png, 0, 6))  # grain unloaded
    replace_old(3348 + o, tmpl_vehicle_road_8view(png, 0, 7))  # wood unloaded
    replace_old(3356 + o, tmpl_vehicle_road_8view(png, 0, 8))  # steel/paper unloaded
    replace_old(3364 + o, tmpl_vehicle_road_8view(png, 0, 9))  # iron/copper ore unloaded
    replace_old(3372 + o, tmpl_vehicle_road_8view(png, 0, 10))  # armoured
    replace_old(3380 + o, tmpl_vehicle_road_8view(png, 1, 0))  # coal loaded
    replace_old(3388 + o, tmpl_vehicle_road_8view(png, 1, 6))  # grain loaded
    replace_old(3396 + o, tmpl_vehicle_road_8view(png, 1, 7))  # wood loaded
    replace_old(3404 + o, tmpl_vehicle_road_8view(png, 1, 8))  # steel loaded
    replace_old(3412 + o, tmpl_vehicle_road_8view(png, 1, 9))  # iron ore loaded
    replace_old(3420 + o, tmpl_vehicle_road_8view(png, 2, 8))  # paper loaded
    replace_old(3428 + o, tmpl_vehicle_road_8view(png, 2, 9))  # copper ore loaded
    replace_old(3436 + o, tmpl_vehicle_road_8view(png, 0, 11))  # water
    replace_old(3444 + o, tmpl_vehicle_road_8view(png, 0, 12))  # fruit unloaded
    replace_old(3452 + o, tmpl_vehicle_road_8view(png, 0, 13))  # rubber unloaded
    replace_old(3460 + o, tmpl_vehicle_road_8view(png, 1, 12))  # fruit loaded
    replace_old(3468 + o, tmpl_vehicle_road_8view(png, 1, 13))  # rubber loaded


replace_rv_generation('sprites/road_lorries_firstgeneration_32bpp.png', 1)
replace_rv_generation('sprites/road_lorries_secondgeneration_32bpp.png', 2)
replace_rv_generation('sprites/road_lorries_thirdgeneration_32bpp.png', 3)

grf.main(g, 'bonkygfx.grf')
