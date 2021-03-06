"""
3D seismic image processing for faults
Author: Xinming Wu, Colorado School of Mines
Version: 2015.05.07
"""
from utils import *
sys.setrecursionlimit(1500)
setupForSubset("ufs")
#setupForSubset("unc")
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count
# Names and descriptions of image files used below.
gxfile = "gx" # input image
gsxfile = "gsx" # image after lsf with fault likelihoods
epfile  = "ep" # eigenvalue-derived planarity
p2file  = "p2" # inline slopes
p3file  = "p3" # crossline slopes
flfile  = "fl" # fault likelihood
fpfile  = "fp" # fault strike (phi)
ftfile  = "ft" # fault dip (theta)
fltfile = "flt" # fault likelihood thinned
fptfile = "fpt" # fault strike thinned
fttfile = "ftt" # fault dip thinned
fskbase = "fsk" # fault skin (basename only)
fslbase = "fsl" # fault skin fault estimating slips(basename only)
fskgood = "fsg" # fault skin with interpolated cells (basename only)
ft1file = "ft1" # fault slip interpolated (1st component)
ft2file = "ft2" # fault slip interpolated (2nd component)
ft3file = "ft3" # fault slip interpolated (3rd component)
fwsfile = "fws" # image after unfaulting
ulfile  = "ul" # unconformity likelihood
ultfile = "ult" # thinned unconformity likelihood
uncfile = "unc" # unconformity surface
fgfile = "fg" #flattened image
rgtfile = "rgt" #relative geologic time image
sx1file = "sx1"
sx2file = "sx2"
sx3file = "sx3"


# These parameters control the scan over fault strikes and dips.
# See the class FaultScanner for more information.
minPhi,maxPhi = 0,150
minTheta,maxTheta = 75,80
sigmaPhi,sigmaTheta = 10,20

# These parameters control the construction of fault skins.
# See the class FaultSkinner for more information.
lowerLikelihood = 0.2
upperLikelihood = 0.5
minSkinSize = 1000

# These parameters control the computation of fault dip slips.
# See the class FaultSlipper for more information.
minThrow = 0.0
maxThrow = 20.0


# Directory for saved png images. If None, png images will not be saved.
#pngDir = None
pngDir = "../../../png/ipsi/"
plotOnly = False

# Processing begins here. When experimenting with one part of this demo, we
# can comment out earlier parts that have already written results to files.
def main(args):
  #goTopHorizon()
  #goSlopes()
  #goScan()
  #goThin()
  #goThinImages()
  #goSkin()
  #goReSkin()
  #goSmooth()
  #goSlip()
  goUnfault()
  #goUnfaultS()
  #goUncScan()
  #goUncConvert()
  #goFlatten()
  #goHorizons()
def goTest():
  rgt = readImage(rgtfile)
  f = zerofloat(n2,n3)
  for i3 in range(n3):
    for i2 in range(n2):
      f[i3][i2] = rgt[i3][i2][110]
  #f = rgt[100]
  rmin = min(f)
  rmax = max(f)
  ct = Contours(f)
  cti = ct.getContour(0.5*(rmin+rmax))
  cx1 = cti.x1
  print cti.ns
  for x1i in cx1:
    for xk in x1i:
      print xk

