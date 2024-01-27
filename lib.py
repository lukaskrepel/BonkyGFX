import os
import pathlib
import subprocess
import time
import tempfile
from collections import defaultdict

import numpy as np
from PIL import Image

import grf
from grf import ZOOM_NORMAL, ZOOM_2X, ZOOM_4X, TEMPERATE, ARCTIC, TROPICAL, TOYLAND, ALL_CLIMATES


# VALUE_TO_BRIGHTNESS = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 91, 91, 92, 93, 94, 95, 95, 96, 97, 98, 99, 100, 100, 101, 102, 103, 104, 105, 105, 106, 107, 108, 109, 109, 110, 111, 112, 113, 114, 114, 115, 116, 117, 118, 118, 119, 120, 121, 122, 123, 123, 124, 125, 126, 127, 127, 128, 129, 130, 131, 107, 108, 109, 109, 110, 111, 111, 112, 113, 113, 114, 115, 115, 116, 117, 117, 118, 119, 119, 120, 121, 121, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 129, 130, 130, 131, 132, 132, 133, 134, 134, 135, 136, 136, 137, 138, 138, 139, 140, 140, 120, 120, 121, 121, 122, 122, 123, 124, 124, 125, 125, 126, 126, 127, 127, 128, 129, 129, 130, 130, 131, 131, 132, 133, 133, 134, 134, 135, 135, 136, 137, 137, 138, 138, 139, 139, 140, 141, 141, 142, 142, 143, 143, 144, 145, 146, 146, 147, 147, 148, 127, 128, 128, 128, 128, 130, 130, 131, 131, 132, 132, 133, 133, 134, 134, 135, 135, 136, 136, 137, 137, 138, 138, 139, 139, 140, 140, 141, 141, 142, 143, 143, 144, 144, 144, 145, 145, 146, 146, 147, 147, 148, 148, 149, 149, 150, 150, 151, 151, 152, 130, 131, 131, 132, 132, 133, 133, 134, 134, 135, 135, 136, 136, 137, 137, 138, 138, 139, 140, 140, 141, 141, 142, 142, 143, 143, 144, 144, 145, 145, 146, 146, 147, 147, 148, 148, 149, 150, 150, 151, 151, 152, 152, 153, 153, 154, 155, 155, 156, 156, 130, 130, 131, 131, 132, 132, 132, 133, 134, 134, 135, 135, 136, 136, 137, 137, 138, 139, 139, 140, 140, 141, 141, 142, 142, 143, 144, 144, 145, 145, 146, 146, 147, 147, 148, 149, 149, 150, 150, 151, 151, 152, 152, 153, 154, 154, 155, 156, 156, 157, 131, 132, 132, 133, 133, 134, 134, 135, 135, 136, 136, 137, 138, 138, 139, 139, 140, 140, 141, 141, 142, 143, 143, 144, 144, 145, 145, 146, 147, 147, 148, 149, 149, 150, 151, 151, 152, 152, 153, 154, 154, 155, 156, 156, 157, 157, 158, 159, 160, 160, 161, 162, 162, 163, 164, 165, 166, 166, 167, 168, 168, 169, 170, 171, 172, 173, 174, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 191, 192, 193, 194, 195, 197, 198, 199, 201, 203, 204, 206, 208, 210, 211, 214, 216, 218, 218])
# VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7])
# VALUE_TO_BRIGHTNESS = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 55, 57, 58, 59, 59, 61, 61, 63, 64, 64, 65, 67, 68, 69, 69, 70, 72, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 96, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 125, 125, 126, 127, 128, 128, 130, 131, 132, 133, 134, 134, 136, 136, 136, 138, 138, 141, 117, 117, 119, 119, 119, 119, 122, 122, 123, 123, 124, 125, 125, 127, 127, 128, 128, 129, 130, 131, 131, 132, 133, 134, 134, 134, 136, 136, 137, 138, 138, 140, 117, 118, 118, 119, 119, 120, 121, 121, 122, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 134, 134, 134, 135, 136, 136, 136, 137, 119, 119, 120, 120, 121, 122, 122, 123, 123, 124, 124, 125, 126, 126, 126, 127, 127, 128, 128, 129, 130, 130, 130, 131, 132, 132, 132, 133, 134, 134, 134, 136, 136, 136, 136, 137, 138, 121, 121, 121, 122, 122, 123, 123, 123, 123, 125, 125, 125, 125, 126, 126, 127, 127, 127, 128, 128, 128, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 133, 134, 135, 135, 135, 135, 136, 136, 137, 138, 120, 120, 120, 121, 122, 122, 123, 123, 123, 123, 124, 124, 125, 125, 125, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 130, 130, 131, 131, 132, 132, 132, 133, 134, 134, 134, 134, 135, 135, 136, 136, 137, 138, 138, 138, 138, 139, 139, 121, 121, 121, 122, 122, 122, 122, 123, 123, 124, 124, 124, 124, 125, 125, 125, 126, 126, 126, 127, 127, 127, 127, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 134, 135, 135, 135, 136, 137, 137, 137, 137, 137, 139, 139, 122, 123, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 133, 133, 134, 135, 135, 135, 136, 137, 137, 137, 137, 138, 138, 139, 139, 141, 141, 141, 141, 141, 141, 141, 142, 143, 144, 144, 144, 145, 145, 149, 151, 152, 153, 153, 153, 155, 155, 155, 156, 158, 158, 159, 159, 159, 163, 163, 164, 164, 164, 166, 168, 168, 168, 168, 236, 236, 236, 245, 245, 249, 250, 252, 253, 254, 254, 215, 219, 238, 238, 242, 245, 248, 248, 248, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
# VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7])
CC_VALUE_TO_BRIGHTNESS = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 55, 57, 58, 59, 59, 61, 61, 63, 64, 64, 65, 67, 68, 69, 69, 70, 72, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 96, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 125, 125, 126, 127, 128, 128, 130, 131, 132, 133, 134, 134, 136, 136, 136, 138, 138, 141, 117, 117, 119, 119, 119, 119, 122, 122, 123, 123, 124, 125, 125, 127, 127, 128, 128, 129, 130, 131, 131, 132, 133, 134, 134, 134, 136, 136, 137, 138, 138, 140, 117, 118, 118, 119, 119, 120, 121, 121, 122, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 134, 134, 134, 135, 136, 136, 136, 137, 119, 119, 120, 120, 121, 122, 122, 123, 123, 124, 124, 125, 126, 126, 126, 127, 127, 128, 128, 129, 130, 130, 130, 131, 132, 132, 132, 133, 134, 134, 134, 136, 136, 136, 136, 137, 138, 121, 121, 121, 122, 122, 123, 123, 123, 123, 125, 125, 125, 125, 126, 126, 127, 127, 127, 128, 128, 128, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 133, 134, 135, 135, 135, 135, 136, 136, 137, 138, 120, 120, 120, 121, 122, 122, 123, 123, 123, 123, 124, 124, 125, 125, 125, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 130, 130, 131, 131, 132, 132, 132, 133, 134, 134, 134, 134, 135, 135, 136, 136, 137, 138, 138, 138, 138, 139, 139, 121, 121, 121, 122, 122, 122, 122, 123, 123, 124, 124, 124, 124, 125, 125, 125, 126, 126, 126, 127, 127, 127, 127, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 134, 135, 135, 135, 136, 137, 137, 137, 137, 137, 139, 139, 122, 123, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 129, 129, 130, 130, 130, 130, 131, 131, 132, 132, 132, 132, 133, 133, 133, 133, 134, 134, 135, 135, 135, 135, 136, 136, 137, 137, 137, 137, 138, 138, 139, 139, 139, 139, 140, 140, 141, 141, 141, 141, 142, 142, 142, 142, 143, 143, 144, 144, 144, 144, 145, 145, 146, 146, 147, 147, 148, 148, 149, 149, 149, 149, 151, 151, 151, 151, 152, 152, 153, 153, 153, 153, 153, 153, 155, 155, 155, 155, 156, 156, 157, 157, 158, 158, 159, 159, 159, 159, 160, 160, 160, 160, 162, 162, 163, 163, 163, 163, 164, 164, 166, 166, 166, 166, 166])
CC_VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7])

