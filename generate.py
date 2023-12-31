import itertools
import pathlib
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

g.add_bool_parameter(
    name='Enable vehicles from all climates',
    description='Sets the climate availability for all vehicles (useful for debugging)',
    default=False,
)

g.add(grf.If(is_static=False, variable=0x01, condition=0x03, value=1, skip=0, varsize=1))  # skip if vehicle param not enabled
for feature in (grf.RV, grf.TRAIN, grf.SHIP, grf.AIRCRAFT):
    count = grf.DisableDefault.DISABLE_INFO[feature][0]
    g.add(grf.DefineMultiple(
        feature=feature,
        first_id=0,
        count=count,
        props={
            'climates_available': [grf.ALL_CLIMATES] * count,
        }
    ))
g.add(grf.Label(0, b''))


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


def tmpl_groundtiles_extra(name, paths, zoom):
    x, y = 0, 0
    @lib.template(grf.FileSprite)
    def tmpl_extra(func, z):
        return [
            func('extra1', 1502 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
            func('extra2', 1567 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
            func('extra3', 1632 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
            func('extra4', 1697 * z + x * z, z + y * z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0 * z),
        ]
    return tmpl_groundtiles(name, paths, zoom, 0) + tmpl_extra(name, paths, zoom)


# Normal land
make_ground = lambda name, y: lib.SpriteCollection(name) \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_1x.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles, ZOOM_NORMAL, y) \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_2x.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles, ZOOM_2X, y, thin=False) \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_2x_thin.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles, ZOOM_2X, y, thin=True)
temperate_ground = make_ground('temperate_ground', 0)
make_ground('temperate_ground_bare', 144).replace_old(3924)  # 0% grass
make_ground('temperate_ground_33', 96).replace_old(3943)   # 33% grass
make_ground('temperate_ground_66', 48).replace_old(3962)   # 66% grass
temperate_ground.replace_old(3981)  # 100% grass

lib.SpriteCollection('temperate_rough') \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_rough_2x.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles_extra, ZOOM_2X) \
    .replace_old(4000)

lib.SpriteCollection('temperate_rocks') \
    .add(TERRAIN_DIR / 'temperate_groundtiles_rocks_1x.ase',
         tmpl_groundtiles, ZOOM_NORMAL, 0) \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_rocks_2x.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles, ZOOM_2X, 0) \
    .replace_old(4023)

tropical_desert = lib.SpriteCollection('tropical_desert') \
    .add(TERRAIN_DIR / 'tropical_groundtiles_desert_1x.ase',
         tmpl_groundtiles, ZOOM_NORMAL, 0) \
    .add(TERRAIN_DIR / 'tropical_groundtiles_desert_2x.ase',
         tmpl_groundtiles, ZOOM_2X, 0) \
    .replace_old(4550, climate=TROPICAL)

lib.SpriteCollection('tropical_transitions') \
    .add(TERRAIN_DIR / 'tropical_groundtiles_deserttransition_1x.ase',
         tmpl_groundtiles, ZOOM_NORMAL, 0) \
    .replace_old(4512, climate=TROPICAL)

general_concrete = lib.SpriteCollection('general_concrete') \
    .add(lib.aseidx(TERRAIN_DIR / 'general_concretetiles_1x.ase', colourkey=(0, 0, 255)),
        tmpl_groundtiles, ZOOM_NORMAL, 0) \
    .add(lib.aseidx(TERRAIN_DIR / 'general_concretetiles_2x.ase', colourkey=(0, 0, 255)),
        tmpl_groundtiles, ZOOM_2X, 0)
general_concrete[0].replace_old(1420)