def goTopHorizon():
  k11 = [22, 11, 12, 38, 30, 33, 40]
  k12 = [70,126,152,283, 55, 85,271]
  k13 = [60, 60, 60,191,191,255,234]
  gx = readImage(gxfile)
  sigma1,sigma2,sigma3,pmax = 4.0,2.0,2.0,5.0
  p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
  wp = pow(ep,10.0) 
  lmt = n1-1
  se = SurfaceExtractorC()
  se.setWeights(0.0)
  se.setSmoothings(4.0,4.0)
  se.setCG(0.01,100)
  surf = se.surfaceInitialization(n2,n3,lmt,k11,k12,k13)
  se.surfaceUpdateFromSlopes(wp,p2,p3,k11,k12,k13,surf)
  fh = FaultHelper()
  fh.mask(surf,gx)
  writeImage(gxfile,gx)
  plot3(gx)
 
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
  gx = readImage(gxfile)
  gx = gain(gx)
  if not plotOnly:
    p2 = readImage(p2file)
    p3 = readImage(p3file)
    gx = FaultScanner.taper(10,0,0,gx)
    fs = FaultScanner(sigmaPhi,sigmaTheta)
    fl,fp,ft = fs.scan(minPhi,maxPhi,minTheta,maxTheta,p2,p3,gx)
    print "fl min =",min(fl)," max =",max(fl)
    print "fp min =",min(fp)," max =",max(fp)
    print "ft min =",min(ft)," max =",max(ft)
    '''
    writeImage(flfile,fl)
    writeImage(fpfile,fp)
    writeImage(ftfile,ft)
    '''
  else:
    fl = readImage(flfile)
    fp = readImage(fpfile)
    ft = readImage(ftfile)
  plot3(gx,fl,cmin=0.25,cmax=1,cmap=jetRamp(1.0),
      clab="Fault likelihood",png="fl")
  plot3(gx,fp,cmin=0,cmax=360,cmap=hueFill(1.0),
      clab="Fault strike (degrees)",cint=45,png="fp")
  plot3(gx,convertDips(ft),cmin=35,cmax=50,cmap=jetFill(1.0),
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
  gx = gain(gx)
  plot3(gx,clab="Amplitude",png="gx")
  plot3(gx,fl,cmin=0.25,cmax=1,cmap=jetRamp(1.0),
        clab="Fault likelihood",png="fl")
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="flt")
  plot3(gx,fpt,cmin=0,cmax=180,cmap=hueFillExceptMin(1.0),
        clab="Fault strike (degrees)",cint=45,png="fpt")
  plot3(gx,convertDips(ftt),cmin=35,cmax=50,cmap=jetFillExceptMin(1.0),
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
def goThinImages():
  gx = readImage(gxfile)
  gx = gain(gx)
  fl = readImage(flfile)
  fp = readImage(fpfile)
  ft = readImage(ftfile)
  fs = FaultSkinner()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  cells = fs.findCells([fl,fp,ft])
  flt = fillfloat(0.0,n1,n2,n3)
  fpt = fillfloat(0.0,n1,n2,n3)
  ftt = fillfloat(0.0,n1,n2,n3)
  FaultCell.getFlThick(0.0,cells,flt)
  FaultCell.getFpThick(0.0,cells,fpt)
  FaultCell.getFtThick(0.0,cells,ftt)
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="flt")
  plot3(gx,fpt,cmin=0,cmax=360,cmap=hueFillExceptMin(1.0),
        clab="Fault strike (degrees)",cint=45,png="fpt")
  plot3(gx,convertDips(ftt),cmin=35,cmax=50,cmap=jetFillExceptMin(1.0),
        clab="Fault dip (degrees)",png="ftt")

def goSkin():
  print "goSkin ..."
  gx = readImage(gxfile)
  gx = gain(gx)
  if not plotOnly:
    fl = readImage(flfile)
    fp = readImage(fpfile)
    ft = readImage(ftfile)
    fs = FaultSkinner()
    fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
    fs.setMaxDeltaStrike(10)
    fs.setMaxPlanarDistance(0.2)
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
  skins = readSkins(fskbase)
  flt = like(gx)
  FaultSkin.getLikelihood(skins,flt)
  plot3(gx,skins=skins)
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="fls")
def goReSkin():
  useOldCells=True
  gx = readImage(gxfile)
  fl = readImage(flfile)
  sk = readSkins(fskbase)
  if not plotOnly:
    fsx = FaultSkinnerX()
    cells = fsx.resetCells(sk)
    fsx = FaultSkinnerX()
    fsx.setParameters(10.0,10.0,2.0)
    fsx.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
    fsx.setMinSkinSize(minSkinSize)
    fsx.setMaxPlanarDistance(0.2)
    fsx.setSkinning(useOldCells)
    sks = fsx.findSkinsXX(cells,fl)
    removeAllSkinFiles(fskgood)
    writeSkins(fskgood,sks)
  skins = readSkins(fskgood)
  sks = []
  for ski in skins:
    if(ski.size()>3000):
      sks.append(ski)
  flt = like(gx)
  #FaultSkin.getLikelihood(skins,flt)
  FaultSkin.getLikelihoods(skins,flt)
  gx = gain(gx)
  plot3(gx)
  plot3(gx,skins=skins,png="skins")
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="flc")

