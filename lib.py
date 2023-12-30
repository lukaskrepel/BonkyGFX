import os
import pathlib
import subprocess
import time
import tempfile

import numpy as np
from PIL import Image

import grf


# VALUE_TO_BRIGHTNESS = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 91, 91, 92, 93, 94, 95, 95, 96, 97, 98, 99, 100, 100, 101, 102, 103, 104, 105, 105, 106, 107, 108, 109, 109, 110, 111, 112, 113, 114, 114, 115, 116, 117, 118, 118, 119, 120, 121, 122, 123, 123, 124, 125, 126, 127, 127, 128, 129, 130, 131, 107, 108, 109, 109, 110, 111, 111, 112, 113, 113, 114, 115, 115, 116, 117, 117, 118, 119, 119, 120, 121, 121, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 129, 130, 130, 131, 132, 132, 133, 134, 134, 135, 136, 136, 137, 138, 138, 139, 140, 140, 120, 120, 121, 121, 122, 122, 123, 124, 124, 125, 125, 126, 126, 127, 127, 128, 129, 129, 130, 130, 131, 131, 132, 133, 133, 134, 134, 135, 135, 136, 137, 137, 138, 138, 139, 139, 140, 141, 141, 142, 142, 143, 143, 144, 145, 146, 146, 147, 147, 148, 127, 128, 128, 128, 128, 130, 130, 131, 131, 132, 132, 133, 133, 134, 134, 135, 135, 136, 136, 137, 137, 138, 138, 139, 139, 140, 140, 141, 141, 142, 143, 143, 144, 144, 144, 145, 145, 146, 146, 147, 147, 148, 148, 149, 149, 150, 150, 151, 151, 152, 130, 131, 131, 132, 132, 133, 133, 134, 134, 135, 135, 136, 136, 137, 137, 138, 138, 139, 140, 140, 141, 141, 142, 142, 143, 143, 144, 144, 145, 145, 146, 146, 147, 147, 148, 148, 149, 150, 150, 151, 151, 152, 152, 153, 153, 154, 155, 155, 156, 156, 130, 130, 131, 131, 132, 132, 132, 133, 134, 134, 135, 135, 136, 136, 137, 137, 138, 139, 139, 140, 140, 141, 141, 142, 142, 143, 144, 144, 145, 145, 146, 146, 147, 147, 148, 149, 149, 150, 150, 151, 151, 152, 152, 153, 154, 154, 155, 156, 156, 157, 131, 132, 132, 133, 133, 134, 134, 135, 135, 136, 136, 137, 138, 138, 139, 139, 140, 140, 141, 141, 142, 143, 143, 144, 144, 145, 145, 146, 147, 147, 148, 149, 149, 150, 151, 151, 152, 152, 153, 154, 154, 155, 156, 156, 157, 157, 158, 159, 160, 160, 161, 162, 162, 163, 164, 165, 166, 166, 167, 168, 168, 169, 170, 171, 172, 173, 174, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 191, 192, 193, 194, 195, 197, 198, 199, 201, 203, 204, 206, 208, 210, 211, 214, 216, 218, 218])
# VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7])
# VALUE_TO_BRIGHTNESS = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 55, 57, 58, 59, 59, 61, 61, 63, 64, 64, 65, 67, 68, 69, 69, 70, 72, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 96, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 125, 125, 126, 127, 128, 128, 130, 131, 132, 133, 134, 134, 136, 136, 136, 138, 138, 141, 117, 117, 119, 119, 119, 119, 122, 122, 123, 123, 124, 125, 125, 127, 127, 128, 128, 129, 130, 131, 131, 132, 133, 134, 134, 134, 136, 136, 137, 138, 138, 140, 117, 118, 118, 119, 119, 120, 121, 121, 122, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 134, 134, 134, 135, 136, 136, 136, 137, 119, 119, 120, 120, 121, 122, 122, 123, 123, 124, 124, 125, 126, 126, 126, 127, 127, 128, 128, 129, 130, 130, 130, 131, 132, 132, 132, 133, 134, 134, 134, 136, 136, 136, 136, 137, 138, 121, 121, 121, 122, 122, 123, 123, 123, 123, 125, 125, 125, 125, 126, 126, 127, 127, 127, 128, 128, 128, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 133, 134, 135, 135, 135, 135, 136, 136, 137, 138, 120, 120, 120, 121, 122, 122, 123, 123, 123, 123, 124, 124, 125, 125, 125, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 130, 130, 131, 131, 132, 132, 132, 133, 134, 134, 134, 134, 135, 135, 136, 136, 137, 138, 138, 138, 138, 139, 139, 121, 121, 121, 122, 122, 122, 122, 123, 123, 124, 124, 124, 124, 125, 125, 125, 126, 126, 126, 127, 127, 127, 127, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 134, 135, 135, 135, 136, 137, 137, 137, 137, 137, 139, 139, 122, 123, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 133, 133, 134, 135, 135, 135, 136, 137, 137, 137, 137, 138, 138, 139, 139, 141, 141, 141, 141, 141, 141, 141, 142, 143, 144, 144, 144, 145, 145, 149, 151, 152, 153, 153, 153, 155, 155, 155, 156, 158, 158, 159, 159, 159, 163, 163, 164, 164, 164, 166, 168, 168, 168, 168, 236, 236, 236, 245, 245, 249, 250, 252, 253, 254, 254, 215, 219, 238, 238, 242, 245, 248, 248, 248, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
# VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7])
VALUE_TO_BRIGHTNESS = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 55, 57, 58, 59, 59, 61, 61, 63, 64, 64, 65, 67, 68, 69, 69, 70, 72, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 96, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 125, 125, 126, 127, 128, 128, 130, 131, 132, 133, 134, 134, 136, 136, 136, 138, 138, 141, 117, 117, 119, 119, 119, 119, 122, 122, 123, 123, 124, 125, 125, 127, 127, 128, 128, 129, 130, 131, 131, 132, 133, 134, 134, 134, 136, 136, 137, 138, 138, 140, 117, 118, 118, 119, 119, 120, 121, 121, 122, 122, 123, 123, 124, 125, 125, 126, 127, 127, 128, 128, 129, 130, 130, 131, 131, 132, 132, 134, 134, 134, 135, 136, 136, 136, 137, 119, 119, 120, 120, 121, 122, 122, 123, 123, 124, 124, 125, 126, 126, 126, 127, 127, 128, 128, 129, 130, 130, 130, 131, 132, 132, 132, 133, 134, 134, 134, 136, 136, 136, 136, 137, 138, 121, 121, 121, 122, 122, 123, 123, 123, 123, 125, 125, 125, 125, 126, 126, 127, 127, 127, 128, 128, 128, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 133, 134, 135, 135, 135, 135, 136, 136, 137, 138, 120, 120, 120, 121, 122, 122, 123, 123, 123, 123, 124, 124, 125, 125, 125, 126, 126, 127, 127, 127, 127, 128, 128, 128, 129, 129, 130, 130, 131, 131, 132, 132, 132, 133, 134, 134, 134, 134, 135, 135, 136, 136, 137, 138, 138, 138, 138, 139, 139, 121, 121, 121, 122, 122, 122, 122, 123, 123, 124, 124, 124, 124, 125, 125, 125, 126, 126, 126, 127, 127, 127, 127, 128, 128, 129, 129, 129, 130, 130, 131, 131, 131, 132, 132, 133, 133, 134, 134, 134, 135, 135, 135, 136, 137, 137, 137, 137, 137, 139, 139, 122, 123, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 126, 127, 127, 127, 127, 128, 128, 129, 129, 130, 130, 130, 130, 131, 131, 132, 132, 132, 132, 133, 133, 133, 133, 134, 134, 135, 135, 135, 135, 136, 136, 137, 137, 137, 137, 138, 138, 139, 139, 139, 139, 140, 140, 141, 141, 141, 141, 142, 142, 142, 142, 143, 143, 144, 144, 144, 144, 145, 145, 146, 146, 147, 147, 148, 148, 149, 149, 149, 149, 151, 151, 151, 151, 152, 152, 153, 153, 153, 153, 153, 153, 155, 155, 155, 155, 156, 156, 157, 157, 158, 158, 159, 159, 159, 159, 160, 160, 160, 160, 162, 162, 163, 163, 163, 163, 164, 164, 166, 166, 166, 166, 166])
VALUE_TO_INDEX = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7])

