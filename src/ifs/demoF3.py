from fakeutilsF3 import *
import random
#n1,n2,n3=462,951,591
n1,n2,n3=90,221,220
s1,s2,s3=Sampling(n1),Sampling(n2),Sampling(n3)
f1,f2,f3=s1.getFirst(),s2.getFirst(),s3.getFirst()
l1,l2,l3=s1.getLast(),s2.getLast(),s3.getLast()
# Names and descriptions of image files used below.
gxfile  = "f3Sub" # input image (maybe after bilateral filtering)
gsxfile = "gsxf3" # image after lsf with fault likelihoods
epfile  = "epf3" # eigenvalue-derived planarity
p2file  = "p2f3" # inline slopes
p3file  = "p3f3" # crossline slopes
p2kfile = "p2kf3" # inline slopes (known)
p3kfile = "p3kf3" # crossline slopes (known)
flfile  = "flf3" # fault likelihood
fpfile  = "fpf3" # fault strike (phi)
ftfile  = "ftf3" # fault dip (theta)
fltfile = "fltf3" # fault likelihood thinned
fptfile = "fptf3" # fault strike thinned
fttfile = "fttf3" # fault dip thinned
fs1file = "fs1f3" # fault slip (1st component)
fs2file = "fs2f3" # fault slip (2nd component)
fs3file = "fs3f3" # fault slip (3rd component)
fskbase = "fskf3" # fault skin (basename only)
fsibase = "fsif3" # fault skin (basename only)
fsgbase = "fsgf3" # fault skin (basename only)

# These parameters control the scan over fault strikes and dips.
# See the class FaultScanner for more information.
minPhi,maxPhi = 0,360
minTheta,maxTheta = 65,85
sigmaPhi,sigmaTheta = 4,20

# These parameters control the construction of fault skins.
# See the class FaultSkinner for more information.
lowerLikelihood = 0.2
upperLikelihood = 0.5
minSkinSize = 2000

# These parameters control the computation of fault dip slips.
# See the class FaultSlipper for more information.
minThrow = 0.01
maxThrow = 15.0

# Directory for saved png images. If None, png images will not be saved;
# otherwise, must create the specified directory before running this script.
pngDir = None
pngDir = "../../../png/ifs/"

# Processing begins here. When experimenting with one part of this demo, we
# can comment out earlier parts that have already written results to files.
def main(args):
  #goSlopes()
  #goScan()
  #goThin()
  #goSmooth()
  #goSkin()
  #goSlip()
  #goCleanCells()
  
  #goTV()
  #goSPS()
  #goPSS()
  #goFSS()
  #goFSM()
  #goFP()
  #goFS()
  #goFSPSS()
  goFSSPS()
  #smoothTest()
  #goInterp()
  #showImage()
def showImage():
  gx = readImage(gxfile)
  gx = copy(90,221,220,371,50,100,gx)
  plot3(gx,clab="Amplitude")
  writeImage("f3Sub",gx)
def goInterp():
  print "imageGuidedInterp ..."
  gx = readImage(gxfile)
  fl = readImage(flfile)
  sk = readSkins(fskbase)
  fc = FaultSkin.getCells(sk[0])
  fs = FaultSurfer(n1,n2,n3,fc)
  fi = fs.interp(fl)

  plot3(gx,fl,cmin=min(fl),cmax=max(fl),cmap=jetRamp(1.0),
        clab="fl",png="fl")
  plot3(gx,fi,cmin=min(fi),cmax=max(fi),cmap=jetRamp(1.0),
        clab="fi",png="fi")