def goSmooth():
  print "goSmooth ..."
  gx = readImage(gxfile)
  if not plotOnly:
    flstop = 0.01
    fsigma = 8.0
    gx = readImage(gxfile)
    sks = readSkins(fskgood)
    flt = zerofloat(n1,n2,n3)
    FaultSkin.getLikelihood(sks,flt)
    sigma1,sigma2,sigma3,pmax = 8.0,3.0,3.0,5.0
    p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
    #p2 = readImage(p2file)
    #p3 = readImage(p3file)
    gsx = FaultScanner.smooth(flstop,fsigma,p2,p3,flt,gx)
    writeImage(gsxfile,gsx)
  gsx = readImage(gsxfile)
  gx = gain(gx)
  gsx = gain(gsx)
  plot3(gx,clab="Amplitude",png="gx")
  plot3(gsx,clab="Amplitude",png="gsx")


def goSlip():
  print "goSlip ..."
  gx = readImage(gxfile)
  gx = gain(gx)
  if not plotOnly:
    skins = readSkins(fskgood)
    plot3(gx,skins=skins,png="skinsfl")
    gsx = readImage(gsxfile)
    sigma1,sigma2,sigma3,pmax = 8.0,3.0,3.0,5.0
    p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
    fsl = FaultSlipper(gsx,p2,p3)
    fsl.setOffset(3.0) # the default is 2.0 samples
    fsl.setZeroSlope(False) # True only to show the error
    fsl.computeDipSlips(skins,minThrow,maxThrow)
    '''
    print "  dip slips computed, now reskinning ..."
    print "  number of skins before =",len(skins),
    fsk = FaultSkinner() # as in goSkin
    fsk.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
    fsk.setMinSkinSize(minSkinSize)
    fsk.setMinMaxThrow(-1.0,maxThrow)
    skins = fsk.reskin(skins)
    '''
    #removeAllSkinFiles(fslbase)
    #writeSkins(fslbase,skins)
  #else:
    #skins = readSkins(fslbase)
  #plot3(gx,skins=skins,png="skinsfl")
  #plot3(gx,skins=skins,smax=6,png="skinss1")

def goUnfault():
  smark = -999.999
  gx = readImage(gxfile)
  gx = gain(gx)
  skins = readSkins(fslbase)
  '''
  fsl = FaultSlipper(gx,gx,gx)
  s1,s2,s3=fsl.getDipSlips(skins,smark)
  s1,s2,s3 = fsl.interpolateDipSlips([s1,s2,s3],smark)
  gw = fsl.unfault([s1,s2,s3],gx)
  gw = gain(gw)
  plot3(gx)
  plot3(gw)
  '''
  mark = -1000000
  flt = like(gx)
  fss = fillfloat(mark,n1,n2,n3)
  FaultSkin.getThrowThick(mark,skins,fss)
  FaultSkin.getLikelihood(skins,flt)
  fss = mul(fss,4) #convert to ms
  for i3 in range(n3):
    for i2 in range(n2):
      for i1 in range(n1):
        fssi = fss[i3][i2][i1]
        if fssi<=0.0 and fssi>mark:
          fss[i3][i2][i1]=0.05
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="fls")
  plot3(gx,fss,cmin=-0.05,cmax=25,cmap=jetFillExceptMin(1.0),
      slices=[93,180,192],clab="Fault throw (ms)",cint=8,png="throw3D")

