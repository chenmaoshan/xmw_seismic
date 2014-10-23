"""
Demonstrate 3D seismic image processing for faults and horizons
Author: Dave Hale, Colorado School of Mines
Version: 2014.07.17
"""
from fakeutils import *
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count

# Names and descriptions of image files used below.
gxfile  = "gx" # input image (maybe after bilateral filtering)
gsxfile = "gsx" # image after lsf with fault likelihoods
epfile  = "ep" # eigenvalue-derived planarity
p2file  = "p2" # inline slopes
p3file  = "p3" # crossline slopes
p2kfile = "p2k" # inline slopes (known)
p3kfile = "p3k" # crossline slopes (known)
flfile  = "fl" # fault likelihood
fpfile  = "fp" # fault strike (phi)
ftfile  = "ft" # fault dip (theta)
gwfile  = "gw" # unfault image
fltfile = "flt" # fault likelihood thinned
fptfile = "fpt" # fault strike thinned
fttfile = "ftt" # fault dip thinned
fs1file = "fs1" # fault slip (1st component)
fs2file = "fs2" # fault slip (2nd component)
fs3file = "fs3" # fault slip (3rd component)
fskbase = "fsk" # fault skin (basename only)

u1file = "u1" # normal vector (1st component)
u2file = "u2" # normal vector (2nd component)
u3file = "u3" # normal vector (3rd component)
gffile  = "gf" # unfolded image 


r1tfile = "r1t" # unfaulting shifts (1st component)
r2tfile = "r2t" # unfaulting shifts (2nd component)
r3tfile = "r3t" # unfaulting shifts (3rd component)
ftfile  = "ft" # unfaulted image 
cpfile  = "cp" # unfaulted image 

r1dfile = "r1d" # unfolding shifts (1st component)
r2dfile = "r2d" # unfolding shifts (2nd component)
r3dfile = "r3d" # unfolding shifts (3rd component)
fdfile  = "fd" # unfolded image 


# These parameters control the scan over fault strikes and dips.
# See the class FaultScanner for more information.
minPhi,maxPhi = 0,360
minTheta,maxTheta = 65,85
sigmaPhi,sigmaTheta = 4,20

# These parameters control the construction of fault skins.
# See the class FaultSkinner for more information.
lowerLikelihood = 0.2
upperLikelihood = 0.5
minSkinSize = 3000

# These parameters control the computation of fault dip slips.
# See the class FaultSlipper for more information.
minThrow = 0.01
maxThrow = 15.0

# Directory for saved png images. If None, png images will not be saved;
# otherwise, must create the specified directory before running this script.
#pngDir = None
pngDir = "../../../png/uff/"

plotOnly = False

# Processing begins here. When experimenting with one part of this demo, we
# can comment out earlier parts that have already written results to files.
def main(args):
  '''
  goFakeData()
  goSlopes()
  goScan()
  goThin()
  goSmooth()
  goSkin()
  goSlip()
  goUnfault()
  '''
  goUnfaultc()
  '''
  goUnfold()
  goUnfoldc2()
  goUnfoldc()
  goFlatten2()
  goTest()
  '''

def goFakeData():
  #sequence = 'A' # 1 episode of faulting only
  sequence = 'OA' # 1 episode of folding, followed by one episode of faulting
  #sequence = 'OOOOOAAAAA' # 5 episodes of folding, then 5 of faulting
  #sequence = 'OAOAOAOAOA' # 5 interleaved episodes of folding and faulting
  nplanar = 3 # number of planar faults
  conjugate = False # if True, two large planar faults will intersect
  conical = False # if True, may want to set nplanar to 0 (or not!)
  impedance = False # if True, data = impedance model
  wavelet = True # if False, no wavelet will be used
  noise = 0.0 # (rms noise)/(rms signal) ratio
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
  for iskin,skin in enumerate(skins):
    plot3(gx,skins=[skin],links=True,png="skin"+str(iskin))

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
  writeImage(gwfile,gw)
  plot3(gx)
  plot3(gw,clab="Amplitude",png="gw")