def goFakeData():
  #sequence = 'A' # 1 episode of faulting only
  sequence = 'OA' # 1 episode of folding, followed by one episode of faulting
  #sequence = 'OOOOOAAAAA' # 5 episodes of folding, then 5 of faulting
  #sequence = 'OAOAOAOAOA' # 5 interleaved episodes of folding and faulting
  nplanar = 3 # number of planar faults
  conjugate = True # if True, two large planar faults will intersect
  conical = True # if True, may want to set nplanar to 0 (or not!)
  impedance = False # if True, data = impedance model
  wavelet = True # if False, no wavelet will be used
  noise = 0.5 # (rms noise)/(rms signal) ratio
  gx,p2,p3 = FakeData.seismicAndSlopes3d2014A(
      sequence,nplanar,conjugate,conical,impedance,wavelet,noise)
  writeImage(gxfile,gx)
  writeImage(p2kfile,p2)
  writeImage(p3kfile,p3)
  print "gx min =",min(gx)," max =",max(gx)
  print "p2 min =",min(p2)," max =",max(p2)
  print "p3 min =",min(p3)," max =",max(p3)
  gmin,gmax,gmap = -3.0,3.0,ColorMap.GRAY
  if impedance:
    gmin,gmax,gmap = 0.0,1.4,ColorMap.JET
  plot3(gx,cmin=gmin,cmax=gmax,cmap=gmap,clab="Amplitude",png="gx")
  #plot3(gx,p2,cmap=bwrNotch(1.0))
  #plot3(gx,p3,cmap=bwrNotch(1.0))

def goSlopes():
  print "goSlopes ..."
  gx = readImage(gxfile)
  sigma1,sigma2,sigma3,pmax = 16.0,1.0,1.0,5.0
  p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
  writeImage(p2file,p2)
  writeImage(p3file,p3)
  writeImage(epfile,ep)
  print "p2  min =",min(p2)," max =",max(p2)
  print "p3  min =",min(p3)," max =",max(p3)
  print "ep min =",min(ep)," max =",max(ep)
  plot3(gx,p2, cmin=-1,cmax=1,cmap=bwrNotch(1.0),
        clab="Inline slope (sample/sample)",png="p2")
  plot3(gx,p3, cmin=-1,cmax=1,cmap=bwrNotch(1.0),
        clab="Crossline slope (sample/sample)",png="p3")
  plot3(gx,sub(1,ep),cmin=0,cmax=1,cmap=jetRamp(1.0),
        clab="Planarity")

def goScan():
  print "goScan ..."
  p2 = readImage(p2file)
  p3 = readImage(p3file)
  gx = readImage(gxfile)
  gx = FaultScanner.taper(10,0,0,gx)
  fs = FaultScanner(sigmaPhi,sigmaTheta)
  fl,fp,ft = fs.scan(minPhi,maxPhi,minTheta,maxTheta,p2,p3,gx)
  print "fl min =",min(fl)," max =",max(fl)
  print "fp min =",min(fp)," max =",max(fp)
  print "ft min =",min(ft)," max =",max(ft)
  writeImage(flfile,fl)
  writeImage(fpfile,fp)
  writeImage(ftfile,ft)
  plot3(gx,clab="Amplitude")
  plot3(gx,fl,cmin=0.25,cmax=1,cmap=jetRamp(1.0),
        clab="Fault likelihood",png="fl")
  plot3(gx,fp,cmin=0,cmax=360,cmap=hueFill(1.0),
        clab="Fault strike (degrees)",cint=45,png="fp")
  plot3(gx,convertDips(ft),cmin=25,cmax=65,cmap=jetFill(1.0),
        clab="Fault dip (degrees)",png="ft")

def goThin():
  print "goThin ..."
  gx = readImage(gxfile)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  flt,fpt,ftt = FaultScanner.thin([fl,fp,ft])
  writeImage(fltfile,flt)
  writeImage(fptfile,fpt)
  writeImage(fttfile,ftt)
  plot3(gx,clab="Amplitude")
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="flt")
  plot3(gx,fpt,cmin=0,cmax=360,cmap=hueFillExceptMin(1.0),
        clab="Fault strike (degrees)",cint=45,png="fpt")
  plot3(gx,convertDips(ftt),cmin=25,cmax=65,cmap=jetFillExceptMin(1.0),
        clab="Fault dip (degrees)",png="ftt")