def goUnfaultS():
  if not plotOnly:
    gx = readImage(gxfile)
    fw = zerofloat(n1,n2,n3)
    lof = LocalOrientFilter(8.0,2.0,2.0)
    et = lof.applyForTensors(gx)
    et.setEigenvalues(0.001,1.0,1.0)

    wp = fillfloat(1.0,n1,n2,n3)
    skins = readSkins(fslbase)
    fsc = FaultSlipConstraints(skins)
    sp = fsc.screenPoints(wp)

    uf = UnfaultS(4.0,2.0)
    uf.setIters(100)
    uf.setTensors(et)
    mul(sp[3][0],10,sp[3][0])
    [x1,x2,x3] = uf.findShifts(sp,wp)
    [t1,t2,t3] = uf.convertShifts(40,[x1,x2,x3])
    uf.applyShifts([t1,t2,t3],gx,fw)
    fx = zerofloat(n1,n2,n3)
    uf.applyShiftsX([x1,x2,x3],fw,fx)
    '''
    writeImage(fwsfile,fw)
    writeImage(ft1file,t1)
    writeImage(ft2file,t2)
    writeImage(ft3file,t3)
    writeImage(sx1file,x1)
    writeImage(sx2file,x2)
    writeImage(sx3file,x3)
    '''

  else :
    gx = readImage(gxfile)
    fw = readImage(fwsfile)
    t1 = readImage(ft1file)
    t2 = readImage(ft2file)
    t3 = readImage(ft3file)
  gx = gain(gx)
  fw = gain(fw)
  plot3(gx)
  plot3(fw,png="unfaulted")
  t1 = mul(t1,4) # convert to ms
  t2 = mul(t2,25) # convert to m
  t3 = mul(t3,25) # convert to m
  print min(t2) 
  print max(t2)
  print min(t3) 
  print max(t3)
  '''
  plot3(gx,t1,cmin=-20,cmax=20,cmap=jetFill(0.3),
        clab="Vertical shift (ms)",png="gxs1i")
  '''
  plot3(gx,t2,cmin=-30,cmax=30,cmap=jetFill(0.3),
        clab="Inline shift (m)",png="gxs2i")
  plot3(gx,t3,cmin=-30,cmax=30,cmap=jetFill(0.3),
        clab="Crossline shift (m)",png="gxs3i")
  '''
  skins = readSkins(fslbase)
  mark = -100
  flt = like(gx)
  fss = fillfloat(mark,n1,n2,n3)
  FaultSkin.getThrow(mark,skins,fss)
  FaultSkin.getLikelihood(skins,flt)
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
        clab="Fault likelihood",png="fls")
  plot3(gx,fss,cmin=-0.5,cmax=10,cmap=jetFillExceptMin(1.0),
      slices=[93,180,192],clab="Fault throw (ms)",cint=5,png="throw3D")
  '''

def goUncScan():
  sig1s,sig2s=1.0,2.0
  gx = readImage(gxfile)
  fw = readImage(fwsfile)
  if not plotOnly:
    fw = smoothF(fw)
    ip = InsPhase()
    cs = like(fw)
    ip.applyForCosine(fw,cs)
    unc = UncSurfer()
    unc.setSampling(2,2)
    unc.setForLof(sig1s,sig2s)
    ul=unc.likelihood(cs)
    ult = like(ul)
    unc.thin(0.1,ul,ult)
    sfs = unc.surfer(n2,n3,0.1,2000,ult,ul)
    #unc.surfaceUpdate(2.0,2.0,fw,sfs)
    removeAllUncFiles(uncfile)
    writeUncs(uncfile,sfs)
    uli = unc.interp(n1,n2,n3,ul)
    writeImage(ulfile,uli)
  fw = gain(fw)
  uc = readImage(ulfile)
  ul = zerofloat(n1,n2,n3)
  copy(n1-4,n2,n3,0,0,0,uc,4,0,0,ul)
  unc = UncSurfer()
  ult = like(ul)
  unc.thin(0.2,ul,ult)
  ul = div(exp(ul),exp(1.0))
  sfs = unc.surfer2(n2,n3,0.2,3000,ult)
  sfs = unc.extractUncs(sfs,fw)
  removeAllUncFiles(uncfile)
  writeUncs(uncfile,sfs)
  uc = gain2(uc,12)
  uc = sub(uc,min(uc))
  uc = div(uc,max(uc))
  copy(n1-4,n2,n3,0,0,0,uc,4,0,0,ul)
  plot3(fw,ul,cmin=0.3,cmax=1.0,cmap=jetRamp(1.0),
        clab="Unconformity likelihood",png="ul")
  plot3(fw,uncs=sfs,png="uncs")