THIS_FILE = grf.PythonFile(__file__)


ASE_IDX = {}
def aseidx(path, layer=None, ignore_layer=None):
    key = (path, layer, ignore_layer)
    ase = ASE_IDX.get(key)
    if ase is None:
        ase = ASE_IDX[key] = AseImageFile(path, layer=layer, ignore_layer=ignore_layer)
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
                        p = aseidx(p)
                    def sprite_func(suffix, *args, **kw):
                        return sprite_class(p, *args, **kw, zoom=zoom, name=name + f'_{suffix}_{z}x')
                    return sprite_func

                res = list(map(make_sprite_func, it))
                if len(res) == 1:
                    return res[0]
                return res

            func1x = make_func_lists(path1x, grf.ZOOM_NORMAL)
            func2x = make_func_lists(path2x, grf.ZOOM_2X)
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


class CCReplacingFileSprite(grf.FileSprite):
    def __init__(self, file, *args, **kw):
        super().__init__(file, *args, **kw, mask=None)

    def get_data_layers(self, encoder=None, *args, **kw):
        w, h, img, bpp = self._do_get_image(encoder)

        t0 = time.time()

        if bpp != grf.BPP_32 and bpp != grf.BPP_24:
            raise RuntimeError('Only 32-bit RGB sprites are currently supported for CC replacement')

        self.bpp = bpp
        npimg = np.asarray(img).copy()

        crop_x, crop_y, w, h, npimg, npalpha = self._do_crop(w, h, npimg, None)

        magenta_mask = (
            (npimg[:, :, 0] == npimg[:, :, 2]) &
            (
                ((npimg[:, :, 0] == 255) & (npimg[:, :, 1] != 255)) |
                ((npimg[:, :, 1] == 0) & (npimg[:, :, 0] != 0))
            )
        )

        value = npimg[magenta_mask][:, 0].astype(np.uint16) + npimg[magenta_mask][:, 1]
        npimg[magenta_mask, 0] = VALUE_TO_BRIGHTNESS[value]
        npimg[magenta_mask, 1] = 0
        npimg[magenta_mask, 2] = 0

        npmask = np.zeros((h, w), dtype=np.uint8)
        npmask[magenta_mask] = VALUE_TO_INDEX[value] + 0xC6

        if encoder is not None:
            encoder.count_composing(time.time() - t0)

        return w, h, self.xofs + crop_x, self.yofs + crop_y, npimg, npalpha, npmask


    def get_resource_files(self):
        return super().get_resource_files() + (THIS_FILE,)