def goTV():
  print "goTensorVoting ..."
  gx = readImage(gxfile)
  sk = readSkins(fskclean)
  sk = [sk[0]]
  fc = FaultSkin.getCells(sk)
  tv = TensorVoting(n1,n2,n3,fc)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  ss = tv.tensorVote(fl,fp,ft)

  #ss[0] = gain(ss[0])
  div(ss[0],max(ss[0]),ss[0])
  div(ss[1],max(ss[1]),ss[1])
  div(ss[2],max(ss[2]),ss[2])

  fs = FaultSkinner()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  sm = ss[0]
  sm = add(sm,ss[1])
  sm = add(sm,ss[2])
  cells = fs.findCells([sm,fp,ft])
  sks = fs.findSkins(cells)
  for iskin,skin in enumerate(sks):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))

  for iskin,skin in enumerate(sk):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))

  plot3(gx,ss[0],cmin=min(ss[0]),cmax=max(ss[0]),cells=cells,cmap=jetRamp(1.0),
    clab="sm",png="sm")
  plot3(gx,ss[1],cmin=min(ss[1]),cmax=max(ss[1]),cells=cells,cmap=jetRamp(1.0),
    clab="cm",png="sm")
  plot3(gx,ss[2],cmin=min(ss[2]),cmax=max(ss[2]),cells=cells,cmap=jetRamp(1.0),
    clab="jm",png="sm")


  '''
  plot3(gx,ss[1],cmin=min(ss[1]),cmax=max(ss[1]),cells=fc,cmap=jetRamp(1.0),
    clab="cm",png="cm")
  plot3(gx,ss[2],cmin=min(ss[2]),cmax=max(ss[2]),cells=fc,cmap=jetRamp(1.0),
    clab="jm",png="jm")
  '''
def gain(x):
  g = mul(x,x) 
  ref = RecursiveExponentialFilter(20.0)
  ref.apply2(g,g)
  ref.apply3(g,g)
  y = zerofloat(n1,n2,n3)
  div(x,sqrt(g),y)
  return y

def goPSS():
  print "goBlocker ..."
  gx = readImage(gxfile)
  #fc = goNoiseCells()
  #sk = goCleanCells()
  sk = readSkins(fskclean)
  for i in range(3):
    fc = FaultSkin.getCells(sk[i])
    pss = PointSetSurface()
    bs = pss.findScalarField(n1,n2,n3,fc)
    plot3(gx,cells=fc,png="cells")
    plot3(gx,bs,cmin=min(bs),cmax=max(bs),cells=fc,fbs=bs,cmap=jetRamp(1.0),
        clab="PointSetSurface",png="pss")

def goFP():
  print "goFaultSurfer ..."
  gx = readImage(gxfile)
  fp = FaultProcessor()
  sk = fp.computeFaultSkins(gx)
  sks = readSkins(fsgbase)
  for i in range(len(sk)):
    skin=sk[i]
    plot3(gx,skins=[skin],clab=str(i)+"new")


def goFSM():
  print "goFaultSurfer ..."
  gx = readImage(gxfile)
  sk = readSkins(fskbase)
  cells = FaultSkin.getCells(sk)
  fs = SkinsFromCellsM(s1,s2,s3,s1,s2,s3,cells)
  #fs = FaultSurfer(n1,n2,n3,cells)
  #sks = fs.applySurferM()
  sks = fs.applyForSkins(sk)
  removeAllSkinFiles(fsgbase)
  writeSkins(fsgbase,sks)
  sks = readSkins(fsgbase)
  plot3(gx,skins=sk,png="oldSkins")
  plot3(gx,skins=sks,png="newSkins")

  '''
  for i in range(len(sks)):
    skin=sks[i]
    plot3(gx,skins=[skin],clab=str(i)+"new")
  for i in range(len(sk)):
    skin=sk[i]
    plot3(gx,skins=[skin],clab=str(i)+"old")
  '''


def goFS():
  print "goFaultSurfer ..."
  gx = readImage(gxfile)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  fb = ScreenFaultSurferClose()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  fs.setMaxPlanarDistance(0.5)
  cells = fs.findCells([fl,fp,ft])
  #cells = fb.removeOutliers(n1,n2,n3,0.95,0.13,cells)
  sk = fs.findSkins(cells)
  cells = FaultSkin.getCells(sk)
  fs = FaultSurfer(n1,n2,n3,cells)
  sks = fs.applySurferM(4000)

  plot3(gx,skins=sks,png="newSkins")
  plot3(gx,skins=sk,png="oldSkins")
  '''
  for iskin,skin in enumerate(sks):
    plot3(gx,skins=[skin],links=True,png="newSkin"+str(iskin))

  for iskin,skin in enumerate(sk):
    plot3(gx,skins=[skin],links=True,png="oldSkin"+str(iskin))
  '''