@lib.template(grf.FileSprite)
def tmpl_airport_tiles(funcs, z):
    func, order = funcs
    with_light = lambda *args, **kw: lib.MagentaToLight(func(*args, **kw), order(*args, **kw))
    return [
        func('apron', z * (1 + 0), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('stand', z * (1 + 65), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_ns_west', z * (1 + 455), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_ew_south', z * (1 + 520), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_xing_south', z * (1 + 585), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_xing_west', z * (1 + 650), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_ns_ctr', z * (1 + 715), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_xing_east', z * (1 + 780), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_ns_east', z * (1 + 845), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_ew_north', z * (1 + 910), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        func('taxi_ew_ctr', z * (1 + 975), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
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


AIRPORT_COMPOSITION = [(None, 0), (None, 1)] + [(0, i) for i in range(2, 11)] + [(None, i) for i in range(11, 18)]
airport_tiles = lib.SpriteCollection('airport_modern') \
    .add((lib.aseidx(INFRA_DIR / 'airport_modern_1x.ase', ignore_layer='Light order'),
          lib.aseidx(INFRA_DIR / 'airport_modern_1x.ase', layer='Light order')),
        tmpl_airport_tiles, ZOOM_NORMAL) \
    .add((lib.aseidx(INFRA_DIR / 'airport_modern_2x.ase', ignore_layer='Light order'),
          lib.aseidx(INFRA_DIR / 'airport_modern_2x.ase', layer='Light order')),
        tmpl_airport_tiles, ZOOM_2X) \
    .compose_on(temperate_ground, AIRPORT_COMPOSITION)
airport_tiles[:16].replace_old(2634)
airport_tiles[16].replace_new(0x15, 86)
airport_tiles[17].replace_new(0x10, 12)


@lib.template(grf.FileSprite)
def tmpl_roadtiles(func, z, x, y):
    x = y = 0
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


road_town = lib.SpriteCollection('road_town') \
    .add(INFRA_DIR / 'road_town_1x.ase',
         tmpl_roadtiles, ZOOM_NORMAL, 0, 0) \
    .add(lib.aseidx(INFRA_DIR / 'road_town_2x.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 0, 0)

road = lib.SpriteCollection('road') \
    .add(INFRA_DIR / 'road_1x.ase',
         tmpl_roadtiles, ZOOM_NORMAL, 0, 0) \
    .add(lib.aseidx(INFRA_DIR / 'road_2x.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 0, 0, thin=False) \
    .add(lib.aseidx(INFRA_DIR / 'road_2x_thin.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 0, 0, thin=True)

ROAD_COMPOSITION = list(zip([0] * 11, range(11))) + list(zip((12, 6, 3, 9), range(15, 19))) + list(zip([0] * 4, range(11, 15)))
road_town.compose_on(general_concrete, ROAD_COMPOSITION).replace_old(1313)
road.compose_on(temperate_ground, ROAD_COMPOSITION).replace_old(1332, climate=TEMPERATE)

road_noline = lib.SpriteCollection('road_noline') \
    .add(INFRA_DIR / 'road_noline_1x.ase',
         tmpl_roadtiles, ZOOM_NORMAL, 0, 0) \
    .add(INFRA_DIR / 'road_noline_2x.ase',
         tmpl_roadtiles, ZOOM_2X, 0, 0)

road_noline.compose_on(temperate_ground, ROAD_COMPOSITION).replace_old(1332, climate=TROPICAL)
road_noline.compose_on(tropical_desert, ROAD_COMPOSITION).replace_old(1351)


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
    def tmpl(suffix, x, y):
        res = lib.SpriteCollection(f'rv_gen{generation}_{suffix}')
        if path1x is not None:
            res.add(path1x, tmpl_vehicle_road_8view, ZOOM_NORMAL, x, y)
        if path2x is not None:
            res.add(path2x, tmpl_vehicle_road_8view, ZOOM_2X, x, y)
        return res

    # base_graphics spr3284(3284, "../graphics/vehicles/64/road_buses_8bpp.png") { template_vehicle_road_8view(0, 0, 1) } // bus
    o = {1: 0, 2: -192, 3: 192}[generation]
    tmpl('coal_empty', 0, 0).replace_old(3292 + o)
    tmpl('mail', 0, 1).replace_old(3300 + o)
    tmpl('oil', 0, 2).replace_old(3308 + o)
    tmpl('livestock', 0, 3).replace_old(3316 + o)
    tmpl('goods', 0, 4).replace_old(3324 + o)
    tmpl('food', 0, 5).replace_old(3332 + o)
    tmpl('grain_empty', 0, 6).replace_old(3340 + o)
    tmpl('wood_empty', 0, 7).replace_old(3348 + o)
    tmpl('steel_paper_empty', 0, 8).replace_old(3356 + o)
    tmpl('ore_empty', 0, 9).replace_old(3364 + o)
    tmpl('armoured', 0, 10).replace_old(3372 + o)
    tmpl('coal_loaded', 1, 0).replace_old(3380 + o)
    tmpl('grain_loaded', 1, 6).replace_old(3388 + o)
    tmpl('wood_loaded', 1, 7).replace_old(3396 + o)
    tmpl('steel_loaded', 1, 8).replace_old(3404 + o)
    tmpl('iron_ore_loaded', 1, 9).replace_old(3412 + o)
    tmpl('paper_loaded', 2, 8).replace_old(3420 + o)
    tmpl('copper_ore_loaded', 2, 9).replace_old(3428 + o)
    tmpl('water', 0, 11).replace_old(3436 + o)
    tmpl('fruit_empty', 0, 12).replace_old(3444 + o)
    tmpl('rubber_empty', 0, 13).replace_old(3452 + o)
    tmpl('fruit_loaded', 1, 12).replace_old(3460 + o)
    tmpl('rubber_loaded', 1, 13).replace_old(3468 + o)


gen1_2x = lib.aseidx(VEHICLE_DIR / 'road_lorries_2x.ase', frame=0)
gen2_2x = lib.aseidx(VEHICLE_DIR / 'road_lorries_2x.ase', frame=1)
gen3_2x = lib.aseidx(VEHICLE_DIR / 'road_lorries_2x.ase', frame=2)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_firstgeneration_1x.ase', gen1_2x, 1)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_secondgeneration_1x.ase', gen2_2x, 2)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_thirdgeneration_1x.ase', gen3_2x, 3)


@lib.template(lib.CCReplacingFileSprite)
def tmpl_road_depot(funcs, z):
    func_front, func_back = funcs

    def sprite(suffix, func, x, y, h, ox, oy):
        xofs = -31 * z + ox * z
        yofs = 32 * z - h * z + oy * z - (z - 1) // 2 - 1
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

lib.SpriteCollection('road_depot') \
    .add((lib.aseidx(STATION_DIR / 'roaddepots_1x.ase', ignore_layer='Behind'),
          lib.aseidx(STATION_DIR / 'roaddepots_1x.ase', layer='Behind')),
         tmpl_road_depot, ZOOM_NORMAL) \
    .add((lib.aseidx(STATION_DIR / 'roaddepots_2x.ase', ignore_layer='Behind'),
          lib.aseidx(STATION_DIR / 'roaddepots_2x.ase', layer='Behind')),
         tmpl_road_depot, ZOOM_2X, thin=False) \
    .add((lib.aseidx(STATION_DIR / 'roaddepots_2x_thin.ase', ignore_layer='Behind'),
          lib.aseidx(STATION_DIR / 'roaddepots_2x_thin.ase', layer='Behind')),
         tmpl_road_depot, ZOOM_2X, thin=True) \
    .replace_old(1408)


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

water = lib.SpriteCollection('water') \
    .add((lib.aseidx(TERRAIN_DIR / 'shorelines_1x_new.ase'),
          lib.aseidx(TERRAIN_DIR / 'shorelines_1x_new.ase', layer='Animated')),
         tmpl_water_full, ZOOM_NORMAL)
water[0].replace_old(4061)


WATER_COMPOSITION = [(x, x) for x in [16, 1, 2, 3, 4, 17, 6, 7, 8, 9, 15, 11, 12, 13, 14, 18]]
water.compose_on(temperate_ground, WATER_COMPOSITION).replace_new(0x0d, 0)


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


for mode in set(lib.old_sprites.keys()) | set(lib.new_sprites.keys()):
    ranges = list(group_ranges(lib.old_sprites[mode]))
    if not ranges and mode not in lib.new_sprites:
        continue

    keys = dict(mode)
    has_if = False
    if 'thin' in keys:
        thin_value = int(keys['thin'])
        g.add(grf.If(is_static=False, variable=0x00, condition=0x03, value=thin_value, skip=0, varsize=1))  # skip if thin param != value
        has_if = True
    if 'climate' in keys:
        climate_value = {TEMPERATE: 0, ARCTIC: 1, TROPICAL: 2, TOYLAND: 3}[keys['climate']]
        g.add(grf.If(is_static=False, variable=0x83, condition=0x03, value=climate_value, skip=0, varsize=1))  # skip if climate != value
        has_if = True

    # print(keys)
    # for c, a in lib.old_sprites_collection.get(mode, {}).items():
    #     print(f'    OLD {c.name} {a}')
    # for set_type, cd in lib.new_sprites_collection[mode].items():
    #     for c, a in cd.items():
    #         print(f'    NEW {set_type} {c.name} {a}')

    if ranges:
        g.add(grf.ReplaceOldSprites([(offset, len(sprites)) for offset, sprites in ranges]))
        for offset, sprites in ranges:
            g.add(*sprites)
            for i, sa in enumerate(sprites):
                names = ', '.join(s.name for s in (sa.sprites if isinstance(sa, grf.AlternativeSprites) else (sa,)))

    for set_type, sprite_dict in lib.new_sprites[mode].items():
        for offset, sprites in group_ranges(sprite_dict):
            g.add(grf.ReplaceNewSprites(set_type, len(sprites), offset=offset))
            g.add(*sprites)
            for i, sa in enumerate(sprites):
                names = ', '.join(s.name for s in (sa.sprites if isinstance(sa, grf.AlternativeSprites) else (sa,)))

    if has_if:
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
