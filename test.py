# Powered by Python 3.8
# To cancel the modifications performed by the script
# on the current graph, click on the undo button.
# Some useful keyboard shortcuts:
#   * Ctrl + D: comment selected lines.
#   * Ctrl + Shift + D: uncomment selected lines.
#   * Ctrl + I: indent selected lines.
#   * Ctrl + Shift + I: unindent selected lines.
#   * Ctrl + Return: run script.
#   * Ctrl + F: find selected text.
#   * Ctrl + R: replace selected text.
#   * Ctrl + Space: show auto-completion dialog.
from tulip import tlp
# The updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views
# The pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the
# "Run script " button.
# The runGraphScript(scriptFile, graph) function can be called to launch
# another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call
# (in the form [a-zA-Z0-9_]+.py)
# The main(graph) function must be defined
# to run the script on the current graph
# id_ = graph['id']
# viewBorderColor = graph['viewBorderColor']
# viewBorderWidth = graph['viewBorderWidth']
# viewColor = graph['viewColor']
# viewFont = graph['viewFont']
# viewFontSize = graph['viewFontSize']
# viewIcon = graph['viewIcon']
# viewLabel = graph['viewLabel']
# viewLabelBorderColor = graph['viewLabelBorderColor']
# viewLabelBorderWidth = graph['viewLabelBorderWidth']
# viewLabelColor = graph['viewLabelColor']
# viewLabelPosition = graph['viewLabelPosition']
# viewLayout = graph['viewLayout']
# viewMetric = graph['viewMetric']
# viewRotation = graph['viewRotation']
# viewSelection = graph['viewSelection']
# viewShape = graph['viewShape']
# viewSize = graph['viewSize']
# viewSrcAnchorShape = graph['viewSrcAnchorShape']
# viewSrcAnchorSize = graph['viewSrcAnchorSize']
# viewTexture = graph['viewTexture']
# viewTgtAnchorShape = graph['viewTgtAnchorShape']
# viewTgtAnchorSize = graph['viewTgtAnchorSize']

g = tlp.loadGraph('marvel.tlpb')

picon = g.getStringProperty("viewIcon")
plabel = g.getStringProperty("viewLabel")

name = 'Marvel Super Heroes (1990) #2'
node = g['viewLabel'].getNodesEqualTo(name).next()
g['viewSelection'].setAllNodeValue(False)
heroes_dict ={}
debug=1
for n in g.getNodes():
    debug+=1
    if debug == 20000:
        print("DEBUG")
    if picon[n]=='md-book-open':
        voisins = list(tlp.Graph.getInOutNodes(g,n))
        counter = 1
        for x in voisins:
            for y in voisins[counter:]:
                edge_x_y = tlp.Graph.existEdge(g,x, y, directed=True)
                edge_y_x = tlp.Graph.existEdge(g,y, x, directed=True)
                if(tlp.edge.isValid(edge_x_y) or tlp.edge.isValid(edge_y_x)):
                    if(tlp.edge.isValid(edge_x_y)):
                        heroes_dict =tlp.Graph.getEdgePropertiesValues(g,edge_x_y)
                        heroes_dict['value']+=1
                        tlp.Graph.setEdgePropertiesValues(g,edge_x_y,heroes_dict)
                    elif(tlp.edge.isValid(edge_y_x)):
                        heroes_dict =tlp.Graph.getEdgePropertiesValues(g,edge_y_x)
                        heroes_dict['value']+=1
                        tlp.Graph.setEdgePropertiesValues(g,edge_y_x,heroes_dict)
                else:
                    tlp.Graph.addEdge(g,x, y,{"value" : 1}) 
            counter+=1  
        tlp.Graph.delNode(g,n)
            
tlp.saveGraph(g, "heroes_final.tlpb") 

# tlp.Graph.getEdgePropertiesValues(edge)
# tlp.Graph.setEdgePropertiesValues(edge, propertiesValues)