def goFSPSS():
  print "goFaultSurfer ..."
  gx = readImage(gxfile)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  #fb = ScreenFaultSurferClose()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  #cells = fb.removeOutliers(n1,n2,n3,0.95,0.13,cells)
  sk = fs.findSkins(cells)
  cells = FaultSkin.getCells(sk)
  #fs = FaultSurferSPS(n1,n2,n3,cells)
  fs = FaultSurferPSS(n1,n2,n3,cells)
  '''
  bs = fs.test()
  plot3(gx,bs,cmin=min(bs),cmax=max(bs),cmap=jetRamp(1.0),
        clab="PointSetSurface")
  '''

  sks = fs.applySurferM(4000)

  plot3(gx,skins=sks,png="newSkins")
  plot3(gx,skins=sk,png="oldSkins")
  for ik in range(10):
    plot3(gx,skins=[sks[ik]],links=True)
  '''
  for iskin,skin in enumerate(sk):
    plot3(gx,skins=[skin],links=True,png="oldSkin"+str(iskin))
  '''

def goFSSPS():
  print "goFaultSurfer ..."
  gx = readImage(gxfile)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  #fb = ScreenFaultSurferClose()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  #cells = fb.removeOutliers(n1,n2,n3,0.95,0.13,cells)
  sk = fs.findSkins(cells)
  cells = FaultSkin.getCells(sk)
  #fs = FaultSurferSPS(n1,n2,n3,cells)
  fs = FaultSurferSPS(n1,n2,n3,cells)
  '''
  bs = fs.test()
  plot3(gx,bs,cmin=min(bs),cmax=max(bs),cmap=jetRamp(1.0),
        clab="PointSetSurface")
  '''

  sks = fs.applySurferM(4000)

  plot3(gx,skins=sks,png="newSkins")
  plot3(gx,skins=sk,png="oldSkins")
  for ik in range(10):
    plot3(gx,skins=[sks[ik]],links=True)

def goFSS():
  print "goBlocker ..."
  gx = readImage(gxfile)
  #fc = goNoiseCells()
  #sk = goCleanCells()
  sk = readSkins(fskclean)
  sk = [sk[2]]
  fc = FaultSkin.getCells(sk)
  fss = FloatScaleSurface()
  #bs = fss.findScalarFieldM(n1,n2,n3,fc)
  fp = readImage(fpfile)
  ft = readImage(ftfile)

  bs = fss.scalarFieldM(n1,n2,n3,fc,fp,ft)
  div(bs,max(bs),bs)

  fs = FaultSkinner()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([bs,fp,ft])
  sks = fs.findSkins(cells)

  for iskin,skin in enumerate(sks):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))

  for iskin,skin in enumerate(sk):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))

  plot3(gx,bs,cmin=min(bs),cmax=max(bs),cmap=jetRamp(1.0),
        clab="PointSetSurface",png="pss")
  plot3(gx,bs,cmin=min(bs),cmax=max(bs),cells=cells,cmap=jetRamp(1.0),
        clab="PointSetSurface",png="pss")

def goSPS():
  print "goBlocker ..."
  gx = readImage(gxfile)
  #fc = goNoiseCells()
  #sk = goCleanCells()
  sk = readSkins(fskclean)
  for i in range(3):
    fc = FaultSkin.getCells(sk[i])
    #fc = FaultSkin.getCells(sk)
    fb = FaultIsosurfer()
    us = fb.normalsFromCellsOpen(n1,n2,n3,fc)
    #us = fb.normalsFromCellsClose(n1,n2,n3,fc)
    bs = fb.faultIndicator(us)
    plot3(gx,cells=fc,png="cells")
    plot3(gx,bs,cmin=min(bs),cmax=max(bs),cells=fc,fbs=bs,cmap=jetRamp(1.0),
        clab="ScreenedPoissonSurface",png="sps")