STRUCT_VALUE_TO_BRIGHTNESS = np.array([0, 0, 0, 0, 0, 2, 2, 3, 3, 3, 5, 6, 10, 11, 15, 15, 19, 19, 23, 25, 31, 31, 35, 37, 42, 47, 47, 51, 57, 63, 63, 63, 69, 74, 79, 83, 87, 89, 95, 99, 105, 107, 111, 115, 120, 125, 128, 128, 128, 132, 132, 132, 132, 136, 136, 136, 136, 136, 136, 136, 140, 140, 140, 93, 95, 95, 98, 101, 101, 101, 106, 106, 108, 108, 108, 113, 115, 115, 117, 119, 120, 121, 124, 125, 127, 128, 128, 131, 132, 135, 136, 137, 137, 139, 142, 142, 144, 144, 147, 110, 111, 111, 113, 115, 115, 116, 118, 119, 121, 121, 123, 124, 124, 126, 127, 128, 128, 130, 130, 132, 133, 134, 136, 136, 136, 138, 140, 141, 141, 144, 144, 144, 110, 111, 112, 112, 113, 115, 115, 116, 118, 118, 119, 119, 120, 121, 122, 123, 124, 124, 125, 126, 127, 127, 128, 129, 130, 131, 131, 132, 133, 134, 134, 134, 136, 137, 137, 139, 139, 140, 117, 117, 119, 119, 119, 120, 121, 122, 122, 123, 123, 124, 124, 125, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 133, 134, 134, 135, 135, 136, 137, 113, 113, 113, 115, 115, 115, 115, 117, 118, 118, 118, 118, 118, 120, 120, 120, 121, 122, 123, 123, 123, 123, 124, 125, 125, 126, 127, 127, 127, 128, 128, 129, 129, 130, 131, 131, 132, 132, 133, 134, 134, 134, 135, 135, 135, 137, 137, 120, 121, 122, 122, 122, 123, 123, 124, 124, 125, 125, 126, 126, 127, 127, 127, 128, 128, 129, 130, 130, 130, 131, 132, 132, 132, 132, 134, 134, 134, 134, 135, 136, 136, 121, 121, 121, 122, 122, 123, 123, 123, 124, 124, 125, 125, 126, 126, 126, 127, 127, 127, 128, 128, 129, 129, 129, 130, 130, 131, 132, 133, 133, 133, 134, 134, 134, 134, 135, 136, 136, 136, 136, 119, 119, 119, 119, 120, 120, 121, 121, 121, 121, 122, 122, 122, 123, 123, 123, 123, 124, 124, 124, 124, 124, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 129, 129, 130, 131, 131, 131, 132, 132, 132, 133, 134, 134, 134, 135, 135, 136, 136, 137, 137, 137, 139, 139, 139, 139, 123, 123, 123, 124, 124, 124, 125, 125, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 134, 135, 135, 135, 135, 135, 136, 136, 136, 137, 137, 137, 139, 139, 139, 139, 144, 144, 144, 144, 146, 146, 146, 147, 149, 149, 152, 152, 152, 152, 152, 156, 158, 158, 159, 159, 160, 162, 162, 163, 163, 163, 169, 171, 181, 181, 183, 185, 185, 185, 187, 187, 189, 190, 191, 191, 191, 194, 196, 196, 198, 198, 198, 198, 201, 202, 204, 204, 205, 207, 210, 210, 210, 210, 212, 214, 216, 217, 217, 234, 236, 240, 240, 243, 243, 248, 248, 251, 253, 255, 255])
STRUCT_VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])

