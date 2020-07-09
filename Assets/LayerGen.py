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
from PIL import Image, ImageTransform, ImageChops
import numpy as np

al=unreal.EditorAssetLibrary
el=unreal.EditorLevelLibrary
sdir=os.path.dirname(os.path.abspath(__file__))
projdir=os.path.join(sdir,"..")

# Parameters

stepSize=10  # [cm] # landscale cell size

# source: source geotiff file name
# out: output 8bit grayscale file name
# add: compositing 8bit grayscale file name

FilesToGo=[
  {
    'source': os.path.join(projdir,"Assets","TC-Park-Green-geo.tif"),
    'out': os.path.join(projdir,"Assets","Layer-Park-Green.png"),
    'add': os.path.join(projdir,"Assets","Layer-Cityhall-Grass.png")
  },
  {
    'source': os.path.join(projdir,"Assets","TC-Pedestrian-geo.tif"),
    'out': os.path.join(projdir,"Assets","Layer-Pedestrian.png"),
    'add': os.path.join(projdir,"Assets","Layer-Cityhall-Tile.png")
  },
  {
    'source': os.path.join(projdir,"Assets","TC-Asphalt-geo.tif"),
    'out': os.path.join(projdir,"Assets","Layer-Asphalt.png")
  },
  {
    'source': os.path.join(projdir,"Assets","TC-Buildings-geo.tif"),
    'out': os.path.join(projdir,"Assets","Layer-Buildings.png"),
    'add': os.path.join(projdir,"Assets","Layer-RoadMarking.png")
  },
  {
    'source': os.path.join(projdir,"Assets","TC-Water-geo.tif"),
    'out': os.path.join(projdir,"Assets","Layer-Water.png")
  },
]

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

class LayerGenerator:
  def __init__(self):
    lx,ly,hx,hy,size=getLandscapeBBox()
    self.size=size
    self.ref=getGeoReference()
    self.tl=self.ref.get_bl(lx,ly)
    self.bl=self.ref.get_bl(lx,hy)
    self.br=self.ref.get_bl(hx,hy)
    self.tr=self.ref.get_bl(hx,ly)
    zo=self.ref.get_actor_location()
    self.zobl=self.ref.get_bl(zo.x,zo.y)

  def resample(self,sourceFile):
    gt=GeoTIFF(sourceFile)
    tluv=gt.getUV(self.tl)
    bluv=gt.getUV(self.bl)
    bruv=gt.getUV(self.br)
    truv=gt.getUV(self.tr)
    zouv=gt.getUV(self.zobl)
    uvquad=tluv+bluv+bruv+truv
    return gt.image.transform(self.size,Image.QUAD,data=uvquad)

# ----------------------------------------------------------------------------------------

nFrames=len(FilesToGo)
text_label="Generating file: {0}"

with unreal.ScopedSlowTask(nFrames, "Transforming reference coordinates") as slow_task:
  slow_task.make_dialog(True)
  layerGen=LayerGenerator()
  for tgt in FilesToGo:
    slow_task.enter_progress_frame(1,text_label.format(os.path.basename(tgt['out'])))
    img=layerGen.resample(tgt['source'])
    if 'add' in tgt:
      add=Image.open(tgt['add'])
      if add.mode != "L":
        print("{0} is not in 8bit grayscale format. Skipping compositing it.".format(tgt['add']))
      else:
        img=ImageChops.lighter(img,add)
    img.save(tgt['out'])
    print("Wrote a layer image: {0}".format(tgt['out']))