def goFaultSurfer():
  gx = readImage(gxfile)
  sk = goCleanCells()
  fs = FaultSurfer()
  sf = fs.surfer(n1,n2,n3,sk)
  fc = FaultSkin.getCells(sk)
  ts = fs.applyTransform(fc,gx)
  plot3T(ts[0],g=ts[1],cmin=min(ts[1]),cmax=max(ts[1]),cmap=jetRamp(1.0))
  plot3T(ts[0],cmin=min(ts[0]),cmax=max(ts[0]),fss=sf)

def goNoiseCells():
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  fb = ScreenFaultSurferClose()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  cells = fb.removeOutliers(n1,n2,n3,0.8,0.3,cells)
  return cells

def goCleanCells():
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  gx = readImage(gxfile)
  fs = FaultSkinner()
  fb = ScreenFaultSurferClose()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  skins1 = fs.findSkins(cells)
  cells = fs.findCells([fl,fp,ft])
  cells = fb.removeOutliers(n1,n2,n3,0.95,0.13,cells)
  skins2 = fs.findSkins(cells)
  skins1[2] = skins2[2]
  cells = FaultSkin.getCells(skins1[0])
  for skin in skins1:
    skin.smoothCellNormals(4)
  for iskin,skin in enumerate(skins1):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))
  #cells = fb.removeOutliers(n1,n2,n3,0.95,0.13,cells)
  #return skins
  writeSkins(fskclean,skins1)
  return cells

def goBlockerFromSkins():
  print "goBlocker ..."
  gx = readImage(gxfile)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  plot3(gx,cells=cells,png="cells")
  skins = fs.findSkins(cells)
  for skin in skins:
    skin.smoothCellNormals(4)
  cells = FaultSkin.getCells(skins)
  #fb = FaultSurfer()
  #fb = ScreenFaultSurferOpen()
  fb = ScreenFaultSurferClose()
  bs = fb.findBlocks(n1,n2,n3,cells)
  mk = fb.removeSmallContours(bs)
  writeImage(bsfile,bs)
  plot3(mk,cmap=ColorMap.JET,png="cells")
  plot3(gx,cells=cells,png="cells")
  for iskin,skin in enumerate(skins):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))
  plot3(gx,bs,cmin=min(bs),cmax=max(bs),cmap=jetRamp(1.0),
        clab="Fault blockers",png="fbs")
  plot3(gx,bs,cmin=min(bs),cmax=max(bs),fbs=bs,cmap=jetRamp(1.0),
        clab="Fault blockers",png="fbsc")

def goContour():
  bs = readImage(bsfile)
  gx = readImage(gxfile)
  plotFaultSurf(gx,bs,cp=ColorMap.GRAY)
  plotFaultSurf(bs,bs,cp=ColorMap.JET)

def goStat():
  def plotStat(s,f,slabel=None):
    sp = SimplePlot.asPoints(s,f)
    sp.setVLimits(0.0,max(f))
    sp.setVLabel("Frequency")
    if slabel:
      sp.setHLabel(slabel)
  fl = readImage(fltfile)
  fp = readImage(fptfile)
  ft = readImage(fttfile)
  fs = FaultScanner(sigmaPhi,sigmaTheta)
  sp = fs.getPhiSampling(minPhi,maxPhi)
  st = fs.getThetaSampling(minTheta,maxTheta)
  pfl = fs.getFrequencies(sp,fp,fl); pfl[-1] = pfl[0] # 360 deg = 0 deg
  tfl = fs.getFrequencies(st,ft,fl)
  plotStat(sp,pfl,"Fault strike (degrees)")
  plotStat(st,tfl,"Fault dip (degrees)")

def goSmooth():
  print "goSmooth ..."
  flstop = 0.1
  fsigma = 8.0
  gx = readImage(gxfile)
  flt = readImage(fltfile)
  p2 = readImage(p2file)
  p3 = readImage(p3file)
  gsx = FaultScanner.smooth(flstop,fsigma,p2,p3,flt,gx)
  writeImage(gsxfile,gsx)
  plot3(gx,clab="Amplitude")
  plot3(gsx,clab="Amplitude",png="gsx")