MAGENTA_TO_CC = (0, 0xC6, CC_VALUE_TO_BRIGHTNESS, CC_VALUE_TO_INDEX)
MAGENTA_TO_STRUCT = (1, 0x46, STRUCT_VALUE_TO_BRIGHTNESS, STRUCT_VALUE_TO_INDEX)
MAGENTA_TO_HOUSE_CC = (
    2, 0xC6,
    np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 5, 5, 7, 7, 7, 7, 9, 9, 11, 11, 12, 13, 14, 15, 15, 17, 17, 19, 19, 21, 21, 23, 24, 25, 26, 27, 29, 29, 31, 31, 31, 35, 35, 37, 37, 39, 39, 41, 41, 43, 44, 46, 47, 47, 49, 51, 51, 53, 54, 55, 57, 58, 59, 61, 63, 63, 63, 67, 67, 69, 69, 71, 73, 73, 75, 76, 78, 79, 81, 83, 83, 85, 85, 87, 89, 90, 91, 93, 95, 95, 97, 98, 99, 101, 103, 104, 105, 107, 108, 110, 111, 113, 114, 115, 117, 118, 119, 121, 123, 124, 126, 127, 128, 128, 130, 131, 132, 133, 134, 134, 136, 136, 136, 138, 138, 141, 117, 117, 118, 119, 119, 119, 122, 122, 123, 123, 124, 125, 125, 126, 127, 128, 128, 129, 130, 131, 131, 132, 132, 134, 134, 134, 136, 136, 137, 137, 138, 116, 117, 118, 118, 119, 119, 120, 121, 121, 122, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 134, 134, 134, 135, 135, 136, 136, 137, 119, 119, 120, 120, 121, 122, 122, 123, 123, 124, 124, 125, 126, 126, 126, 127, 127, 128, 128, 129, 130, 130, 130, 132, 132, 132, 132, 133, 134, 134, 135, 136, 136, 136, 137, 137, 120, 121, 121, 121, 122, 122, 123, 123, 123, 123, 125, 125, 125, 125, 126, 126, 127, 127, 127, 128, 128, 128, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 135, 135, 135, 135, 119, 119, 119, 120, 120, 120, 121, 121, 122, 122, 123, 123, 123, 123, 124, 124, 125, 125, 125, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 130, 131, 131, 132, 132, 133, 133, 133, 134, 134, 134, 135, 135, 136, 137, 137, 137, 119, 119, 120, 120, 121, 121, 121, 121, 122, 122, 122, 122, 122, 123, 124, 124, 124, 124, 125, 125, 125, 125, 126, 126, 127, 127, 127, 127, 127, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 134, 135, 135, 135, 136, 137, 137, 137, 137, 137, 139, 122, 122, 123, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 129, 130, 131, 131, 131, 131, 132, 132, 133, 133, 133, 134, 134, 135, 135, 135, 137, 137, 137, 137, 137, 138, 138, 139, 139, 141, 141, 141, 141, 141, 141, 141, 143, 144, 144, 144, 144, 145, 148, 149, 151, 152, 153, 153, 153, 155, 155, 156, 156, 158, 158, 159, 159, 159, 163, 163, 164, 164, 166, 166, 168, 168, 168, 236, 236, 236, 245, 245, 249, 250, 252, 253, 254, 254, 254, 254, 238, 238, 242, 245, 245, 248, 248, 254, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]),
    np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]),
)

THIS_FILE = grf.PythonFile(__file__)

ASE_IDX = {}
def aseidx(path, **kw):
    key = (path, tuple(kw.items()))
    ase = ASE_IDX.get(key)
    if ase is None:
        ase = ASE_IDX[key] = AseImageFile(path, **kw)
    return ase


def zoom_to_factor(zoom):
    return {
        grf.ZOOM_NORMAL: 1,
        grf.ZOOM_2X: 2,
        grf.ZOOM_4X: 4,
    }[zoom]


# Takes a list of sprites or AlternativeSprites and shifts their xofs and yofs by provided values (multiplied by zoom factor)
def move(sprites, *, xofs, yofs):
    for s in sprites:
        if isinstance(s, grf.AlternativeSprites):
            sl = s.sprites
        else:
            sl = (s,)
        for s in sl:
            z = zoom_to_factor(s.zoom)
            s.xofs += xofs * z
            s.yofs += yofs * z
    return sprites


def template(sprite_class):
    def decorator(tmpl_func):
        def wrapper(name, paths, zoom, *args):
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
                        p = aseidx(p)
                    def sprite_func(suffix, *args, **kw):
                        return sprite_class(p, *args, **kw, zoom=zoom, name=name.format(suffix=suffix))
                    return sprite_func

                res = list(map(make_sprite_func, it))
                if len(res) == 1:
                    return res[0]
                return res

            funcs = make_func_lists(paths, zoom)
            return tmpl_func(funcs, zoom_to_factor(zoom), *args)

        return wrapper
    return decorator


