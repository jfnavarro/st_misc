from ij import IJ,WindowManager
from ij.plugin.frame import RoiManager
from ij.plugin import ChannelSplitter,Thresholder
from ij.plugin.filter import ParticleAnalyzer
from ij.io import FileSaver
import time,sys

imp = IJ.getImage()
csplitter = ChannelSplitter()
thresholder = Thresholder()

channels = csplitter.splitRGB(imp.getStack(), False)

blueImp = ImagePlus("blue",channels[2]) 
blueImp.getProcessor().invert()
blueImp.show()
WindowManager.setTempCurrentImage(blueImp)
IJ.run("Make Binary")
blueImp.hide()

roim = RoiManager(True)
# Create a ParticleAnalyzer, with arguments:
# 1. options (could be SHOW_ROI_MASKS, SHOW_OUTLINES, SHOW_MASKS, SHOW_NONE, ADD_TO_MANAGER, and others; combined with bitwise-or)
# 2. measurement options (see [http://rsb.info.nih.gov/ij/developer/api/ij/measure/Measurements.html Measurements])
# 3. a ResultsTable to store the measurements
# 4,5. The min and max size of a particle to consider for measurement
# 6,7. The min and max circularity (values between 0 and 1 perfect circle)

pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA, None, 200, 4000, 0.4, 1.0)
pa.setHideOutputImage(True)
 
if pa.analyze(blueImp):
  print "All ok"
else:
  print "There was a problem in analyzing", blueImp

#Export roi center and radius to TSV
default_name = imp.getShortTitle() + "_cells"
sd = SaveDialog('Save ellypses to file', default_name, '.tsv')
dirToSave = sd.getDirectory()
fileh = open(dirToSave+sd.getFileName(), "w")
#fileh.write("name\tx1\tx2\ty1\ty2\n")

roim = RoiManager.getInstance()
if roim is None:
	sys.exit(1)
rois = roim.getRoisAsArray()
print rois
for roi in rois:
	bounds = roi.getBounds()
	x1 = (float(bounds.x) + float(bounds.x + bounds.width )) / 2.
	y1 = (float(bounds.y) + float(bounds.y + bounds.height)) / 2.
	
	fileh.write("\t".join([roi.getName(),
		   str(x1),
		   str(y1),
		   str(bounds.width),
		   str(bounds.height)
	])+"\n")
fileh.close()

#Export overlay
IJ.doCommand("Flatten")
time.sleep(1)
ids = WindowManager.getIDList()
imp_overlay = None
print ids
for id_img in ids:
   if imp.getID() != id_img:
   	imp_overlay = WindowManager.getImage(id_img)
   	break

if imp_overlay is None:
   sys.exit(1)

fs = FileSaver(imp_overlay)
fs.saveAsJpeg(dirToSave+imp.getShortTitle()+"_cells.jpg")
imp_overlay.hide()
imp_overlay.flush()

IJ.freeMemory()