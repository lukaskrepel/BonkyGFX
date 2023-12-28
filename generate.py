import itertools
import pathlib
from typing import Optional, Union

from typeguard import typechecked

import grf
from grf import ZOOM_NORMAL, ZOOM_2X, ZOOM_4X

import lib

SPRITE_DIR = pathlib.Path('sprites')
TERRAIN_DIR = SPRITE_DIR / 'terrain'
VEHICLE_DIR = SPRITE_DIR / 'vehicles'
INFRA_DIR = SPRITE_DIR / 'infrastructure'
STATION_DIR = SPRITE_DIR / 'stations'
DEBUG_ZOOM = False

g = grf.NewGRF(
    grfid=b'TODO',
    name='BonkyGFX',
    description='BonkyGFX',
    min_compatible_version=0,
    version=0,
)

ASE_IDX = {}


def get_ase(path, layer=None, ignore_layer=None):
    key = (path, layer, ignore_layer)
    ase = ASE_IDX.get(key)
    if ase is None:
        ase = ASE_IDX[key] = lib.AseImageFile(path, layer=layer, ignore_layer=ignore_layer)
    return ase


def template(sprite_class):
    def decorator(tmpl_func):
        def wrapper(name, path1x, path2x, *args, layer=None, ignore_layer=None, **kw):
            def make_func_lists(path, zoom):
                if path is None:
                    return None
                try:
                    it = iter(path)
                except TypeError:
                    it = iter((path,))

                z = zoom_to_factor(zoom)
                def make_sprite_func(p):
                    if isinstance(p, (str, pathlib.Path)):
                        p = get_ase(p)
                    def sprite_func(suffix, *args, **kw):
                        return sprite_class(p, *args, **kw, zoom=zoom, name=name + f'_{suffix}_{z}x')
                    return sprite_func

                res = list(map(make_sprite_func, it))
                if len(res) == 1:
                    return res[0]
                return res

            func1x = make_func_lists(path1x, ZOOM_NORMAL)
            func2x = make_func_lists(path2x, ZOOM_2X)
            if path1x is None:
                if path2x is None:
                    raise ValueError('At least one of path1x or path2x should be not None')
                return tmpl_func(func2x, 2, *args, **kw)
            else:
                if path2x is None:
                    return tmpl_func(func1x, 1, *args, **kw)
                res = []
                x1 = tmpl_func(func1x, 1, *args, **kw)
                x2 = tmpl_func(func2x, 2, *args, **kw)
                for sprites in zip(x1, x2):
                    res.append(grf.AlternativeSprites(*sprites))
                return res

        return wrapper
    return decorator


def zoom_to_factor(zoom):
    return {
        ZOOM_NORMAL: 1,
        ZOOM_2X: 2,
        ZOOM_4X: 4,
    }[zoom]


def replace_old(first_id, sprites):
    if isinstance(sprites, (grf.Resource, grf.ResourceAction)):
        sprites = [sprites]
    amount = len(sprites)
    g.add(grf.ReplaceOldSprites([(first_id, amount)]))
    g.add(*sprites)


