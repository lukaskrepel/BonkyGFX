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
INDUSTRY_DIR = SPRITE_DIR / 'industries'
STATION_DIR = SPRITE_DIR / 'stations'
TREE_DIR = SPRITE_DIR / 'trees'
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


# ------------------------------ Ground Tiles ------------------------------

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
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_2x.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles, ZOOM_2X, y, thin=False, climate=TEMPERATE) \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_2x_thin.ase', colourkey=(0, 0, 255)),
         tmpl_groundtiles, ZOOM_2X, y, thin=True, climate=TEMPERATE) \
    .add(TERRAIN_DIR / 'tropical_groundtiles_2x.ase',
         tmpl_groundtiles, ZOOM_2X, y, climate=TROPICAL) \
    .add(TERRAIN_DIR / 'arctic_groundtiles_2x.ase',
         tmpl_groundtiles, ZOOM_2X, y, climate=ARCTIC)
ground = make_ground('ground', 0)
make_ground('ground_bare', 144).replace_old(3924)  # 0% grass
make_ground('ground_33', 96).replace_old(3943)   # 33% grass
make_ground('ground_66', 48).replace_old(3962)   # 66% grass
ground.replace_old(3981)  # 100% grass

lib.SpriteCollection('temperate_rough') \
    .add(TERRAIN_DIR / 'temperate_groundtiles_rough_2x.ase',
         tmpl_groundtiles_extra, ZOOM_2X) \
    .replace_old(4000)

lib.SpriteCollection('temperate_rocks') \
    .add(TERRAIN_DIR / 'temperate_groundtiles_rocks_2x.ase',
         tmpl_groundtiles, ZOOM_2X, 0) \
    .replace_old(4023)

tropical_desert = lib.SpriteCollection('tropical_desert') \
    .add(TERRAIN_DIR / 'tropical_groundtiles_desert_2x.ase',
         tmpl_groundtiles, ZOOM_2X, 0) \
    .replace_old(4550, climate=TROPICAL)

lib.SpriteCollection('tropical_transitions') \
    .add(TERRAIN_DIR / 'tropical_groundtiles_deserttransition_2x.ase',
         tmpl_groundtiles, ZOOM_2X, 0) \
    .replace_old(4512, climate=TROPICAL)

general_concrete = lib.SpriteCollection('general_concrete') \
    .add(lib.aseidx(TERRAIN_DIR / 'general_concretetiles_2x.ase', colourkey=(0, 0, 255)),
        tmpl_groundtiles, ZOOM_2X, 0)
general_concrete[0].replace_old(1420)


# ------------------------------ Airport Tiles ------------------------------