class MagentaToLight(grf.Sprite):
    def __init__(self, sprite, order):
        self.sprite = sprite
        self.order = order
        super().__init__(w=sprite.w, h=sprite.h, xofs=sprite.xofs, yofs=sprite.yofs, zoom=sprite.zoom, bpp=sprite.bpp, name=self.sprite.name)

    def get_data_layers(self, encoder=None, *args, **kw):
        w, h, xofs, yofs, npimg, npalpha, npmask = self.sprite.get_data_layers(encoder, crop=False)
        assert npmask is None
        ow, oh, _, _, ni, na, nm = self.order.get_data_layers(encoder, crop=False)
        assert na is None and nm is None
        assert w == ow and h == oh

        crop_x, crop_y, w, h, npimg, npalpha = self._do_crop(w, h, npimg, npalpha)
        magenta_mask = (
            (npimg[:, :, 0] == npimg[:, :, 2]) &
            (
                ((npimg[:, :, 0] == 255) & (npimg[:, :, 1] != 255)) |
                ((npimg[:, :, 1] == 0) & (npimg[:, :, 0] != 0))
            )
        )

        if na is None:
            assert ni.shape[2] == 4
            na = ni[:, :, 3]
            ni = ni[:, :, :3]

        order_mask = (na > 0)
        colours = list(set(map(tuple, ni[order_mask])))
        if len(colours) != 4:
            raise ValueError(f'Expected 4 colors in order mask, found {len(colours)} in {self.order.name}')
        colours.sort(key=lambda x: int(x[0]) + x[1] + x[2], reverse=True)

        order_mask = order_mask[crop_y:crop_y + h, crop_x:crop_x + w] & magenta_mask
        order = ni[crop_y:crop_y + h, crop_x:crop_x + w][order_mask]
        if np.any(magenta_mask != order_mask):
            raise ValueError(f'Not all magenta pixels of sprite {self.sprite.name} have a defined order in {self.order.name}')

        npmask = np.zeros((h, w), dtype=np.uint8)
        ordered = np.zeros(order.shape[0], dtype=np.uint8)
        for i, c in enumerate(colours):
            ordered[(order == c).all(axis=1)] = 0xf1 + i
        npmask[order_mask] = ordered
        return w, h, xofs + crop_x, yofs + crop_y, npimg, npalpha, npmask


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

    def get_data_layers(self, encoder=None, crop=None):
        w, h, xofs, yofs, npimg, npalpha, npmask = self.sprite.get_data_layers(encoder, crop=False)
        assert npmask is None
        ow, oh, _, _, ni, na, nm = self.mask.get_data_layers(encoder, crop=False)
        assert na is None and nm is None
        assert w == ow and h == oh

        crop_x, crop_y, w, h, npimg, npalpha = self._do_crop(w, h, npimg, npalpha, crop=crop)
        magenta_mask = (
            (npimg[:, :, 0] == npimg[:, :, 2]) &
            (
                ((npimg[:, :, 0] == 255) & (npimg[:, :, 1] != 255)) |
                ((npimg[:, :, 1] == 0) & (npimg[:, :, 0] != 0))
            )
        )

        if na is None:
            assert ni.shape[2] == 4
            na = ni[crop_y:crop_y + h, crop_x:crop_x + w, 3]
            ni = ni[crop_y:crop_y + h, crop_x:crop_x + w, :3]
        else:
            na = na[crop_y:crop_y + h, crop_x:crop_x + w]
            ni = ni[crop_y:crop_y + h, crop_x:crop_x + w, :]

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
        return w, h, xofs + crop_x, yofs + crop_y, npimg, npalpha, npmask


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


