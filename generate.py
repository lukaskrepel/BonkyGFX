import itertools
import pathlib
from collections import defaultdict
from typing import Optional, Union

from typeguard import typechecked

import grf
from grf import ZOOM_NORMAL, ZOOM_2X, ZOOM_4X, TEMPERATE, ARCTIC, TROPICAL, TOYLAND, ALL_CLIMATES

import lib


SPRITE_DIR = pathlib.Path('sprites')
TERRAIN_DIR = SPRITE_DIR / 'terrain'
VEHICLE_DIR = SPRITE_DIR / 'vehicles'
INFRA_DIR = SPRITE_DIR / 'infrastructure'
STATION_DIR = SPRITE_DIR / 'stations'
THICK = 1 << 4
THIN = 2 << 4
MODES = (TEMPERATE, ARCTIC, TOYLAND, TROPICAL)

g = grf.NewGRF(
    grfid=b'TODO',
    name='BonkyGFX',
    description='BonkyGFX',
    min_compatible_version=0,
    version=0,
)
g.add_bool_parameter(
    name='Use thin lines',
    description='Changes between graphical styles for 2x zoom',
    default=False,
)

old_sprites = defaultdict(dict)
new_sprites = defaultdict(lambda: defaultdict(dict))


def replace_old(first_id, sprites, *, mode=0):
    if isinstance(sprites, (grf.Resource, grf.ResourceAction)):
        sprites = [sprites]

    amount = len(sprites)
    assert first_id + amount < 4896
    for i, s in enumerate(sprites):
        old_sprites[mode][first_id + i] = s


def replace_new(set_type, offset, sprites, *, mode=0):
    if isinstance(sprites, (grf.Resource, grf.ResourceAction)):
        sprites = [sprites]
    for i, s in enumerate(sprites):
        new_sprites[mode][set_type][offset + i] = s