def house_grid(*, func, height, width=64, padding=1, z=2):
    zheight = height * z + z - 1
    zpadding = padding * z
    zwidth = width * z
    def sprite_func(name, grid_pos, bb=None, rel=None, **kw):
        assert bb is None or rel is None
        x, y = grid_pos
        fx = x * zwidth + zpadding * (x + 1)
        fy = y * zheight + zpadding * (y + 1)
        if rel is not None:
            zxofs = -rel[0] * z
            zyofs = -rel[1] * z + 1
        else:
            zxofs = -31 * z
            zyofs = (31 - height) * z # - z // 2
            if bb is not None:
                zxofs -= z * (bb[1] - bb[0]) * 2
                zyofs -= z * (bb[0] + bb[1])
        return func(name, fx, fy, zwidth, zheight, xofs=zxofs, yofs=zyofs, **kw)

    return sprite_func


old_sprites = defaultdict(dict)
new_sprites = defaultdict(lambda: defaultdict(dict))
old_sprites_collection = defaultdict(lambda: defaultdict(lambda: (10000, 0)))
new_sprites_collection = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: (10000, 0))))


dict_to_key = lambda d : tuple(sorted(d.items()))

def replace_old(collection, first_id, sprites, **kw):
    if isinstance(sprites, (grf.Resource, grf.ResourceAction)):
        sprites = [sprites]

    amount = len(sprites)
    assert first_id + amount < 4896
    key = dict_to_key(kw)
    first, amount = old_sprites_collection[key][collection]
    old_sprites_collection[key][collection] = (min(first, first_id), amount + len(sprites))
    for i, s in enumerate(sprites):
        old_sprites[key][first_id + i] = s


def replace_new(collection, set_type, offset, sprites, **kw):
    if isinstance(sprites, (grf.Resource, grf.ResourceAction)):
        sprites = [sprites]
    key = dict_to_key(kw)
    first, amount = new_sprites_collection[key][set_type][collection]
    new_sprites_collection[key][set_type][collection] = (min(first, offset), amount + len(sprites))
    for i, s in enumerate(sprites):
        new_sprites[key][set_type][offset + i] = s


class SpriteCollection:
    def __init__(self, name):
        self.name = name
        self.sprites = []

    def __getitem__(self, sl):
        if isinstance(sl, int):
            sl = slice(sl, sl + 1)
        res = SpriteCollection(self.name)
        for zoom, kw, sprites in self.sprites:
            res.sprites.append((zoom, kw, sprites[sl]))
        return res

    def add(self, files, template, zoom, *args, **kw):
        if not isinstance(files, tuple):
            files = (files,)
        files = tuple(aseidx(f) if isinstance(f, str) else f for f in files)
        z = zoom_to_factor(zoom)
        kwsuffix = ''
        if 'thin' in kw:
            kwsuffix = 'thin_' if kw['thin'] else 'thick_'
        sprites = template(f'{self.name}_{{suffix}}_{kwsuffix}{z}x', files, zoom, *args)
        assert all(s.zoom  == zoom or s == grf.EMPTY_SPRITE for s in sprites)
        self.sprites.append((zoom, kw, sprites))
        return self

    def add_sprites(self, sprites, **kw):
        zoom = sprites[0].zoom
        self.sprites.append((zoom, kw, sprites))
        return self

    def compose_on(self, dest, pattern=None):
        srckeys = set(tuple(p) for _, kw, _ in self.sprites for p in kw.items())
        dstkeys = set(tuple(p) for _, kw, _ in dest.sprites for p in kw.items())

        compose_keys = set()
        # print(self.name, dest.name)
        for srckeys in self.get_keys():
            for dstkeys in dest.get_keys():
                srckw = dict(srckeys)
                dstkw = dict(dstkeys)
                if any(k in dstkw and dstkw[k] != v for k, v in srckw.items()):
                    # have same key with different values -> incompatible
                    continue
                compose_keys.add(dict_to_key({**dstkw, **srckw}))
        #         print('    ', srckw, dstkw)
        # print()

        res = SpriteCollection(f'{dest.name}+{self.name}')

        def patternzip(dstl, srcl):
            if pattern is None:
                l = zip(dstl, srcl)
            else:
                l = ((None if i is None else dstl[i], srcl[j]) for i, j in pattern)
            return [s if d is None else CompositeSprite((d, s)) for d, s in l]

        for keys in compose_keys:
            srcl = self.get_sprites(keys)
            dstl = dest.get_sprites(keys)
            # print(keys)
            # for s in self.sprites:
            #     print('SRC', s)
            # for s in dest.sprites:
            #     print('DST', s)
            assert srcl is not None and dstl is not None
            src1x, src2x = srcl
            dst1x, dst2x = dstl
            if src1x is not None and dst1x is not None:
                res.sprites.append((ZOOM_NORMAL, dict(keys), patternzip(dst1x, src1x)))
            if src2x is not None and dst2x is not None:
                res.sprites.append((ZOOM_2X, dict(keys), patternzip(dst2x, src2x)))
        return res

    def get_keys(self):
        keys1x = set(dict_to_key(kw) for zoom, kw, _ in self.sprites if zoom == ZOOM_NORMAL)
        keys2x = set(dict_to_key(kw) for zoom, kw, _ in self.sprites if zoom == ZOOM_2X)
        if len(keys2x) > len(keys1x):
            return keys2x
        return keys1x

    def _find_sprites(self, keys, exact):
        kw = dict(keys)
        d = {}
        for zoom, params, sprites in self.sprites:
            if any(k not in kw for k in params):
                continue
            if any(k in params and params[k] != v for k, v in kw.items()):
                continue
            matches = sum(k in params for k in kw)
            if zoom not in d or d[zoom][0] < matches:
                d[zoom] = (matches, sprites)

        # print(self.name, ', '.join(map(str, d.keys())), kw)
        # for zoom in (ZOOM_NORMAL, ZOOM_2X):
        #     if zoom in d:
        #         print('  ', zoom_to_factor(zoom), ', '.join(x.name for x in d[zoom][1]))
        # print()

        if exact and all(v[0] != len(kw) for v in d.values()):
            return None, None

        return d.get(ZOOM_NORMAL, (0, None))[1], d.get(ZOOM_2X, (0, None))[1]

    def get_sprites(self, keys):
        return self._find_sprites(keys, False)

    def get_exact_sprites(self, keys):
        x1, x2 = self._find_sprites(keys, True)
        if x2 is None and x1 is None:
            return None
        if x2 is None:
            return x1
        if x1 is None:
            return x2
        res = []
        for x1, x2 in zip(x1, x2):
            res.append(grf.AlternativeSprites(x1, x2))
        return res

    def replace_old(self, first_id, **kw):
        for k in self.get_keys():
            sprites = self.get_exact_sprites(k)
            replace_old(self, first_id, sprites, **dict(k), **kw)
        return self

    def replace_new(self, set_type, offset, **kw):
        for k in self.get_keys():
            sprites = self.get_exact_sprites(k)
            replace_new(self, set_type, offset, sprites, **dict(k), **kw)
        return self