class AseImageFile(grf.ImageFile):
    def __init__(self, *args, layer=None, ignore_layer=None, **kw):
        super().__init__(*args, **kw)
        self.layer = layer
        self.ignore_layer = ignore_layer

    def load(self):
        if self._image is not None:
            return

        aseprite_executible = os.environ.get('ASEPRITE_EXECUTABLE', 'aseprite')
        with tempfile.NamedTemporaryFile(suffix='.png') as f:
            args = [aseprite_executible, '-b', self.path, '--color-mode', 'rgb']
            if self.layer is not None:
                args.extend(('--layer', self.layer))
            if self.ignore_layer is not None:
                args.extend(('--ignore-layer', self.ignore_layer))
            res = subprocess.run(args + ['--save-as', f.name])
            if res.returncode != 0:
                raise RuntimeError(f'Aseprite returned non-zero code {res.returncode}')
            img = Image.open(f.name)
        if img.mode == 'P':
            self._image = (img, grf.BPP_8)
        elif img.mode == 'RGB':
            self._image = (img, grf.BPP_24)
        else:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            self._image = (img, grf.BPP_32)


class CompositeSprite(grf.Sprite):
    def __init__(self, sprites, colourkey=None, **kw):
        if len(sprites) == 0:
            raise ValueError('CompositeSprite requires a non-empty list of sprites to compose')
        if len(set(s.zoom for s in sprites)) > 1:
            sprite_list = ', '.join(f'{s.name}<zoom={s.zoom}>' for s in sprites)
            raise ValueError(f'CompositeSprite requires a list of sprites of same zoom level: {sprite_list}')
        self.sprites = sprites
        self.colourkey = colourkey
        super().__init__(sprites[0].w, sprites[0].h, xofs=sprites[0].xofs, yofs=sprites[0].yofs, zoom=sprites[0].zoom, **kw)

    def get_colourkey(self):
        return self.colourkey

    def get_data_layers(self, encoder=None, crop=None):
        npimg = None
        npalpha = None
        npmask = None
        nw, nh = self.w, self.h
        for s in self.sprites:
            w, h, _, _, ni, na, nm = s.get_data_layers(encoder, crop=False)
            if nw is None:
                nw = w
            if nh is None:
                nh = h
            if nw != w or nh != h:
                raise RuntimeError(f'CompositeSprite layers have different size: {self.sprites[0].name}({nw}, {nh}) vs {s.name}({w}, {h})')

            if na is None and ni.shape[2] == 4:
                na = ni[:, :, 3]
                ni = ni[:, :, :3]

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
                        npalpha_norm_mask = np.full((len(partial_mask)), 1.0)
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

        crop_x, crop_y, w, h, npimg, npalpha = self._do_crop(w, h, npimg, npalpha, crop=crop)
        if npmask is not None:
            npmask = npmask[crop_y: crop_y + h, crop_x: crop_x + w]

        colourkey = self.get_colourkey()
        if colourkey is not None:
            mask = np.all(np.equal(npimg, colourkey), axis=2)
            if np.any(mask):
                if npalpha is None:
                    npalpha = np.fill((h, w), 255, dtype=np.uint8)
                npalpha[mask] = 0
        return w, h, self.xofs + crop_x, self.yofs + crop_y, npimg, npalpha, npmask

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

    slayers = []
    for i, s in enumerate(sprites):
        slayers.append(s.get_data_layers())

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
    for jj, s, (w, h, xofs, yofs, npimg, npalpha, npmask) in zip(range(len(sprites)), sprites, slayers):
        if npmask is None:
            raise ValueError(f'Sprite {s.name} has no mask!')

        for ii, recolour in enumerate(recolours):
            x, y = pos[ii][jj]
            for i in range(h):
                for j in range(w):
                    rgb = recolour.get(npmask[i, j])
                    if rgb is None:
                        npres[y + i, x + j, :3] = npimg[i, j, :3]
                    else:
                        b = max(npimg[i, j, :3])
                        npres[y + i, x + j, :3] = adjust_brightness(rgb, b)
                    if npalpha is not None:
                        npres[y + i, x + j, 3] = npalpha[i, j]
                    elif npimg.shape[2] == 4:
                        npres[y + i, x + j, 3] = npimg[i, j, 3]
                    else:
                        npres[y + i, x + j, 3] = 255

    im = Image.fromarray(npres, mode='RGBA')
    im.show()


def debug_cc_recolour(sprites, horizontal=False):
    recolours = []
    for cl in grf.CC_COLOURS:
        recolours.append({
            0xC6 + i : grf.PALETTE[m * 3: m * 3 + 3]
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
