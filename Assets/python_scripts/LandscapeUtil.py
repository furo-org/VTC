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
import math
import sys

al=unreal.EditorAssetLibrary
el=unreal.EditorLevelLibrary
sdir=os.path.dirname(os.path.abspath(__file__))
projdir=os.path.join(sdir,"..","..")
# Utilities

# FVector  ([deg], [min], [sec]) -> float [deg]
def Decode60(vec):
  return ((vec.z/60.)+vec.y)/60.+vec.x;

# float [deg] -> FVector ([deg], [min], [sec])
def Encode60(v):
  d=math.floor(v)
  m=math.floor((v-d)*60.)
  s=(v-d-m/60.)*3600.
  return unreal.Vector(d,m,s)

class LandscapeParams:
  def __init__(self):
    self.setStepSize(10)
    self.setZScale(10)
    self.setZEnhance(1)  

  # landscale cell size [cm]
  def setStepSize(self, size):
    self.stepSize=size
    return self

  # landscape z scale value  100-> +/-256 [m],   10-> +/-25.6 [m]  1-> +/-256 [cm]
  def setZScale(self, scale):
    self.toUEScale=100.*128./scale
    self.zScale=scale
    return self

  # optional z scaling factor
  def setZEnhance(self, enh):
    self.zEnhance=enh
    return self

class GeoTIFF:
  def __init__(self, file, lp):
    self.stepSize=lp.stepSize

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
    self.iaf = np.array([[ self.mat[5],-self.mat[2]],
                         [-self.mat[4], self.mat[1]]])*d
    self.offset = np.array([[self.mat[0]], [self.mat[3]]])
    self.af=np.array([[self.mat[1], self.mat[2]],
                      [self.mat[4], self.mat[5]]])

  def setSrcEPSG(self, epsg):
    self.src_cs = osr.SpatialReference()
    self.src_cs.ImportFromEPSG(epsg)
    self.transS2G = osr.CoordinateTransformation(self.src_cs, self.dst_cs)
    # Geotiff CS to Interface CS
    self.transG2S=osr.CoordinateTransformation(self.dst_cs,self.src_cs)

  def getBL(self,uv):
    u=uv[0]
    v=uv[1]
    bl=np.dot(self.af,np.array([[u],[v]]))+self.offset
    sbl=self.transG2S.TransformPoint(bl[1][0],bl[0][0])
    return (sbl[0],sbl[1])

  def getBBoxBL(self):
    # Geotiff CS to Interface CS
    return (self.getBL((0,0)),self.getBL((self.gt.RasterXSize,self.gt.RasterYSize)))

  def sanitizedBounds(self, bbox=None):
    if bbox is None:
      bbox=self.getBBoxBL()
    tl,br=bbox
    bmin, bmax = tl[0], br[0]
    if bmin>bmax:
      bmin, bmax = bmax, bmin
    lmin, lmax = tl[1], br[1]
    if lmin>lmax:
      lmin, lmax = lmax, lmin
    return ((bmin,bmax,lmin,lmax))

  def getIntersection(self, bboxBL):
    bbox=self.sanitizedBounds(bboxBL)
    sbbox=self.sanitizedBounds()
    bmin=max(bbox[0],sbbox[0])
    bmax=min(bbox[1],sbbox[1])
    lmin=max(bbox[2],sbbox[2])
    lmax=min(bbox[3],sbbox[3])
    if lmax < lmin or bmax < bmin:   # No intersection
      return None
    return ((bmax,lmin),(bmin,lmax))  # North-East, South-West

  def getUV(self, srcBL):
    gtBL = self.transS2G.TransformPoint(srcBL[1], srcBL[0])
    bl=np.array([[gtBL[0]],[gtBL[1]]])
    uv = np.dot(self.iaf, bl-self.offset)
    return (uv[0][0], uv[1][0])

def getLandscapeBBox(lp):
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
  size=(int((hx-lx)/lp.stepSize+1),int((hy-ly)/lp.stepSize+1))
  print("Landscape grid size: {0}".format(size))
  return (lx,ly,hx,hy,size)

def getGeoReference():
  w=el.get_all_level_actors()
  theFirst=True
  for a in w:
    if(a.get_class().get_name().startswith("GeoReferenceBP")):
      print("GeoReference Found")
      ref=a
  ref.initialize_geo_conv()
  return ref


class LayerGenerator:
  # lp: LandscapeParams
  def __init__(self, lp):
    self.lp=lp
    # Landscape quad in BL coordinate
    lx,ly,hx,hy,size=getLandscapeBBox(lp)
    self.size=size
    self.ref=getGeoReference()
    self.tl=tuple(map(Decode60, self.ref.get_bl(lx,ly)))
    self.bl=tuple(map(Decode60, self.ref.get_bl(lx,hy)))
    self.br=tuple(map(Decode60, self.ref.get_bl(hx,hy)))
    self.tr=tuple(map(Decode60, self.ref.get_bl(hx,ly)))

    print("Reference Quad=tl:{0} bl:{1} br:{2} tr:{3}".format(self.tl, self.bl, self.br, self.tr))

    self.zo=self.ref.get_actor_location()
    self.zobl=tuple(map(Decode60, self.ref.get_bl(self.zo.x,self.zo.y)))
    print("GeoReference in BL {0} {1}".format(self.zobl[0], self.zobl[1]))
    print("GeoReference in UE {0}".format(self.zo))

  # Clip lowest height [m]   (None for no clipping)
  def setZClipping(self, zClipping):
    self.zClipping=zClipping

  def resample(self, sourceFile, slow_task):
  # Landscape quad on geotiff image in UV coordinate
    gt=GeoTIFF(sourceFile,self.lp)
    tluv=gt.getUV(self.tl)
    bluv=gt.getUV(self.bl)
    bruv=gt.getUV(self.br)
    truv=gt.getUV(self.tr)
    zouv=gt.getUV(self.zobl)
    uvquad=tluv+bluv+bruv+truv

    if self.zClipping is not None:
      imageref=Image.new(gt.image.mode,gt.image.size,self.zClipping)
      clippedimg=ImageMath.eval("max(a,b)",a=gt.image,b=imageref)
      #clippedimg.save(os.path.join(projdir,"Assets","clipped.tif"))
    else:
      clippedimg=gt.image

    # resample geotiff image
    slow_task.enter_progress_frame(1,"Transforming image region")
    img=clippedimg.transform(self.size,Image.QUAD,data=uvquad,resample=Image.BICUBIC)#, fillcolor=sys.float.min)

    slow_task.enter_progress_frame(1,"Transforming height values")
    zov=gt.image.getpixel(zouv)
    zos=32768-(zov*self.lp.zEnhance-self.zo.z/100.)*self.lp.toUEScale   # 32768: mid point (height=0)
    # convert height value [m] to unreal height value
    slow_task.enter_progress_frame(1,"Converting to 16bit grayscale")
    iarrf=np.array(img.getdata())*self.lp.toUEScale*self.lp.zEnhance + zos
    return iarrf.clip(0,65535), img.size