@lib.template(grf.FileSprite)
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
    z = lib.zoom_to_factor(zoom)
    x, y = 0, 0
    return tmpl_groundtiles(name, None, img, 0) + [
        func('extra1', 1502 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('extra2', 1567 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('extra3', 1632 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('extra4', 1697 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
    ]


# Normal land
ase_temperate_ground_1x = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_1x.ase', colourkey=(0, 0, 255))
ase_temperate_ground_2x = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_2x.ase', colourkey=(0, 0, 255))
ase_temperate_ground_2x_thin = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_2x_thin.ase', colourkey=(0, 0, 255))
make_ground = lambda name, y: tmpl_groundtiles(name, ase_temperate_ground_1x, ase_temperate_ground_2x, 0)
make_ground_thin = lambda name, y: tmpl_groundtiles(name, ase_temperate_ground_1x, ase_temperate_ground_2x_thin, 0)
temperate_ground = make_ground('temperate_ground', 0)
temperate_ground_thin = make_ground_thin('temperate_ground', 0)
replace_old(3924, make_ground('temperate_ground_bare', 144), mode=THICK)  # 0% grass
replace_old(3943, make_ground('temperate_ground_33', 96), mode=THICK)   # 33% grass
replace_old(3962, make_ground('temperate_ground_66', 48), mode=THICK)   # 66% grass
replace_old(3981, temperate_ground, mode=THICK)  # 100% grass
replace_old(3924, make_ground_thin('temperate_ground_bare', 144), mode=THIN)  # 0% grass
replace_old(3943, make_ground_thin('temperate_ground_33', 96), mode=THIN)   # 33% grass
replace_old(3962, make_ground_thin('temperate_ground_66', 48), mode=THIN)   # 66% grass
replace_old(3981, temperate_ground_thin, mode=THIN)  # 100% grass

ase = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_rough_2x.ase', colourkey=(0, 0, 255))
replace_old(4000, tmpl_groundtiles_extra('temperate_rough', ase, ZOOM_2X))
ase1x = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_rocks_1x.ase')
ase2x = lib.AseImageFile(TERRAIN_DIR / 'temperate_groundtiles_rocks_2x.ase', colourkey=(0, 0, 255))
replace_old(4023, tmpl_groundtiles('temperate_rocks', ase1x, ase2x, 0))
ase1x = lib.aseidx(TERRAIN_DIR / 'tropical_groundtiles_desert_1x.ase')
ase2x = lib.aseidx(TERRAIN_DIR / 'tropical_groundtiles_desert_2x.ase')
tropical_desert = tmpl_groundtiles('tropical_desert', ase1x, ase2x, 0)
replace_old(4550, tropical_desert, mode=TROPICAL)
ase = lib.AseImageFile(TERRAIN_DIR / 'tropical_groundtiles_deserttransition_1x.ase')
replace_old(4512, tmpl_groundtiles('tropical_transition', ase, None, 0), mode=TROPICAL)

ase1x = lib.AseImageFile(TERRAIN_DIR / 'general_concretetiles_1x.ase', colourkey=(0, 0, 255))
ase2x = lib.AseImageFile(TERRAIN_DIR / 'general_concretetiles_2x.ase', colourkey=(0, 0, 255))
general_concrete = tmpl_groundtiles('general_concrete', ase1x, ase2x, 0)
replace_old(1420, general_concrete[0])


def on_grass(sprite, thin):
    ground = temperate_ground_thin[0] if thin else temperate_ground[0]
    grass = ground.get_sprite(zoom=sprite.zoom)
    return lib.CompositeSprite((grass, sprite))


@lib.template(grf.FileSprite)
def tmpl_airport_tiles(funcs, z, thin):
    func, order = funcs
    with_light = lambda *args, **kw: lib.MagentaToLight(func(*args, **kw), order(*args, **kw))
    return [
        func('apron', z * (1 + 0), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('stand', z * (1 + 65), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        on_grass(func('taxi_ns_west', z * (1 + 455), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_ew_south', z * (1 + 520), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_xing_south', z * (1 + 585), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_xing_west', z * (1 + 650), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_ns_ctr', z * (1 + 715), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_xing_east', z * (1 + 780), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_ns_east', z * (1 + 845), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_ew_north', z * (1 + 910), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        on_grass(func('taxi_ew_ctr', z * (1 + 975), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0), thin),
        with_light('runway_a', z * (1 + 130), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_b', z * (1 + 195), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_c', z * (1 + 260), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_d', z * (1 + 325), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_end', z * (1 + 390), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('helipad', z * (1 + 1365), z, 64 * z, 32 * z - 1, xofs=-22 * z, yofs=-15 * z),
        func('new_helipad', z * (1 + 1430), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
    ]


@lib.template(grf.FileSprite)
def tmpl_flat_tile(func, z, suffix, x):
    return [func(suffix, z * (1 + x), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0)]


ase1x = lib.aseidx(INFRA_DIR / 'airport_modern_1x.ase', ignore_layer='Light order')
ase1x_order = lib.aseidx(INFRA_DIR / 'airport_modern_1x.ase', layer='Light order')
ase2x = lib.aseidx(INFRA_DIR / 'airport_modern_2x.ase', ignore_layer='Light order')
ase2x_order = lib.aseidx(INFRA_DIR / 'airport_modern_2x.ase', layer='Light order')
airport_tiles = tmpl_airport_tiles('airport_modern', (ase1x, ase1x_order), (ase2x, ase2x_order), False)
replace_old(2634, airport_tiles[:16], mode=THICK)
replace_new(0x15, 86, airport_tiles[16], mode=THICK)
replace_new(0x10, 12, airport_tiles[17], mode=THICK)
airport_tiles = tmpl_airport_tiles('airport_modern', (ase1x, ase1x_order), (ase2x, ase2x_order), True)
replace_old(2634, airport_tiles[:16], mode=THIN)
replace_new(0x15, 86, airport_tiles[16], mode=THIN)
replace_new(0x10, 12, airport_tiles[17], mode=THIN)


@lib.template(grf.FileSprite)
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


def compose_sprites(a, b, **kw):
    compose = lambda a, b: lib.CompositeSprite(
        (a, b),
        name=f'{a.name}_{b.name}',
        **kw,
    )

    def list_zooms(s):
        if isinstance(s, grf.AlternativeSprites):
            return {x.zoom for x in s.sprites}
        return {s.zoom}

    def get_sprite(s, zoom):
        if isinstance(s, grf.AlternativeSprites):
            return s.get_sprite(zoom=zoom)
        return s

    a_zooms, b_zooms = list_zooms(a), list_zooms(b)
    common_zooms = a_zooms & b_zooms

    sprites = [compose(get_sprite(a, zoom), get_sprite(b, zoom)) for zoom in common_zooms]
    if len(sprites) == 1:
        return sprites[0]
    return grf.AlternativeSprites(*sprites)


def make_infra_overlay_sprites(ground, infra):
    GROUND_INFRA_RANGES = (
        ([0] * 11, range(11)),
        ((12, 6, 3, 9), range(15, 19)),
        ([0] * 4, range(11, 15)),
    )
    res = []
    for rg, ri in GROUND_INFRA_RANGES:
        for i, j in zip(rg, ri):
            res.append(compose_sprites(ground[i], infra[j], colourkey=(0, 0, 255)))
    return res


road_town = tmpl_roadtiles('road_town', INFRA_DIR / 'road_town_1x.ase', INFRA_DIR / 'road_town_2x.ase', 0, 0)
road = tmpl_roadtiles('road', INFRA_DIR / 'road_1x.ase', INFRA_DIR / 'road_2x.ase', 0, 0)
road_thin = tmpl_roadtiles('road', INFRA_DIR / 'road_1x.ase', INFRA_DIR / 'road_2x_thin.ase', 0, 0)
replace_old(1313, make_infra_overlay_sprites(general_concrete, road_town))
replace_old(1332, make_infra_overlay_sprites(temperate_ground, road), mode=TEMPERATE | THICK)
replace_old(1332, make_infra_overlay_sprites(temperate_ground_thin, road_thin), mode=TEMPERATE | THIN)
road_noline = tmpl_roadtiles('road_noline', INFRA_DIR / 'road_noline_1x.ase', INFRA_DIR / 'road_noline_2x.ase', 0, 0)
replace_old(1332, make_infra_overlay_sprites(temperate_ground, road_noline), mode=TROPICAL | THICK)
replace_old(1332, make_infra_overlay_sprites(temperate_ground_thin, road_noline), mode=TROPICAL | THIN)
replace_old(1351, make_infra_overlay_sprites(tropical_desert, road_noline))


@lib.template(lib.CCReplacingFileSprite)
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


replace_rv_generation(VEHICLE_DIR / 'road_lorries_firstgeneration_1x.ase', None, 1)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_secondgeneration_1x.ase', VEHICLE_DIR / 'road_lorries_secondgeneration_2x.ase', 2)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_thirdgeneration_1x.ase', None, 3)


@lib.template(lib.CCReplacingFileSprite)
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


imgfront1x = lib.aseidx(STATION_DIR / 'roaddepots_1x.ase', ignore_layer='Behind')
imgback1x = lib.aseidx(STATION_DIR / 'roaddepots_1x.ase', layer='Behind')
imgfront2x = lib.aseidx(STATION_DIR / 'roaddepots_2x.ase', ignore_layer='Behind')
imgback2x = lib.aseidx(STATION_DIR / 'roaddepots_2x.ase', layer='Behind')
imgfront2x_thin = lib.aseidx(STATION_DIR / 'roaddepots_2x_thin.ase', ignore_layer='Behind')
imgback2x_thin = lib.aseidx(STATION_DIR / 'roaddepots_2x_thin.ase', layer='Behind')
replace_old(1408, tmpl_road_depot('road_depot', (imgfront1x, imgback1x), (imgfront2x, imgback2x)), mode=THICK)
replace_old(1408, tmpl_road_depot('road_depot', (imgfront1x, imgback1x), (imgfront2x_thin, imgback2x_thin)), mode=THIN)


@lib.template(grf.FileSprite)
def tmpl_water(funcs, z, suffix, x):
    magenta, mask = funcs
    func = lambda *args, **kw: lib.MagentaAndMask(magenta(*args, **kw), mask(*args, **kw))
    return [func(suffix, z * (1 + x), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0)]


@lib.template(grf.FileSprite)
def tmpl_water_full(funcs, z):
    x = y = 0
    magenta, mask = funcs
    func = lambda *args, **kw: lib.MagentaAndMask(magenta(*args, **kw), mask(*args, **kw))
    return [
        func('full', 1 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('1', 81 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('2', 161 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('3', 241 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('4', 321 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('5', 399 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('6', 479 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('7', 559 * z + x * z, 1 * z + y * z, 64 * z, 24 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('8', 639 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('9', 719 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('10', 799 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('11', 879 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('12', 959 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('13', 1039 * z + x * z, 1 * z + y * z, 64 * z, 40 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('14', 1119 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('15', 1197 * z + x * z, 1 * z + y * z, 64 * z, 48 * z - 1, xofs=-31 * z, yofs=16 * z),
        func('16', 1277 * z + x * z, 1 * z + y * z, 64 * z, 16 * z - 1, xofs=-31 * z, yofs=0 * z),
        func('17', 1357 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
        func('18', 1437 * z + x * z, 1 * z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=-8 * z),
    ]

ase_magenta = lib.aseidx(TERRAIN_DIR / 'shorelines_1x_new.ase')
ase_mask = lib.aseidx(TERRAIN_DIR / 'shorelines_1x_new.ase', layer='Animated')
water = tmpl_water_full('water', (ase_magenta, ase_mask), None)
replace_old(4061, water[0])


def make_shore_sprites(ground, water):
    ORDER = [16, 1, 2, 3, 4, 17, 6, 7, 8, 9, 15, 11, 12, 13, 14, 18]
    return [compose_sprites(ground[i], water[i]) for i in ORDER]

replace_new(0x0d, 0, make_shore_sprites(temperate_ground, water), mode=THICK)
replace_new(0x0d, 0, make_shore_sprites(temperate_ground_thin, water), mode=THIN)


def group_ranges(sprites):
    last_id = cur_range = None
    for i in sorted(sprites.keys()):
        s = sprites[i]
        if last_id is None:
            cur_range = [s]
        elif last_id + 1 == i and len(cur_range) < 255:
            cur_range.append(s)
        else:
            yield (last_id - len(cur_range) + 1, cur_range)
            cur_range = [s]
        last_id = i
    if cur_range:
        yield (last_id - len(cur_range) + 1, cur_range)


for mode in set(old_sprites.keys()) | set(new_sprites.keys()):
    ranges = list(group_ranges(old_sprites[mode]))
    if not ranges and mode not in new_sprites:
        continue

    climate_value = thin_value = None
    if mode & 0xf0 == THICK:
        thin_value = 0
    if mode & 0xf0 == THIN:
        thin_value = 1
    if mode & 15 > 0:
        climate_value = {TEMPERATE: 0, ARCTIC: 1, TROPICAL: 2, TOYLAND: 3}[mode & 15]

    if climate_value is not None:
        g.add(grf.If(is_static=False, variable=0x83, condition=0x03, value=climate_value, skip=0, varsize=1))  # skip if climate != value
    if thin_value is not None:
        g.add(grf.If(is_static=False, variable=0x00, condition=0x03, value=thin_value, skip=0, varsize=1))  # skip if thin param != value

    if ranges:
        g.add(grf.ReplaceOldSprites([(offset, len(sprites)) for offset, sprites in ranges]))
        for offset, sprites in ranges:
            g.add(*sprites)

    for set_type, sprite_dict in new_sprites[mode].items():
        for offset, sprites in group_ranges(sprite_dict):
            g.add(grf.ReplaceNewSprites(set_type, len(sprites), offset=offset))
            g.add(*sprites)
    if climate_value is not None or thin_value is not None:
        g.add(grf.Label(0, b''))


def cmd_debugcc_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')


def cmd_debugcc_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file, layer=args.layer)
    sprite = lib.CCReplacingFileSprite(ase, 0, 0, None, None, name=args.ase_file)
    lib.debug_cc_recolour([sprite], horizontal=args.horizontal)


def cmd_debuglight_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')


def cmd_debuglight_handler(g, grf_file, args):
    in_file = args.ase_file
    ase = lib.AseImageFile(in_file, ignore_layer='Light order')
    aseo = lib.AseImageFile(in_file, layer='Light order')
    sprite = grf.FileSprite(ase, 0, 0, None, None, name=f'{in_file}_image')
    order = grf.FileSprite(aseo, 0, 0, None, None, name=f'{in_file}_order')
    lib.debug_light_cycle([lib.MagentaToLight(sprite, order)], horizontal=args.horizontal)


grf.main(
    g,
    'bonkygfx.grf',
    commands=[{
        'name': 'debugcc',
        'help': 'Takes an image and produces another image with all variants of CC recolour',
        'add_args': cmd_debugcc_add_args,
        'handler': cmd_debugcc_handler,
    }, {
        'name': 'debuglight',
        'help': 'Takes an image and produces animated gif with light cycle',
        'add_args': cmd_debuglight_add_args,
        'handler': cmd_debuglight_handler,
    }]
)