def goUnfault():
  smark = -999.999
  gx = readImage(gxfile)
  gsx = readImage(gsxfile)
  p2 = readImage(p2file)
  p3 = readImage(p3file)
  s1 = readImage(fs1file)
  s2 = readImage(fs2file)
  s3 = readImage(fs3file)
  fsl = FaultSlipper(gsx,p2,p3)
  s1,s2,s3 = fsl.interpolateDipSlips([s1,s2,s3],smark)
  plot3(gx,s1,cmin=0.0,cmax=10.0,cmap=jetFill(0.3),
        clab="Vertical shift (samples)",png="gxs1i")
  plot3(gx,s2,cmin=-2.0,cmax=2.0,cmap=jetFill(0.3),
        clab="Inline shift (samples)",png="gxs2i")
  plot3(gx,s3,cmin=-1.0,cmax=1.0,cmap=jetFill(0.3),
        clab="Crossline shift (samples)",png="gxs3i")
  gw = fsl.unfault([s1,s2,s3],gx)
  plot3(gw,clab="Unfault",png="gw")
  plot3(gx,clab="Amplitude",png="gx")



def goUnfold():
  if not plotOnly:
    gx = readImage(gwfile)
    u1 = zerofloat(n1,n2,n3)
    u2 = zerofloat(n1,n2,n3)
    u3 = zerofloat(n1,n2,n3)
    ep = zerofloat(n1,n2,n3)
    gf = zerofloat(n1,n2,n3)
    lof = LocalOrientFilter(2.0,1.0)
    lof.applyForNormalPlanar(gx,u1,u2,u3,ep)
    p = array(u1,u2,u3,pow(ep,8.0))
    flattener = FlattenerRT(6.0,6.0)
    r = flattener.findShifts(p)
    flattener.applyShifts(r,gx,gf)
    writeImage(gffile,gf)
  else:
    gf = readImage(gffile)
  hmin,hmax,hmap = -3.0,3.0,ColorMap.GRAY
  plot3(gf,cmin=hmin,cmax=hmax,cmap=hmap,clab="Unfold",png="gf")

def goTest():
  gx = readImage(gxfile)
  p2,p3,ep = FaultScanner.slopes(2.0,1.0,1.0,5.0,gx)
  skins = readSkins(fskbase)
  cfs = ConstraintsFromFaults(skins,p2,p3,ep)
  cp  = zerofloat(n1,n2,n3)
  cs = cfs.getWeightsAndConstraints(ep,cp)
  hmin,hmax,hmap = -3.0,3.0,ColorMap.GRAY
  plot3(gx,cmin=hmin,cmax=hmax,cmap=hmap,clab="Amplitude",png="gx")
  plot3(cp,cmin=hmin,cmax=hmax,cmap=hmap,clab="ControlPoints",png="gx")

def goUnfaultc():
  if not plotOnly:
    ft = zerofloat(n1,n2,n3)
    gx = readImage(gxfile)
    cp  = zerofloat(n1,n2,n3)
    p2,p3,ep = FaultScanner.slopes(4.0,1.0,1.0,5.0,gx)
    skins = readSkins(fskbase)
    cfs = ConstraintsFromFaults(skins,ep)
    wp = pow(ep,2.0)
    cs = cfs.getWeightsAndConstraints(wp,cp)
    fm = cfs.getFaultMap()
    u1 = fillfloat(1.0,n1,n2,n3)
    u2 = fillfloat(0.0,n1,n2,n3)
    u3 = fillfloat(0.0,n1,n2,n3)
    p = array(u1,u2,u3,wp)
    flattener = FlattenerRTD(4.0,4.0)
    [r1,r2,r3] = flattener.computeShifts(True,fm,cs,p)
    flattener.applyShifts([r1,r2,r3],gx,ft)
    writeImage(r1tfile,r1)
    writeImage(r2tfile,r2)
    writeImage(r3tfile,r3)
    writeImage(ftfile,ft)
    writeImage(cpfile,cp)
  else:
    r1 = readImage(r1tfile)
    r2 = readImage(r2tfile)
    r3 = readImage(r3tfile)
    ft = readImage(ftfile)
    cp = readImage(cpfile)
    gx = readImage(gxfile)

  s1 = readImage(fs1file)
  hmin,hmax,hmap = -3.0,3.0,ColorMap.GRAY
  plot3(gx,s1,cmin=-0.01,cmax=10.0,cmap=jetFillExceptMin(1.0),
        clab="Fault throw (samples)",png="gxs1")
  plot3(cp,cmin=hmin,cmax=hmax,cmap=hmap,clab="ControlPointsM",png="cp")
  plot3(ft,cmin=hmin,cmax=hmax,cmap=hmap,clab="UnfaultC",png="ft")
  plot3(gx,r1,cmin=-5.0,cmax=8.0,cmap=jetFill(0.3),
        clab="Vertical shift (samples)",png="gxs1i")
  plot3(gx,r2,cmin=-2.0,cmax=2.0,cmap=jetFill(0.3),
        clab="Inline shift (samples)",png="gxs2i")
  plot3(gx,r3,cmin=-1.0,cmax=1.0,cmap=jetFill(0.3),
        clab="Crossline shift (samples)",png="gxs3i")


