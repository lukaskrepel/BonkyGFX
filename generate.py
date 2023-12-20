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

def tmpl_groundtiles(png, y, **kw):
    func = lambda x, y, *args, **kw: grf.FileSprite(png, x, y, *args, zoom=grf.ZOOM_2X, **kw)
    # Same spriteset template as in OpenGFX2
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


def replace_old(first_id, sprites):
    amount = len(sprites)
    g.add(grf.ReplaceOldSprites([(first_id, amount)]))
    g.add(*sprites)

# Normal land

temperate_ground_png = grf.ImageFile('sprites/temperate_groundtiles_32bpp.png', colourkey=(0, 0, 255))
replace_old(3924, tmpl_groundtiles(temperate_ground_png, 144))  # 0% grass
replace_old(3943, tmpl_groundtiles(temperate_ground_png, 96))   # 33% grass
replace_old(3962, tmpl_groundtiles(temperate_ground_png, 48))   # 66% grass
replace_old(3981, tmpl_groundtiles(temperate_ground_png, 0))    # 100% grass

grf.main(g, 'bonkygfx.grf')