def goSkin():
  print "goSkin ..."
  gx = readImage(gxfile)
  gsx = readImage(gsxfile)
  p2 = readImage(p2file)
  p3 = readImage(p3file)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  skins = fs.findSkins(cells)
  for skin in skins:
    skin.smoothCellNormals(4)
  print "total number of cells =",len(cells)
  print "total number of skins =",len(skins)
  print "number of cells in skins =",FaultSkin.countCells(skins)
  removeAllSkinFiles(fskbase)
  writeSkins(fskbase,skins)
  plot3(gx,cells=cells,png="cells")
  plot3(gx,skins=skins,png="skins")
  '''
  for iskin,skin in enumerate(skins):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))
  '''

def goSlip():
  print "goSlip ..."
  gx = readImage(gxfile)
  gsx = readImage(gsxfile)
  p2 = readImage(p2file)
  p3 = readImage(p3file)
  skins = readSkins(fskbase)
  fsl = FaultSlipper(gsx,p2,p3)
  fsl.setOffset(2.0) # the default is 2.0 samples
  fsl.setZeroSlope(False) # True only if we want to show the error
  fsl.computeDipSlips(skins,minThrow,maxThrow)
  print "  dip slips computed, now reskinning ..."
  print "  number of skins before =",len(skins),
  fsk = FaultSkinner() # as in goSkin
  fsk.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fsk.setMinSkinSize(minSkinSize)
  fsk.setMinMaxThrow(minThrow,maxThrow)
  skins = fsk.reskin(skins)
  print ", after =",len(skins)
  removeAllSkinFiles(fskbase)
  writeSkins(fskbase,skins)
  smark = -999.999
  s1,s2,s3 = fsl.getDipSlips(skins,smark)
  writeImage(fs1file,s1)
  writeImage(fs2file,s2)
  writeImage(fs3file,s3)
  plot3(gx,skins=skins,smax=10.0,png="skinss1")
  plot3(gx,s1,cmin=-0.01,cmax=10.0,cmap=jetFillExceptMin(1.0),
        clab="Fault throw (samples)",png="gxs1")
  s1,s2,s3 = fsl.interpolateDipSlips([s1,s2,s3],smark)
  plot3(gx,s1,cmin=0.0,cmax=10.0,cmap=jetFill(0.3),
        clab="Vertical shift (samples)",png="gxs1i")
  plot3(gx,s2,cmin=-2.0,cmax=2.0,cmap=jetFill(0.3),
        clab="Inline shift (samples)",png="gxs2i")
  plot3(gx,s3,cmin=-1.0,cmax=1.0,cmap=jetFill(0.3),
        clab="Crossline shift (samples)",png="gxs3i")
  gw = fsl.unfault([s1,s2,s3],gx)
  plot3(gx)
  plot3(gw,clab="Amplitude",png="gw")

#############################################################################
# graphics

def jetFill(alpha):
  return ColorMap.setAlpha(ColorMap.JET,alpha)
def jetFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.JET,a)
def jetRamp(alpha):
  return ColorMap.setAlpha(ColorMap.JET,rampfloat(0.0,alpha/256,256))
def bwrFill(alpha):
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,alpha)
def bwrNotch(alpha):
  a = zerofloat(256)
  for i in range(len(a)):
    if i<128:
      a[i] = alpha*(128.0-i)/128.0
    else:
      a[i] = alpha*(i-127.0)/128.0
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,a)
def hueFill(alpha):
  return ColorMap.getHue(0.0,1.0,alpha)
def hueFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.getHue(0.0,1.0),a)

def addColorBar(frame,clab=None,cint=None):
  cbar = ColorBar(clab)
  if cint:
    cbar.setInterval(cint)
  cbar.setFont(Font("Arial",Font.PLAIN,32)) # size by experimenting
  cbar.setWidthMinimum
  cbar.setBackground(Color.WHITE)
  frame.add(cbar,BorderLayout.EAST)
  return cbar

def convertDips(ft):
  return FaultScanner.convertDips(0.2,ft) # 5:1 vertical exaggeration