def goUnfoldc():
  if not plotOnly:
    gx = readImage(gxfile)
    u1 = zerofloat(n1,n2,n3)
    u2 = zerofloat(n1,n2,n3)
    u3 = zerofloat(n1,n2,n3)
    ep = zerofloat(n1,n2,n3)
    fd = zerofloat(n1,n2,n3)
    lof = LocalOrientFilter(2.0,1.0)
    lof.applyForNormalPlanar(gx,u1,u2,u3,ep)
    wp = copy(ep)
    cp  = zerofloat(n1,n2,n3)
    skins = readSkins(fskbase)
    cfs = ConstraintsFromFaults(skins,wp)
    wp = pow(wp,2.0)
    cs = cfs.getWeightsAndConstraints(wp,cp)
    fm = cfs.getFaultMap()
    p = array(u1,u2,u3,wp)
    flattener = FlattenerRTD(6.0,6.0)
    [r1,r2,r3] = flattener.computeShifts(False,fm,cs,p)
    flattener.applyShifts([r1,r2,r3],gx,fd)
    writeImage(r1dfile,r1)
    writeImage(r2dfile,r2)
    writeImage(r3dfile,r3)
    writeImage(fdfile,fd)
  else:
    fd = readImage(fdfile)
    r1 = readImage(r1dfile)
    r2 = readImage(r2dfile)
    r3 = readImage(r3dfile)
    gx = readImage(gxfile)
  hmin,hmax,hmap = -3.0,3.0,ColorMap.GRAY
  plot3(fd,cmin=hmin,cmax=hmax,cmap=hmap,clab="Amplitude",png="fd")
  plot3(gx,r1,cmin=0.0,cmax=12.0,cmap=jetFill(0.3),
        clab="Vertical shift (samples)",png="gxs1i")
  plot3(gx,r2,cmin=-10,cmax=10,cmap=jetFill(0.3),
        clab="Inline shift (samples)",png="gxs2i")
  plot3(gx,r3,cmin=-8,cmax=8,cmap=jetFill(0.3),
        clab="Crossline shift (samples)",png="gxs3i")
def goUnfoldc2():
  if not plotOnly:
    goUnfaultc()
    gx = readImage(ftfile)
    u1 = zerofloat(n1,n2,n3)
    u2 = zerofloat(n1,n2,n3)
    u3 = zerofloat(n1,n2,n3)
    ep = zerofloat(n1,n2,n3)
    fd = zerofloat(n1,n2,n3)
    lof = LocalOrientFilter(2.0,1.0)
    lof.applyForNormalPlanar(gx,u1,u2,u3,ep)
    p = array(u1,u2,u3,pow(ep,8.0))
    flattener = FlattenerRT(6.0,6.0)
    r = flattener.findShifts(p)
    flattener.applyShifts(r,gx,fd)
    r1 = readImage(r1tfile)
    r2 = readImage(r2tfile)
    r3 = readImage(r3tfile)
    r1 = add(r1,r[0])
    r2 = add(r2,r[1])
    r3 = add(r3,r[2])
    writeImage(r1dfile,r1)
    writeImage(r2dfile,r2)
    writeImage(r3dfile,r3)
    writeImage(fdfile,fd)
  else:
    fd = readImage(fdfile)
    r1 = readImage(r1dfile)
    r2 = readImage(r2dfile)
    r3 = readImage(r3dfile)
    gx = readImage(gxfile)
  hmin,hmax,hmap = -3.0,3.0,ColorMap.GRAY
  plot3(fd,cmin=hmin,cmax=hmax,cmap=hmap,clab="Amplitude",png="fd")
  plot3(gx,r1,cmin=0.0,cmax=12.0,cmap=jetFill(0.3),
        clab="Vertical shift (samples)",png="gxs1i")
  plot3(gx,r2,cmin=-10,cmax=10,cmap=jetFill(0.3),
        clab="Inline shift (samples)",png="gxs2i")
  plot3(gx,r3,cmin=-8,cmax=8,cmap=jetFill(0.3),
        clab="Crossline shift (samples)",png="gxs3i")

