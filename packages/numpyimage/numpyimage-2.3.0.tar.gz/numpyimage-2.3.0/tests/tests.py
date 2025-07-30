#!/usr/bin/env python3

import numpy as np
import fire

import npimage
import npimage.operations

test_im = np.zeros((8, 8), dtype=np.uint8)
test_im[0:1, 0:2] = 255
test_im[1:3, 2:4] = 255
test_im[3:7, 3:7] = 255


def mplshow(*args):
    npimage.show(*args, mode='matplotlib')


def test_offset():
    mplshow(test_im)
    mplshow(npimage.operations.offset(test_im, (0.5, 0)))
    mplshow(npimage.operations.offset(test_im, (0, 0.5)))
    mplshow(npimage.operations.offset(test_im, (0.5, 0.5)))
    mplshow(npimage.operations.offset(test_im, (1, 1)))


def test_paste():
    offsets = [('++', [100, 50]),
               ('+-', [100, -50]),
               ('-+', [-100, 50]),
               ('--', [-100, -50])]
    for offset in offsets:
        im = npimage.load('firefox-logo.png', dim_order='xy')
        npimage.operations.paste(im, im, offset[1])
        npimage.save(im, 'firefox-logo_paste' + offset[0] + '.png', dim_order='xy')


if __name__ == '__main__':
    fire.Fire()