def plot3T(f,g=None,cmin=None,cmax=None,cmap=None,clab=None,cint=None,
          fss=None,smax=0.0,png=None):
  n3 = len(f)
  n2 = len(f[0])
  n1 = len(f[0][0])
  s1 = Sampling(n1,1.0,0.0)
  s2 = Sampling(n2,1.0,0.0)
  s3 = Sampling(n3,1.0,0.0)
  sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  cbar = None
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      ipg.setClips(-3.0,3.0)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMapListener(cbar)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-3.0,3.0)
    if cmin!=None and cmax!=None:
      ipg.setClips2(cmin,cmax)
    if cmap==None:
      cmap = jetFill(0.8)
    ipg.setColorModel2(cmap)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMap2Listener(cbar)
    sf.world.addChild(ipg)
  if cbar:
    cbar.setWidthMinimum(120)
  if fss:
    tg  = TriangleGroup(True,s3,s2,fss)
    states = StateSet()
    cs = ColorState()
    cs.setColor(Color.CYAN)
    states.add(cs)
    lms = LightModelState()
    lms.setTwoSide(True)
    states.add(lms)
    ms = MaterialState()
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setSpecular(Color.WHITE)
    ms.setShininess(100.0)
    states.add(ms)
    tg.setStates(states);
    sf.world.addChild(tg)
  #ipg.setSlices(95,5,51)
  #ipg.setSlices(95,5,95)
  ipg.setSlices(95,5,76)
  if cbar:
    sf.setSize(837,700)
  else:
    sf.setSize(700,700)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  ov = sf.getOrbitView()
  ov.setWorldSphere(BoundingSphere(0.5*n1,0.5*n2,0.5*n3,radius))
  
  #ov.setAzimuthAndElevation(-55.0,25.0)
  ov.setAzimuthAndElevation(-85.0,25.0)
  ov.setTranslate(Vector3(0.0241,0.0517,0.0103))
  ov.setScale(1.2)
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(137,1,pngDir+png+"cbar.png")


