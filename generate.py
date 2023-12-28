import itertools
from typing import Optional, Union

from typeguard import typechecked

import grf

import lib


g = grf.NewGRF(
    grfid=b'TODO',
    name='BonkyGFX',
    description='BonkyGFX',
    min_compatible_version=0,
    version=0,
)

def zoom_to_factor(zoom):
    return {
        grf.ZOOM_NORMAL: 1,
        grf.ZOOM_2X: 2,
        grf.ZOOM_4X: 4,
    }[zoom]


def replace_old(first_id, sprites):
    if isinstance(sprites, (grf.Resource, grf.ResourceAction)):
        sprites = [sprites]
    amount = len(sprites)
    g.add(grf.ReplaceOldSprites([(first_id, amount)]))
    g.add(*sprites)


def tmpl_groundtiles(name, imgfile, y, zoom, **kw):
    z = zoom_to_factor(zoom)
    func = lambda i, x, y, *args, **kw: grf.FileSprite(imgfile, x, y, *args, zoom=zoom, name=f'{name}_{i}_{z}x', **kw)
    x = 0
    return [
        func('FLAT', 1 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('W', 81 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('S', 161 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('SW', 241 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),

        func('E', 321 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('EW', 399 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('SE', 479 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('WSE', 559 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),

        func('N', 639 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('NW', 719 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('NS', 799 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('NWS', 879 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),

        func('NE', 959 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('ENW', 1039 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('SEN', 1119 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('STEEP_N', 1197 * z + x * z, z + y * z, 64 * z, 48 * z - 1, xofs=-31 * z, yofs=-16 * z, **kw),

        func('STEEP_S', 1277 * z + x * z, z + y * z, 64 * z, 16 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('STEEP_W', 1357 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('STEEP_E', 1437 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
    ]


def tmpl_groundtiles_extra(name, imgfile, zoom, **kw):
    func = lambda i, x, y, *args, **kw: grf.FileSprite(imgfile, x, y, *args, zoom=zoom, name=f'{name}_{i}_{z}x', **kw)
    z = zoom_to_factor(zoom)
    x, y = 0, 0
    return tmpl_groundtiles(name, imgfile, y, zoom, **kw) + [
        func('EXTRA1', 1502 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('EXTRA2', 1567 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('EXTRA3', 1632 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('EXTRA4', 1697 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
    ]


def zip_alternative(*sequences):
    res = []
    for sprites in zip(*sequences):
        res.append(grf.AlternativeSprites(*sprites))
    return res

# Terrain: Single flat tile
# def tmpl_flattile_single(png, x, y, **kw):
#     func = lambda x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=grf.ZOOM_2X, **kw)
#     z = 2
#     return [func(1 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0*z, **kw)]

def make_groundtile_sprites(name, img_1x, img_2x, tmpl_y):
    return zip_alternative(
        tmpl_groundtiles(name, img_1x, tmpl_y, grf.ZOOM_NORMAL),
        tmpl_groundtiles(name, img_2x, tmpl_y, grf.ZOOM_2X),
    )

# Normal land
ase_temperate_ground_1x = lib.AseImageFile('sprites/terrain/temperate_groundtiles_32bpp_1x.ase', colourkey=(0, 0, 255))
ase_temperate_ground_2x = lib.AseImageFile('sprites/terrain/temperate_groundtiles_32bpp.ase', colourkey=(0, 0, 255))
temperate_ground_1x = tmpl_groundtiles('temperate_ground', ase_temperate_ground_1x, 0, grf.ZOOM_NORMAL)
temperate_ground_2x = tmpl_groundtiles('temperate_ground', ase_temperate_ground_2x, 0, grf.ZOOM_2X)
replace_old(3924, make_groundtile_sprites('temperate_ground_bare', ase_temperate_ground_1x, ase_temperate_ground_2x, 144))  # 0% grass
replace_old(3943, make_groundtile_sprites('temperate_ground_33', ase_temperate_ground_1x, ase_temperate_ground_2x, 96))   # 33% grass
replace_old(3962, make_groundtile_sprites('temperate_ground_66', ase_temperate_ground_1x, ase_temperate_ground_2x, 48))   # 66% grass
replace_old(3981, zip_alternative(temperate_ground_1x, temperate_ground_2x))    # 100% grass

ase = lib.AseImageFile('sprites/terrain/temperate_groundtiles_rough_32bpp.ase', colourkey=(0, 0, 255))
replace_old(4000, tmpl_groundtiles_extra('temperate_rough', ase, grf.ZOOM_2X))
ase = lib.AseImageFile('sprites/terrain/temperate_groundtiles_rocks_32bpp.ase', colourkey=(0, 0, 255))
replace_old(4023, tmpl_groundtiles('temperate_rocks', ase, 0, grf.ZOOM_2X))

general_concrete_png = lib.AseImageFile('sprites/terrain/general_concretetiles_32bpp.ase', colourkey=(0, 0, 255))
general_concrete = tmpl_groundtiles('general_concrete', general_concrete_png, 0, grf.ZOOM_2X)
replace_old(1420, general_concrete[0])


# Infrastructure: road tiles
def tmpl_roadtiles(png, x, y, z, **kw):
    func = lambda i, x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=grf.ZOOM_2X, name=f'road_{i}', **kw)
    return [
        func('Y', 1 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('X', 66 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('FULL', 131 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('T_Y_NE', 196 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('T_X_NW', 261 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('T_Y_SW', 326 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('T_X_SE', 391 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('W', 456 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('N', 521 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('E', 586 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('S', 651 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),

        func('NE', 846 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('SE', 911 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('SW', 716 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('NW', 781 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),

        func('SLOPE_NE', 976 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
        func('SLOPE_SE', 1041 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('SLOPE_SW', 1106 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z, **kw),
        func('SLOPE_NW', 1171 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z, **kw),
    ]


def make_infra_overlay_sprites(ground, infra):
    GROUND_INFRA_RANGES = (
        ([0] * 11, range(11)),
        ((12, 6, 3, 9), range(15, 19)),
        ([0] * 4, range(11, 15)),
    )
    return [
        lib.CompositeSprite((ground[i], infra[j]), name='{ground[i].name}_{infra[j].name}', colourkey=(0, 0, 255))
        for rg, ri in GROUND_INFRA_RANGES for i, j in zip(rg, ri)
    ]


road_town_png = lib.AseImageFile('sprites/infrastructure/road_town_overlayalpha_2x.ase')
road_town = tmpl_roadtiles(road_town_png, 0, 0, 2)
road_png = lib.AseImageFile('sprites/infrastructure/road_overlayalpha_2x.ase')
road = tmpl_roadtiles(road_png, 0, 0, 2)
replace_old(1313, make_infra_overlay_sprites(general_concrete, road_town))
replace_old(1332, make_infra_overlay_sprites(temperate_ground_2x, road))


def tmpl_vehicle_road_8view(imgfile, x, y, **kw):
    # Same spriteset template as in OpenGFX2
    func = lambda x, y, *args, **kw: lib.CCReplacingFileSprite(imgfile, x, y, *args, zoom=grf.ZOOM_NORMAL, **kw)
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
    png = lib.AseImageFile(file)
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


replace_rv_generation('sprites/vehicles/road_lorries_firstgeneration_32bpp.ase', 1)
replace_rv_generation('sprites/vehicles/road_lorries_secondgeneration_32bpp.ase', 2)
replace_rv_generation('sprites/vehicles/road_lorries_thirdgeneration_32bpp.ase', 3)


def tmpl_road_depot(imgfront, imgback, zoom):
    z = zoom_to_factor(zoom)

    def func(imgfile, x, y, h, ox, oy, **kw):
        xofs = -31 * z + ox * z
        yofs = 32 * z - h * z + oy * z - z - 1

        return lib.CCReplacingFileSprite(imgfile,
            1 * z + x * z, 1 * z + y * z, 64 * z, h * z - z + 1,
            xofs=xofs, yofs=yofs, zoom=zoom, **kw)

    return [
        func(imgback, 0, 0, 64, 0, 1),
        func(imgfront, 0, 0, 64, 30, -14),
        func(imgback, 0, 65, 64, 0, 1),
        func(imgfront, 0, 65, 64, -30, -14),
        func(imgfront, 0, 195, 64, -30, -14),
        func(imgfront, 0, 130, 64, 30, -14),
    ]

imgfront_1x = lib.AseImageFile('sprites/stations/roaddepots_1x.ase')
imgback_1x = lib.AseImageFile('sprites/stations/roaddepots_1x.ase', layer='Behind')
imgfront_2x = lib.AseImageFile('sprites/stations/roaddepots_2x.ase', ignore_layer='Behind')
imgback_2x = lib.AseImageFile('sprites/stations/roaddepots_2x.ase', layer='Behind')
replace_old(1408, zip_alternative(tmpl_road_depot(imgfront_1x, imgback_1x, grf.ZOOM_NORMAL),
                                  tmpl_road_depot(imgfront_2x, imgback_2x, grf.ZOOM_2X)))


def cmd_debugcc_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')


def cmd_debugcc_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file, layer=args.layer)
    sprite = lib.CCReplacingFileSprite(ase, 0, 0, None, None, name=args.ase_file)
    lib.debug_cc_recolour([sprite], horizontal=args.horizontal)


grf.main(
    g,
    'bonkygfx.grf',
    commands=[
        {
            'name': 'debugcc',
            'help': 'Takes an image and produces another image with all variants of CC recolour',
            'add_args': cmd_debugcc_add_args,
            'handler': cmd_debugcc_handler,
        }
    ]
)
