"""
Jython utilities for F3d block data set.
Author: Xinming Wu, Colorado School of Mines
Version: 2015.04.07
"""
from common import *

#############################################################################
# Internal constants

_datdir = "../../../data/seis/ipsi/"

#############################################################################
# Setup

def setupForSubset(name):
  """
  Setup for a specified directory includes:
    seismic directory
    samplings s1,s2,s3
  Example: setupForSubset("s1")
  """
  global seismicDir
  global s1,s2,s3
  global n1,n2,n3
  if name=="f3draw":
    """ the whole f3d seismic image """
    print "setupForSubset: the whole image"
    seismicDir = _datdir
    n1,n2,n3 = 462,951,591
    d1,d2,d3 = 1.0,1.0,1.0 
    #d1,d2,d3 = 0.004,0.025,0.024999 # (s,km,km)
    f1,f2,f3 = 0.0,0.0,0.0 # = 0.000,0.000,0.000
    s1,s2,s3 = Sampling(n1,d1,f1),Sampling(n2,d2,f2),Sampling(n3,d3,f3)
  elif name=="uf":
    """ subset with unconformities and faults """
    print "setupForSubset: uf"
    seismicDir = _datdir+"uf/"
    n1,n2,n3 = 118,420,300
    d1,d2,d3 = 1.0,1.0,1.0 
    #j1,j2,j3 = 344,0,0
    #d1,d2,d3 = 0.004,0.025,0.024999 # (s,km,km)
    #f1,f2,f3 = 0.472,0.0,0.0 # = 0.000,0.000,0.000
    f1,f2,f3 = 0.0,0.0,0.0 # = 0.000,0.000,0.000
    s1,s2,s3 = Sampling(n1,d1,f1),Sampling(n2,d2,f2),Sampling(n3,d3,f3)
  elif name=="ufs":
    """ subset with unconformities and faults """
    print "setupForSubset: ufs"
    seismicDir = _datdir+"ufs/"
    n1,n2,n3 = 118,310,300
    d1,d2,d3 = 1.0,1.0,1.0 
    #j1,j2,j3 = 344,0,0
    #d1,d2,d3 = 0.004,0.025,0.024999 # (s,km,km)
    #f1,f2,f3 = 0.472,0.0,0.0 # = 0.000,0.000,0.000
    f1,f2,f3 = 0.0,0.0,0.0 # = 0.000,0.000,0.000
    s1,s2,s3 = Sampling(n1,d1,f1),Sampling(n2,d2,f2),Sampling(n3,d3,f3)

  elif name=="uncs":
    """ subset of f3d data set with unconformities """
    print "setupForSubset: uncs"
    seismicDir = _datdir+"../../../data/unc/"
    n1,n2,n3 = 120,200,260
    d1,d2,d3 = 1.0,1.0,1.0 
    f1,f2,f3 = 0.0,0.0,0.0 # = 0.000,0.000,0.000
    s1,s2,s3 = Sampling(n1,d1,f1),Sampling(n2,d2,f2),Sampling(n3,d3,f3)

  elif name=="unc":
    """ subset of delhi data set with unconformities """
    print "setupForSubset: unc"
    seismicDir = _datdir+"unc/"
    n1,n2,n3 = 200,133,294
    d1,d2,d3 = 1.0,1.0,1.0 
    #j1,j2,j3 = 344,0,0
    #d1,d2,d3 = 0.004,0.025,0.024999 # (s,km,km)
    #f1,f2,f3 = 0.472,0.0,0.0 # = 0.000,0.000,0.000
    f1,f2,f3 = 0.0,0.0,0.0 # = 0.000,0.000,0.000
    s1,s2,s3 = Sampling(n1,d1,f1),Sampling(n2,d2,f2),Sampling(n3,d3,f3)

  else:
    print "unrecognized subset:",name
    System.exit

def getSamplings():
  return s1,s2,s3

def getSeismicDir():
  return seismicDir

#############################################################################
# read/write images

def readImage(basename):
  """ 
  Reads an image from a file with specified basename
  """
  fileName = seismicDir+basename+".dat"
  image = zerofloat(n1,n2,n3)
  ais = ArrayInputStream(fileName)
  ais.readFloats(image)
  ais.close()
  return image

def writeImage(basename,image):
  """ 
  Writes an image to a file with specified basename
  """
  fileName = seismicDir+basename+".dat"
  aos = ArrayOutputStream(fileName)
  aos.writeFloats(image)
  aos.close()
  return image

#############################################################################
# read/write fault skins

def skinName(basename,index):
  return basename+("%03i"%(index))
def skinIndex(basename,fileName):
  assert fileName.startswith(basename)
  i = len(basename)
  return int(fileName[i:i+3])

def listAllSkinFiles(basename):
  """ Lists all skins with specified basename, sorted by index. """
  fileNames = []
  for fileName in File(seismicDir).list():
    if fileName.startswith(basename):
      fileNames.append(fileName)
  fileNames.sort()
  return fileNames

def removeAllSkinFiles(basename):
  """ Removes all skins with specified basename. """
  fileNames = listAllSkinFiles(basename)
  for fileName in fileNames:
    File(seismicDir+fileName).delete()

def readSkin(basename,index):
  """ Reads one skin with specified basename and index. """
  return FaultSkin.readFromFile(seismicDir+skinName(basename,index)+".dat")

def readSkins(basename):
  """ Reads all skins with specified basename. """
  fileNames = []
  for fileName in File(seismicDir).list():
    if fileName.startswith(basename):
      fileNames.append(fileName)
  fileNames.sort()
  skins = []
  for iskin,fileName in enumerate(fileNames):
    index = skinIndex(basename,fileName)
    skin = readSkin(basename,index)
    skins.append(skin)
  return skins

def writeSkin(basename,index,skin):
  """ Writes one skin with specified basename and index. """
  FaultSkin.writeToFile(seismicDir+skinName(basename,index)+".dat",skin)

def writeSkins(basename,skins):
  """ Writes all skins with specified basename. """
  for index,skin in enumerate(skins):
    writeSkin(basename,index,skin)

from org.python.util import PythonObjectInputStream
def readObject(name):
  fis = FileInputStream(seismicDir+name+".dat")
  ois = PythonObjectInputStream(fis)
  obj = ois.readObject()
  ois.close()
  return obj
def writeObject(name,obj):
  fos = FileOutputStream(seismicDir+name+".dat")
  oos = ObjectOutputStream(fos)
  oos.writeObject(obj)
  oos.close()
