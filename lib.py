import time

import numpy as np

import grf


THIS_FILE = grf.PythonFile(__file__)


class CCReplacingFileSprite(grf.FileSprite):
    def __init__(self, file, *args, **kw):
        super().__init__(file, *args, **kw, mask=None, bpp=grf.BPP_32)

    def get_data_layers(self, encoder=None):
        w, h, img, bpp = self._do_get_image(encoder)

        t0 = time.time()

        if bpp != grf.BPP_32:
            raise RuntimeError('Only 32-bit RGB sprites are currently supported for CC replacement')

        npimg = np.asarray(img).copy()

        crop_x, crop_y, w, h, npimg, npalpha = self._do_crop(w, h, npimg, None)

        magenta_mask = (npimg[:, :, 0] == npimg[:, :, 2])
        luminosity = ((npimg[magenta_mask][:, 0] + npimg[magenta_mask][:, 1]) // 2)
        npimg[magenta_mask][:, 0] = luminosity
        npimg[magenta_mask][:, 1] = luminosity
        npimg[magenta_mask][:, 2] = luminosity

        npmask = np.zeros((h, w), dtype=np.uint8)
        npmask[magenta_mask] = 0xCA

        if encoder is not None:
            encoder.count_composing(time.time() - t0)

        return w, h, self.xofs + crop_x, self.yofs + crop_y, npimg, npalpha, npmask


    def get_resource_files(self):
        return super().get_resource_files() + (THIS_FILE,)
