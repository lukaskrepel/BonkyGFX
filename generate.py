import itertools
import pathlib
from collections import defaultdict
from typing import Optional, Union

from typeguard import typechecked

import grf
from grf import ZOOM_NORMAL, ZOOM_2X, ZOOM_4X, TEMPERATE, ARCTIC, TROPICAL, TOYLAND, ALL_CLIMATES

import lib

cc = lib.MagentaToCC
struct = lib.MagentaToStruct

def animated(name, grid, *args, layers=None, ignore_layers=None, **kw):
    grid_args = {}
    if isinstance(grid, lib.BaseGrid):
        grid_args = {'keep_state': True}

    if ignore_layers is None:
        ignore_layers = ()
    elif isinstance(ignore_layers, tuple):
        ignore_layers = ignore_layers
    else:
        ignore_layers = (ignore_layers,)

    return lib.AlphaAndMask(
        grid(name + '_rgb', *args, **kw, layers=layers, ignore_layers=ignore_layers + ('ANIMATED',), **grid_args),
        grid(name + '_anim', *args, **kw, layers=('ANIMATED',)),
        name=name,
    )


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

# TODO (I commented this part out as it was often giving me all vehicles even though the paremeter was set to false)
# g.add_bool_parameter(
#     name='Enable vehicles from all climates',
#     description='Sets the climate availability for all vehicles (useful for debugging)',
#     default=False,
# )

# g.add(grf.If(is_static=False, variable=0x01, condition=0x03, value=1, skip=0, varsize=1))  # skip if vehicle param not enabled
# for feature in (grf.RV, grf.TRAIN, grf.SHIP, grf.AIRCRAFT):
#     count = grf.DisableDefault.DISABLE_INFO[feature][0]
#     g.add(grf.DefineMultiple(
#         feature=feature,
#         first_id=0,
#         count=count,
#         props={
#             'climates_available': [grf.ALL_CLIMATES] * count,
#         }
#     ))
# g.add(grf.Label(0, b''))


# ------------------------------ Cursors ------------------------------

# TODO Animated "Zzzz" waiting cursor if possible, otherwise use better colors than anim-palette
# TODO compositing icons onto cursor
# TODO sprite width is 104/2=52 to be able to add wider icons such as station
@lib.template(grf.FileSprite)
def tmpl_cursors(func, z, frame):
    grid = lib.RectGrid(func=func, width=48 * z, height=32 * z, padding=z)
    grid.set_default(frame=frame)
    return [grid(str(i), (0, 0))]

for i in range(2):
    lib.SpriteCollection(f'cursor{i}') \
        .add(ICON_DIR / 'cursor.ase', tmpl_cursors, ZOOM_2X, i + 1) \
        .replace_old(i)

# ------------------------------ Ground Tiles ------------------------------