def goUncConvert():
  gx  = readImage(gxfile)
  fw  = readImage(fwsfile)
  rw1 = readImage(ft1file)
  rw2 = readImage(ft2file)
  rw3 = readImage(ft3file)
  rgt = readImage(rgtfile)
  sks = readSkins(fskgood)
  uncs = readUncs(uncfile)

  uc = readImage(ulfile)
  ul = zerofloat(n1,n2,n3)
  uc = gain2(uc,12)
  uc = sub(uc,min(uc))
  uc = div(uc,max(uc))
  copy(n1-4,n2,n3,0,0,0,uc,4,0,0,ul)
  uf = UnfaultS(4.0,2.0)
  hfr = HorizonFromRgt(s1,s2,s3,None,rgt)
  funcs = hfr.ulOnSurface(uncs,ul)
  fw = gain(fw)
  #plot3(fw,uncs=[uncs[0]],png="unc1")
  #plot3(fw,uncs=[uncs[1]],png="unc2")
  for unc in uncs:
    uf.applyShiftsR([rw1,rw2,rw3],unc,unc)
  hs = hfr.trigSurfaces(-1.0,uncs,sks,funcs)
  gx = gain(gx)
  #plot3(gx,hs=[hs[0]],png="unc1X")
  #plot3(gx,hs=[hs[1]],png="unc2X")
  plot3(gx,hs=hs,png="uncsX")
def goFlatten():
  fw = readImage(fwsfile)
  if not plotOnly:
    sigma1,sigma2,sigma3,pmax = 2.0,1.0,1.0,5.0
    p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,fw)
    wp = pow(ep,8.0)
    lmt = n1-1
    se = SurfaceExtractorC()
    se.setWeights(0.0)
    se.setSmoothings(4.0,4.0)
    se.setCG(0.01,100)
    k11 = [ 31, 38, 39, 36]
    k12 = [ 25, 38,282,290]
    k13 = [105,249,232,145]
    surf = se.surfaceInitialization(n2,n3,lmt,k11,k12,k13)
    se.surfaceUpdateFromSlopes(wp,p2,p3,k11,k12,k13,surf)
    uncs = readUncs(uncfile)
    sc = SetupConstraints()
    cs = sc.constraintsFromSurfaces([sub(uncs[1],1.0),surf])
    #cs = sc.constraintsFromSurfaces([surf])
    #cs = sc.constraintsFromSurfaces([uncs[0]])
    #cs = sc.constraintsFromSurfaces(uncs)
    sfs = copy(uncs)
    for i3 in range(206,n3):
      for i2 in range(180,n2):
        sfs[0][i3][i2] = -100
    for i3 in range(n3-150,n3):
      for i2 in range(0,120):
        sfs[1][i3][i2] = -100
    sfs = sc.uncConstraints(sfs)
    rs = zerofloat(n1,n2,n3)
    fl3 = Flattener3Unc()
    sig1,sig2=4.0,4.0
    fl3.setSmoothings(sig1,sig2)
    fl3.setIterations(0.01,300);
    #fl3.computeShifts(p2,p3,wp,cs,sfs,rs)
    mp = fl3.getMappingsFromSlopes(s1,s2,s3,p2,p3,wp,cs,sfs,rs)
    #mp = fl3.getMappingsFromShifts(s1,s2,s3,rs)
    rgt = mp.u1
    fg  = mp.flatten(fw)
    writeImage(fgfile,fg)
    writeImage(rgtfile,rgt)
  fg  = readImage(fgfile)
  rgt = readImage(rgtfile)
  fw = gain(fw)
  fg = gain(fg)
  #plot3(fw)
  #plot3(fg,png="fg")
  fs = zerofloat(n1,n2,n3)
  for i3 in range(n3):
    for i2 in range(n2):
      for i1 in range(n1):
        fs[i3][i2][i1] = rgt[i3][i2][i1]-i1
  fs = mul(fs,4) # convert to ms
  plot3(fw,fs,cmin=-110,cmax=70,cmap=jetFill(1.0),
        clab="Vertical shift (ms)",png="shifts")
  plot3(fw,rgt,cmin=10.0,cmax=n1,cmap=jetFill(1.0),
        clab="Relative geologic time",png="rgt")

