#export scherm naar plaatje 
iface.mapCanvas().saveAsImage(os.path.join(pad_basis,pad_scen,filename+'.png'), None, 'PNG')

#____________________________________________________________________________________________
# Extent zetten
canvas = iface.mapCanvas()
rect_gilzerbaan = QgsRectangle(127157,394319, 129724,398491)
canvas.setExtent(rect_gilzerbaan)

#____________________________________________________________________________________________
#Voeg  laag toe aan je project
QgsProject.instance().addMapLayer(la_buffer)