class CCReplacingFileSprite(grf.FileSprite):
    def __init__(self, file, *args, **kw):
        super().__init__(file, *args, **kw)

    def get_data_layers(self, context, *args, **kw):
        w, h, img, bpp = self._do_get_image(context)

        timer = context.start_timer()

        if bpp != grf.BPP_32 and bpp != grf.BPP_24:
            raise RuntimeError('Only 32-bit RGB sprites are currently supported for CC replacement')

        self.bpp = bpp
        npimg = np.asarray(img).copy()

        magenta_mask = (
            (npimg[:, :, 0] == npimg[:, :, 2]) &
            (
                ((npimg[:, :, 0] == 255) & (npimg[:, :, 1] != 255)) |
                ((npimg[:, :, 1] == 0) & (npimg[:, :, 0] != 0))
            )
        )

        value = npimg[magenta_mask][:, 0].astype(np.uint16) + npimg[magenta_mask][:, 1]
        npimg[magenta_mask, 0] = CC_VALUE_TO_BRIGHTNESS[value]
        npimg[magenta_mask, 1] = 0
        npimg[magenta_mask, 2] = 0

        mask = np.zeros((h, w), dtype=np.uint8)
        mask[magenta_mask] = CC_VALUE_TO_INDEX[value] + 0xC6

        if bpp == grf.BPP_32:
            rgb, alpha = npimg[:, :, :3], npimg[:, :, 3]
        else:
            rgb, alpha = npimg, None

        timer.count_custom('Magenta and mask processing')

        return w, h, rgb, alpha, mask


    def get_resource_files(self):
        return super().get_resource_files() + (THIS_FILE,)


class SpriteWrapper(grf.Sprite):
    def __init__(self, sprites, *, name=None):
        self.sprites = sprites
        try:
            f = next(iter(self._iter_sprites()))
        except StopIteration:
            raise ValueError('SpriteWrapper sprites to wrap')
        super().__init__(w=f.w, h=f.h, xofs=f.xofs, yofs=f.yofs, zoom=f.zoom, bpp=f.bpp, crop=f.crop)

    def _iter_sprites(self):
        if isinstance(self.sprites, dict):
            i = self.sprites.values()
        else:
            i = self.sprites
        for s in i:
            if s is not None:
                yield s

    def get_image_files(self):
        return ()

    def get_resource_files(self):
        # TODO add wrapped class __file__, possibly traversing mro (do that globally?)
        res = super().get_resource_files() + (THIS_FILE,)
        for s in self._iter_sprites():
            res += s.get_resource_files()
        return res

    def get_fingerprint(self):
        res = {'class': self.__class__.__name__}
        if isinstance(self.sprites, dict):
            sf = {}
            for k, s in self.sprites.items():
                if s is None:
                    sf[k] = None
                else:
                    f = s.get_fingerprint()
                    if f is None:
                        return None
                    sf[k] = f
        else:
            sf = []
            for s in self.sprites:
                if s is None:
                    sf.append(None)
                    continue
                f = s.get_fingerprint()
                if f is None:
                    return None
                sf.append(f)
        res['sprites'] = sf
        return res

    def prepare_files(self):
        for s in self._iter_sprites():
            s.prepare_files()