def goHorizons():
  gx  = readImage(gxfile)
  rgt = readImage(rgtfile)
  sx1 = readImage(sx1file)
  sx2 = readImage(sx2file)
  sx3 = readImage(sx3file)
  rw1 = readImage(ft1file)
  rw2 = readImage(ft2file)
  rw3 = readImage(ft3file)

  sks = readSkins(fslbase)
  uncs = readUncs(uncfile)
  rgtx = zerofloat(n1,n2,n3)
  uf = UnfaultS(4.0,2.0)
  uf.applyShiftsX([sx1,sx2,sx3],rgt,rgtx)
  hfr = HorizonExtraction(s1,s2,s3,None,rgtx)
  gx = gain(gx)
  '''
  fs = [20,58,72]
  dt = 2
  ns = ["horizonsSlide","horizonsub1Slide","horizonsub2Slide"]
  for ik, ft in enumerate(fs):
    name = ns[ik]
    nt = (round((n1-ft)/dt)-10)
    st = Sampling(nt,dt,ft)
    hs = hfr.multipleHorizons(st,sks)
    plot3(gx,hs=hs,png=name)
  '''
  '''
  ft=60  
  dt=5
  nt = (round((n1-ft)/dt)-1)
  st = Sampling(nt,dt,ft)
  hs = hfr.multipleHorizons(st,sks)
  for unc in uncs:
    uf.applyShiftsR([rw1,rw2,rw3],unc,unc)
  hc = hfr.trigSurfaces(0.1,uncs,sks,None)
  plot3(gx,hs=hs,png="cwpLettersHorizons")
  ft = 20
  dt = 2
  nt = (round((n1-ft)/dt)-1)
  st = Sampling(nt,dt,ft)
  k3,k2=249,25
  for unc in uncs:
    uf.applyShiftsR([rw1,rw2,rw3],unc,unc)
  sub(uncs,1,uncs)
  hls  = hfr.horizonCurves(st,k2,k3,sks,uncs)
  uls = hfr.horizonCurves(uncs,k2,k3,sks)
  plot3(gx,curve=True,hs=hls,uncx=uls,png="horizonLines")
  '''

  ft=20  
  dt=2
  nt = (round((n1-ft)/dt)-10)
  st = Sampling(nt,dt,ft)
  hs = hfr.multipleHorizons(st,sks)
  for unc in uncs:
    uf.applyShiftsR([rw1,rw2,rw3],unc,unc)
  sub(uncs,1,uncs)
  hc = hfr.trigSurfaces(0.1,uncs,sks,None)
  #plot3(gx,skins=sks,hs=hs,uncx=hc,png="allSurfaces")

def smoothF(x):
  fsigma = 4.0
  flstop = 0.9
  flt = fillfloat(0.0,n1,n2,n3)
  sigma1,sigma2,sigma3,pmax = 8.0,1.0,1.0,1.0
  p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,x)
  return FaultScanner.smooth(flstop,fsigma,p2,p3,flt,x)

def like(x):
  n3 = len(x)
  n2 = len(x[0])
  n1 = len(x[0][0])
  return zerofloat(n1,n2,n3)


def gain2(x,sigma):
  g = mul(x,x) 
  ref = RecursiveExponentialFilter(sigma)
  ref.apply1(g,g)
  y = like(x)
  div(x,sqrt(g),y)
  return y

def gain(x):
  g = mul(x,x) 
  ref = RecursiveExponentialFilter(20.0)
  ref.apply1(g,g)
  y = like(x)
  div(x,sqrt(g),y)
  return y

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

def rgbFromHeight(h,r,g,b):
  n1 = len(h[0])
  n2 = len(h)
  ht = zerofloat(n1*n2)
  mp = ColorMap(-max(h),-min(h),ColorMap.JET)
  i = 0
  for i1 in range(n1):
    for i2 in range(n2):
      ht[i] = -h[i2][i1]
      i=i+1
  htRGB = mp.getRgbFloats(ht)
  i = 0
  for i1 in range(n1):
    for i2 in range(n2):
      r[i2][i1] = htRGB[i  ] 
      g[i2][i1] = htRGB[i+1] 
      b[i2][i1] = htRGB[i+2] 
      i = i+3

