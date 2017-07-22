polygons = []
for roi in RoiManager.getInstance().getRoisAsArray():
	if roi.getClass() != PolygonRoi:
		continue

	polygon = {}
	polygon['name'] = roi.getName()
	polygon['x_origin'] = roi.getBounds().x
	polygon['y_origin'] = roi.getBounds().y
	polygon['x'] = roi.getXCoordinates().tolist()
	polygon['y'] = roi.getYCoordinates().tolist()

	polygons.append(polygon)

if len(polygons) == 0:
	print('No polygons in ROI Manager')
else:
	default_name = IJ.getImage().getOriginalFileInfo().fileName + '_' + polygons[0]['name']
	sd = SaveDialog('Save polygons to file', default_name, '.json')
	if sd.getFileName():
		fh = open(sd.getDirectory() + sd.getFileName(), 'w')
		fh.write(str(polygons))
		fh.close()