@lib.template(grf.FileSprite)
def tmpl_groundtiles(func, z, frame=1, above=0):
    grid = lib.FlexGrid(func=func, padding=z, start=(0, 0), add_yofs=-(z // 2) - above * z, add_height=above * z)
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


def tmpl_groundtiles_extra(name, paths, zoom, *args):
    @lib.template(grf.FileSprite)
    def tmpl_extra(func, z, frame=1):
        assert z == 2
        grid = lib.FlexGrid(func=func, padding=z, start=(1235 * z, 0), add_yofs=-(z // 2))
        grid.set_default(width=64 * z, height=32 * z - 1, xofs=-31 * z, yofs=0, frame=frame)
        return [
            grid('extra1'),
            grid('extra2'),
            grid('extra3'),
            grid('extra4'),
        ]
    return tmpl_groundtiles(name, paths, zoom, *args) + tmpl_extra(name, paths, zoom, *args)


def make_ground(name, frame, *, extra=False):
    tmpl = tmpl_groundtiles_extra if extra else tmpl_groundtiles
    return lib.SpriteCollection(name) \
        .add(TERRAIN_DIR / 'groundtiles.ase',
             tmpl, ZOOM_2X, frame, climate=TEMPERATE) \
        .add(TERRAIN_DIR / 'groundtiles.ase',
             tmpl, ZOOM_2X, frame + 7, climate=ARCTIC) \
        .add(TERRAIN_DIR / 'groundtiles.ase',
             tmpl, ZOOM_2X, frame + 18, climate=TROPICAL) \
        .add(TERRAIN_DIR / 'groundtiles.ase',
             tmpl, ZOOM_2X, frame + 27, climate=TOYLAND)


ground = make_ground('ground', 4)
make_ground('ground_bare', 1).replace_old(3924)  # 0% grass
make_ground('ground_33', 2).replace_old(3943)   # 33% grass
make_ground('ground_66', 3).replace_old(3962)   # 66% grass
ground.replace_old(3981)  # 100% grass

make_ground('rough', 5, extra=True).replace_old(4000)

make_ground('rocks', 6).replace_old(4023)

for i in range(9):
    lib.SpriteCollection(f'farmland{i}') \
        .add(TERRAIN_DIR / 'farmtiles.ase', tmpl_groundtiles, ZOOM_2X, i + 1, 5, climate=TEMPERATE) \
        .add(TERRAIN_DIR / 'farmtiles.ase', tmpl_groundtiles, ZOOM_2X, i + 10, 5, climate=ARCTIC) \
        .add(TERRAIN_DIR / 'farmtiles.ase', tmpl_groundtiles, ZOOM_2X, i + 19, 5, climate=TROPICAL) \
        .replace_old(4126 + 19 * i)

for i in range(3):
    lib.SpriteCollection(f'snow_{25 * i}') \
        .add(TERRAIN_DIR / 'groundtiles.ase',
             tmpl_groundtiles, ZOOM_2X, 15 + i) \
        .replace_old(4493 + i * 19, climate=ARCTIC)

lib.SpriteCollection('desert_and_snow_transition') \
    .add(TERRAIN_DIR / 'groundtiles.ase',
         tmpl_groundtiles, ZOOM_2X, 26) \
    .replace_old(4512)

desert_and_snow = lib.SpriteCollection('desert_and_snow') \
    .add(TERRAIN_DIR / 'groundtiles.ase',
         tmpl_groundtiles, ZOOM_2X, 27) \
    .add(TERRAIN_DIR / 'groundtiles.ase',
         tmpl_groundtiles, ZOOM_2X, 15 + 3, climate=ARCTIC)
desert_and_snow.replace_old(4550)

general_concrete = make_ground('general_concrete', 7)
general_concrete[0].replace_old(1420)
general_concrete[0].replace_old(4675)  # Toyland extra concrete
general_concrete[0].replace_old(4676)  # Toyland extra concrete
general_concrete[0].replace_old(2022, climate=TOYLAND)  # Some toyland industries use coal mine dirt tile, replace it with concrete


@lib.template(grf.FileSprite)
def tmpl_foundations(func, z, frame=1):
    grid = lib.RectGrid(func=func, width=64 * z, height=41 * z - 1, padding=z, add_yofs=-(z // 2))
    # TODO figure out why it glitches with crop
    grid.set_default(xofs=-31 * z, yofs=-9 * z, frame=frame, crop=False)

    return (
        [grid(f'base_{i}', (i % 7, i // 7)) for i in range(14)] +
        [grid(f'new_{i}', (i % 7, i // 7 + 2)) for i in range(74)] +
        [
            grid('new_74', (4, 12), xofs=-15 * z, yofs=-17 * z),
            grid('new_75', (5, 12), yofs=-25 * z),
            grid('new_76', (6, 12), xofs=-47 * z, yofs=-17 * z),
            grid('new_77', (0, 13), yofs=-9 * z),
            grid('new_78', (1, 13), xofs=-15 * z, yofs=-17 * z),
            grid('new_79', (2, 13), yofs=-25 * z),
            grid('new_80', (3, 13), xofs=-47 * z, yofs=-17 * z),
            grid('new_81', (4, 13), yofs=-9 * z),
            grid('new_82', (5, 13), xofs=-15 * z, yofs=-17 * z),
            grid('new_83', (6, 13), yofs=-25 * z),
            grid('new_84', (0, 14), xofs=-47 * z, yofs=-17 * z),
            grid('new_85', (1, 14), yofs=-9 * z),
            grid('new_86', (2, 14), xofs=-15 * z, yofs=-17 * z),
            grid('new_87', (3, 14), yofs=-25 * z),
            grid('new_88', (4, 14), xofs=-47 * z, yofs=-17 * z),
            grid('new_89', (5, 14), yofs=-9 * z),
        ]
    )


foundations = lib.SpriteCollection('foundations') \
    .add(TERRAIN_DIR / 'foundations.ase', tmpl_foundations, ZOOM_2X, 1, climate=TEMPERATE) \
    .add(TERRAIN_DIR / 'foundations.ase', tmpl_foundations, ZOOM_2X, 2, climate=ARCTIC) \
    .add(TERRAIN_DIR / 'foundations.ase', tmpl_foundations, ZOOM_2X, 3, climate=TROPICAL) \
    .add(TERRAIN_DIR / 'foundations.ase', tmpl_foundations, ZOOM_2X, 4, climate=TOYLAND)
foundations[:14].replace_old(990)
foundations[14:].replace_new(0x06, 0)

# ------------------------------ Airport Tiles ------------------------------

@lib.template(grf.FileSprite)
def tmpl_airport_tiles(func, z):
    grid = lib.FlexGrid(func=func, padding=2, add_yofs=-(z // 2))
    grid.set_default(width=64 * z, height=32 * z - 1, xofs=-31 * z, yofs=0)
    kw_default = {'ignore_layers': 'ANIMATED/*'}

    sprites = [
        grid('apron', **kw_default),
        grid('stand', **kw_default),
        animated('runway_a', grid),
        animated('runway_b', grid),
        animated('runway_c', grid),
        animated('runway_d', grid),
        animated('runway_end', grid),
        grid('taxi_ns_west', **kw_default),
        grid('taxi_ew_south', **kw_default),
        grid('taxi_xing_south', **kw_default),
        grid('taxi_xing_west', **kw_default),
        grid('taxi_ns_ctr', **kw_default),
        grid('taxi_xing_east', **kw_default),
        grid('taxi_ns_east', **kw_default),
        grid('taxi_ew_north', **kw_default),
        grid('taxi_ew_ctr', **kw_default),
        animated('runway_y_a', grid),  # unused
        animated('runway_y_b', grid),  # unused
        animated('runway_y_c', grid),  # unused
        animated('runway_y_d', grid),  # unused
        animated('runway_y_end', grid),  # unused
        animated('helipad', grid, yofs = -15 * z),
        grid('new_helipad', **kw_default),
    ]

    # Rearrange to OpenTTD sprite order
    return [sprites[k] for k in (0, 1, 7, 8, 9, 10, 11, 12, 13, 14, 15, 2, 3, 4, 5, 6, 21, 22)]


AIRPORT_COMPOSITION = [(None, 0), (None, 1)] + [(0, i) for i in range(2, 11)] + [(None, i) for i in range(11, 18)]
airport_tiles = lib.SpriteCollection('airport_modern') \
    .add(INFRA_DIR / 'airport_modern.ase',
        tmpl_airport_tiles, ZOOM_2X) \
    .compose_on(ground, AIRPORT_COMPOSITION)
airport_tiles[:16].replace_old(2634)
airport_tiles[16].replace_new(0x15, 86)
airport_tiles[17].replace_new(0x10, 12)


def tmpl_tile_selection(name, paths, zoom, *args):
    return [lib.MoveSprite(lib.MagentaToSelection(s), yofs=14) for s in tmpl_groundtiles(name, paths, zoom, *args)]


lib.SpriteCollection('tile_selection') \
    .add(TERRAIN_DIR / 'selectiontiles.ase', tmpl_tile_selection, ZOOM_2X) \
    .replace_old(752)

# ------------------------------ Trees ------------------------------


def tree(name, sprite_id, path, **kw):
    @lib.template(grf.FileSprite)
    def tmpl(func, z, frame):
        # Variation of OpenGFX1 template with 2x zoom and only one tree
        return [
            func('', 2 + 0 * z, 2, 45 * z, 80 * z, xofs=-24 * z, yofs=-73 * z - (z // 2), frame=frame, **kw)
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
    tree('temperate_tree', 1576 + i * 7, TREE_DIR / 'temperate_tree.ase')

for i in range(8):
    tree('arctic_tree', 1709 + i * 7, TREE_DIR / 'arctic_tree.ase', ignore_layers='SNOW/*')
    tree('arctic_tree_snow', 1765 + i * 7, TREE_DIR / 'arctic_tree.ase')

for i in range(18):
    tree('tropic_tree', 1821 + i * 7, TREE_DIR / 'tropical_tree.ase')

tree('fruit_tree', 1821 + 7 * 11, TREE_DIR / 'fruit_tree.ase')
tree('rubber_tree', 1821 + 7 * 12, TREE_DIR / 'rubber_tree.ase')
tree('cactus', 1821 + 7 * 13, TREE_DIR / 'cactus.ase')
tree('cactus', 1821 + 7 * 14, TREE_DIR / 'cactus.ase')

for i in range(7):
    tree('toyland_tree', 1947 + i * 7, TREE_DIR / 'toyland_tree.ase')

tree('toyland_tree', 1947 + 7 * 7, TREE_DIR / 'battery_tree.ase')
tree('toyland_tree', 1947 + 7 * 8, TREE_DIR / 'cottoncandy_tree.ase')

# ------------------------------ Road Vehicles ------------------------------

@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_road_8view(func, z, x, y, frame):
    grid = lib.FlexGrid(func=func, padding=2, start=(x * 174 * z, y * 24 * z), add_yofs=-(z // 2))
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


replace_rv_generation(VEHICLE_DIR / 'road_trucks.ase', 1)
replace_rv_generation(VEHICLE_DIR / 'road_trucks.ase', 2)
replace_rv_generation(VEHICLE_DIR / 'road_trucks.ase', 3)
lib.SpriteCollection('bus_gen1') \
    .add(VEHICLE_DIR / 'road_buses.ase', tmpl_vehicle_road_8view, ZOOM_2X, 0, 0, 0) \
    .replace_old(3284)
lib.SpriteCollection('bus_gen2') \
    .add(VEHICLE_DIR / 'road_buses.ase', tmpl_vehicle_road_8view, ZOOM_2X, 0, 1, 0) \
    .replace_old(3284 - 192)
lib.SpriteCollection('bus_gen2') \
    .add(VEHICLE_DIR / 'road_buses.ase', tmpl_vehicle_road_8view, ZOOM_2X, 0, 2, 0) \
    .replace_old(3284 + 192)


def replace_rv_toyland(path2x):
    def tmpl(suffix, x, y, frame):
        return lib.SpriteCollection(f'rv_toyland_{suffix}') \
            .add(path2x, tmpl_vehicle_road_8view, ZOOM_2X, x, y, frame, climate=TOYLAND)
    tmpl('passengers', 0, 0, 1).replace_old(3092)
    tmpl('sugar_empty', 0, 1, 1).replace_old(3100)
    tmpl('sugar_loaded', 0, 1, 2).replace_old(3108)
    tmpl('cola_empty', 0, 2, 1).replace_old(3116)
    tmpl('cola_loaded', 0, 2, 2).replace_old(3124)
    tmpl('cotton_candy_empty', 0, 3, 1).replace_old(3132)
    tmpl('cotton_candy_loaded', 0, 3, 2).replace_old(3140)
    tmpl('toffee_empty', 0, 4, 1).replace_old(3148)
    tmpl('toffee_loaded', 0, 4, 2).replace_old(3156)
    tmpl('toys', 0, 5, 1).replace_old(3164)
    tmpl('mail', 0, 6, 1).replace_old(3172)
    tmpl('candy', 0, 7, 1).replace_old(3180)
    tmpl('batteries_empty', 0, 8, 1).replace_old(3188)
    tmpl('batteries_loaded', 0, 8, 2).replace_old(3196)
    tmpl('fizzy_drinks_empty', 0, 9, 1).replace_old(3204)
    tmpl('fizzy_drinks_loaded', 0, 9, 2).replace_old(3212)
    tmpl('plastic_empty', 0, 10, 1).replace_old(3220)
    tmpl('plastic_loaded', 0, 10, 2).replace_old(3228)
    tmpl('bubbles_empty', 0, 11, 1).replace_old(3236)
    tmpl('bubbles_loaded', 0, 11, 2).replace_old(3244)
replace_rv_toyland(VEHICLE_DIR / 'road_trucks_toyland.ase')


# ------------------------------ Rail Vehicles ------------------------------

@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_rail_4view(func, z, y, frame, **kw):
    grid = lib.FlexGrid(func=func, padding=2, start=(0 * 87 * z, y * 24 * z), add_yofs=-(z // 2))
    grid.set_default(frame=frame, **kw)
    return [
        grid( 'n', width= 8 * z, height=23 * z, xofs=-3 * z, yofs=-13 * z),
        grid('ne', width= 22 * z, height=19 * z, xofs=-15 * z, yofs=-12 * z),
        grid( 'e', width= 31 * z, height=15 * z, xofs=-16 * z, yofs=-9 * z),
        grid('se', width= 22 * z, height=19 * z, xofs=-7 * z, yofs=-12 * z),
    ]


@lib.template(lib.CCReplacingFileSprite)
def tmpl_vehicle_rail_8view(func, z, y, frame, **kw):
    grid = lib.FlexGrid(func=func, padding=2, start=(0 * 174 * z, y * 24 * z), add_yofs=-(z // 2))
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
        .add(VEHICLE_DIR / 'rail_wagons.ase', tmpl_vehicle_rail_4view, ZOOM_2X, y, frame) \
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
        .add(VEHICLE_DIR / 'rail_engines_temperate.ase', tmpl, ZOOM_2X, y, 0) \
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
    grid = lib.FlexGrid(func=func, padding=2, add_yofs=-(z // 2))
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
    .add(lib.aseidx(INFRA_DIR / 'roads.ase'),
         tmpl_roadtiles, ZOOM_2X, 2)

road = lib.SpriteCollection('road') \
    .add(lib.aseidx(INFRA_DIR / 'roads.ase'),
         tmpl_roadtiles, ZOOM_2X, 1) \
    .add(INFRA_DIR / 'roads.ase',
         tmpl_roadtiles, ZOOM_2X, 3, climate=TROPICAL)

ROAD_COMPOSITION = list(zip([0] * 11, range(11))) + list(zip((12, 6, 3, 9), range(15, 19))) + list(zip([0] * 4, range(11, 15)))
road_town.compose_on(general_concrete, ROAD_COMPOSITION).replace_old(1313)
road.compose_on(ground, ROAD_COMPOSITION).replace_old(1332)
desert_and_snow_road = road.compose_on(desert_and_snow, ROAD_COMPOSITION)

desert_and_snow_road.unspecify(climate=ARCTIC).replace_old(1351)  # default sprite - snowy road
desert_and_snow_road.replace_old(1351, climate=TROPICAL)  # in tropic - desert road


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
    .add(STATION_DIR / 'roaddepots.ase',
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
    .add(STATION_DIR / 'truckstop.ase', tmpl_truck_stop, ZOOM_2X)
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
    .add(STATION_DIR / 'busstop.ase', tmpl_bus_stop, ZOOM_2X)
bus_stops[:16].replace_old(2692)
bus_stops[16:].replace_new(0x11, 0)

# ------------------------------ Rail infrastructure ------------------------------

@lib.template(grf.FileSprite)
def tmpl_rails(func, z, layers, frame):
    grid = lib.FlexGrid(func=func, padding=2, add_yofs=-(z // 2))
    grid.set_default(width=64 * z, height = 32 * z - 1, xofs=-31 * z, yofs=0, layers=layers, frame=frame)
    return list(map(grid, ('y', 'x', 'n', 's', 'e', 'w', 'cross')))


@lib.template(grf.FileSprite)
def tmpl_ballast(func, z, layers, frame):
    grid = lib.FlexGrid(func=func, padding=2, start=(910, 0), add_yofs=-(z // 2))
    grid.set_default(width=64 * z, height = 32 * z - 1, xofs=-31 * z, yofs=0, layers=layers, frame=frame)
    return list(map(grid, ('ground_tne', 'ground_tsw', 'ground_tnw', 'ground_tse', 'ground_x')))


@lib.template(grf.FileSprite)
def tmpl_slope_rails(func, z, layers, frame):
    grid = lib.FlexGrid(func=func, padding=2, start=(1560, 0), add_yofs=-(z // 2))
    grid.set_default(width=64 * z, xofs=-31 * z, yofs=0, layers=layers, frame=frame)
    return [
        grid('ne', height=40 * z - 1),
        grid('se', height=24 * z - 1),
        grid('sw', height=24 * z - 1),
        grid('nw', height=40 * z - 1),
    ]


def replace_climate_rail_sprites(rails, slope_rails, ballast, ground, first_id):
    rails.compose_on(ground[0]).replace_old(first_id)

    ballast.compose_on(ground[0]).replace_old(first_id + 7)

    rails.pick(3, 5, 4, 2, 4, 3, 5, 2).compose_on(
            ground.pick(8, 4, 1, 2, 14, 7, 11, 13),
            exact_size=False,
            offsets=((0, 16), None, None, None, None, (0, -16), None, None),
        ).replace_old(first_id + 12)
    slope_rails.compose_on(ground.pick(12, 6, 3, 9)).replace_old(first_id + 20)

    rails[3].compose_on(rails[2]).compose_on(ground[0]).replace_old(first_id + 24)  # double diagonal tile Y
    rails[5].compose_on(rails[4]).compose_on(ground[0]).replace_old(first_id + 25)  # double diagonal tile X


def replace_rail_type(name, frame, first_id):
    rails = lib.SpriteCollection(name) \
        .add(INFRA_DIR / 'rail.ase', tmpl_rails, ZOOM_2X, ('RAILS/*','SLEEPERS/*'), frame)
    rail_overlays = lib.SpriteCollection(f'{name}_overlay') \
        .add(INFRA_DIR / 'rail.ase', tmpl_rails, ZOOM_2X, ('RAILS/*',), frame)
    slope_rails = lib.SpriteCollection(f'{name}_slope') \
        .add(INFRA_DIR / 'rail.ase', tmpl_slope_rails, ZOOM_2X, ('RAILS/*','SLEEPERS/*'), frame)
    # sleepers = lib.SpriteCollection('rail_overlays') \
    #     .add(INFRA_DIR / 'rail.ase', tmpl_rails, ZOOM_2X, (SLEEPERS/*'))
    ballast = lib.SpriteCollection(f'{name}_ballast') \
        .add(INFRA_DIR / 'rail.ase', tmpl_ballast, ZOOM_2X, ('BALLAST/*',), frame)

    rail_overlays.pick(1, 0, 2, 3, 4, 5).replace_old(first_id)

    replace_climate_rail_sprites(rails, slope_rails, ballast, ground, first_id + 6)
    replace_climate_rail_sprites(rails, slope_rails, ballast, desert_and_snow, first_id + 32)


replace_rail_type('rail', 1, 1005)
replace_rail_type('mono', 2, 1087)
replace_rail_type('maglev', 3, 1169)



@lib.template(grf.FileSprite)
def tmpl_rail_fences(func, z):
    assert z == 2  # xofs/yofs are fixed
    relative = 2
    x_xofs, x_yofs = -59 - relative, -12 - relative // 2
    y_xofs, y_yofs = -3 + relative, -12 - relative // 2
    grid = lib.FlexGrid(func=func, padding=2, add_yofs=-(z // 2))
    return [
        cc(grid('flat_x', width=33 * z, height=22 * z, xofs=x_xofs, yofs=x_yofs)),
        cc(grid('flat_y', width=33 * z, height=22 * z, xofs=y_xofs, yofs=y_yofs)),
        cc(grid('vert', width=3 * z, height=38 * z, xofs=0, yofs=-40)),
        cc(grid('hor', width=65 * z, height=6 * z, xofs=-61, yofs=-8)),
        cc(grid('low_x', width=33 * z, height=14 * z, xofs=x_xofs, yofs=x_yofs + 0)),
        cc(grid('low_y', width=33 * z, height=14 * z, xofs=y_xofs, yofs=y_yofs + 0)),
        cc(grid('high_x', width=33 * z, height=30 * z, xofs=x_xofs, yofs=x_yofs - 16)),
        cc(grid('high_y', width=33 * z, height=30 * z, xofs=y_xofs, yofs=y_yofs - 16)),
    ]


lib.SpriteCollection('rail_fence') \
    .add(INFRA_DIR / 'rail_fences.ase', tmpl_rail_fences, ZOOM_2X) \
    .replace_old(1301)


# ------------------------------ Water ------------------------------

@lib.template(grf.FileSprite)
def tmpl_water_full(func, z):
    x = y = 0
    grid = lib.FlexGrid(func=func, padding=z, start=(0, 0), add_yofs=-(z // 2))
    grid.set_default(width=64 * z, xofs=-31 * z)
    return [
        animated('full', grid, height=32 * z - 1, yofs=0 * z),
        animated('1', grid, height=32 * z - 1, yofs=0 * z),
        animated('2', grid, height=24 * z - 1, yofs=0 * z),
        animated('3', grid, height=24 * z - 1, yofs=0 * z),
        animated('4', grid, height=32 * z - 1, yofs=0 * z),
        animated('5', grid, height=32 * z - 1, yofs=0 * z),
        animated('6', grid, height=24 * z - 1, yofs=0 * z),
        animated('7', grid, height=24 * z - 1, yofs=0 * z),
        animated('8', grid, height=40 * z - 1, yofs=-8 * z),
        animated('9', grid, height=40 * z - 1, yofs=-8 * z),
        animated('10', grid, height=32 * z - 1, yofs=-8 * z),
        animated('11', grid, height=32 * z - 1, yofs=-8 * z),
        animated('12', grid, height=40 * z - 1, yofs=-8 * z),
        animated('13', grid, height=40 * z - 1, yofs=-8 * z),
        animated('14', grid, height=32 * z - 1, yofs=-8 * z),
        animated('15', grid, height=48 * z - 1, yofs=16 * z),
        animated('16', grid, height=16 * z - 1, yofs=0 * z),
        animated('17', grid, height=32 * z - 1, yofs=-8 * z),
        animated('18', grid, height=32 * z - 1, yofs=-8 * z),
    ]


water = lib.SpriteCollection('water') \
    .add(TERRAIN_DIR / 'shorelines.ase',
         tmpl_water_full, ZOOM_2X)
water[0].replace_old(4061)


WATER_COMPOSITION = [(x, x) for x in [16, 1, 2, 3, 4, 17, 6, 7, 8, 9, 15, 11, 12, 13, 14, 18]]
water.compose_on(ground, WATER_COMPOSITION).replace_new(0x0d, 0)


# ------------------------------ Towns ------------------------------

@lib.template(grf.FileSprite)
def tmpl_street_lights(func, z, frame):
    grid = lib.HouseGrid(func=func, height=49, z=z)
    grid.set_default(frame=frame)
    return [
        grid('ne', (0, 0), bb=(1, 8)),
        grid('nw', (1, 0), bb=(8, 1)),
    ]


lib.SpriteCollection('street_lights') \
    .add(TOWN_DIR / 'streetlights.ase', tmpl_street_lights, ZOOM_2X, 1, climate=TEMPERATE) \
    .add(TOWN_DIR / 'streetlights.ase', tmpl_street_lights, ZOOM_2X, 2, climate=ARCTIC) \
    .add(TOWN_DIR / 'streetlights.ase', tmpl_street_lights, ZOOM_2X, 3, climate=TROPICAL) \
    .add(TOWN_DIR / 'streetlights.ase', tmpl_street_lights, ZOOM_2X, 4, climate=TOYLAND) \
    .pick(1, 0) \
    .replace_old(1406)

@lib.template(grf.FileSprite)
def tmpl_statues(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    return [
        grid('statue', (0, 0), bb=(6, 5)),
        animated('fountain', grid, (1, 0), bb=(3, 3)),
        cc(grid('owner_statue', (2, 0), bb=(0, 0))),
        grid('toy_statue', (3, 0), bb=(0, 0)),
        grid('piggy_bank', (4, 0), bb=(0, 0)),
    ]

statues = lib.SpriteCollection('house') \
    .add(TOWN_DIR / 'statues.ase', tmpl_statues, ZOOM_2X)
statues[:2].replace_old(1454)
statues[2].replace_old(2632)
statues[3].replace_old(4694)
statues[4].replace_old(4698)

@lib.template(grf.FileSprite)
def tmpl_shops_and_offices(func, z):
    grid = lib.HouseGrid(func=func, height=100, z=z)
    return [
        struct(grid('29a_ground', (0, 0), bb=(0, 0), frame=3, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder'))),
        struct(grid('29a', (0, 0), bb=(0, 0), frame=3, ignore_layers=('TILE/*', 'FOUNDATION/*'))),
        struct(grid('29b_ground', (1, 0), bb=(0, 0), frame=3, layers=('TILE/*', 'FOUNDATION/*', 'Spriteborder'))),
        struct(grid('29b', (1, 0), bb=(0, 0), frame=3, ignore_layers=('TILE/*', 'FOUNDATION/*'))),

        struct(grid('16_stage1', (2, 0), bb=(2, 0), frame=1, ignore_layers='TILE/*')),
        struct(grid('16_stage2', (2, 0), bb=(2, 0), frame=2, ignore_layers='TILE/*')),
        struct(grid('16_stage3', (2, 0), bb=(2, 0), frame=3, ignore_layers='TILE/*')),

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
    .add(TOWN_DIR / 'shopsandoffices.ase', tmpl_shops_and_offices, ZOOM_2X) \

houses[0:4].replace_old(1536)  # 29
houses[4:7].replace_old(1467)  # 16
houses[7:10].replace_old(1461)  # 14
houses[10:13].replace_old(1466)  # 15
houses[13:19].replace_old(1540)  # 30


# TODO Amateur code, toyhouses
# 4627 first stage of first toy house
# 4628
# 4629 final stage of first toy house
# --
# 4674 final stage of last toy house
@lib.template(grf.FileSprite)
def tmpl_houses_toyland(func, z):
    grid = lib.HouseGrid(func=func, height=100, z=z)
    return [
        grid('church_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('church_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('church_stage3', (0, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('house1_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('house1_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('house1_stage3', (1, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('house2_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('house2_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('house2_stage3', (2, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('house3_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('house3_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('house3_stage3', (3, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('house4_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('house4_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('house4_stage3', (4, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('house5_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('house5_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('house5_stage3', (5, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('house6_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('house6_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('house6_stage3', (6, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('tall-office1_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('tall-office1_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('tall-office1_stage3', (7, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('shoe-left_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('shoe-right_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('shoe-left_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('shoe-right_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('shoe-left_stage3', (8, 0), frame=3, layers=('BUILDING/*', 'Spriteborder')),
        grid('shoe-right_stage3', (0, 1), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('tall-office2_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('tall-office2_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('tall-office2_stage3', (1, 1), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('igloo_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('igloo_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('igloo_stage3', (2, 1), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('tepees_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('tepees_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('tepees_stage3', (3, 1), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('shops-and-offices1_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('shops-and-offices1_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        animated('shops-and-offices2_stage3', grid, (4, 1), frame=3),

        grid('shops-and-offices2_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('shops-and-offices2_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        animated('shops-and-offices2_stage3', grid, (5, 1), frame=3),

        grid('tall-office3_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('tall-office3_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('tall-office3_stage3', (6, 1), frame=3, layers=('BUILDING/*', 'Spriteborder')),

        grid('teapot_stage1', (0, 0), frame=1, layers=('BUILDING/*', 'Spriteborder')),
        grid('teapot_stage2', (0, 0), frame=2, layers=('BUILDING/*', 'Spriteborder')),
        grid('teapot_stage3', (7, 1), frame=3, layers=('BUILDING/*', 'Spriteborder')),
    ]

# TODO Amateur Code
houses_toyland = lib.SpriteCollection('toyhouse') \
    .add(TOWN_DIR / 'houses_toyland.ase', tmpl_houses_toyland, ZOOM_2X) \
    #.replace_old(4627)
houses_toyland[:48].replace_old(4627)
houses_toyland[48:51].replace_old(4695)


@lib.template(grf.FileSprite)
def tmpl_transmitter(func, z):
    grid = lib.HouseGrid(func=func, height=123, z=z)
    return [animated('', grid, (0, 0), bb=(7, 7))]


lib.SpriteCollection('transmitter') \
    .add(TOWN_DIR / 'transmitter.ase', tmpl_transmitter, ZOOM_2X) \
    .replace_old(2601)


@lib.template(grf.FileSprite)
def tmpl_lighthouse(func, z):
    grid = lib.HouseGrid(func=func, height=123, z=z)
    return [animated('', grid, (0, 0), bb=(4, 4))]


lib.SpriteCollection('lighthouse') \
    .add(TOWN_DIR / 'lighthouse.ase', tmpl_lighthouse, ZOOM_2X) \
    .replace_old(2602)


@lib.template(grf.FileSprite)
def tmpl_town_tree(func, z, x):
    grid = lib.RectGrid(func=func, width=19 * z, height=41 * z, padding=z)
    return [grid('', (x, 0), xofs=-9 * z, yofs=-37 * z)]


lib.SpriteCollection('town_tree') \
    .add(TREE_DIR / 'town_trees.ase', tmpl_town_tree, ZOOM_2X, 0, climate=TEMPERATE) \
    .add(TREE_DIR / 'town_trees.ase', tmpl_town_tree, ZOOM_2X, 1, climate=ARCTIC) \
    .add(TREE_DIR / 'town_trees.ase', tmpl_town_tree, ZOOM_2X, 2, climate=TROPICAL) \
    .replace_old(4626)


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
    .add(lib.aseidx(INDUSTRY_DIR / 'coalmine.ase'), tmpl_coal_mine, ZOOM_2X, climate=TEMPERATE) \
    .add(lib.aseidx(INDUSTRY_DIR / 'coalmine.ase'), tmpl_coal_mine, ZOOM_2X, climate=ARCTIC) \
    .add(lib.aseidx(INDUSTRY_DIR / 'coalmine.ase'), tmpl_coal_mine, ZOOM_2X, climate=TROPICAL) \
    .add(lib.aseidx(INDUSTRY_DIR / 'marshmallowmine.ase'), tmpl_coal_mine, ZOOM_2X, climate=TOYLAND) \
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
    .add(lib.aseidx(INDUSTRY_DIR / 'powerplant.ase'), tmpl_powerplant, ZOOM_2X) \
    .replace_old(2045)


@lib.template(grf.FileSprite)
def tmpl_chimney_smoke(func, z):
    return [
        func(f'{i}', x=2, y=2, w=128, h=128, xofs=0, yofs=-128 - (z // 2), frame=i + 1)
        for i in range(8)
    ]

lib.SpriteCollection('chimney_smoke') \
    .add(lib.aseidx(EFFECT_DIR / 'chimney_smoke.ase'), tmpl_chimney_smoke, ZOOM_2X) \
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
lib.SpriteCollection('forest') \
    .add(INDUSTRY_DIR / 'forest_temperate.ase', tmpl_forest, ZOOM_2X) \
    .add(INDUSTRY_DIR / 'forest_arctic.ase', tmpl_forest, ZOOM_2X, climate=ARCTIC) \
    .add(INDUSTRY_DIR / 'cottoncandyforest.ase', tmpl_forest, ZOOM_2X, climate=TOYLAND) \
    .replace_old(2072)


# TODO This is basically a copy of the forest template except for the tile sprite,
# not sure if that's the proper way to do this or to manipulate the forest template to be able to...
# skip the ground sprite for the battery farm.
@lib.template(grf.FileSprite)
def tmpl_batteryfarm(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('growth1', (0, 0), frame=1, ignore_layers=ground_layers),
        grid('growth2', (0, 0), frame=2, ignore_layers=ground_layers),
        grid('growth3', (0, 0), frame=3, ignore_layers=ground_layers),
        grid('grown', (0, 0), frame=4, ignore_layers=ground_layers),
        grid('logs', (0, 0), frame=5, ignore_layers=ground_layers),
    ]


lib.SpriteCollection('batteryfarm') \
    .add(INDUSTRY_DIR / 'batteryfarm.ase', tmpl_batteryfarm, ZOOM_2X) \
    .replace_old(4686)


@lib.template(grf.FileSprite)
def tmpl_plantation(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('plantation_ground', (0, 0), frame=1, layers=ground_layers),
        grid('trees_fruit', (0, 0), frame=1, ignore_layers=ground_layers),
        grid('trees_rubber', (0, 0), frame=2, ignore_layers=ground_layers),
    ]


lib.SpriteCollection('plantation') \
    .add(INDUSTRY_DIR / 'plantation.ase', tmpl_plantation, ZOOM_2X) \
    .replace_old(2341)


@lib.template(grf.FileSprite)
def tmpl_water_tower(func, z):
    grid = lib.HouseGrid(func=func, height=128, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('water_tower_stage1', (0, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('water_tower_stage2', (0, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('water_tower_stage3', grid, (0, 0), frame=3, ignore_layers=ground_layers)),
    ]


lib.SpriteCollection('water_tower') \
    .add(INDUSTRY_DIR / 'water_tower.ase', tmpl_water_tower, ZOOM_2X) \
    .replace_old(2344)


@lib.template(grf.FileSprite)
def tmpl_water_supply(func, z):
    grid = lib.HouseGrid(func=func, height=128, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('building1_stage1', (0, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('building1_stage2', (0, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('building1_stage3', grid, (0, 0), frame=3, ignore_layers=ground_layers)),
        grid('building2_stage1', (1, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('building2_stage2', (1, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('building2_stage3', grid, (1, 0), frame=3, ignore_layers=ground_layers)),
    ]


lib.SpriteCollection('water_supply') \
    .add(INDUSTRY_DIR / 'water_supply.ase', tmpl_water_supply, ZOOM_2X) \
    .replace_old(2347)


@lib.template(grf.FileSprite)
def tmpl_food_processing_plant(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('building1_stage1', (0, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('building1_stage2', (0, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('building1_stage3', grid, (0, 0), frame=3, ignore_layers=ground_layers)),
        grid('building2_stage1', (1, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('building2_stage2', (1, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('building2_stage3', grid, (1, 0), frame=3, ignore_layers=ground_layers)),
        grid('building3_stage1', (2, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('building3_stage2', (2, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('building3_stage3', grid, (2, 0), frame=3, ignore_layers=ground_layers)),
        grid('building4_stage1', (3, 0), frame=1, ignore_layers=ground_layers),
        cc(grid('building4_stage2', (3, 0), frame=2, ignore_layers=ground_layers)),
        cc(animated('building4_stage3', grid, (3, 0), frame=3, ignore_layers=ground_layers)),
    ]


lib.SpriteCollection('food_processing_plant') \
    .add(INDUSTRY_DIR / 'food_processing_plant.ase', tmpl_food_processing_plant, ZOOM_2X) \
    .replace_old(2188)


@lib.template(grf.FileSprite)
def tmpl_paper_mill(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    ground_layers = ('TILE/*', 'Spriteborder')
    return [
        grid('building1_stage1', (0, 0), frame=1, ignore_layers=ground_layers),
        grid('building1_stage2', (0, 0), frame=2, ignore_layers=ground_layers),
        grid('building1_stage3', (0, 0), frame=3, ignore_layers=ground_layers),

        grid('building2_stage1', (1, 0), frame=1, ignore_layers=ground_layers),
        grid('building2_stage2', (1, 0), frame=2, ignore_layers=ground_layers),
        grid('building2_stage3', (1, 0), frame=3, ignore_layers=ground_layers),
        animated('building2_animated', grid, (1, 0), frame=4),

        grid('building3_stage1', (2, 0), frame=1, ignore_layers=ground_layers),
        grid('building3_stage2', (2, 0), frame=1, ignore_layers=ground_layers),
        grid('building3_stage3', (2, 0), frame=1, ignore_layers=ground_layers),
        
        grf.EMPTY_SPRITE,

        grid('building4_stage1', (3, 0), frame=1, ignore_layers=ground_layers),
        grid('building4_stage2', (3, 0), frame=1, ignore_layers=ground_layers),
        grid('building4_stage3', (3, 0), frame=1, ignore_layers=ground_layers),

        grid('building5', (4, 0), frame=1, ignore_layers=ground_layers),
    ]


lib.SpriteCollection('paper_mill') \
    .add(INDUSTRY_DIR / 'paper_mill.ase', tmpl_paper_mill, ZOOM_2X) \
    .replace_old(2200)
    # 123 # 1234 # 123 #empty # 123 # afdakje
    # 2206 heeft anim


@lib.template(grf.FileSprite)
def tmpl_oil_refinery(func, z):
    grid = lib.HouseGrid(func=func, height=128, z=z)
    return [
        cc(grid('building1_stage1', (0, 0), bb=(1, 1), frame=1)),
        cc(grid('building1_stage2', (0, 0), bb=(1, 1), frame=2)),
        cc(grid('building1_stage3', (0, 0), bb=(1, 1), frame=3)),
        cc(grid('building2_stage1', (1, 0), bb=(3, 3), frame=1)),
        cc(grid('building2_stage2', (1, 0), bb=(3, 3), frame=2)),
        cc(grid('building2_stage3', (1, 0), bb=(3, 3), frame=3)),
        cc(grid('building3_stage1', (2, 0), bb=(4, 4), frame=1)),
        cc(grid('building3_stage2', (2, 0), bb=(4, 4), frame=2)),
        cc(animated('building3', grid, (2, 0), bb=(4, 4), frame=3)),
        cc(grid('building4_stage1', (3, 0), bb=(2, 0), frame=1)),
        cc(grid('building4_stage2', (3, 0), bb=(2, 0), frame=2)),
        cc(grid('building4_stage3', (3, 0), bb=(2, 0), frame=3)),
        cc(grid('building5_stage1', (4, 0), bb=(0, 0), frame=1)),
        cc(grid('building5_stage2', (4, 0), bb=(0, 0), frame=2)),
        cc(grid('building5_stage3', (4, 0), bb=(0, 0), frame=3)),
        cc(grid('building6_stage1', (5, 0), bb=(3, 1), frame=1)),
        cc(grid('building6_stage2', (5, 0), bb=(3, 1), frame=2)),
        cc(grid('building6_stage3', (5, 0), bb=(3, 1), frame=3)),
    ]

lib.SpriteCollection('oil_refinery') \
    .add(INDUSTRY_DIR / 'oilrefinery.ase', tmpl_oil_refinery, ZOOM_2X) \
    .replace_old(2078)


@lib.template(grf.FileSprite)
def tmpl_oil_rig(func, z):
    assert z == 2

    def chunk(name, x, w, h, *, xofs, frame):
        x = x + 2
        yofs = -282 + h - (z // 2)
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
    .add(INDUSTRY_DIR / 'oilrig.ase', tmpl_oil_rig, ZOOM_2X) \
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
    .add(INDUSTRY_DIR / 'farm_temperate.ase', tmpl_farm, ZOOM_2X, climate=TEMPERATE) \
    .add(INDUSTRY_DIR / 'farm_arctic.ase', tmpl_farm, ZOOM_2X, climate=ARCTIC) \
    .add(INDUSTRY_DIR / 'farm_tropical.ase', tmpl_farm, ZOOM_2X, climate=TROPICAL) \
    .replace_old(2106)


@lib.template(grf.FileSprite)
def tmpl_farm_fences(func, z, frame):
    relative = 0
    x_xofs, x_yofs = -59 - relative, 21 - relative // 2
    y_xofs, y_yofs = -3 + relative, 21 - relative // 2
    return [
        func('flat_x', 2 + 68 * 1, 2, 66, 44, xofs=x_xofs, yofs=x_yofs - (z // 2), frame=frame),
        func('flat_y', 2 + 68 * 0, 2, 66, 44, xofs=y_xofs, yofs=y_yofs - (z // 2), frame=frame),
        func('high_x', 2 + 68 * 5, 2, 66, 60, xofs=x_xofs, yofs=x_yofs - 16 - (z // 2), frame=frame),
        func('high_y', 2 + 68 * 4, 2, 66, 60, xofs=y_xofs, yofs=y_yofs - 16 - (z // 2), frame=frame),
        func('low_x', 2 + 68 * 3, 2, 66, 28, xofs=x_xofs, yofs=x_yofs + 16 - (z // 2), frame=frame),
        func('low_y', 2 + 68 * 2, 2, 66, 28, xofs=y_xofs, yofs=y_yofs + 16 - (z // 2), frame=frame),
    ]


for i in range(6):
    lib.SpriteCollection(f'farm_fence{i}') \
        .add(TERRAIN_DIR / 'farmfences.ase', tmpl_farm_fences, ZOOM_2X, i + 1) \
        .replace_old(4090 + i * 6)


@lib.template(grf.FileSprite)
def tmpl_steel_mill(func, z):
    assert z == 2
    ground_layers = ('TILE/*', 'Spriteborder')
    building_layers = ('BUILDING/*', 'Spriteborder')

    def building(name, *args, **kw):
        return cc(lib.AlphaAndMask(
            func(name, *args, **kw, layers=building_layers),
            func(name + '_anim', *args, **kw, layers=('ANIMATED/*',)),
        ))

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
    .add(INDUSTRY_DIR / 'steelmill.ase', tmpl_steel_mill, ZOOM_2X) \
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
        func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=2),
    ]


lib.SpriteCollection('factory') \
    .add(INDUSTRY_DIR / 'factory.ase', tmpl_factory, ZOOM_2X) \
    .replace_old(2146)


@lib.template(grf.FileSprite)
def tmpl_printing_works(func, z):
    assert z == 2
    return [
        grf.EMPTY_SPRITE,
        func('building2_stage1', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building3_stage1', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building4_stage1', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),

        grf.EMPTY_SPRITE,
        cc(func('building2_stage2', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=2)),
        cc(func('building3_stage2', 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=2)),
        cc(func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=2)),
        
        grf.EMPTY_SPRITE,
        cc(func('building2_stage3', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        cc(func('building3_stage3', 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        cc(func('building4_stage3', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=3)),
    ]


lib.SpriteCollection('printing_works') \
    .add(INDUSTRY_DIR / 'printing_works.ase', tmpl_printing_works, ZOOM_2X) \
    .replace_old(2161)


# TODO Amateur Code
@lib.template(grf.FileSprite)
def tmpl_candy_factory(func, z):
    assert z == 2
    return [
        func('building2_stage1', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building4_stage1', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),
        func('building3_stage1', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building2_stage2', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=2),
        func('building3_stage2', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=2),
        cc(func('building2_stage3', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        grf.EMPTY_SPRITE, # Left and right buildings cover this one completely and also closest one that doesn't have a sprite (possible glitchy though)
        cc(func('building3_stage3', 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
    ]


# TODO Amateur Code
candy_factory = lib.SpriteCollection('candy_factory') \
    .add(INDUSTRY_DIR / 'candyfactory.ase', tmpl_candy_factory, ZOOM_2X) \
    .replace_old(4677)


# TODO Amateur Code
@lib.template(grf.FileSprite)
def tmpl_toy_shop(func, z):
    assert z == 2
    return [
        func('building2_stage1', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building3_stage1', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building4_stage1', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),
        func('building2_stage2', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building3_stage2', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=2),
        cc(func('building2_stage3', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        cc(animated('building3_stage3', func, 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        grf.EMPTY_SPRITE, # Left and right buildings cover this one completely and also closest one that doesn't have a sprite (possible glitchy though)
    ]


# TODO Amateur Code
toy_shop = lib.SpriteCollection('toy_shop') \
    .add(INDUSTRY_DIR / 'toyshop.ase', tmpl_toy_shop, ZOOM_2X) \
    .replace_old(4699)


# TODO Amateur Code
@lib.template(grf.FileSprite)
def tmpl_lumber_mill(func, z):
    assert z == 2
    return [
        grf.EMPTY_SPRITE,
        func('building2_stage1', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building3_stage1', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=1),
        func('building4_stage1', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),
        grf.EMPTY_SPRITE,
        func('building2_stage2', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building3_stage2', 2, 2, 64, 169, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=2),
        func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=2),
        grf.EMPTY_SPRITE,
        cc(func('building2_stage3', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        cc(func('building3_stage3', 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        grf.EMPTY_SPRITE,
    ]


# TODO Amateur Code
lumber_mill = lib.SpriteCollection('lumber_mill') \
    .add(INDUSTRY_DIR / 'lumber_mill.ase', tmpl_lumber_mill, ZOOM_2X) \
    .replace_old(2353)


# TODO Amateur Code
# building1 = north
# building2 = east
# building3 = west
# building4 = south
@lib.template(grf.FileSprite)
def tmpl_fizzy_drink_factory(func, z):
    assert z == 2
    return [
        func('building4_stage1', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=1),
        func('building4_stage2', 66, 2, 128, 169 + 32, xofs=-62, yofs=-106-32, ignore_layers='TILE/*', frame=2),
        func('building2_stage2', 130 + 64, 2, 64, 169, xofs=2, yofs=-106, ignore_layers='TILE/*', frame=2),
        cc(func('building2_stage3', 130, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
        grf.EMPTY_SPRITE, # Center. Left and right buildings cover this one completely and also closest one that doesn't have a sprite (possible glitchy though)
        cc(func('building3_stage3', 2, 2, 128, 169 + 32, xofs=-62, yofs=-106, ignore_layers='TILE/*', frame=3)),
    ]


# TODO Amateur Code
fizzy_drink_factory = lib.SpriteCollection('fizzy_drink_factory') \
    .add(INDUSTRY_DIR / 'fizzydrinkfactory.ase', tmpl_fizzy_drink_factory, ZOOM_2X) \
    .replace_old(4737)


@lib.template(grf.FileSprite)
def tmpl_oil_wells(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    f = lambda frame: grid('frame{i}', (0, 0), layers=('BUILDING/*', 'Spriteborder'), frame=frame)
    return [
        func('ground', 2, 90, 128, 63, xofs=-31 * z, yofs=0, layers=('TILE/*', 'Spriteborder'), frame=1)
    ] + [f(i + 1) for i in range(6)]


oil_wells = lib.SpriteCollection('oil_wells') \
    .add(INDUSTRY_DIR / 'oilwells.ase', tmpl_oil_wells, ZOOM_2X)
oil_wells[0].compose_on(ground[0]).replace_old(2173)
oil_wells[1:].replace_old(2174)


# TODO Check amateur code, Plastic Fountain template
# Even though the current TILE is not animated,
# it would be nice to use the frames anyway in case it changes into animation later.
@lib.template(grf.FileSprite)
def tmpl_plastic_fountains(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    f = lambda frame: grid('frame{i}', (0, 0), layers=('BUILDING/*', 'Spriteborder'), frame=frame)
    return [
        func('ground', 2, 90, 128, 63, xofs=-31 * z, yofs=0, layers=('TILE/*', 'Spriteborder'), frame=1)
    ] + [f(i + 1) for i in range(8)]


# TODO Check amateur code, Plastic Fountain
plastic_fountain = lib.SpriteCollection('plastic_fountain') \
    .add(INDUSTRY_DIR / 'plasticfountain.ase', tmpl_plastic_fountains, ZOOM_2X)
plastic_fountain[0].compose_on(ground[0]).replace_old(4721)
plastic_fountain[0].compose_on(ground[0]).replace_old(4722)
plastic_fountain[0].compose_on(ground[0]).replace_old(4723)
plastic_fountain[0].compose_on(ground[0]).replace_old(4724)
plastic_fountain[0].compose_on(ground[0]).replace_old(4725)
plastic_fountain[0].compose_on(ground[0]).replace_old(4726)
plastic_fountain[0].compose_on(ground[0]).replace_old(4727)
plastic_fountain[0].compose_on(ground[0]).replace_old(4728)
plastic_fountain[1:].replace_old(4729)


# TODO Check amateur code, Cola Wells template
@lib.template(grf.FileSprite)
def tmpl_cola_wells(func, z):
    grid = lib.HouseGrid(func=func, height=75, z=z)
    f = lambda frame: animated('frame{i}', grid, (0, 0), bb=(0, 0), frame=frame)
    return [f(i + 1) for i in range(3)]


# TODO Check amateur code, Cola Wells
cola_wells = lib.SpriteCollection('cola_wells') \
    .add(INDUSTRY_DIR / 'colawells.ase', tmpl_cola_wells, ZOOM_2X)
cola_wells.replace_old(4691)


@lib.template(grf.FileSprite)
def tmpl_bank(func, z, frame):
    assert z == 2
    ground = func('ground', 2, 2, 192, 160, xofs=-126, yofs=-65, layers=('TILE/*', 'Spriteborder'), frame=frame)
    return [
        func('building1', 130, 2, 64, 160, xofs=2, yofs=-65, layers=('BUILDING/*', 'Spriteborder'), frame=frame),
        func('building2', 2, 2, 128, 160, xofs=-62, yofs=-97, layers=('BUILDING/*', 'Spriteborder'), frame=frame),
        lib.CutGround(ground, (1, 0), name='ground1'),
        lib.CutGround(ground, (0, 0), name='ground2'),
    ]


lib.SpriteCollection('bank') \
    .add(INDUSTRY_DIR / 'bank.ase', tmpl_bank, ZOOM_2X, 1) \
    .replace_old(2180)

lib.SpriteCollection('bank') \
    .add(INDUSTRY_DIR / 'bank.ase', tmpl_bank, ZOOM_2X, 2, climate=ARCTIC) \
    .add(INDUSTRY_DIR / 'bank.ase', tmpl_bank, ZOOM_2X, 3, climate=TROPICAL) \
    .pick(3, 2, 0, 1) \
    .replace_old(2184)


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
        .add(INDUSTRY_DIR / 'ironoremine.ase', tmpl_iron_mine, ZOOM_2X, i + 1, name=f'stage{i + 1}') \
        .replace_old(2293 + 16 * i)


@lib.template(grf.FileSprite)
def tmpl_toy_factory(func, z):
    grid = lib.BuildingSlicesGrid(func=func, offset=(z, z), z=z, tile_size=(4, 2), xofs=-256, yofs=-135)
    grid.set_default(layers=('BUILDING', 'BUILDING_INSIDE', 'Spriteborder'))
    # building stage 4708
    # grid('', (0, 1)),
    # grid('', (1, 1)), # back
    # grid('', (2, 1)),
    # grid('', (3, 1)),
    # no 3, 0
    assert z == 2
    toy_grid = lib.RectGrid(func=func, width=26, height=41, padding=z)
    toy_grid.set_default(layers='OBJECTS')
    return [
        grid('0_1', (0, 1)),
        grid('1_1_back', (1, 1), layers=('BUILDING_INSIDE', 'Spriteborder')),
        grid('2_1', (2, 1)),
        grid('3_1', (3, 1)),
        grid('3_0', (3, 0)),
        grid('1_1_front', (1, 1), xofs=0, yofs=-110, layers=('BUILDING', 'Spriteborder')),  # WARNING relative offset nonsense
        func('stomper', 198, 2, 54, 196, xofs=-32, yofs=-64, layers='STOMPER'),  # NOTE positioned randomly
        toy_grid('lump', (0, 0), xofs=-32, yofs=-100 + 16 - 32),  # NOTE positioned randomly
        toy_grid('duck', (1, 0), xofs=-32, yofs=-100 + 16),  # NOTE positioned randomly
    ]

lib.SpriteCollection('toy_factory') \
    .add(INDUSTRY_DIR / 'toyfactory.ase', tmpl_toy_factory, ZOOM_2X, name='toy_factory') \
    .replace_old(4712)


# ------------------------------ User Interface ------------------------------

@lib.template(grf.FileSprite)
def tmpl_cargo_icons(func, z, frame):
    grid = lib.RectGrid(func=func, width=11 * z, height=11 * z, padding=z)
    grid.set_default(frame=frame)
    return [grid(str(i), (i, 0)) for i in range(27)]


lib.SpriteCollection('cargo_icon') \
    .add(ICON_DIR / 'cargo.ase', tmpl_cargo_icons, ZOOM_2X, 1, climate=TEMPERATE) \
    .add(ICON_DIR / 'cargo.ase', tmpl_cargo_icons, ZOOM_2X, 2, climate=ARCTIC) \
    .add(ICON_DIR / 'cargo.ase', tmpl_cargo_icons, ZOOM_2X, 3, climate=TROPICAL) \
    .add(ICON_DIR / 'cargo.ase', tmpl_cargo_icons, ZOOM_2X, 4, climate=TOYLAND) \
    .replace_old(4297)


# NOTE this table uses sprite ids outside of the original range that can become outdated.
# But the code below translates them into Action 5 range so compiled grf will work fine.
ICON_SHEET = (
    ( 679,  680,  681,  684,  708,  713,  723, 4083, 4986),
    ( 724,  725,  726,  735,  736,  737,  745,  751,   -1),  # TODO
    ( 693,  694,  695,  703,  714, 4987,  -1,  -1,  -1),  # 704-707 removed dynamite cursor
    ( 709,  710,  711,  712,  -1,  697,  698,  700,  701),
    ( 727,  728,  729,  730, 5075, 2594),
    ( 731,  732,  733,  734,   -1,   -1,   -1),  # TODO
    ( 738,  739,  740,  741,  742,  743, 4077, 4082,   -1),  # TODO
    (1298,    0,  746,  744,    0,  750,  749, 1299, 1291),
    ( 685,  686,  748, 5391,   -1, 1291, 4972, 4984, 5041),  # TODO  685 dup? 686->1295 ?
    (1251, 1252, 1253, 1254, 2430, 4949, 4951, 1294),  # rail
    (5667, 5668, 5669, 5670, 5675, 4953, 4955, 4957),  # elrl
    (1255, 1256, 1257, 1258, 2431, 4959, 4961, 4963),  # mono
    (1259, 1260, 1261, 1262, 2432, 4965, 4967, 4969),  # maglev
    (   0, 5986,    0, 5985,   -1, 4980, 5078),  # tram  tunnel seems unused
    (   0, 1309,    0, 1310, 2429, 4978, 5076),  # road
    (4084, 4085, 4086, 4791, 5032, 5030, 4085),
    (4989, 4990, 4991, 4992, 4993, 4994, 4995, 4996, 5001),  # 4993-4996?
    (4997, 4998, 4999, 5000, 5010, 5011, 5012, 5013), # 5014, 5015, 5016, 5017
    (5022, 5023, 5024, 5025, 5018, 5019, 5020, 5021, 5031),
    (5026, 5027, 5028, 5029),
    (5065, 5066, 5067, 5068, 5069, 5070),
    (5071, 5072, 5073, 5074, 5002, 5003, 5004, 5005),

)
# 694: 696,
# 695: 699,
# 703: 704,
# 4077: 4088,  # that's lighthouse cursor though
# 1291: 1293,
# 1251 - 1262 -> 1263 - 1274

# 4084, 4085, 4086 - > 4087, 4088, 4089
CURSOR_SPRITES = [697,  698,  700,  701]
ICON_WIDTH = {2594: 43, 1298: 40, 744: 39}
ANIMATED_SRPITES = (4085, 4086)  # TODO
COPY_ICONS = {4993: 5014, 4994: 5015, 4995: 5016, 4996: 5017}

ase = lib.aseidx(ICON_DIR / 'icons.ase')
func = lambda name, *args, **kw: grf.FileSprite(ase, *args, **kw, name=name, ignore_layers='REF Numbers')
z = 2
grid = lib.RectGrid(func=func, width=20 * z, height=20 * z, padding=z)
grid.set_default(zoom=ZOOM_2X)
res = []

ACTION5_RANGES = [
    (4896, 191, 0x15),
    (5327, 65, 0x08),
    (5631, 48, 0x05),
    (5985, 119, 0x0B),
]

def replace_by_global_id(sid, sprites):
    if sid < 4896:
        lib.replace_old(None, sid, sprites)
        return

    for start, count, set_type in ACTION5_RANGES:
        if start <= sid < start + count:
            lib.replace_new(None, set_type, sid - start, sprites)
            return

    assert False, sid


for i, row in enumerate(ICON_SHEET):
    for j, sid in enumerate(row):
        if sid <= 0:
            continue
        sprite = grid(f'ui_{sid}', (j, i), width=ICON_WIDTH.get(sid, 20) * z)
        replace_by_global_id(sid, [sprite])
        if sid in COPY_ICONS:
            replace_by_global_id(COPY_ICONS[sid], [sprite])

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
modes = list(set(lib.old_sprites.keys()) | set(lib.new_sprites.keys()))

# Toposort
covers = defaultdict(list)
ncovered = [0] * len(modes)
for i, mi in enumerate(modes):
    mikeys = frozenset(x[0] for x in mi)
    for j, mj in enumerate(modes):
        if i == j:
            continue
        mjkeys = frozenset(x[0] for x in mj)
        if mikeys == mjkeys:
            continue
        if mikeys.issubset(mjkeys):
            ncovered[i] += 1
            covers[j].append(i)

unordered = list(range(len(modes)))
modes_order = []
while unordered:
    new_unordered = []
    for k in unordered:
        if ncovered[k] > 0:
            new_unordered.append(k)
            continue

        modes_order.append(k)
        for i in covers[k]:
            ncovered[i] -= 1

    unordered = new_unordered


for i in reversed(modes_order):
    mode = modes[i]
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


# ------------------------------ Command Line Interface ------------------------------

def cmd_debugcc_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')
    parser.add_argument('--frame', help='Frame number to export', type=int, default=1)


def cmd_debugcc_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file)
    sprite = grf.FileSprite(ase, 0, 0, None, None, name=args.ase_file, layers=args.layer, frame=args.frame)
    sprite = cc(sprite)
    lib.debug_cc_recolour([sprite], horizontal=args.horizontal)


def cmd_debugstruct_add_args(parser):
    parser.add_argument('ase_file', help='Aseprite image file')
    parser.add_argument('--horizontal', action='store_true', help='Stack resulting images horizontally')
    parser.add_argument('--layer', help='Name of the layer in aseprite file to export')
    parser.add_argument('--frame', help='Frame number to export', type=int, default=1)


def cmd_debugstruct_handler(g, grf_file, args):
    ase = lib.AseImageFile(args.ase_file)
    sprite = grf.FileSprite(ase, 0, 0, None, None, name=args.ase_file, layers=args.layer, frame=args.frame)
    sprite = struct(sprite)
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