def plot3(f,g=None,cmin=None,cmax=None,cmap=None,clab=None,cint=None,
          xyz=None,cells=None,skins=None,smax=0.0,slices=None,
          links=False,curve=False,trace=False,hs=None,uncs=None,uncx=None,png=None):
  n1,n2,n3 = s1.count,s2.count,s3.count
  d1,d2,d3 = s1.delta,s2.delta,s3.delta
  f1,f2,f3 = s1.first,s2.first,s3.first
  l1,l2,l3 = s1.last,s2.last,s3.last

  sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  cbar = None
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      #ipg.setClips(-2.0,2.0)
      ipg.setClips(-2.0,1.5) # use for subset plots
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMapListener(cbar)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-2.0,1.5)
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
    xyz,uvw,rgb = FaultCell.getXyzUvwRgbForLikelihood(0.7,cmap,cells,False)
    qg = QuadGroup(xyz,uvw,rgb)
    qg.setStates(ss)
    sf.world.addChild(qg)
  if uncs:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    lms.setLocalViewer(True)
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ss.add(ms)
    sg.setStates(ss)
    us = UncSurfer()
    uc=readImage(ulfile)
    uc = gain2(uc,12)
    uc = sub(uc,min(uc))
    uc = div(uc,max(uc))
    ul = zerofloat(n1,n2,n3)
    copy(n1-4,n2,n3,0,0,0,uc,4,0,0,ul)
    for unc in uncs:
      [xyz,rgb]=us.buildTrigs(n1,s3,s2,-0.1,unc,ul)
      #[xyz,rgb]=us.buildTrigs(n1,s3,s2,0.01,unc,ul)
      tg  = TriangleGroup(True,xyz,rgb)
      sg.addChild(tg)
    sf.world.addChild(sg)
  if uncx:
    for unc in uncx:
      if not curve:
        tg = TriangleGroup(True,unc[0])
        tg.setColor(Color.MAGENTA)
        sf.world.addChild(tg)
      else:
        lg = LineGroup(unc[0],unc[1])
        ss = StateSet()
        lg.setStates(ss)
        ls = LineState()
        ls.setWidth(6)
        ls.setSmooth(False)
        ss.add(ls)
        sf.world.addChild(lg)
  if hs:
    for hi in hs:
      if not curve:
        tg = TriangleGroup(True,hi[0],hi[1])
        sf.world.addChild(tg)
      else:
        lg = LineGroup(hi[0],hi[1])
        ss = StateSet()
        lg.setStates(ss)
        ls = LineState()
        ls.setWidth(2)
        ls.setSmooth(False)
        ss.add(ls)
        sf.world.addChild(lg)

  if skins:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    lms.setLocalViewer(True)
    #lms.setTwoSide(True)
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
      size = 0.65 
      ls = LineState()
      ls.setWidth(4.0)
      ls.setSmooth(True)
      ss.add(ls)
    ct = 0
    for skin in skins:
      if smax>0.0: # show fault throws
        cmap = ColorMap(-1.0,smax,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForThrow(size,cmap,False)
      else: # show fault likelihood
        cmap = ColorMap(0.0,1.0,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForLikelihood(size,cmap,False)
      qg = QuadGroup(xyz,uvw,rgb)
      qg.setStates(None)
      sg.addChild(qg)
      if links:
        if ct==0:
          r,g,b=0,0,0
        if ct==1:
          r,g,b=0,0,1
        if ct==2:
          r,g,b=0,1,1
        if ct==3:
          #r,g,b=0.627451,0.12549,0.941176
          r,g,b=1,1,1
        r,g,b=0,0,1
        xyz = skin.getCellLinksXyz()
        rgb = skin.getCellLinksRgb(r,g,b,xyz)
        lg = LineGroup(xyz,rgb)
        #lg = LineGroup(xyz)
        sg.addChild(lg)
        #ct = ct+1
    sf.world.addChild(sg)
  ipg.setSlices(117,40,220)
  ipg.setSlices(110,25,249)
  #ipg.setSlices(115,25,167)
  if cbar:
    sf.setSize(987,720)
  else:
    sf.setSize(850,720)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  ov = sf.getOrbitView()
  zscale = 0.5*max(n2*d2,n3*d3)/(n1*d1)
  ov.setAxesScale(1.0,1.0,zscale)
  ov.setScale(1.3)
  ov.setWorldSphere(BoundingSphere(BoundingBox(f3,f2,f1,l3,l2,l1)))
  ov.setTranslate(Vector3(0.0,0.15,0.05))
  ov.setAzimuthAndElevation(-56.0,35.0)
  #ov.setAzimuthAndElevation(-56.0,40.0)
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(720,1,pngDir+png+"cbar.png")


#############################################################################
run(main)
