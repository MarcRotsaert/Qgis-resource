"""
Label zetten
"""
import Layers
import Fields as Fi

l = La.returnLayersbyname('Lijnen')[0]
#l = iface.activeLayer()

fi_idx = Fi.indexFieldname(l[0],'Thema')
l_setting = QgsPalLayerSettings()
#l.fieldName = "my_attribute"
l_setting.fieldName = 'Thema' # eigenlijk overbodig.
text_format = QgsTextFormat()
text_format.setFont(QFont("Arial", 12))
text_format.setSize(12)
l_setting.setFormat(text_format)

l_setting = QgsVectorLayerSimpleLabeling(l_setting)
l.setLabelsEnabled(True)
l.setLabeling(l_setting)
l.triggerRepaint()

"""aanpassen label met expressie"""
l_setting = QgsPalLayerSettings()
l_setting.isExpression = True
l_setting.fieldName = 'regexp_replace( "TYPE      ",\'.+- \',\'lala\' )'

l_setting = QgsVectorLayerSimpleLabeling(l_setting)
l.setLabelsEnabled(True)
l.setLabeling(l_setting)
l.triggerRepaint()