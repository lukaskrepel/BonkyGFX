import itertools
import pathlib
from typing import Optional, Union

from typeguard import typechecked

import grf
from grf import ZOOM_NORMAL, ZOOM_2X, ZOOM_4X, TEMPERATE, ARCTIC, TROPICAL, TOYLAND, ALL_CLIMATES

import lib

cc = lib.MagentaToCC

SPRITE_DIR = pathlib.Path('sprites')
TERRAIN_DIR = SPRITE_DIR / 'terrain'
VEHICLE_DIR = SPRITE_DIR / 'vehicles'
INFRA_DIR = SPRITE_DIR / 'infrastructure'
INDUSTRY_DIR = SPRITE_DIR / 'industries'
TOWN_DIR = SPRITE_DIR / 'towns'
STATION_DIR = SPRITE_DIR / 'stations'
TREE_DIR = SPRITE_DIR / 'trees'
EFFECT_DIR = SPRITE_DIR / 'effects'
ICON_DIR = SPRITE_DIR / 'icons'


g = grf.NewGRF(
    grfid=b'TODO',
    name='BonkyGFX',
    description='BonkyGFX',
    min_compatible_version=0,
    version=0,
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
def tmpl_groundtiles(func, z, frame=1):
    # TODO grid = lib.FlexGrid(func=func, padding=2, add_yofs=-(z // 2), start=(0, z * y))
    grid = lib.FlexGrid(func=func, padding=z, start=(0, 0))
    grid.set_default(width=64 * z, height=32 * z - 1, xofs=-31 * z, yofs=0, frame=frame)

    return [
        grid('flat'),
        grid('w'),
        grid('s', height=24 * z - 1),
        grid('sw', height=24 * z - 1),

        grid('e'),
        grid('ew'),
        grid('se', height=24 * z - 1),
        grid('wse', height=24 * z - 1),

        grid('n', height=40 * z - 1, yofs=-8 * z),
        grid('nw', height=40 * z - 1, yofs=-8 * z),
        grid('ns', yofs=-8 * z),
        grid('nws', yofs=-8 * z),

        grid('ne', height=40 * z - 1, yofs=-8 * z),
        grid('enw', height=40 * z - 1, yofs=-8 * z),
        grid('sen', yofs=-8 * z),

        grid('steep_n', height=48 * z - 1, yofs=-16 * z),
        grid('steep_s', height=16 * z - 1),
        grid('steep_w', yofs=-8 * z),
        grid('steep_e', yofs=-8 * z),
    ]


def tmpl_groundtiles_extra(name, paths, zoom):
    @lib.template(grf.FileSprite)
    def tmpl_extra(func, z):
        assert z == 2
        grid = lib.FlexGrid(func=func, padding=z, start=(1235 * z, 0))
        # TODO grid = lib.FlexGrid(func=func, padding=2, add_yofs=-(z // 2), start=(1235 * z, 0))
        grid.set_default(width=64 * z, height=32 * z - 1, xofs=-31 * z, yofs=0, frame=1)
        return [
            grid('extra1'),
            grid('extra2'),
            grid('extra3'),
            grid('extra4'),
        ]
    return tmpl_groundtiles(name, paths, zoom) + tmpl_extra(name, paths, zoom)


# Normal land
make_ground = lambda name, frame: lib.SpriteCollection(name) \
    .add(lib.aseidx(TERRAIN_DIR / 'temperate_groundtiles_2x.ase'),
         tmpl_groundtiles, ZOOM_2X, frame, climate=TEMPERATE) \
    .add(TERRAIN_DIR / 'tropical_groundtiles_2x.ase',
         tmpl_groundtiles, ZOOM_2X, frame, climate=TROPICAL) \
    .add(TERRAIN_DIR / 'arctic_groundtiles_2x.ase',
         tmpl_groundtiles, ZOOM_2X, frame, climate=ARCTIC)
ground = make_ground('ground', 1)
make_ground('ground_bare', 4).replace_old(3924)  # 0% grass
make_ground('ground_33', 3).replace_old(3943)   # 33% grass
make_ground('ground_66', 2).replace_old(3962)   # 66% grass
ground.replace_old(3981)  # 100% grass

lib.SpriteCollection('temperate_rough') \
    .add(TERRAIN_DIR / 'temperate_groundtiles_rough_2x.ase',
         tmpl_groundtiles_extra, ZOOM_2X) \
    .replace_old(4000)

lib.SpriteCollection('temperate_rocks') \
    .add(TERRAIN_DIR / 'temperate_groundtiles_rocks_2x.ase',
         tmpl_groundtiles, ZOOM_2X) \
    .replace_old(4023)

for i in range(9):
    lib.SpriteCollection(f'farmland{i}') \
        .add(TERRAIN_DIR / 'farmtiles_2x.ase', tmpl_groundtiles, ZOOM_2X, i + 1) \
        .replace_old(4126 + 19 * i)

tropical_desert = lib.SpriteCollection('tropical_desert') \
    .add(TERRAIN_DIR / 'tropical_groundtiles_desert_2x.ase',
         tmpl_groundtiles, ZOOM_2X) \
    .replace_old(4550, climate=TROPICAL)

lib.SpriteCollection('tropical_transitions') \
    .add(TERRAIN_DIR / 'tropical_groundtiles_deserttransition_2x.ase',
         tmpl_groundtiles, ZOOM_2X) \
    .replace_old(4512, climate=TROPICAL)

general_concrete = lib.SpriteCollection('general_concrete') \
    .add(lib.aseidx(TERRAIN_DIR / 'general_concretetiles_2x.ase', colourkey=(0, 0, 255)),
        tmpl_groundtiles, ZOOM_2X)
general_concrete[0].replace_old(1420)


# ------------------------------ Airport Tiles ------------------------------

@lib.template(grf.FileSprite)
def tmpl_airport_tiles(func, z):
    grid = lib.FlexGrid(func=func, padding=2)  # TODO add_yofs=-(z // 2)
    grid.set_default(width=64 * z, height=32 * z - 1, xofs=-31 * z, yofs=0)
    kw_default = {'ignore_layers': 'ANIMATED/*'}
    kw_light = {'layers': 'ANIMATED/*'}

    def with_light(*args, **kw):
        return lib.AlphaAndMask(
            grid(*args, **kw, **kw_default, keep_state=True),
            grid(*args, **kw, **kw_light)
        )

    sprites = [
        grid('apron', **kw_default),
        grid('stand', **kw_default),
        with_light('runway_a'),
        with_light('runway_b'),
        with_light('runway_c'),
        with_light('runway_d'),
        with_light('runway_end'),
        grid('taxi_ns_west', **kw_default),
        grid('taxi_ew_south', **kw_default),
        grid('taxi_xing_south', **kw_default),
        grid('taxi_xing_west', **kw_default),
        grid('taxi_ns_ctr', **kw_default),
        grid('taxi_xing_east', **kw_default),
        grid('taxi_ns_east', **kw_default),
        grid('taxi_ew_north', **kw_default),
        grid('taxi_ew_ctr', **kw_default),
        with_light('runway_y_a'),  # unused
        with_light('runway_y_b'),  # unused
        with_light('runway_y_c'),  # unused
        with_light('runway_y_d'),  # unused
        with_light('runway_y_end'),  # unused
        with_light('helipad', yofs = -15 * z),
        grid('new_helipad', **kw_default),
    ]

    # Rearrange to OpenTTD sprite order
    return [sprites[k] for k in (0, 1, 7, 8, 9, 10, 11, 12, 13, 14, 15, 2, 3, 4, 5, 6, 21, 22)]


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
        sprites.extend(tmpl(f'stage{i}', lib.aseidx(path), ZOOM_2X, i + 1))
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
    grid = lib.FlexGrid(func=func, padding=2, start=(x * 174 * z, y * 24 * z))  # TODO add_yofs=-(z // 2)
    grid.set_default(frame=frame)
    res = [
        grid('n', width=8 * z, height=23 * z, xofs=-3 * z, yofs=-15 * z),
        grid('ne', width=22 * z, height=19 * z, xofs=-15 * z, yofs=-10 * z),
        grid('e', width=31 * z, height=15 * z, xofs=-15 * z, yofs=-9 * z),
        grid('se', width=22 * z, height=19 * z, xofs=-7 * z, yofs=-10 * z),
        grid('s', width=8 * z, height=23 * z, xofs=-3 * z, yofs=-15 * z),
        grid('sw', width=22 * z, height=19 * z, xofs=-15 * z, yofs=-10 * z),
        grid('w', width=31 * z, height=15 * z, xofs=-15 * z, yofs=-9 * z),
        grid('nw', width=22 * z, height=19 * z, xofs=-7 * z, yofs=-10 * z),
    ]
    return res


def replace_rv_generation(path2x, generation):
    def tmpl(suffix, x, y):
        return lib.SpriteCollection(f'rv_gen{generation}_{suffix}') \
            .add(path2x, tmpl_vehicle_road_8view, ZOOM_2X, x, y, generation)

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
def tmpl_vehicle_rail_4view(func, z, y, frame, **kw):
    grid = lib.FlexGrid(func=func, padding=2, start=(0 * 87 * z, y * 24 * z))  # TODO add_yofs=-(z // 2)
    grid.set_default(frame=frame, **kw)
    return [
        grid( 'n', width= 8 * z, height=23 * z, xofs=-3 * z, yofs=-13 * z),
        grid('ne', width= 22 * z, height=19 * z, xofs=-15 * z, yofs=-12 * z),
        grid( 'e', width= 31 * z, height=15 * z, xofs=-16 * z, yofs=-9 * z),
        grid('se', width= 22 * z, height=19 * z, xofs=-7 * z, yofs=-12 * z),
    ]


@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_rail_8view(func, z, y, frame, **kw):
    grid = lib.FlexGrid(func=func, padding=2, start=(0 * 174 * z, y * 24 * z))  # TODO add_yofs=-(z // 2)
    grid.set_default(frame=frame, **kw)
    x = 0
    return [
        grid( 'n', width=8 * z, height=23 * z, xofs=-3 * z, yofs=-13 * z),
        grid('ne', width=22 * z, height=19 * z, xofs=-15 * z, yofs=-12 * z),
        grid( 'e', width=31 * z, height=15 * z, xofs=-16 * z,  yofs=-9 * z),
        grid('se', width=22 * z, height=19 * z, xofs=-7 * z, yofs=-12 * z),
        grid( 's', width=8 * z, height=23 * z, xofs=-3 * z, yofs=-13 * z),
        grid('sw', width=22 * z, height=19 * z, xofs=-15 * z, yofs=-12 * z),
        grid( 'w', width=31 * z, height=15 * z, xofs=-16 * z,  yofs=-9 * z),
        grid('nw', width=22 * z, height=19 * z, xofs=-7 * z, yofs=-12 * z),
    ]


def wagon(name, sprite_id, y, *, frame):
    lib.SpriteCollection('wagon_' + name) \
        .add(VEHICLE_DIR / 'rail_wagons_2x.ase', tmpl_vehicle_rail_4view, ZOOM_2X, y, frame) \
        .replace_old(sprite_id)


wagon('passengers', 2733, 0, frame=1)  # temperate rail passenger wagon (full + empty)
wagon('coal_empty', 2737, 1, frame=1 )  # temperate rail coal wagon (empty)
wagon('mail', 2741, 2, frame=1)  # temperate rail mail wagon (full + empty)
wagon('oil', 2745, 3, frame=1)  # temperate rail oil wagon (full + empty)
wagon('livestock', 2749, 4, frame=1)  # temperate rail livestock wagon (full + empty)
wagon('goods', 2753, 5, frame=1)  # temperate rail goods wagon (full + empty)
wagon('food', 2757, 6, frame=1)  # arctic rail food wagon (full + empty)
wagon('grain_empty', 2761, 7, frame=1)  # temperate rail grain wagon (empty)
wagon('wood_empty', 2765, 8, frame=1)  # temperate rail wood wagon (empty)
wagon('steel_paper_empty', 2769, 9, frame=1)  # temperate rail steel/paper wagon (empty)
wagon('ore_empty', 2773, 10, frame=1)  # temperate rail iron/coer ore wagon (empty)
wagon('valuables', 2777, 11, frame=1)  # temperate rail valuables wagon (full + empty)
wagon('coal_full', 2781, 1, frame=2)  # temperate rail coal wagon (full)
wagon('grain_full', 2785, 7, frame=2)  # temperate rail grain wagon (full)
wagon('wood_full', 2789, 8, frame=2)  # temperate rail wood wagon (full)
wagon('steel_full', 2793, 9, frame=2)  # temperate rail steel wagon (full)
wagon('iron_ore_full', 2797, 10, frame=2)  # temperate rail iron ore wagon (full)
wagon('paper_full', 2801, 9, frame=3)  # arctic rail paper wagon (full)
wagon('copper_ore_full', 2805, 10, frame=2)  # tropical rail copper ore wagon (full)
wagon('water', 2809, 12, frame=1)  # tropical rail water wagon (full + empty)
wagon('fruit_empty', 2813, 13, frame=1)  # tropical rail fruit wagon (empty)
wagon('fruit_full', 2817, 13, frame=2)  # tropical rail fruit wagon (full)
wagon('rubber_empty', 2821, 14, frame=1)  # tropical rail rubber wagon (empty)
wagon('rubber_full', 2825, 14, frame=2)  # tropical rail rubber wagon (full)


def engine(name, sprite_id, tmpl, y):
    lib.SpriteCollection(name) \
        .add(VEHICLE_DIR / 'rail_engines_temperate_2x.ase', tmpl, ZOOM_2X, y, 0) \
        .replace_old(sprite_id)


engine('jubilee_sh8p', 2905, tmpl_vehicle_rail_8view, 0)  # Chaney Jubilee + SH 8P (Steam)
engine('ginzu', 2913, tmpl_vehicle_rail_8view, 1)  # Ginzu A4 (Steam)
engine('kirby', 2921, tmpl_vehicle_rail_8view, 2)  # Kirby Paul (Steam)
engine('sh25_floss47', 2929, tmpl_vehicle_rail_4view, 3)  # SH/Hendry 25 + Floss 47 (Diesel)
engine('uu37', 2933, tmpl_vehicle_rail_4view, 4)  # UU/37 (Diesel)
engine('sh30_sh40', 2937, tmpl_vehicle_rail_4view, 5)  # SH/30 + SH/40 (Diesel)
engine('sh_125', 2941, tmpl_vehicle_rail_8view, 6)  # SH 125 (Diesel)
engine('manley', 2949, tmpl_vehicle_rail_8view, 7)  # Manley-Morel VT (Diesel)
engine('dash', 2957, tmpl_vehicle_rail_8view, 8)  # Dash (Diesel)
engine('asia', 2965, tmpl_vehicle_rail_8view, 9)  # Asia Star (Electric)
engine('tim', 2973, tmpl_vehicle_rail_8view, 10)  # T.I.M. (Electric)

# engine('', 2981, tmpl_vehicle_rail_4view, 0, 0)  # X2001
# engine('', 2985, tmpl_vehicle_rail_8view, 0, 1)  # Millenium

# engine('', 2993, tmpl_vehicle_rail_8view, 0, 2)  # Lev3 Pegasus
# engine('', 3001, tmpl_vehicle_rail_8view, 0, 3)  # Lev4 Chimaera
# engine('', 3009, tmpl_vehicle_rail_4view, 0, 0)  # Lev1 Leviathan
# engine('', 3013, tmpl_vehicle_rail_4view, 0, 1)  # Lev2 Cyclops


# ------------------------------ Road Infrastructure ------------------------------

@lib.template(grf.FileSprite)
def tmpl_roadtiles(func, z, frame, **kw):
    grid = lib.FlexGrid(func=func, padding=2)  # TODO add_yofs=-(z // 2)
    grid.set_default(frame=frame, width=64 * z, height=32 * z - 1, xofs=-31 * z, yofs=0, **kw)
    return [
        grid('y'),
        grid('x'),
        grid('full'),
        grid('t_y_ne'),
        grid('t_x_nw'),
        grid('t_y_sw'),
        grid('t_x_se'),
        grid('w'),
        grid('n'),
        grid('e'),
        grid('s'),

        grid('sw'),
        grid('nw'),
        grid('ne'),
        grid('se'),

        grid('slope_ne', height=40 * z - 1, yofs=-8 * z),
        grid('slope_se', height=24 * z - 1),
        grid('slope_sw', height=24 * z - 1),
        grid('slope_nw', height=40 * z - 1, yofs=-8 * z),
    ]


road_town = lib.SpriteCollection('road_town') \
    .add(lib.aseidx(INFRA_DIR / 'road_town_2x.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 1)

road = lib.SpriteCollection('road') \
    .add(lib.aseidx(INFRA_DIR / 'road_2x.ase', colourkey=(0, 0, 255)),
         tmpl_roadtiles, ZOOM_2X, 1) \
    .add(INFRA_DIR / 'road_noline_2x.ase',
         tmpl_roadtiles, ZOOM_2X, 1, climate=TROPICAL)

ROAD_COMPOSITION = list(zip([0] * 11, range(11))) + list(zip((12, 6, 3, 9), range(15, 19))) + list(zip([0] * 4, range(11, 15)))
road_town.compose_on(general_concrete, ROAD_COMPOSITION).replace_old(1313)
road.compose_on(ground, ROAD_COMPOSITION).replace_old(1332)

# TODO do not replace in non-tropical
road.compose_on(tropical_desert, ROAD_COMPOSITION).replace_old(1351)


@lib.template(lib.CCReplacingFileSprite)
def tmpl_road_depot(func, z):
    # bb values are (dx, dy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/road_land.h
    grid = lib.HouseGrid(func=func, height=75, z=z)
    back_kw = {'layers': ('Behind', 'Spriteborder')}
    front_kw = {'ignore_layers': ('Behind',)}
    return [
        grid('se_back', (0, 0), bb=(0, 0), **back_kw),
        grid('se_front', (0, 0), bb=(15, 0), **front_kw),
        grid('sw_back', (1, 0), bb=(0, 0), **back_kw),
        grid('sw_front', (1, 0), bb=(0, 15), **front_kw),
        grid('ne', (2, 0), bb=(0, 15), **front_kw),
        grid('nw', (3, 0), bb=(15, 0), **front_kw),
    ]


lib.SpriteCollection('road_depot') \
    .add(STATION_DIR / 'roaddepots_2x.ase',
         tmpl_road_depot, ZOOM_2X) \
    .replace_old(1408)


@lib.template(lib.CCReplacingFileSprite)
def tmpl_truck_stop(func, z):
    # TODO cut front wals out of the back sprites for better transparency
    # bb values are (dx, dy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/station_land.h
    grid = lib.HouseGrid(func=func, height=75, z=z)
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
    # NOTE it's different from truck stop in bb and wall order (same in x/y views though)
    grid = lib.HouseGrid(func=func, height=75, z=z)
    ne_pos, se_pos, sw_pos, nw_pos = (2, 0), (0, 0), (1, 0), (3, 0)
    return [
        grid('ne_ground', ne_pos, layers='Tile/*'),
        grid('se_ground', se_pos, layers='Tile/*'),
        grid('sw_ground', sw_pos, layers='Tile/*'),
        grid('nw_ground', nw_pos, layers='Tile/*'),

        grid('ne_wall_nw', ne_pos, bb=(2, 0), layers='FacingNE/NW/*'),
        grid('se_wall_ne', se_pos, bb=(0, 3), layers='FacingSE/NE/*'),
        grid('sw_wall_se', sw_pos, bb=(3, 15), layers='FacingSW/SE/*'),
        grid('nw_wall_sw', nw_pos, bb=(15, 2), layers='FacingNW/SW/*'),

        grid('ne_wall_sw', ne_pos, bb=(13, 0), layers='FacingNE/SW/*'),
        grid('se_wall_nw', se_pos, bb=(0, 0), layers='FacingSE/NW/*'),
        grid('sw_wall_ne', sw_pos, bb=(0, 0), layers='FacingSW/NE/*'),
        grid('nw_wall_se', nw_pos, bb=(0, 13), layers='FacingNW/SE/*'),

        grid('ne_wall_se', ne_pos, bb=(0, 13), layers='FacingNE/SE/*'),
        grid('se_wall_sw', se_pos, bb=(13, 3), layers='FacingSE/SW/*'),
        grid('sw_wall_nw', sw_pos, bb=(3, 0), layers='FacingSW/NW/*'),
        grid('nw_wall_ne', nw_pos, bb=(0, 0), layers='FacingNW/NE/*'),

        grid('dt_y_wall_s', (4, 0), bb=(13, 0), layers='DriveTroughY NW-SE/S/*'),
        grid('dt_y_wall_n', (4, 0), bb=(0, 0), layers='DriveTroughY NW-SE/N/*'),
        grid('dt_x_wall_n', (5, 0), bb=(0, 0), layers='DriveTroughX SW-NE/N/*'),
        grid('dt_x_wall_s', (5, 0), bb=(0, 13), layers='DriveTroughX SW-NE/S/*'),
    ]


bus_stops = lib.SpriteCollection('bus_stop') \
    .add(STATION_DIR / 'busstop_2x.ase', tmpl_bus_stop, ZOOM_2X)
bus_stops[:16].replace_old(2692)
bus_stops[16:].replace_new(0x11, 0)

# ------------------------------ Rail infrastructure ------------------------------

@lib.template(grf.FileSprite)
def tmpl_rails(func, z, layers):
    grid = lib.FlexGrid(func=func, padding=2)
    grid.set_default(width=64 * z, height = 32 * z - 1, xofs=-31 * z, yofs=0, layers=layers)
    return list(map(grid, ('y', 'x', 'n', 's', 'e', 'w', 'cross')))


@lib.template(grf.FileSprite)
def tmpl_ballast(func, z, layers):
    grid = lib.FlexGrid(func=func, padding=2, start=(910, 0))
    grid.set_default(width=64 * z, height = 32 * z - 1, xofs=-31 * z, yofs=0, layers=layers)
    return list(map(grid, ('ground_tne', 'ground_tsw', 'ground_tnw', 'ground_tse', 'ground_x')))


rails = lib.SpriteCollection('rail') \
    .add(INFRA_DIR / 'rail_2x.ase', tmpl_rails, ZOOM_2X, ('RAILS/*', 'SLEEPERS_ODD/*','SLEEPERS/*', 'SHADOW/*'))
rail_overlays = lib.SpriteCollection('rail_overlays') \
    .add(INFRA_DIR / 'rail_2x.ase', tmpl_rails, ZOOM_2X, ('RAILS/*',))
# sleepers = lib.SpriteCollection('rail_overlays') \
#     .add(INFRA_DIR / 'rail_2x.ase', tmpl_rails, ZOOM_2X, ('SLEEPERS_ODD/*','SLEEPERS/*'))
ballast = lib.SpriteCollection('ballast') \
    .add(INFRA_DIR / 'rail_2x.ase', tmpl_ballast, ZOOM_2X, ('BALLAST/*',))

rail_overlays.pick(1, 0, 2, 3, 4, 5).replace_old(1005)
rails[:7].compose_on(ground[0]).replace_old(1011)
# (ground[0] * 5).replace_old(1018)
# rails[7:].compose_on(ground[0]).replace_old(1018)
ballast.compose_on(ground[0]).replace_old(1018)
rails[3].compose_on(rails[2]).compose_on(ground[0]).replace_old(1035)  # double diagonal tile Y
rails[5].compose_on(rails[4]).compose_on(ground[0]).replace_old(1036)  # double diagonal tile X


@lib.template(grf.FileSprite)
def tmpl_rail_fences(func, z):
    assert z == 2  # xofs/yofs are fixed
    relative = 2
    x_xofs, x_yofs = -59 - relative, -12 - relative // 2
    y_xofs, y_yofs = -3 + relative, -12 - relative // 2
    grid = lib.FlexGrid(func=func, padding=2)
    return [
        cc(grid('flat_x', width=33 * z, height=22 * z, xofs=x_xofs, yofs=x_yofs)),
        cc(grid('flat_y', width=33 * z, height=22 * z, xofs=y_xofs, yofs=y_yofs)),
        cc(grid('vert', width=3 * z, height=38 * z, xofs=0, yofs=-40)),
        cc(grid('hor', width=65 * z, height=6 * z, xofs=-61, yofs=-8)),
        cc(grid('low_x', width=33 * z, height=28 * z, xofs=x_xofs, yofs=x_yofs + 16)),
        cc(grid('low_y', width=33 * z, height=28 * z, xofs=y_xofs, yofs=y_yofs + 16)),
        cc(grid('high_x', width=33 * z, height=30 * z, xofs=x_xofs, yofs=x_yofs - 16)),
        cc(grid('high_y', width=33 * z, height=30 * z, xofs=y_xofs, yofs=y_yofs - 16)),
    ]


lib.SpriteCollection('rail_fence') \
    .add(INFRA_DIR / 'rail_fences_2x.ase', tmpl_rail_fences, ZOOM_2X) \
    .replace_old(1301)


# ------------------------------ Water ------------------------------

@lib.template(grf.FileSprite)
def tmpl_water_full(sprite_func, z):
    # TODO switch to grid and add z // 2 yofs
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


# ------------------------------ Towns ------------------------------

@lib.template(grf.FileSprite)
def tmpl_statues(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    return [
        grid('statue', (0, 0), bb=(6, 5)),
        grid('fountain', (1, 0), bb=(3, 3)),
        lib.MagentaToCC(grid('owner_statue', (2, 0), bb=(0, 0))),
    ]

statues = lib.SpriteCollection('house') \
    .add(lib.aseidx(TOWN_DIR / 'statues_2x.ase'), tmpl_statues, ZOOM_2X)
statues[:2].replace_old(1454)
statues[2].replace_old(2632)


@lib.template(grf.FileSprite)
def tmpl_shops_and_offices(func, z):
    grid = lib.HouseGrid(func=func, height=100, z=z)
    return [
        lib.MagentaToStruct(grid('29a_ground', (0, 0), bb=(0, 0), frame=3, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder'))),
        lib.MagentaToStruct(grid('29a', (0, 0), bb=(0, 0), frame=3, ignore_layers=('TILE/*', 'FOUNDATION/*'))),
        lib.MagentaToStruct(grid('29b_ground', (1, 0), bb=(0, 0), frame=3, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder'))),
        lib.MagentaToStruct(grid('29b', (1, 0), bb=(0, 0), frame=3, ignore_layers=('TILE/*', 'FOUNDATION/*'))),

        lib.MagentaToStruct(grid('16_stage1', (2, 0), bb=(2, 0), frame=1, ignore_layers='TILE/*')),
        lib.MagentaToStruct(grid('16_stage2', (2, 0), bb=(2, 0), frame=2, ignore_layers='TILE/*')),
        lib.MagentaToStruct(grid('16_stage3', (2, 0), bb=(2, 0), frame=3, ignore_layers='TILE/*')),

        grid('14_stage1', (3, 0), bb=(1, 3), frame=1, ignore_layers='TILE/*'),
        grid('14_stage2', (3, 0), bb=(1, 3), frame=2, ignore_layers='TILE/*'),
        grid('14_stage3', (3, 0), bb=(1, 3), frame=3, ignore_layers='TILE/*'),

        grid('15_stage1', (4, 0), bb=(3, 1), frame=1, ignore_layers='TILE/*'),
        grid('15_stage2', (4, 0), bb=(3, 1), frame=2, ignore_layers='TILE/*'),
        grid('15_stage3', (4, 0), bb=(3, 1), frame=3, ignore_layers='TILE/*'),

        grid('30_ground1', (5, 0), bb=(0, 0), frame=1, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder')),
        grid('30_stage1', (5, 0), bb=(0, 0), frame=1, ignore_layers=('TILE/*', 'FOUNDATION/*')),
        grid('30_ground2', (5, 0), bb=(0, 0), frame=2, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder')),
        grid('30_stage2', (5, 0), bb=(0, 0), frame=2, ignore_layers=('TILE/*', 'FOUNDATION/*')),
        grid('30_ground3', (5, 0), bb=(0, 0), frame=3, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder')),
        grid('30_stage3', (5, 0), bb=(0, 0), frame=3, ignore_layers=('TILE/*', 'FOUNDATION/*')),
    ]

houses = lib.SpriteCollection('house') \
    .add(lib.aseidx(TOWN_DIR / 'shopsandoffices_2x.ase'), tmpl_shops_and_offices, ZOOM_2X) \

houses[0:4].replace_old(1536)  # 29
houses[4:7].replace_old(1467)  # 16
houses[7:10].replace_old(1461)  # 14
houses[10:13].replace_old(1466)  # 15
houses[13:19].replace_old(1540)  # 30


# ------------------------------ Industries ------------------------------

@lib.template(grf.FileSprite)
def tmpl_coal_mine(func, z):
    # bb values are (sx, sy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/industry_land.h
    grid = lib.HouseGrid(func=func, height=75, z=z)
    return [
        grid('building1_stage1', (0, 0), bb=(7, 0), frame=1),
        grid('building1_stage2', (0, 0), bb=(7, 0), frame=2),
        grid('building1_stage3_frame1', (0, 0), bb=(7, 0), frame=3),
        grid('building1_stage3_frame2', (0, 0), bb=(7, 0), frame=4),
        grid('building1_stage3_frame3', (0, 0), bb=(7, 0), frame=5),
        grid('building2_stage1', (1, 0), bb=(1, 2), frame=1),
        grid('building2_stage2', (1, 0), bb=(1, 2), frame=2),
        grid('building2_stage3', (1, 0), bb=(1, 2), frame=3),
        grid('building3_stage1', (2, 0), bb=(4, 4), frame=1),
        grid('building3_stage2', (2, 0), bb=(4, 4), frame=2),
        grid('building3_stage3', (2, 0), bb=(4, 4), frame=3),
        grid('ground1', (3, 0), frame=1),
        grid('coal1', (4, 0), frame=1),
        grid('coal2', (5, 0), frame=1),
        grid('coal3', (6, 0), frame=1),
    ]


lib.SpriteCollection('coal_mine') \
    .add(lib.aseidx(INDUSTRY_DIR / 'coalmine_2x.ase'), tmpl_coal_mine, ZOOM_2X) \
    .replace_old(2011)


@lib.template(grf.FileSprite)
def tmpl_powerplant(func, z):
    # bb values are (sx, sy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/industry_land.h
    grid = lib.HouseGrid(func=func, height=75, z=z)
    return [
        grid('building1_stage1', (0, 0), bb=(1, 1), frame=1),
        grid('building1_stage2', (0, 0), bb=(1, 1), frame=2),
        grid('building1_stage3', (0, 0), bb=(1, 1), frame=3),
        grid('building2_stage1', (1, 0), bb=(0, 2), frame=1),
        grid('building2_stage2', (1, 0), bb=(0, 2), frame=2),
        grid('building2_stage3', (1, 0), bb=(0, 2), frame=3),
        grid('building3_stage1', (2, 0), bb=(1, 0), frame=1),
        grid('building3_stage2', (2, 0), bb=(1, 0), frame=2),
        grid('building3_stage3', (2, 0), bb=(1, 0), frame=3),
        grid('transformer', (3, 0), bb=(1, 2), frame=3, crop=False),  # TODO find a better solution to child sprite positioning than crop=False
        grid('spark1', (3, 0), rel=(11, 23), frame=4, layers='Animated Zap'),
        grid('spark2', (3, 0), rel=(11, 11), frame=5, layers='Animated Zap'),
        grid('spark3', (3, 0), rel=(14, 6), frame=6, layers='Animated Zap'),
        grid('spark4', (3, 0), rel=(13, 3), frame=7, layers='Animated Zap'),
        grid('spark5', (3, 0), rel=(18, 1), frame=8, layers='Animated Zap'),
        grid('spark6', (3, 0), rel=(15, 0), frame=9, layers='Animated Zap'),
    ]


lib.SpriteCollection('power_plant') \
    .add(lib.aseidx(INDUSTRY_DIR / 'powerplant_2x.ase'), tmpl_powerplant, ZOOM_2X) \
    .replace_old(2045)


@lib.template(grf.FileSprite)
def tmpl_chimney_smoke(func, z):
    return [
        func(f'{i}', x=2, y=2, w=128, h=128, xofs=0, yofs=-128, frame=i + 1)
        for i in range(8)
    ]

lib.SpriteCollection('chimney_smoke') \
    .add(lib.aseidx(EFFECT_DIR / 'chimney_smoke_2x.ase'), tmpl_chimney_smoke, ZOOM_2X) \
    .replace_old(3701)


@lib.template(grf.FileSprite)
def tmpl_sawmill(func, z):
    # bb values are (sx, sy) from https://github.com/OpenTTD/OpenTTD/blob/master/src/table/industry_land.h
    grid = lib.HouseGrid(func=func, height=75, z=z)
    return [
        grid('building1_stage1', (0, 0), bb=(1, 0), frame=1),
        grid('building1_stage2', (0, 0), bb=(1, 0), frame=2),
        grid('building1_stage3', (0, 0), bb=(1, 0), frame=3),
        grid('building2_stage1', (1, 0), bb=(0, 1), frame=1),
        grid('building2_stage2', (1, 0), bb=(0, 1), frame=2),
        grid('building2_stage3', (1, 0), bb=(0, 1), frame=3),
        grid('building3_stage1', (2, 0), bb=(1, 1), frame=1),
        grid('building3_stage2', (2, 0), bb=(1, 1), frame=2),
        grid('building3_stage3', (2, 0), bb=(1, 1), frame=3),
        grid('logs1', (3, 0), frame=3),
        grid('logs2', (4, 0), bb=(0, 1), frame=3)
    ]


lib.SpriteCollection('sawmill') \
    .add(lib.aseidx(INDUSTRY_DIR / 'sawmill.ase'), tmpl_sawmill, ZOOM_2X) \
    .replace_old(2061)


@lib.template(grf.FileSprite)
def tmpl_forest(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('growth1', (0, 0), frame=1, ignore_layers=ground_layers),
        grid('growth2', (0, 0), frame=2, ignore_layers=ground_layers),
        grid('growth3', (0, 0), frame=3, ignore_layers=ground_layers),
        grid('grown', (0, 0), frame=4, ignore_layers=ground_layers),
        grid('logs', (0, 0), frame=5, ignore_layers=ground_layers),
        grid('ground', (0, 0), layers=ground_layers + ('Spriteborder',)),
    ]


# TODO Why are 128/322 forest sprites too?
# TODO remove climate=TEMPERATE? (but ensure the right order)
lib.SpriteCollection('forest') \
    .add(INDUSTRY_DIR / 'forest_temperate.ase', tmpl_forest, ZOOM_2X, climate=TEMPERATE) \
    .replace_old(2072)
    # .add(INDUSTRY_DIR / 'forest.ase', tmpl_forest, ZOOM_2X, 76, climate=ARCTIC) \


@lib.template(grf.FileSprite)
def tmpl_oil_refinery(func, z):
    grid = lib.HouseGrid(func=func, height=128, z=z)
    return [
        cc(grid('building1_stage1', (0, 0), frame=1)),
        cc(grid('building1_stage2', (0, 0), frame=2)),
        cc(grid('building1_stage3', (0, 0), frame=3)),
        cc(grid('building2_stage1', (1, 0), frame=1)),
        cc(grid('building2_stage2', (1, 0), frame=2)),
        cc(grid('building2_stage3', (1, 0), frame=3)),
        cc(grid('building3_stage1', (2, 0), frame=1)),
        cc(grid('building3_stage2', (2, 0), frame=2)),
        lib.AlphaAndMask(
            cc(grid('building3', (2, 0), frame=3, ignore_layers=('ANIMATED',))),
            grid('building3_fire', (2, 0), frame=3, layers=('ANIMATED',)),
        ),
        cc(grid('building4_stage1', (3, 0), frame=1)),
        cc(grid('building4_stage2', (3, 0), frame=2)),
        cc(grid('building4_stage3', (3, 0), frame=3)),
        cc(grid('building5_stage1', (4, 0), frame=1)),
        cc(grid('building5_stage2', (4, 0), frame=2)),
        cc(grid('building5_stage3', (4, 0), frame=3)),
        cc(grid('building6_stage1', (5, 0), frame=1)),
        cc(grid('building6_stage2', (5, 0), frame=2)),
        cc(grid('building6_stage3', (5, 0), frame=3)),
    ]

lib.SpriteCollection('oil_refinery') \
    .add(INDUSTRY_DIR / 'oilrefinery_2x.ase', tmpl_oil_refinery, ZOOM_2X) \
    .replace_old(2078)


@lib.template(grf.FileSprite)
def tmpl_oil_rig(func, z):
    assert z == 2

    def chunk(name, x, w, h, *, xofs, frame):
        x = x + 2
        yofs = -282 + h
        h = 345 - h
        return lib.AlphaAndMask(
            func(name, x, 2, w, h, xofs=xofs, yofs=yofs, ignore_layers='REF/*', frame=frame),
            func(name + '_anim', x, 2, w, h, xofs=xofs, yofs=yofs, layers='ANIMATED/*', frame=frame)
        )

    return [
        chunk(f'stage3_chunk1', 0, 64, 64, xofs=-62, frame=3),
        chunk(f'stage3_chunk2', 64, 64, 32, xofs=-62, frame=3),
        chunk(f'stage3_chunk3', 128, 128, 0, xofs=-62, frame=3),
        chunk(f'stage3_chunk4', 256, 64, 32, xofs=2, frame=3),

        chunk(f'stage2_chunk1', 0, 64, 64, xofs=-62, frame=2),
        chunk(f'stage2_chunk2', 64, 64, 32, xofs=-62, frame=2),
        chunk(f'stage2_chunk3', 128, 128, 0, xofs=-62, frame=2),

        chunk(f'stage1_chunk1', 0, 64, 64, xofs=-62, frame=1),
        chunk(f'stage1_chunk2', 64, 64, 32, xofs=-62, frame=1),
        chunk(f'stage1_chunk3', 128, 128, 0, xofs=-62, frame=1),
    ]


lib.SpriteCollection('oil_rig') \
    .add(INDUSTRY_DIR / 'oilrig_2x.ase', tmpl_oil_rig, ZOOM_2X) \
    .replace_old(2096)


@lib.template(grf.FileSprite)
def tmpl_farm(func, z):
    ground = func('ground1_whole', 2, 2, 192, 151, xofs=-62, yofs=-56, layers=('TILE/*', 'Spriteborder'))
    building = func('building1_whole', 2, 2, 192, 151, xofs=-126, yofs=-88, ignore_layers=('TILE/*',))
    grid = lib.HouseGrid(func=func, height=75, z=z, offset=(194, 0))
    return [
        lib.CutGround(ground, (0, 0), name='ground1a'),
        lib.CutGround(ground, (0, 1), name='ground1b'),
        cc(lib.CutBuilding(building, (0, 1), name='building1a')),
        cc(lib.CutBuilding(building, (0, 0), name='building1b')),
        grid('ground2', (0, 0), layers=('TILE/*', 'Spriteborder')),
        cc(grid('building2', (0, 0), ignore_layers=('TILE/*',))),
        grid('ground3', (1, 0), layers=('TILE/*', 'Spriteborder')),
        grid('building3', (1, 0), ignore_layers=('TILE/*',)),
        grid('ground4', (2, 0), layers=('TILE/*', 'Spriteborder')),
        grid('building4', (2, 0), ignore_layers=('TILE/*',)),
        grid('ground5', (3, 0), layers=('TILE/*', 'Spriteborder')),
        grid('building5', (3, 0), ignore_layers=('TILE/*',)),
    ]


lib.SpriteCollection('farm') \
    .add(INDUSTRY_DIR / 'farm_2x.ase', tmpl_farm, ZOOM_2X) \
    .replace_old(2106)


@lib.template(grf.FileSprite)
def tmpl_farm_fences(func, z, frame):
    relative = 0
    x_xofs, x_yofs = -59 - relative, 21 - relative // 2
    y_xofs, y_yofs = -3 + relative, 21 - relative // 2
    return [
        func('flat_x', 2 + 68 * 1, 2, 66, 44, xofs=x_xofs, yofs=x_yofs, frame=frame),
        func('flat_y', 2 + 68 * 0, 2, 66, 44, xofs=y_xofs, yofs=y_yofs, frame=frame),
        func('high_x', 2 + 68 * 5, 2, 66, 60, xofs=x_xofs, yofs=x_yofs - 16, frame=frame),
        func('high_y', 2 + 68 * 4, 2, 66, 60, xofs=y_xofs, yofs=y_yofs - 16, frame=frame),
        func('low_x', 2 + 68 * 3, 2, 66, 28, xofs=x_xofs, yofs=x_yofs + 16, frame=frame),
        func('low_y', 2 + 68 * 2, 2, 66, 28, xofs=y_xofs, yofs=y_yofs + 16, frame=frame),
    ]


for i in range(6):
    lib.SpriteCollection(f'farm_fence{i}') \
        .add(TERRAIN_DIR / 'farmfences_2x.ase', tmpl_farm_fences, ZOOM_2X, i + 1) \
        .replace_old(4090 + i * 6)


@lib.template(grf.FileSprite)
def tmpl_steel_mill(func, z):
    assert z == 2
    ground_layers = ('TILE/*', 'Spriteborder')
    building_layers = ('BUILDING/*', 'Spriteborder')

    def building(name, *args, **kw):
        return lib.AlphaAndMask(
            cc(func(name, *args, **kw, layers=building_layers)),
            func(name + '_anim', *args, **kw, layers=('ANIMATED/*',)),
        )

    def full_stage(frame):
        ground1 = func('ground1', 2, 2, 192, 161, xofs=-126, yofs=-34-32, layers=ground_layers, frame=frame)
        ground2 = func('ground2', 196, 2, 256, 161, xofs=-126, yofs=-34, layers=ground_layers, frame=frame)
        return [
            cc(lib.CutGround(ground2, (0, 0), name='ground2a')),
            grf.EMPTY_SPRITE, # Left and right buildings cover this one completely and also closest one that doesn't have a sprite (possible glitchy though)
            cc(lib.CutGround(ground2, (0, 1), name='ground2b')),
            building(f'building2_stage{frame}', 196 + 128, 2, 128, 129 + 32, xofs=-62, yofs=-66, frame=frame),
            cc(lib.CutGround(ground2, (1, 0), name='ground2c')),
            building(f'building2_stage{frame}', 196, 2, 128, 129 + 32, xofs=-62, yofs=-66, frame=frame),
            cc(lib.CutGround(ground2, (1, 1), name='ground2d')),
            cc(lib.CutGround(ground1, (0, 0), name='ground1a')),
            building(f'building1_stage{frame}', 130, 2, 64, 129, xofs=2, yofs=-66, frame=frame),
            cc(lib.CutGround(ground1, (1, 0), name='ground1b')),
            building(f'building1_stage{frame}', 2, 2, 128, 129 + 32, xofs=-62, yofs=-98, frame=frame),
        ]

    return (
        full_stage(3) +
        full_stage(2) +
        [
            # Stage 1 has no ground sprites (uses 2022), also don't bother animating it
            # What it has though is southernmost sprite
            grf.EMPTY_SPRITE, # Furthest building is covered by the closest one,
            func('building2_stage1', 196 + 128 + 64, 2, 64, 129, xofs=2, yofs=-66, layers=building_layers, frame=1),
            func('building3_stage1', 196 + 2, 2, 64, 129, xofs=-62, yofs=-66, layers=building_layers, frame=1),
            func('building4_stage1', 196 + 64, 2, 128, 129 + 32, xofs=-62, yofs=-66 - 32, layers=building_layers, frame=1),
            func('building1_stage1', 130, 2, 64, 129, xofs=2, yofs=-66, layers=building_layers, frame=1),
            func('building1_stage1', 2, 2, 128, 129 + 32, xofs=-62, yofs=-98, layers=building_layers, frame=1),
        ]
    )


lib.SpriteCollection('steel_mill') \
    .add(INDUSTRY_DIR / 'steelmill_2x.ase', tmpl_steel_mill, ZOOM_2X) \
    .replace_old(2118)


@lib.template(grf.FileSprite)
def tmpl_factory(func, z):
    assert z == 2
    ground = func('ground', 2, 2, 256, 201, xofs=-126, yofs=-74, layers=('TILE/*', 'Spriteborder'), frame=3)
    return [
        cc(lib.CutGround(ground, (1, 1), name='ground1_stage3')),
        cc(lib.CutGround(ground, (1, 0), name='ground2_stage3')),
        cc(lib.CutGround(ground, (0, 1), name='ground3_stage3')),
        cc(lib.CutGround(ground, (0, 0), name='ground4_stage3')),
        grf.EMPTY_SPRITE, # Left and right buildings cover this one completely and also closest one that doesn't have a sprite (possible glitchy though)
        cc(func('building2_stage3', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        cc(func('building3_stage3', 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        grf.EMPTY_SPRITE, # Furthest building is covered by the closest one,
        func('building2_stage1', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building3_stage1', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building4_stage1', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),
        grf.EMPTY_SPRITE, # Furthest building is covered by the closest one,
        func('building2_stage2', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building3_stage2', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),
    ]


lib.SpriteCollection('factory') \
    .add(INDUSTRY_DIR / 'factory_2x.ase', tmpl_factory, ZOOM_2X) \
    .replace_old(2146)


@lib.template(grf.FileSprite)
def tmpl_oil_wells(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    f = lambda frame: grid('frame{i}', (0, 0), layers=('BUILDING/*', 'Spriteborder'), frame=frame)
    return [
        func('ground', 2, 90, 128, 63, xofs=-31 * z, yofs=0, layers=('TILE/*', 'Spriteborder'), frame=1)
    ] + [f(i + 1) for i in range(6)]


oil_wells = lib.SpriteCollection('oil_wells') \
    .add(INDUSTRY_DIR / 'oilwells_2x.ase', tmpl_oil_wells, ZOOM_2X)
oil_wells[0].compose_on(ground[0]).replace_old(2173)
oil_wells[1:].replace_old(2174)


@lib.template(grf.FileSprite)
def tmpl_bank(func, z):
    assert z == 2
    ground = func('ground', 2, 2, 192, 160, xofs=-126, yofs=-65, layers=('TILE/*', 'Spriteborder'))
    return [
        func('building1', 130, 2, 64, 160, xofs=2, yofs=-65, layers=('BUILDING/*', 'Spriteborder')),
        func('building2', 2, 2, 128, 160, xofs=-62, yofs=-97, layers=('BUILDING/*', 'Spriteborder')),
        lib.CutGround(ground, (1, 0), name='ground1'),
        lib.CutGround(ground, (0, 0), name='ground2'),
    ]


lib.SpriteCollection('bank') \
    .add(INDUSTRY_DIR / 'bank_2x.ase', tmpl_bank, ZOOM_2X) \
    .replace_old(2180)


@lib.template(grf.FileSprite)
def tmpl_iron_mine(func, z, frame):
    ground = func('ground', 2, 2, 512, 294, xofs=-254, yofs=-39, frame=frame)
    return [
        lib.CutGround(ground, (x, y), name=f'{x}_{y}', above=((0, 10)[y == 0], (0, 10)[x == 0]))
        for x in range(4)
        for y in range(4)
    ]


for i in range(0, 3):
    lib.SpriteCollection('iron_mine') \
        .add(INDUSTRY_DIR / 'ironoremine_2x.ase', tmpl_iron_mine, ZOOM_2X, i + 1, name=f'stage{i + 1}') \
        .replace_old(2293 + 16 * i)


# ------------------------------ User Interface ------------------------------

@lib.template(grf.FileSprite)
def tmpl_cargo_icons(func, z):
    grid = lib.grid(func=func, width=11, height=11)
    return [grid(str(i), (i, 0)) for i in range(27)]

lib.SpriteCollection('cargo_icon') \
    .add(ICON_DIR / 'cargo_2x.ase', tmpl_cargo_icons, ZOOM_2X) \
    .replace_old(4297)

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
    parser.add_argument('--frame', help='Frame number to export', type=int, default=1)


def cmd_debugcc_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file)
    sprite = grf.FileSprite(ase, 0, 0, None, None, name=args.ase_file, layers=args.layer, frame=args.frame)
    sprite = lib.MagentaToCC(sprite)
    lib.debug_cc_recolour([sprite], horizontal=args.horizontal)


def cmd_debugstruct_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')
    parser.add_argument('--frame', help='Frame number to export', type=int, default=1)


def cmd_debugstruct_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file)
    sprite = grf.FileSprite(ase, 0, 0, None, None, name=args.ase_file, layers=args.layer, frame=args.frame)
    sprite = lib.MagentaToStruct(sprite)
    lib.debug_struct_recolour([sprite], horizontal=args.horizontal)


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
        'name': 'debugstruct',
        'help': 'Takes an image and produces another image with all variants of structure recolour',
        'add_args': cmd_debugstruct_add_args,
        'handler': cmd_debugstruct_handler,
    }, {
        'name': 'debuglight',
        'help': 'Takes an image and produces animated gif with light cycle',
        'add_args': cmd_debuglight_add_args,
        'handler': cmd_debuglight_handler,
    }]
)