class MagentaRecolour(SpriteWrapper):
    def __init__(self, sprite, magenta_map):
        self.magenta_map = magenta_map
        super().__init__((sprite, ))

    def get_data_layers(self, context):
        _fingerprint, first, vtb, vti = self.magenta_map
        w, h, rgb, alpha, mask = self.sprites[0].get_data_layers(context)

        timer = context.start_timer()

        if mask is not None:
            raise RuntimeError('Only 32-bit RGB sprites are currently supported for CC replacement')

        rgb = grf.np_make_writable(rgb)
        magenta_mask = (
            (rgb[:, :, 0] == rgb[:, :, 2]) &
            (
                ((rgb[:, :, 0] == 255) & (rgb[:, :, 1] != 255)) |
                ((rgb[:, :, 1] == 0) & (rgb[:, :, 0] != 0))
            )
        )

        value = rgb[magenta_mask][:, 0].astype(np.uint16) + rgb[magenta_mask][:, 1]
        rgb[magenta_mask, 0] = vtb[value]
        rgb[magenta_mask, 1] = 0
        rgb[magenta_mask, 2] = 0

        mask = np.zeros((h, w), dtype=np.uint8)
        mask[magenta_mask] = vti[value] + first

        timer.count_custom('Magenta and mask processing')

        return w, h, rgb, alpha, mask

    def get_fingerprint(self):
        return grf.combine_fingerprint(
            super().get_fingerprint(),
            map=self.magenta_map[0],
        )


class MagentaToCC(MagentaRecolour):
    def __init__(self, sprite):
        super().__init__(sprite, MAGENTA_TO_CC)

class MagentaToHCC(MagentaRecolour):
    def __init__(self, sprite):
        super().__init__(sprite, MAGENTA_TO_HOUSE_CC)

class MagentaToStruct(MagentaRecolour):
    def __init__(self, sprite):
        super().__init__(sprite, MAGENTA_TO_STRUCT)


class MagentaToLight(grf.Sprite):
    def __init__(self, sprite, order):
        self.sprite = sprite
        self.order = order
        super().__init__(w=sprite.w, h=sprite.h, xofs=sprite.xofs, yofs=sprite.yofs, zoom=sprite.zoom, bpp=sprite.bpp, name=self.sprite.name)

    def prepare_files(self):
        self.sprite.prepare_files()
        self.order.prepare_files()

    def get_data_layers(self, context):
        w, h, npimg, npalpha, npmask = self.sprite.get_data_layers(context)

        assert npmask is None
        ow, oh, ni, na, nm = self.order.get_data_layers(context)
        assert nm is None
        assert w == ow and h == oh

        timer = context.start_timer()

        magenta_mask = (
            (npimg[:, :, 0] == npimg[:, :, 2]) &
            (
                ((npimg[:, :, 0] == 255) & (npimg[:, :, 1] != 255)) |
                ((npimg[:, :, 1] == 0) & (npimg[:, :, 0] != 0))
            )
        )

        order_mask = (na > 0)
        colours = list(set(map(tuple, ni[order_mask])))
        if len(colours) != 4:
            raise ValueError(f'Expected 4 colors in order mask, found {len(colours)} in {self.order.name}')
        colours.sort(key=lambda x: int(x[0]) + x[1] + x[2], reverse=True)

        order_mask &= magenta_mask
        order = ni[order_mask]
        if np.any(magenta_mask != order_mask):
            raise ValueError(f'Not all magenta pixels of sprite {self.sprite.name} have a defined order in {self.order.name}')

        npmask = np.zeros((h, w), dtype=np.uint8)
        ordered = np.zeros(order.shape[0], dtype=np.uint8)
        for i, c in enumerate(colours):
            ordered[(order == c).all(axis=1)] = 0xf1 + i
        npmask[order_mask] = ordered

        timer.count_custom('Magenta and mask processing')

        return w, h, npimg, npalpha, npmask

    def get_image_files(self):
        return ()

    def get_resource_files(self):
        return super().get_resource_files() + (THIS_FILE,) + self.sprite.get_resource_files() + self.order.get_resource_files()

    def get_fingerprint(self):
        return {
            'class': self.__class__.__name__,
            'sprite': self.sprite.get_fingerprint(),
            'order': self.order.get_fingerprint(),
        }


class MagentaAndMask(grf.Sprite):
    def __init__(self, sprite, mask):
        self.sprite = sprite
        super().__init__(w=sprite.w, h=sprite.h, xofs=sprite.xofs, yofs=sprite.yofs, zoom=sprite.zoom, bpp=sprite.bpp, name=self.sprite.name)
        self.mask = mask  # TODO sprite mask has a special meaning

    def prepare_files(self):
        self.sprite.prepare_files()
        self.mask.prepare_files()

    def get_data_layers(self, context):
        w, h, npimg, npalpha, npmask = self.sprite.get_data_layers(context)
        assert npmask is None
        ow, oh, ni, na, nm = self.mask.get_data_layers(context)
        assert nm is None
        assert w == ow and h == oh

        timer = context.start_timer()

        magenta_mask = (
            (npimg[:, :, 0] == npimg[:, :, 2]) &
            (
                ((npimg[:, :, 0] == 255) & (npimg[:, :, 1] != 255)) |
                ((npimg[:, :, 1] == 0) & (npimg[:, :, 0] != 0))
            )
        )

        mask = (na > 0) & magenta_mask
        if np.any(magenta_mask != mask):
            raise ValueError(f'Not all magenta pixels of sprite {self.sprite.name} have a defined mask in {self.mask.name}')

        masked = ni[mask]
        colours = set(map(tuple, masked))
        npmask = np.zeros((h, w), dtype=np.uint8)
        new_masked = np.zeros(masked.shape[0], dtype=np.uint8)

        for c in colours:
            m = grf.PALETTE_IDX.get(c)
            if m is None:
                raise ValueError(f'Color {c} is not in the palette in sprite {self.mask.name}')
            new_masked[(masked == c).all(axis=1)] = m

        npmask[mask] = new_masked

        timer.count_custom('Magenta and mask processing')

        return w, h, npimg, npalpha, npmask


    def get_image_files(self):
        return ()


    def get_resource_files(self):
        return super().get_resource_files() + (THIS_FILE,) + self.sprite.get_resource_files() + self.mask.get_resource_files()


    def get_fingerprint(self):
        return {
            'class': self.__class__.__name__,
            'sprite': self.sprite.get_fingerprint(),
            'mask': self.mask.get_fingerprint(),
        }