def goFlatten1():
  gx = readImage(gwfile)
  gsx = readImage(gwfile)
  sigma1,sigma2,sigma3,pmax = 2.0,2.0,2.0,5.0
  p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gsx)
  skins = readSkins(fskbase)
  wse,cse=1,1
  #cfs = ConstraintsFromSkins(skins,wse,cse,p,q,pow(ep,8.0))
  cfs = ConstraintsFromSkinsM(skins,wse,cse,p2,p3,pow(ep,8.0))
  ws = pow(ep,8.0)
  sh = fillfloat(0.0,n1,n2,n3)
  cs = cfs.getWeightsAndConstraints(ws)
  flc = Flattener3C()
  flc.setSmoothings(12.0,12.0);
  flc.setIterations(0.01,200);
  flc.computeShifts(p2,p3,ws,None,sh);
  fm = flc.getMappingsFromShifts(s1,s2,s3,sh)
  gf = fm.flatten(gx)
#  plot3(ws,clab="Weights",png="ws")
  plot3(gx,clab="Amplitude",png="gx")
  plot3(gf,clab="Amplitude",png="gf")

def goFlatten2():
  gx = readImage(gxfile)
  sigma1,sigma2,sigma3,pmax = 2.0,1.0,1.0,5.0
  p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
  skins = readSkins(fskbase)
  wse,cse=1,1
  cfs = ConstraintsFromSkinsM(skins,wse,cse,p2,p3,pow(ep,1.0))
  ws = pow(ep,2.0)
  sh = fillfloat(0.0,n1,n2,n3)
  cp = fillfloat(0.0,n1,n2,n3)
  cs = cfs.getWeightsAndConstraintsM(ws,cp)
  fk = cfs.getFaultMap()
  p2 = zerofloat(n1,n2,n3)
  p3 = zerofloat(n1,n2,n3)
  flc = Flattener3C()
  flc.setSmoothings(12.0,12.0);
  flc.setIterations(0.01,200);
  flc.computeShifts(p2,p3,ws,fk,cs,sh);
  vs = copy(sh)
  fm = flc.getMappingsFromShifts(s1,s2,s3,sh)
  gf = fm.flatten(gx)
  plot3(cp,clab="ControlPoints",png="cp")
  plot3(gf,clab="Amplitude",png="gf")
  plot3(gx,vs,cmin=0.0,cmax=10.0,cmap=jetFill(0.3),
        clab="Vertical shift (samples)",png="gxsh")


def array(x1,x2,x3=None,x4=None):
  if x3 and x4:
    return jarray.array([x1,x2,x3,x4],Class.forName('[[[F'))
  elif x3:
    return jarray.array([x1,x2,x3],Class.forName('[[[F'))
  else:
    return jarray.array([x1,x2],Class.forName('[[[F'))


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

def plot3(f,g=None,cmin=None,cmax=None,cmap=None,clab=None,cint=None,
          xyz=None,cells=None,skins=None,smax=0.0,
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
    size = 2.0
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
  ipg.setSlices(95,5,44)
  #ipg.setSlices(95,5,95)
  if cbar:
    sf.setSize(837,700)
  else:
    sf.setSize(700,700)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  ov = sf.getOrbitView()
  ov.setWorldSphere(BoundingSphere(0.5*n1,0.5*n2,0.5*n3,radius))
  ov.setAzimuthAndElevation(-55.0,25.0)
  ov.setTranslate(Vector3(0.0241,0.0517,0.0103))
  ov.setScale(1.2)
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(137,1,pngDir+png+"cbar.png")

#############################################################################
run(main)