@template(grf.FileSprite)
def tmpl_groundtiles(func, z, y):
    x = 0
    return [
        func('flat', 1 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('w', 81 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('s', 161 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('sw', 241 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),

        func('e', 321 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('ew', 399 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('se', 479 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('wse', 559 * z + x * z, z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),

        func('n', 639 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('nw', 719 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('ns', 799 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('nws', 879 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),

        func('ne', 959 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('enw', 1039 * z + x * z, z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('sen', 1119 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),

        func('steep_n', 1197 * z + x * z, z + y * z, 64 * z, 48 * z - 1, xofs=-31 * z, yofs=-16 * z),
        func('steep_s', 1277 * z + x * z, z + y * z, 64 * z, 16 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('steep_w', 1357 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('steep_e', 1437 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
    ]


def tmpl_groundtiles_extra(name, img, zoom):
    func = lambda i, x, y, *args, **kw: grf.FileSprite(img, x, y, *args, zoom=zoom, name=f'{name}_{i}_{z}x', **kw)
    z = zoom_to_factor(zoom)
    x, y = 0, 0
    return tmpl_groundtiles(name, None, img, 0) + [
        func('extra1', 1502 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('extra2', 1567 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('extra3', 1632 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('extra4', 1697 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
    ]


# Terrain: Single flat tile
# def tmpl_flattile_single(png, x, y, **kw):
#     func = lambda x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=ZOOM_2X, **kw)
#     z = 2
#     return [func(1 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0*z, **kw)]


# Normal land
ase_temperate_ground_1x = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_32bpp_1x.ase', colourkey=(0, 0, 255))
ase_temperate_ground_2x = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_32bpp.ase', colourkey=(0, 0, 255))
make_ground = lambda name, y: tmpl_groundtiles(name, ase_temperate_ground_1x, ase_temperate_ground_2x, 0)
temperate_ground = make_ground('temperate_ground', 0)
replace_old(3924, make_ground('temperate_ground_bare', 144))  # 0% grass
replace_old(3943, make_ground('temperate_ground_33', 96))   # 33% grass
replace_old(3962, make_ground('temperate_ground_66', 48))   # 66% grass
replace_old(3981, temperate_ground)  # 100% grass

ase = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_rough_32bpp.ase', colourkey=(0, 0, 255))
replace_old(4000, tmpl_groundtiles_extra('temperate_rough', ase, ZOOM_2X))
ase = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_rocks_32bpp.ase', colourkey=(0, 0, 255))
replace_old(4023, tmpl_groundtiles('temperate_rocks', None, ase, 0))

ase1x = lib.AseImageFile(TERRAIN_DIR / 'general_concretetiles_1x.ase', colourkey=(0, 0, 255))
ase2x = lib.AseImageFile(TERRAIN_DIR / 'general_concretetiles_2x.ase', colourkey=(0, 0, 255))
general_concrete = tmpl_groundtiles('general_concrete', ase1x, ase2x, 0)
replace_old(1420, general_concrete[0])


@template(grf.FileSprite)
def tmpl_airport_tiles(func, z):
    return [
        func('empty', z * (1 + 0), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('square', z * (1 + 65), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('landing1', z * (1 + 455), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('landing2', z * (1 + 520), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('landing3', z * (1 + 585), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('landing4', z * (1 + 650), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('1', z * (1 + 715), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('2', z * (1 + 780), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('3', z * (1 + 845), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('4', z * (1 + 910), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('5', z * (1 + 975), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('6', z * (1 + 130), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('7', z * (1 + 195), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('8', z * (1 + 260), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('9', z * (1 + 325), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('10', z * (1 + 390), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
    ]

replace_old(2634, tmpl_airport_tiles('airport_modern', INFRA_DIR / 'airport_modern_1x.ase', INFRA_DIR / 'airport_modern_2x.ase'))


@template(grf.FileSprite)
def tmpl_roadtiles(func, z, x, y):
    return [
        func('y', 1 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('x', 66 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('full', 131 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('t_y_ne', 196 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('t_x_nw', 261 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('t_y_sw', 326 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('t_x_se', 391 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('w', 456 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('n', 521 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('e', 586 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('s', 651 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),

        func('ne', 846 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('se', 911 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('sw', 716 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('nw', 781 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),

        func('slope_ne', 976 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('slope_se', 1041 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('slope_sw', 1106 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('slope_nw', 1171 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
    ]


def make_infra_overlay_sprites(ground, infra):
    GROUND_INFRA_RANGES = (
        ([0] * 11, range(11)),
        ((12, 6, 3, 9), range(15, 19)),
        ([0] * 4, range(11, 15)),
    )
    res = []
    for rg, ri in GROUND_INFRA_RANGES:
        for i, j in zip(rg, ri):
            sg, si = ground[i], infra[j]
            assert isinstance(sg, grf.AlternativeSprites) and isinstance(si, grf.AlternativeSprites)
            compose = lambda zoom: lib.CompositeSprite(
                (sg.get_sprite(zoom=zoom), si.get_sprite(zoom=zoom)),
                name='{sg.name}_{si.name}_{z}x',
                colourkey=(0, 0, 255)
            )
            res.append(grf.AlternativeSprites(compose(ZOOM_NORMAL), compose(ZOOM_2X)))
    return res


road_town = tmpl_roadtiles('road_town', INFRA_DIR / 'road_town_overlayalpha_1x.ase', INFRA_DIR / 'road_town_overlayalpha_2x.ase', 0, 0)
road = tmpl_roadtiles('road', INFRA_DIR / 'road_overlayalpha_1x.ase', INFRA_DIR / 'road_overlayalpha_2x.ase', 0, 0)
replace_old(1313, make_infra_overlay_sprites(general_concrete, road_town))
replace_old(1332, make_infra_overlay_sprites(temperate_ground, road))


@template(lib.CCReplacingFileSprite)
def tmpl_vehicle_road_8view(func, z, x, y):
    res = [
        func('n', (1 + 0 + x * 174) * z, (1 + y * 24) * z, 8 * z, 23 * z, xofs=-3 * z, yofs=-15 * z),
        func('ne', (2 + 8 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-10 * z),
        func('e', (3 + 30 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-15 * z, yofs=-9 * z),
        func('se', (4 + 61 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-10 * z),
        func('s', (5 + 83 + x * 174) * z, (1 + y * 24) * z, 8 * z, 23 * z, xofs=-3 * z, yofs=-15 * z),
        func('sw', (6 + 91 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-10 * z),
        func('w', (7 + 113 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-15 * z, yofs=-9 * z),
        func('nw', (8 + 144 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-10 * z),
    ]
    return res


def replace_rv_generation(path1x, path2x, generation):
    # base_graphics spr3284(3284, "../graphics/vehicles/64/road_buses_8bpp.png") { template_vehicle_road_8view(0, 0, 1) } // bus
    tmpl = lambda suffix, x, y: tmpl_vehicle_road_8view(f'rv_gen{generation}_{suffix}', path1x, path2x, x, y)
    o = {1: 0, 2: -192, 3: 192}[generation]
    replace_old(3292 + o, tmpl('coal_empty', 0, 0))
    replace_old(3300 + o, tmpl('mail', 0, 1))
    replace_old(3308 + o, tmpl('oil', 0, 2))
    replace_old(3316 + o, tmpl('livestock', 0, 3))
    replace_old(3324 + o, tmpl('goods', 0, 4))
    replace_old(3332 + o, tmpl('food', 0, 5))
    replace_old(3340 + o, tmpl('grain_empty', 0, 6))
    replace_old(3348 + o, tmpl('wood_empty', 0, 7))
    replace_old(3356 + o, tmpl('steel_paper_empty', 0, 8))
    replace_old(3364 + o, tmpl('ore_empty', 0, 9))
    replace_old(3372 + o, tmpl('armoured', 0, 10))
    replace_old(3380 + o, tmpl('coal_loaded', 1, 0))
    replace_old(3388 + o, tmpl('grain_loaded', 1, 6))
    replace_old(3396 + o, tmpl('wood_loaded', 1, 7))
    replace_old(3404 + o, tmpl('steel_loaded', 1, 8))
    replace_old(3412 + o, tmpl('iron_ore_loaded', 1, 9))
    replace_old(3420 + o, tmpl('paper_loaded', 2, 8))
    replace_old(3428 + o, tmpl('copper_ore_loaded', 2, 9))
    replace_old(3436 + o, tmpl('water', 0, 11))
    replace_old(3444 + o, tmpl('fruit_empty', 0, 12))
    replace_old(3452 + o, tmpl('rubber_empty', 0, 13))
    replace_old(3460 + o, tmpl('fruit_loaded', 1, 12))
    replace_old(3468 + o, tmpl('rubber_loaded', 1, 13))


replace_rv_generation(VEHICLE_DIR / 'road_lorries_firstgeneration_32bpp.ase', None, 1)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_secondgeneration_32bpp.ase', VEHICLE_DIR / 'road_lorries_secondgeneration_32bpp_2x.ase', 2)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_thirdgeneration_32bpp.ase', None, 3)


@template(lib.CCReplacingFileSprite)
def tmpl_road_depot(funcs, z):
    func_front, func_back = funcs

    def sprite(suffix, func, x, y, h, ox, oy):
        xofs = -31 * z + ox * z
        yofs = 32 * z - h * z + oy * z - z - 1
        return func(
            suffix,
            1 * z + x * z, 1 * z + y * z, 64 * z, h * z - z + 1,
            xofs=xofs, yofs=yofs)

    return [
        sprite('se_back', func_back, 0, 0, 64, 0, 1),
        sprite('se_front', func_front, 0, 0, 64, 30, -14),
        sprite('sw_back', func_back, 0, 65, 64, 0, 1),
        sprite('sw_front', func_front, 0, 65, 64, -30, -14),
        sprite('ne', func_front, 0, 195, 64, -30, -14),
        sprite('nw', func_front, 0, 130, 64, 30, -14),
    ]


imgfront1x = get_ase(STATION_DIR / 'roaddepots_1x.ase', ignore_layer='Behind')
imgback1x = get_ase(STATION_DIR / 'roaddepots_1x.ase', layer='Behind')
imgfront2x = get_ase(STATION_DIR / 'roaddepots_2x.ase', ignore_layer='Behind')
imgback2x = get_ase(STATION_DIR / 'roaddepots_2x.ase', layer='Behind')
replace_old(1408, tmpl_road_depot('road_depot', (imgfront1x, imgback1x), (imgfront2x, imgback2x)))


def cmd_debugcc_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')


def cmd_debugcc_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file, layer=args.layer)
    sprite = lib.CCReplacingFileSprite(ase, 0, 0, None, None, name=args.ase_file)
    lib.debug_cc_recolour([sprite], horizontal=args.horizontal)


if DEBUG_ZOOM:
    def wrap_sprite(sprite):
        return lib.DebugRecolourSprite(sprite, (1, 0, 0) if sprite.zoom == ZOOM_NORMAL else (0, 0, 1))

    for s in g.generators:
        if isinstance(s, grf.AlternativeSprites):
            s.sprites = list(map(wrap_sprite, s.sprites))
        elif isinstance(s, grf.SingleResourceAction):
            s.resource = wrap_sprite(s.resource)


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