class CutGround(grf.Sprite):
    def __init__(self, sprite, position, name=None):
        assert sprite.zoom == ZOOM_2X
        z = 2
        self.sprite = sprite
        self.position = position
        super().__init__(w=64 * z, h=32 * z - 1, xofs=-31 * z, yofs=0, zoom=sprite.zoom, bpp=sprite.bpp, name=name)

    def prepare_files(self):
        self.sprite.prepare_files()

    def get_data_layers(self, context):
        gx, gy = self.position
        x = -self.sprite.xofs - 62 + (gx - gy) * 64
        y = -self.sprite.yofs - (gx + gy) * 32

        w, h, rgb, alpha, mask = self.sprite.get_data_layers(context)
        ground_mask = np.full((self.h, self.w), True)
        for i in range(self.h):
            n = i if i <= 31 else 62 - i
            n = (n + 1) * 2
            ground_mask[i, 64 - n: 64 + n] = False

        if x < 0 or y < 0 or y + self.h > h or x + self.w > w:
            raise ValueError(f'Ground sprite region({x}..{x + self.w}, {y}..{y + self.h}) is outside sprite boundaries (0..{w}, 0..{h})')

        if rgb is not None:
            rgb = rgb[y:y + self.h, x:x + self.w].copy()
            rgb[ground_mask, :] = 0
        if alpha is not None:
            alpha = alpha[y:y + self.h, x:x + self.w].copy()
            alpha[ground_mask] = 0
        if mask is not None:
            mask = mask[y:y + self.h, x:x + self.w].copy()
            mask[ground_mask] = 0

        return self.w, self.h, rgb, alpha, mask


    def get_image_files(self):
        return ()

    def get_resource_files(self):
        return super().get_resource_files() + (THIS_FILE,) + self.sprite.get_resource_files()

    def get_fingerprint(self):
        return {
            'class': self.__class__.__name__,
            'position': self.position,
            'xofs': self.xofs,
            'yofs': self.yofs,
            'sprite': self.sprite.get_fingerprint(),
        }


class AseImageFile(grf.ImageFile):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._images = None
        self._kw_requested = set()

    @staticmethod
    def _make_kw_key(frame=1, layers=None, ignore_layers=None):
        if isinstance(layers, str):
            layers = (layers,)
        if isinstance(ignore_layers, str):
            ignore_layers = (ignore_layers,)
        return (frame, tuple(layers or ()), tuple(ignore_layers or ()))

    def prepare(self, **kw):
        self._kw_requested.add(self._make_kw_key(**kw))

    def _load_frame(self, fname):
        img = Image.open(fname)
        if img.mode == 'P':
            return (img, grf.BPP_8)
        elif img.mode == 'RGB':
            return (img, grf.BPP_24)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        return (img, grf.BPP_32)

    def load(self):
        if self._images is not None:
            return

        aseprite_executible = os.environ.get('ASEPRITE_EXECUTABLE', 'aseprite')
        self._images = {}
        for kw in self._kw_requested:
            frame, layers, ignore_layers = kw
            with tempfile.NamedTemporaryFile(suffix='.png') as f:
                args = [aseprite_executible, '-b', str(self.path), '--color-mode', 'rgb']
                for l in layers:
                    args.extend(('--layer', l))
                for l in ignore_layers:
                    args.extend(('--ignore-layer', l))
                args.extend(('--frame-range', f'{frame - 1},{frame - 1}'))
                res = subprocess.run(args + ['--save-as', f.name])
                if res.returncode != 0:
                    raise RuntimeError(f'Aseprite returned non-zero code {res.returncode}')
                self._images[kw] = self._load_frame(f.name)

    def get_image(self, **kw):
        self.load()
        key = self._make_kw_key(**kw)
        return self._images[key]


