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
import gdal
import osr
import os
from PIL import Image, ImageTransform, ImageMath
import numpy as np

al=unreal.EditorAssetLibrary
el=unreal.EditorLevelLibrary
sdir=os.path.dirname(os.path.abspath(__file__))
projdir=os.path.join(sdir,"..")

# Parameters

stepSize=10  # [cm] # landscale cell size
zScale=10    # 100: +/-256 [m], 10: +/-25.6 [m]  1: 256 [cm]     # landscape z scale value
zEnhance=1   # optional z scaling factor
zClipping=19.0 # Clip lowest height [m]   (None for no clipping)
inputGeotiff=os.path.join(projdir,"Assets","TC-DEM-geo.tif")
outputHeightmap=os.path.join(projdir,"Assets","heightmap.png")
toUEScale=100.*128./zScale   # [m]->[cm]->[heightmap unit]

# Utilities

class GeoTIFF:
  def __init__(self, file):
    self.gt = gdal.Open(file, gdal.GA_ReadOnly)
    #self.rast = np.array([self.gt.GetRasterBand(1).ReadAsArray()])
    self.image = Image.fromarray(self.gt.GetRasterBand(1).ReadAsArray())
    self.src_cs = osr.SpatialReference()
    self.dst_cs = osr.SpatialReference()
    self.dst_cs.ImportFromWkt(self.gt.GetProjectionRef())
    self.setSrcEPSG(6668)   # default to JGD2011

    # inverse transform from GeoTIFF(UV) to GeoTIFF(Logical)
    self.mat = self.gt.GetGeoTransform()
    d = 1./(self.mat[5]*self.mat[1]-self.mat[4]*self.mat[2])
    self.iaf = np.array([[self.mat[5], -self.mat[2]],
                         [-self.mat[4], self.mat[1]]])*d
    self.offset = np.array([[self.mat[0]], [self.mat[3]]])

  def setSrcEPSG(self, epsg):
    self.src_cs = osr.SpatialReference()
    self.src_cs.ImportFromEPSG(epsg)
    self.transform = osr.CoordinateTransformation(self.src_cs, self.dst_cs)

  def getUV(self, srcBL):
    gtBL = self.transform.TransformPoint(srcBL[1], srcBL[0])
    bl=np.array([[gtBL[0]],[gtBL[1]]])
    uv = np.dot(self.iaf, bl-self.offset)
    return (uv[0][0], uv[1][0])


def getLandscapeBBox():
  # search for landscape proxy actors
  w=el.get_all_level_actors()
  theFirst=True
  for a in w:
    if(a.get_class().get_name().startswith("Landscape") and not a.get_class().get_name().startswith("LandscapeGizmo")):
      #print("Landscape Found : "+ a.get_name())
      o,box=a.get_actor_bounds(True)
      h=o+box
      l=o-box
      if(theFirst):
        lx=l.x
        ly=l.y
        hx=h.x
        hy=h.y
        theFirst=False
      else:
        if(lx>l.x):
          lx=l.x
        if(ly>l.y):
          ly=l.y
        if(hx<h.x):
          hx=h.x
        if(hy<h.y):
          hy=h.y
  print("Landscape bounding box: ({0}, {1}  -  {2}, {3})".format(lx,ly,hx,hy))
  print("Landscape size: {0} x {1}".format(hx-lx,hy-ly))
  size=(int((hx-lx)/stepSize+1),int((hy-ly)/stepSize+1))
  print("Landscape grid size: {0}".format(size))
  return (lx,ly,hx,hy,size)

def getGeoReference():
  w=el.get_all_level_actors()
  theFirst=True
  for a in w:
    if(a.get_class().get_name().startswith("GeoReferenceBP")):
      print("GeoReference Found")
      ref=a
  return ref

# ----------------------------------------------------------------------------------------

lx,ly,hx,hy,size=getLandscapeBBox()
ref=getGeoReference()

text_label="Projecting coordinates"
nFrames=5
with unreal.ScopedSlowTask(nFrames, text_label) as slow_task:
  slow_task.make_dialog(True)

  tl=ref.get_bl(lx,ly)
  bl=ref.get_bl(lx,hy)
  br=ref.get_bl(hx,hy)
  tr=ref.get_bl(hx,ly)
  zo=ref.get_actor_location()
  zobl=ref.get_bl(zo.x,zo.y)
  #print("Reference Quad=tl:{0} bl:{1} br:{2} tr:{3}".format(tl, bl, br, tr))
  #print("GeoReference in UE {0}".format(zo))
  #print("GeoReference in BL {0}".format(zobl))

  gt=GeoTIFF(inputGeotiff)
  tluv=gt.getUV(tl)
  bluv=gt.getUV(bl)
  bruv=gt.getUV(br)
  truv=gt.getUV(tr)
  zouv=gt.getUV(zobl)

  #print("Reference Quad on GeoTIFF image =tl:{0} bl:{1} br:{2} tr:{3}".format(tluv, bluv, bruv, truv, zouv))

  slow_task.enter_progress_frame(1,"Clipping z range")
  print(gt.image.mode)
  print(gt.image)
  if zClipping is not None:
    imageref=Image.new(gt.image.mode,gt.image.size,zClipping)
    clippedimg=ImageMath.eval("max(a,b)",a=gt.image,b=imageref)
    clippedimg.save(os.path.join(projdir,"Assets","clipped.tif"))
  else:
    clippedimg=gt.image

  slow_task.enter_progress_frame(1,"Transforming image region")

  uvf=tluv+bluv+bruv+truv
  img=clippedimg.transform(size,Image.QUAD,data=uvf,resample=Image.BICUBIC)

  slow_task.enter_progress_frame(1,"Transforming height values")

  # scale to match landscape scaling, and offset to align to GeoReference actor
  zov=gt.image.getpixel(zouv)
  zos=32768-(zov*zEnhance-zo.z/100.)*toUEScale   # 32768: mid point (height=0)
  iarrf=np.array(img.getdata()).clip(zcmin,zcmax)*toUEScale*zEnhance + zos

  slow_task.enter_progress_frame(1,"Converting to 16bit grayscale")
  # convert to uint16 using numpy
  # PIL cannot handle this operation because of CLIP16() which limits each pixel value in -32768 to 32767.
  # This clipping must be avoided because destination dtype is uint16.
  iarrs=np.array(iarrf,dtype="uint16")

  slow_task.enter_progress_frame(1,"Saving as {0}".format(os.path.basename(outputHeightmap)))

  imgS=Image.frombuffer("I;16",img.size,iarrs.data, "raw", "I;16", 0, 1)
  imgS.save(outputHeightmap)
  print("Heightmap saved as {0}".format(outputHeightmap))
