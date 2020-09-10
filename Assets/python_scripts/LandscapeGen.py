# Copyright 2020 Tomoaki Yoshida<yoshida@furo.org>
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
#
#
# You need following modules to run this script
#   + pillow
#   + numpy
#   + gdal
#
# You can install these modules by running following commands on a posh prompt
#  PS> cd C:\Program Files\Epic Games\UE_4.25\Engine\Binaries\ThirdParty\Python\Win64
#  PS> ./python.exe -m pip install pillow numpy
# GDAL cannot install by this simple method. You need to download whl file from
#  https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
# and then, install it by the similar command
#  PS> ./python.exe -m pip install /path/to/GDAL-2.2.4-cp27-cp27m-win_amd64.whl
#
#  You may want to add 
#   --target="C:\Program Files\Epic Games\UE_4.25\Engine\Source\ThirdParty\Python\Win64\Lib\site-packages"
#  to each pip install command. Without this --target option, modules will be installed in this folder.
#    C:\Program Files\Epic Games\UE_4.25\Engine\Binaries\ThirdParty\Python\Win64\Lib\site-packages

import unreal
#import gdal
#import osr
import os
from PIL import Image, ImageTransform, ImageMath
import numpy as np
#import math
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from LandscapeUtil import LayerGenerator, LandscapeParams
#import LandscapeUtil

al=unreal.EditorAssetLibrary
el=unreal.EditorLevelLibrary
sdir=os.path.dirname(os.path.abspath(__file__))
projdir=os.path.join(sdir,"..","..")

# Parameters

lp=LandscapeParams().setStepSize(10).setZScale(10).setZEnhance(1)
inputGeotiff=os.path.join(projdir,"Assets","DEM_SPAN_Composition0909.tif");
outputHeightmap=os.path.join(projdir,"Assets","heightmap-0909.png")
zClipping=None

# ----------------------------------------------------------------------------------------

text_label="Projecting coordinates"
nFrames=5
with unreal.ScopedSlowTask(nFrames, text_label) as slow_task:
  slow_task.make_dialog(True)

  layerGen=LayerGenerator(lp)
  layerGen.setZClipping(zClipping)

  img,size=layerGen.resample(inputGeotiff, slow_task)

  iarrs=np.array(img,dtype="uint16")
  imgS=Image.frombuffer("I;16",size,iarrs.data, "raw", "I;16", 0, 1)
  imgS.save(outputHeightmap)
  print("Heightmap saved as {0}".format(outputHeightmap))