class CompositeSprite(grf.Sprite):
    def __init__(self, sprites, **kw):
        if len(sprites) == 0:
            raise ValueError('CompositeSprite requires a non-empty list of sprites to compose')
        if len(set(s.zoom for s in sprites)) > 1:
            sprite_list = ', '.join(f'{s.name}<zoom={s.zoom}>' for s in sprites)
            raise ValueError(f'CompositeSprite requires a list of sprites of same zoom level: {sprite_list}')
        self.sprites = sprites
        super().__init__(sprites[0].w, sprites[0].h, xofs=sprites[0].xofs, yofs=sprites[0].yofs, zoom=sprites[0].zoom, **kw)

    def prepare_files(self):
        for s in self.sprites:
            s.prepare_files()

    def get_data_layers(self, context):
        npimg = None
        npalpha = None
        npmask = None
        nw, nh = self.w, self.h
        for s in self.sprites:
            w, h, ni, na, nm = s.get_data_layers(context)
            timer = context.start_timer()

            if nw is None:
                nw = w
            if nh is None:
                nh = h
            if nw != w or nh != h:
                raise RuntimeError(f'CompositeSprite layers have different size: {self.sprites[0].name}({nw}, {nh}) vs {s.name}({w}, {h})')

            if ni is not None:
                if npimg is None or na is None:
                    npimg = ni.copy()
                    if na is not None:
                        npalpha = na.copy()
                    else:
                        npalpha = None
                else:
                    full_mask = (na[:, :] == 255)
                    partial_mask = (na[:, :] > 0) & ~full_mask

                    npimg[full_mask] = ni[full_mask]
                    if npalpha is not None:
                        npalpha[full_mask] = 255

                    if npalpha is None:
                        npalpha_norm_mask = np.full(partial_mask.sum(), 1.0)
                    else:
                        npalpha_norm_mask = npalpha[partial_mask] / 255.0

                    na_norm_mask = na[partial_mask] / 255.0
                    resa = npalpha_norm_mask + na_norm_mask * (1 - npalpha_norm_mask)

                    npimg[partial_mask] = (
                        npimg[partial_mask] * npalpha_norm_mask[..., np.newaxis] +
                        ni[partial_mask] * (na_norm_mask * (1.0 - npalpha_norm_mask))[..., np.newaxis]
                    ) / resa[..., np.newaxis]
                    if npalpha is not None:
                        npalpha[partial_mask] = (resa * 255).astype(np.uint8)

            if nm is not None:
                if npmask is None:
                    npmask = nm.copy()
                else:
                    mask = (nm[:, :] != 0)
                    npmask[mask] = nm[mask]

            timer.count_custom('Layering')

        return w, h, npimg, npalpha, npmask

    def get_resource_files(self):
        res = [THIS_FILE]
        for s in self.sprites:
            res.extend(s.get_resource_files())
        return tuple(res)

    def get_fingerprint(self):
        return {
            'class': self.__class__.__name__,
            'sprites': [s.get_fingerprint() for s in self.sprites]
        }


def adjust_brightness(c, brightness):
    if brightness == 128:
        return c

    r, g, b = c
    combined = (r << 32) | (g << 16) | b
    combined *= brightness

    r = (combined >> 39) & 0x1ff
    g = (combined >> 23) & 0x1ff
    b = (combined >> 7) & 0x1ff

    if (combined & 0x800080008000) == 0:
        return (r, g, b)

    ob = 0
    # Sum overbright
    if r > 255: ob += r - 255
    if g > 255: ob += g - 255
    if b > 255: ob += b - 255

    # Reduce overbright strength
    ob //= 2
    return (
        255 if r >= 255 else min(r + ob * (255 - r) // 256, 255),
        255 if g >= 255 else min(g + ob * (255 - g) // 256, 255),
        255 if b >= 255 else min(b + ob * (255 - b) // 256, 255),
    )


def debug_recolour(sprites, recolours, horizontal=False):
    PADDING = 10

    context = grf.WriteContext()
    slayers = []
    for i, s in enumerate(sprites):
        slayers.append(s.get_data_layers(context))

    pos = []
    if horizontal:
        maxw = max(x[0] for x in slayers)
        x = PADDING
        for i in range(len(recolours)):
            y = PADDING
            row = []
            for s in slayers:
                row.append(((x, y)))
                y += s[1] + PADDING
            pos.append(row)
            x += maxw + PADDING
    else:
        # s = (sumh + (len(slayers) + 1) * PADDING, maxw + 2 * PADDING)
        y = PADDING
        maxh = max(x[1] for x in slayers)
        for i in range(len(recolours)):
            x = PADDING
            row = []
            for s in slayers:
                row.append(((x, y)))
                x += s[0] + PADDING
            pos.append(row)
            y += maxh + PADDING

    npres = np.zeros((y, x, 4), dtype=np.uint8)
    for jj, s, (w, h, rgb, alpha, mask) in zip(range(len(sprites)), sprites, slayers):
        if mask is None:
            raise ValueError(f'Sprite {s.name} has no mask!')

        for ii, recolour in enumerate(recolours):
            x, y = pos[ii][jj]
            for i in range(h):
                for j in range(w):
                    mrgb = recolour.get(mask[i, j])
                    if mrgb is None:
                        npres[y + i, x + j, :3] = rgb[i, j, :]
                    else:
                        b = max(rgb[i, j])
                        npres[y + i, x + j, :3] = adjust_brightness(mrgb, b)
                    if alpha is not None:
                        npres[y + i, x + j, 3] = alpha[i, j]
                    else:
                        npres[y + i, x + j, 3] = 255

    im = Image.fromarray(npres, mode='RGBA')
    im.show()


def debug_cc_recolour(sprites, horizontal=False):
    recolours = []
    for cl in grf.CC_COLOURS:
        recolours.append({
            0xC6 + i : grf.PALETTE[m]
            for i, m in enumerate(cl)
        })
    debug_recolour(sprites, recolours, horizontal=horizontal)


def debug_light_cycle(sprites, horizontal=False):
    ON = (240, 208, 0)
    OFF = (0, 0, 0)
    recolours = [
        {0xf1: OFF, 0xf2: OFF, 0xf3: OFF, 0xf4: ON},
        {0xf1: OFF, 0xf2: OFF, 0xf3: ON, 0xf4: OFF},
        {0xf1: OFF, 0xf2: ON, 0xf3: OFF, 0xf4: OFF},
        {0xf1: ON, 0xf2: OFF, 0xf3: OFF, 0xf4: OFF},
    ]
    debug_recolour(sprites, recolours, horizontal=horizontal)