def plot3(f,g=None,cmin=None,cmax=None,cmap=None,clab=None,cint=None,
          xyz=None,cells=None,skins=None,fbs=None,fss=None,smax=0.0,
          links=False,curve=False,trace=False,png=None):
  n1 = len(f[0][0])
  n2 = len(f[0])
  n3 = len(f)
  sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  cbar = None
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      ipg.setClips(-3.0,3.0)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMapListener(cbar)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-3.0,3.0)
    if cmin!=None and cmax!=None:
      ipg.setClips2(cmin,cmax)
    if cmap==None:
      cmap = jetFill(0.8)
    ipg.setColorModel2(cmap)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMap2Listener(cbar)
    sf.world.addChild(ipg)
  if cbar:
    cbar.setWidthMinimum(120)
  if xyz:
    pg = PointGroup(0.2,xyz)
    ss = StateSet()
    cs = ColorState()
    cs.setColor(Color.YELLOW)
    ss.add(cs)
    pg.setStates(ss)
    #ss = StateSet()
    #ps = PointState()
    #ps.setSize(5.0)
    #ss.add(ps)
    #pg.setStates(ss)
    sf.world.addChild(pg)
  if cells:
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    cmap = ColorMap(0.0,1.0,ColorMap.JET)
    xyz,uvw,rgb = FaultCell.getXyzUvwRgbForLikelihood(0.5,cmap,cells,False)
    qg = QuadGroup(xyz,uvw,rgb)
    qg.setStates(ss)
    sf.world.addChild(qg)
  if fbs:
    mc = MarchingCubes(s1,s2,s3,fbs)
    ct = mc.getContour(0.0)
    tg = TriangleGroup(ct.i,ct.x,ct.u)
    states = StateSet()
    cs = ColorState()
    cs.setColor(Color.CYAN)
    states.add(cs)
    lms = LightModelState()
    lms.setTwoSide(True)
    states.add(lms)
    ms = MaterialState()
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setSpecular(Color.WHITE)
    ms.setShininess(100.0)
    states.add(ms)
    tg.setStates(states);
    sf.world.addChild(tg)
  if fss:
    tg = TriangleGroup(True,fss)
    states = StateSet()
    cs = ColorState()
    cs.setColor(Color.CYAN)
    states.add(cs)
    lms = LightModelState()
    lms.setTwoSide(True)
    states.add(lms)
    ms = MaterialState()
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setSpecular(Color.WHITE)
    ms.setShininess(100.0)
    states.add(ms)
    tg.setStates(states);
    sf.world.addChild(tg)

  if skins:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    if not smax:
      ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    sg.setStates(ss)
    size = 1.5
    if links:
      size = 0.5 
    for skin in skins:
      if smax>0.0: # show fault throws
        cmap = ColorMap(0.0,smax,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForThrow(size,cmap,False)
      else: # show fault likelihood
        cmap = ColorMap(0.0,1.0,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForLikelihood(size,cmap,False)
      qg = QuadGroup(xyz,uvw,rgb)
      qg.setStates(None)
      sg.addChild(qg)
      if curve or trace:
        cell = skin.getCellNearestCentroid()
        if curve:
          xyz = cell.getFaultCurveXyz()
          pg = PointGroup(0.5,xyz)
          sg.addChild(pg)
        if trace:
          xyz = cell.getFaultTraceXyz()
          pg = PointGroup(0.5,xyz)
          sg.addChild(pg)
      if links:
        xyz = skin.getCellLinksXyz()
        lg = LineGroup(xyz)
        sg.addChild(lg)
    sf.world.addChild(sg)
  #ipg.setSlices(95,5,51)
  #ipg.setSlices(95,5,95)
  #ipg.setSlices(100,90,0)
  ipg.setSlices(105,0,590)
  if cbar:
    sf.setSize(1037,900)
  else:
    sf.setSize(900,900)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  ov = sf.getOrbitView()
  ov.setWorldSphere(BoundingSphere(BoundingBox(f3,f2,f1,l3,l2,l1)))
  ov.setAxesScale(1.0,1.0,1.5)
  #radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  #ov.setWorldSphere(BoundingSphere(1.0*n1,0.3*n2,0.2*n3,radius))
  
  #ov.setAzimuthAndElevation(-55.0,25.0)
  #ov.setAzimuthAndElevation(-85.0,25.0)
  #ov.setAzimuthAndElevation(135.0,25.0)
  ov.setAzimuthAndElevation(-50.0,25.0)

  #ov.setTranslate(Vector3(0.0241,0.0517,0.0103))
  ov.setScale(1.2)
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(137,1,pngDir+png+"cbar.png")

def plotFaultSurf(f,bs,cp=ColorMap.GRAY):
  ipg = ImagePanelGroup(s1,s2,s3,f)
  ipg.setColorModel(cp)
  world = World()
  nc,dc= 1,0.1
  colors = [Color.RED,Color.GREEN,Color.BLUE,Color.WHITE,Color.BLACK,
            Color.CYAN,Color.YELLOW,Color.MAGENTA,Color.ORANGE,Color.PINK]
  for c in range(0,nc,1):
    color = colors[c]
    mc = MarchingCubes(s1,s2,s3,bs)
    ct = mc.getContour((c-nc/2)*0.2)
    tg = TriangleGroup(ct.i,ct.x,ct.u)
    states = StateSet()
    cs = ColorState()
    cs.setColor(color)
    states.add(cs)
    lms = LightModelState()
    lms.setTwoSide(True)
    states.add(lms)
    ms = MaterialState()
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setSpecular(Color.WHITE)
    ms.setShininess(100.0)
    states.add(ms)
    tg.setStates(states);
    world.addChild(tg)
  world.addChild(ipg)
  frame = makeFrame(world)
  #frame = TestFrame(world)
  frame.setVisible(True)

def makeFrame(world,png=None):
  #lightPosition=[0.,0.,1.0,0.0] #default position
  f1,f2,f3 = s1.first,s2.first,s3.first
  l1,l2,l3 = s1.last,s2.last,s3.last
  d1,d2,d3 = s1.delta,s2.delta,s3.delta
  frame = SimpleFrame(world)
  view = frame.getOrbitView()
  zscale = 0.5*max(n2*d2,n3*d3)/(n1*d1)
  radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  #view.setAxesScale(1.0,1.0,zscale)
  view.setScale(1.1)
  view.setAzimuth(-55.0)
  view.setElevation(25.0)
  view.setWorldSphere(BoundingSphere(0.5*n1,0.5*n2,0.5*n3,radius))
  #frame.viewCanvas.setBackground(frame.getBackground())
  frame.setSize(1000,900)
  frame.setVisible(True)
  if png:
    frame.paintToFile(png+".png")
  return frame



#############################################################################
run(main)
