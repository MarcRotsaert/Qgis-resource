from qgis.core import QgsField

def listFieldnames(layer):
    availablefields=[str(f.name()) for f in layer.dataProvider().fields()]
    return availablefields

def indexFieldname(layer, fieldstr):
    i_field = layer.fields().indexFromName(fieldstr)  
    assert i_field!=-1, 'ongeldig fieldname. Beschikbare velden bij laag zijn:'+ str(listFieldnames(layer))
    return i_field
    
def checkFieldname(layer,fieldstr):
    """
    Controleer of een laag een attribuut met een bepaalde naam heeft.
    INPUT:
        - layer = QgsVectorLayer-object 
        - fieldstr = naam van veld(field) dat geplot moet worden (STRING)
    """
    availablefields = listFieldnames(layer)
    #availablefields=[str(f.name()) for f in layer.dataProvider().fields()]
    
    assert(layer.dataProvider().fields().indexFromName(fieldstr)>=0), fieldstr +' is een verkeerd Veld opgegeven. Beschikbare velden bij laag zijn:'+ str(availablefields)

def existFieldname(layer,fieldstr):
    availablefields = listFieldnames(layer)
    return fieldstr in availablefields

class FieldProperties():
    def __init__(self,layer,fieldstr):
        assert existFieldname(layer,fieldstr)
        self.layer=layer
        self.fieldstr=fieldstr
        self.fieldindex = indexFieldname(layer,fieldstr)
        self.field=layer.fields().field(self.fieldindex)
    def returnName(self):
        return self.field.name()
    def returnType(self):
        return self.field.type()
    def returnTypename(self):
        return self.field.type()
    def returnLength(self):
        return self.field.length()
    def returnPrecision(self):
        return self.field.precision()
    def returnFieldindex(self):
        return self.fieldindex

def addFields(layer,qgsfieldlist):
    """
    Voeg attribuutvelden toe aan een laag
    INPUT:
        - layer = QgsVectorLayer-object 
        - qgsfieldlist = list van QgsField -objecten  dat toegevoegd moet worden (STRING)
    """
    #assert isinstance(qgsfieldlist,QgsFields)
    listfn = listFieldnames(layer)
        
    for qgsfield in qgsfieldlist:
       assert(qgsfield.type()>0)
       assert(len(qgsfield.name())>0), 'No variable name claimed'
       assert(qgsfield.name() not in listfn), 'variable name already exists'
    #x

    for qgsfield in qgsfieldlist:
        g=layer.dataProvider().addAttributes([qgsfield])
    assert(g is True)
    layer.updateFields()

def copyField(layer,fieldname_in,fieldname_out):
    checkFieldname(layer,fieldname_in)
    listfn = listFieldnames(layer)
    assert(fieldname_out not in listfn), 'variable name already exists'

    i = indexFieldname(layer,fieldname_in)
    vartype = layer.fields().field(i).type()
    precision = layer.fields().field(i).precision()
    length = layer.fields().field(i).length()
    qf = QgsField(fieldname_out,
        type=vartype,prec=precision,len=length)

    addFields(layer,[qf])
    return qf
    
    
    
    
    
    
    