@lib.template(grf.FileSprite)
def tmpl_airport_tiles(func, z):
    kw_default = {'ignore_layers': 'Light order'}
    kw_light = {'layers': 'Light order'}
    with_light = lambda *args, **kw: lib.MagentaToLight(func(*args, **kw, **kw_default), func(*args, **kw, **kw_light))
    return [
        func('apron', z * (1 + 0), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('stand', z * (1 + 65), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_ns_west', z * (1 + 455), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_ew_south', z * (1 + 520), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_xing_south', z * (1 + 585), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_xing_west', z * (1 + 650), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_ns_ctr', z * (1 + 715), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_xing_east', z * (1 + 780), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_ns_east', z * (1 + 845), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_ew_north', z * (1 + 910), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        func('taxi_ew_ctr', z * (1 + 975), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
        with_light('runway_a', z * (1 + 130), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_b', z * (1 + 195), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_c', z * (1 + 260), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_d', z * (1 + 325), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('runway_end', z * (1 + 390), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0),
        with_light('helipad', z * (1 + 1365), z, 64 * z, 32 * z - 1, xofs=-22 * z, yofs=-15 * z),
        func('new_helipad', z * (1 + 1430), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0, **kw_default),
    ]


@lib.template(grf.FileSprite)
def tmpl_flat_tile(func, z, suffix, x):
    return [func(suffix, z * (1 + x), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0)]


AIRPORT_COMPOSITION = [(None, 0), (None, 1)] + [(0, i) for i in range(2, 11)] + [(None, i) for i in range(11, 18)]
airport_tiles = lib.SpriteCollection('airport_modern') \
    .add(INFRA_DIR / 'airport_modern_2x.ase',
        tmpl_airport_tiles, ZOOM_2X) \
    .compose_on(ground, AIRPORT_COMPOSITION)
airport_tiles[:16].replace_old(2634)
airport_tiles[16].replace_new(0x15, 86)
airport_tiles[17].replace_new(0x10, 12)


# ------------------------------ Trees ------------------------------


def tree(name, sprite_id, path):
    @lib.template(grf.FileSprite)
    def tmpl(func, z, frame):
        # Variation of OpenGFX1 template with 2x zoom and only one tree
        return [
            func('', 0 * z, 0, 45 * z, 80 * z, xofs=-24 * z, yofs=-73 * z, frame=frame)
        ]
    sprites = []
    for i in range(7):
        sprites.extend(tmpl(f'stage{i}', lib.aseidx(path), ZOOM_2X, i))
    lib.SpriteCollection(name).add_sprites(sprites).replace_old(sprite_id)

TREE_RANGES = [
    (1576, 19),  # temperate
    (1709, 8),  # arctic
    (1765, 8),  # arctic-snow
    (1821, 18),  # tropic
    (1947, 9),  # toyland
]

for i in range(19):
    tree('temperate_tree', 1576 + i * 7, TREE_DIR / 'temperate_tree_2x.ase')

for i in range(8):
    tree('arctic_tree', 1709 + i * 7, TREE_DIR / 'arctic_tree_2x.ase')
    tree('arctic_tree_snow', 1765 + i * 7, TREE_DIR / 'arctic_tree_snow_2x.ase')

for i in range(18):
    tree('tropic_tree', 1821 + i * 7, TREE_DIR / 'tropical_tree_2x.ase')

tree('cactus', 1821 + 7 * 13, TREE_DIR / 'cactus_2x.ase')
tree('cactus', 1821 + 7 * 14, TREE_DIR / 'cactus_2x.ase')

# ------------------------------ Road Vehicles ------------------------------

@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_road_8view(func, z, x, y, frame):
    res = [
        func('n', (1 + 0 + x * 174) * z, (1 + y * 24) * z, 8 * z, 23 * z, xofs=-3 * z, yofs=-15 * z, frame=frame),
        func('ne', (2 + 8 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-10 * z, frame=frame),
        func('e', (3 + 30 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-15 * z, yofs=-9 * z, frame=frame),
        func('se', (4 + 61 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-10 * z, frame=frame),
        func('s', (5 + 83 + x * 174) * z, (1 + y * 24) * z, 8 * z, 23 * z, xofs=-3 * z, yofs=-15 * z, frame=frame),
        func('sw', (6 + 91 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-10 * z, frame=frame),
        func('w', (7 + 113 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-15 * z, yofs=-9 * z, frame=frame),
        func('nw', (8 + 144 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-10 * z, frame=frame),
    ]
    return res


def replace_rv_generation(path2x, generation):
    def tmpl(suffix, x, y):
        return lib.SpriteCollection(f'rv_gen{generation}_{suffix}') \
            .add(path2x, tmpl_vehicle_road_8view, ZOOM_2X, x, y, generation - 1)

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


replace_rv_generation(VEHICLE_DIR / 'road_lorries_2x.ase', 1)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_2x.ase', 2)
replace_rv_generation(VEHICLE_DIR / 'road_lorries_2x.ase', 3)
lib.SpriteCollection('bus_gen1') \
    .add(VEHICLE_DIR / 'road_buses_2x.ase', tmpl_vehicle_road_8view, ZOOM_2X, 0, 0, 0) \
    .replace_old(3284)
lib.SpriteCollection('bus_gen2') \
    .add(VEHICLE_DIR / 'road_buses_2x.ase', tmpl_vehicle_road_8view, ZOOM_2X, 0, 1, 0) \
    .replace_old(3284 - 192)
lib.SpriteCollection('bus_gen2') \
    .add(VEHICLE_DIR / 'road_buses_2x.ase', tmpl_vehicle_road_8view, ZOOM_2X, 0, 2, 0) \
    .replace_old(3284 + 192)


# ------------------------------ Rail Vehicles ------------------------------

@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_rail_4view(func, z, x, y):
    # Horizontal views have zoom-specific optimisation for perfect depot window alignment
    return [
        func( 'n', (1 +   0 + x * 87) * z, (1 + y * 24) * z,  8 * z, 23 * z, xofs=-3 * z, yofs=-13 * z),
        func('ne', (2 +   8 + x * 87) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-12 * z),
        func( 'e', (3 +  30 + x * 87) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-16 * z + z // 2, yofs=-9 * z),
        func('se', (4 +  61 + x * 87) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-12 * z),
    ]


@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_rail_8view(func, z, x, y):
    # Horizontal views have zoom-specific optimisation for perfect depot window alignment
    return [
        func( 'n', (1 +   0 + x * 174) * z, (1 + y * 24) * z,  8 * z, 23 * z, xofs=-3 * z, yofs=-13 * z),
        func('ne', (2 +   8 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-12 * z),
        func( 'e', (3 +  30 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-16 * z + z // 2,  yofs=-9 * z),
        func('se', (4 +  61 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-12 * z),
        func( 's', (5 +  83 + x * 174) * z, (1 + y * 24) * z,  8 * z, 23 * z, xofs=-3 * z, yofs=-13 * z),
        func('sw', (6 +  91 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-15 * z, yofs=-12 * z),
        func( 'w', (7 + 113 + x * 174) * z, (1 + y * 24) * z, 31 * z, 15 * z, xofs=-16 * z + z // 2,  yofs=-9 * z),
        func('nw', (8 + 144 + x * 174) * z, (1 + y * 24) * z, 22 * z, 19 * z, xofs=-7 * z, yofs=-12 * z),
    ]


def wagon(name, sprite_id, x, y):
    lib.SpriteCollection('wagon_' + name) \
        .add(VEHICLE_DIR / 'rail_wagons_2x.ase', tmpl_vehicle_rail_4view, ZOOM_2X, x, y) \
        .replace_old(sprite_id)

wagon('passengers', 2733, 0, 0)  # temperate rail passenger wagon (full + empty)
wagon('coal_empty', 2737, 0, 1)  # temperate rail coal wagon (empty)
wagon('mail', 2741, 0, 2)  # temperate rail mail wagon (full + empty)
wagon('oil', 2745, 0, 3)  # temperate rail oil wagon (full + empty)
wagon('livestock', 2749, 0, 4)  # temperate rail livestock wagon (full + empty)
wagon('goods', 2753, 0, 5)  # temperate rail goods wagon (full + empty)
wagon('food', 2757, 0, 6)  # arctic rail food wagon (full + empty)
wagon('grain_empty', 2761, 0, 7)  # temperate rail grain wagon (empty)
wagon('wood_empty', 2765, 0, 8)  # temperate rail wood wagon (empty)
wagon('steel_paper_empty', 2769, 0, 9)  # temperate rail steel/paper wagon (empty)
wagon('ore_empty', 2773, 0, 10)  # temperate rail iron/coer ore wagon (empty)
wagon('valuables', 2777, 0, 11)  # temperate rail valuables wagon (full + empty)
wagon('coal_full', 2781, 1, 1)  # temperate rail coal wagon (full)
wagon('grain_full', 2785, 1, 7)  # temperate rail grain wagon (full)
wagon('wood_full', 2789, 1, 8)  # temperate rail wood wagon (full)
wagon('steel_full', 2793, 1, 9)  # temperate rail steel wagon (full)
wagon('iron_ore_full', 2797, 1, 10)  # temperate rail iron ore wagon (full)
wagon('paper_full', 2801, 2, 9)  # arctic rail paper wagon (full)
wagon('copper_ore_full', 2805, 1, 10)  # tropical rail copper ore wagon (full)
wagon('water', 2809, 0, 12)  # tropical rail water wagon (full + empty)
wagon('fruit_empty', 2813, 0, 13)  # tropical rail fruit wagon (empty)
wagon('fruit_full', 2817, 1, 13)  # tropical rail fruit wagon (full)
wagon('rubber_empty', 2821, 0, 14)  # tropical rail rubber wagon (empty)
wagon('rubber_full', 2825, 1, 14)  # tropical rail rubber wagon (full)


def engine(name, sprite_id, tmpl, x, y):
    lib.SpriteCollection(name) \
        .add(VEHICLE_DIR / 'rail_engines_temperate_2x.ase', tmpl, ZOOM_2X, x, y) \
        .replace_old(sprite_id)


engine('jubilee_sh8p', 2905, tmpl_vehicle_rail_8view, 0, 0)  # Chaney Jubilee + SH 8P (Steam)
engine('ginzu', 2913, tmpl_vehicle_rail_8view, 0, 1)  # Ginzu A4 (Steam)
engine('kirby', 2921, tmpl_vehicle_rail_8view, 0, 2)  # Kirby Paul (Steam)
engine('sh25_floss47', 2929, tmpl_vehicle_rail_4view, 0, 3)  # SH/Hendry 25 + Floss 47 (Diesel)
engine('uu37', 2933, tmpl_vehicle_rail_4view, 0, 4)  # UU/37 (Diesel)
engine('sh30_sh40', 2937, tmpl_vehicle_rail_4view, 0, 5)  # SH/30 + SH/40 (Diesel)
engine('sh_125', 2941, tmpl_vehicle_rail_8view, 0, 6)  # SH 125 (Diesel)
engine('manley', 2949, tmpl_vehicle_rail_8view, 0, 7)  # Manley-Morel VT (Diesel)
engine('dash', 2957, tmpl_vehicle_rail_8view, 0, 8)  # Dash (Diesel)
engine('asia', 2965, tmpl_vehicle_rail_8view, 0, 9)  # Asia Star (Electric)
engine('tim', 2973, tmpl_vehicle_rail_8view, 0, 10)  # T.I.M. (Electric)

# engine('', 2981, tmpl_vehicle_rail_4view, 0, 0)  # X2001
# engine('', 2985, tmpl_vehicle_rail_8view, 0, 1)  # Millenium

# engine('', 2993, tmpl_vehicle_rail_8view, 0, 2)  # Lev3 Pegasus
# engine('', 3001, tmpl_vehicle_rail_8view, 0, 3)  # Lev4 Chimaera
# engine('', 3009, tmpl_vehicle_rail_4view, 0, 0)  # Lev1 Leviathan
# engine('', 3013, tmpl_vehicle_rail_4view, 0, 1)  # Lev2 Cyclops


# ------------------------------ Road Infrastructure ------------------------------

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
    .add(lib.aseidx(INFRA_DIR / 'road_town_2x.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 0, 0)

road = lib.SpriteCollection('road') \
    .add(lib.aseidx(INFRA_DIR / 'road_2x.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 0, 0, thin=False) \
    .add(lib.aseidx(INFRA_DIR / 'road_2x_thin.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 0, 0, thin=True) \
    .add(INFRA_DIR / 'road_noline_2x.ase',
         tmpl_roadtiles, ZOOM_2X, 0, 0, climate=TROPICAL)

ROAD_COMPOSITION = list(zip([0] * 11, range(11))) + list(zip((12, 6, 3, 9), range(15, 19))) + list(zip([0] * 4, range(11, 15)))
road_town.compose_on(general_concrete, ROAD_COMPOSITION).replace_old(1313)
road.compose_on(ground, ROAD_COMPOSITION).replace_old(1332)

# TODO do not replace in non-tropical
road.compose_on(tropical_desert, ROAD_COMPOSITION).replace_old(1351)


def subtmpl_house_1x1(suffix, func, x, y, h, ox=0, oy=0, **kw):
    z = 2
    # OpenGFX2 uses h = h * z - z + 1 and
    # yofs = 32 * z - h * z + oy * z - (z - 1) // 2 - 1
    xofs = -31 * z + ox * z
    yofs = (31 - h) * z + oy * z
    return func(
        suffix,
        1 * z + x * z, 1 * z + y * z, 64 * z, h * z + z - 1,
        xofs=xofs, yofs=yofs,
        **kw
    )


@lib.template(lib.CCReplacingFileSprite)
def tmpl_road_depot_old(func, z):
    kw_front = {'ignore_layers': 'Behind'}
    kw_back = {'layers': 'Behind'}
    return [
        subtmpl_house_1x1('se_back', func, 0, 0, 64, 0, 1, **kw_back),
        subtmpl_house_1x1('se_front', func, 0, 0, 64, 30, -14, **kw_front),
        subtmpl_house_1x1('sw_back', func, 0, 65, 64, 0, 1, **kw_back),
        subtmpl_house_1x1('sw_front', func, 0, 65, 64, -30, -14, **kw_front),
        subtmpl_house_1x1('ne', func, 0, 195, 64, -30, -14, **kw_front),
        subtmpl_house_1x1('nw', func, 0, 130, 64, 30, -14, **kw_front),
    ]


@lib.template(lib.CCReplacingFileSprite)
def tmpl_road_depot(func, z):
    # bb values are (dx, dy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/road_land.h
    grid = lib.house_grid(func=func, height=75, z=z)
    back_layer = 'Behind'
    return [
        grid('se_back', (0, 0), bb=(0, 0), layers=back_layer),
        grid('se_front', (0, 0), bb=(15, 0), ignore_layers=back_layer),
        grid('sw_back', (1, 0), bb=(0, 0), layers=back_layer),
        grid('sw_front', (1, 0), bb=(0, 15), ignore_layers=back_layer),
        grid('ne', (2, 0), bb=(0, 15), ignore_layers=back_layer),
        grid('nw', (3, 0), bb=(15, 0), ignore_layers=back_layer),
    ]


lib.SpriteCollection('road_depot') \
    .add(STATION_DIR / 'roaddepots_2x_newlayout.ase',
         tmpl_road_depot, ZOOM_2X, thin=False) \
    .add(STATION_DIR / 'roaddepots_2x_thin.ase',
         tmpl_road_depot_old, ZOOM_2X, thin=True) \
    .replace_old(1408)


@lib.template(lib.CCReplacingFileSprite)
def tmpl_truck_stop(func, z):
    # TODO cut front wals out of the back sprites for better transparency
    # bb values are (dx, dy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/station_land.h
    grid = lib.house_grid(func=func, height=75, z=z)
    ne_pos, se_pos, sw_pos, nw_pos = (2, 0), (0, 0), (1, 0), (3, 0)
    return [
        grid('ne_ground', ne_pos, layers='Tile/*'),
        grid('se_ground', se_pos, layers='Tile/*'),
        grid('sw_ground', sw_pos, layers='Tile/*'),
        grid('nw_ground', nw_pos, layers='Tile/*'),

        grid('ne_wall_se', ne_pos, bb=(0, 15), layers='FacingNE/SE/*'),
        grid('se_wall_sw', se_pos, bb=(15, 3), layers='FacingSE/SW/*'),
        grid('sw_wall_nw', sw_pos, bb=(3, 0), layers='FacingSW/NW/*'),
        grid('nw_wall_ne', nw_pos, bb=(0, 0), layers='FacingNW/NE/*'),

        grid('ne_wall_sw', ne_pos, bb=(13, 0), layers='FacingNE/SW/*'),
        grid('se_wall_nw', se_pos, bb=(0, 0), layers='FacingSE/NW/*'),
        grid('sw_wall_ne', sw_pos, bb=(0, 0), layers='FacingSW/NE/*'),
        grid('nw_wall_se', nw_pos, bb=(0, 13), layers='FacingNW/SE/*'),

        grid('ne_wall_nw', ne_pos, bb=(2, 0), layers='FacingNE/NW/*'),
        grid('se_wall_ne', se_pos, bb=(0, 3), layers='FacingSE/NE/*'),
        grid('sw_wall_se', sw_pos, bb=(3, 15), layers='FacingSW/SE/*'),
        grid('nw_wall_sw', nw_pos, bb=(15, 2), layers='FacingNW/SW/*'),

        grid('dt_y_wall_s', (4, 0), bb=(13, 0), layers='DriveTroughY NW-SE/S/*'),
        grid('dt_y_wall_n', (4, 0), bb=(0, 0), layers='DriveTroughY NW-SE/N/*'),
        grid('dt_x_wall_n', (5, 0), bb=(0, 0), layers='DriveTroughX SW-NE/N/*'),
        grid('dt_x_wall_s', (5, 0), bb=(0, 13), layers='DriveTroughX SW-NE/S/*'),
    ]

truck_stops = lib.SpriteCollection('truck_stop') \
    .add(STATION_DIR / 'truckstop_2x.ase', tmpl_truck_stop, ZOOM_2X)
truck_stops[:16].replace_old(2708)
truck_stops[16:].replace_new(0x11, 4)


@lib.template(lib.CCReplacingFileSprite)
def tmpl_bus_stop(func, z):
    # TODO cut front wals out of the back sprites for better transparency
    # bb values are (dx, dy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/station_land.h
    # NOTE only diffence from truck template is bb and layer names same bb for x/y views though
    grid = lib.house_grid(func=func, height=75, z=z)
    ne_pos, se_pos, sw_pos, nw_pos = (2, 0), (0, 0), (1, 0), (3, 0)
    return [
        grid('ne_ground', ne_pos, layers='Road?'),
        grid('se_ground', se_pos, layers='Road?'),
        grid('sw_ground', sw_pos, layers='Road?'),
        grid('nw_ground', nw_pos, layers='Road?'),

        grid('ne_wall_se', ne_pos, bb=(2, 0), layers='SE Orange'),
        grid('se_wall_sw', se_pos, bb=(0, 3), layers='SW Red'),
        grid('sw_wall_nw', sw_pos, bb=(3, 15), layers='NW Yellow'),
        grid('nw_wall_ne', nw_pos, bb=(15, 2), layers='NE Green'),

        grid('ne_wall_sw', ne_pos, bb=(13, 0), layers='SW Red'),
        grid('se_wall_nw', se_pos, bb=(0, 0), layers='NW Yellow'),
        grid('sw_wall_ne', sw_pos, bb=(0, 0), layers='NE Green'),
        grid('nw_wall_se', nw_pos, bb=(0, 13), layers='SE Orange'),

        grid('ne_wall_nw', ne_pos, bb=(0, 13), layers='NW Yellow'),
        grid('se_wall_ne', se_pos, bb=(13, 3), layers='NE Green'),
        grid('sw_wall_se', sw_pos, bb=(3, 0), layers='SE Orange'),
        grid('nw_wall_sw', nw_pos, bb=(0, 0), layers='SW Red'),

        grid('dt_y_wall_s', (4, 0), bb=(13, 0), layers='SW Red'),
        grid('dt_y_wall_n', (4, 0), bb=(0, 0), layers='NE Green'),
        grid('dt_x_wall_n', (5, 0), bb=(0, 0), layers='NW Yellow'),
        grid('dt_x_wall_s', (5, 0), bb=(0, 13), layers='SE Orange'),
    ]


bus_stops = lib.SpriteCollection('bus_stop') \
    .add(STATION_DIR / 'busstop_2x.ase', tmpl_bus_stop, ZOOM_2X)
bus_stops[:16].replace_old(2692)
bus_stops[16:].replace_new(0x11, 0)


# ------------------------------ Water ------------------------------

@lib.template(grf.FileSprite)
def tmpl_water(funcs, z, suffix, x):
    magenta, mask = funcs
    func = lambda *args, **kw: lib.MagentaAndMask(magenta(*args, **kw), mask(*args, **kw))
    return [func(suffix, z * (1 + x), z, 64 * z, 32 * z - 1, xofs=-31 * z, yofs=0)]


@lib.template(grf.FileSprite)
def tmpl_water_full(sprite_func, z):
    x = y = 0
    func = lambda *args, **kw: lib.MagentaAndMask(sprite_func(*args, **kw), sprite_func(*args, **kw, layers='Animated'))
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
    .add(TERRAIN_DIR / 'shorelines_2x.ase',
         tmpl_water_full, ZOOM_2X)
water[0].replace_old(4061)


WATER_COMPOSITION = [(x, x) for x in [16, 1, 2, 3, 4, 17, 6, 7, 8, 9, 15, 11, 12, 13, 14, 18]]
water.compose_on(ground, WATER_COMPOSITION).replace_new(0x0d, 0)


# ------------------------------ Industries ------------------------------

@lib.template(grf.FileSprite)
def tmpl_forest(func, z):
    grid = lib.house_grid(func=func, height=75, z=z)
    ground_layers = ('Tile Shadow 64', 'Tile Grid', 'Tile Solid Green')
    return [
        grid('growth1', (0, 0), frame=0, ignore_layers=ground_layers),
        grid('growth2', (0, 0), frame=1, ignore_layers=ground_layers),
        grid('growth3', (0, 0), frame=2, ignore_layers=ground_layers),
        grid('grown', (0, 0), frame=3, ignore_layers=ground_layers),
        grid('logs', (0, 0), frame=4, ignore_layers=ground_layers),
        grid('ground', (0, 0), layers=ground_layers + ('Spriteborder',)),
    ]

# TODO Why are 128/322 forest sprites too?
# TODO remove climate=TEMPERATE? (but ensure the right order)
lib.SpriteCollection('forest') \
    .add(INDUSTRY_DIR / 'forest_temperate.ase', tmpl_forest, ZOOM_2X, climate=TEMPERATE) \
    .replace_old(2072)
    # .add(INDUSTRY_DIR / 'forest.ase', tmpl_forest, ZOOM_2X, 76, climate=ARCTIC) \


@lib.template(grf.FileSprite)
def tmpl_sawmill(func, z):
    # bb values are (sx, sy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/industry_land.h
    grid = lib.house_grid(func=func, height=75, z=z)
    return [
        grid('building1_stage1', (0, 0), bb=(1, 0), frame=0),
        grid('building1_stage2', (0, 0), bb=(1, 0), frame=1),
        grid('building1_stage3', (0, 0), bb=(1, 0), frame=2),
        grid('building2_stage1', (1, 0), bb=(0, 1), frame=0),
        grid('building2_stage2', (1, 0), bb=(0, 1), frame=1),
        grid('building2_stage3', (1, 0), bb=(0, 1), frame=2),
        grid('building3_stage1', (2, 0), bb=(1, 1), frame=0),
        grid('building3_stage2', (2, 0), bb=(1, 1), frame=1),
        grid('building3_stage3', (2, 0), bb=(1, 1), frame=2),
        grid('logs1', (3, 0), frame=2),
        grid('logs2', (4, 0), bb=(0, 1), frame=2)
    ]


lib.SpriteCollection('sawmill') \
    .add(lib.aseidx(INDUSTRY_DIR / 'sawmill.ase'), tmpl_sawmill, ZOOM_2X) \
    .replace_old(2061)

# ------------------------------ Sprite Replacement Magic ------------------------------

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


offset_sprites = set()
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
    # for c, (f, a) in lib.old_sprites_collection.get(mode, {}).items():
    #     print(f'    OLD {f} {c.name} {a}')
    # for set_type, cd in lib.new_sprites_collection[mode].items():
    #     for c, (f, a) in cd.items():
    #         print(f'    NEW [{set_type}]+{f} {c.name} {a}')

    def add_global_offset(sprites):
        global offset_sprites
        for s in sprites:
            if id(s) in offset_sprites:
                continue
            s.yofs -= 1
            offset_sprites.add(id(s))

    if ranges:
        g.add(grf.ReplaceOldSprites([(offset, len(sprites)) for offset, sprites in ranges]))
        for offset, sprites in ranges:
            add_global_offset(sprites)
            g.add(*sprites)
            for i, sa in enumerate(sprites):
                names = ', '.join(s.name for s in (sa.sprites if isinstance(sa, grf.AlternativeSprites) else (sa,)))

    for set_type, sprite_dict in lib.new_sprites[mode].items():
        for offset, sprites in group_ranges(sprite_dict):
            g.add(grf.ReplaceNewSprites(set_type, len(sprites), offset=offset))
            add_global_offset(sprites)
            g.add(*sprites)
            for i, sa in enumerate(sprites):
                names = ', '.join(s.name for s in (sa.sprites if isinstance(sa, grf.AlternativeSprites) else (sa,)))

    if has_if:
        g.add(grf.Label(0, b''))


# ------------------------------ Command Line Interface ------------------------------

def cmd_debugcc_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')


def cmd_debugcc_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file)
    sprite = lib.CCReplacingFileSprite(ase, 0, 0, None, None, name=args.ase_file, layers=args.layer)
    lib.debug_cc_recolour([sprite], horizontal=args.horizontal)


def cmd_debuglight_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')


def cmd_debuglight_handler(g, grf_file, args):
    in_file = args.ase_file
    ase = lib.AseImageFile(in_file)
    aseo = lib.AseImageFile(in_file)
    sprite = grf.FileSprite(ase, 0, 0, None, None, name=f'{in_file}_image', ignore_layers='Light order')
    order = grf.FileSprite(aseo, 0, 0, None, None, name=f'{in_file}_order', layers='Light order')
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
