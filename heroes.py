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
def main(graph):
    id_ = graph['id']
    viewBorderColor = graph['viewBorderColor']
    viewBorderWidth = graph['viewBorderWidth']
    viewColor = graph['viewColor']
    viewFont = graph['viewFont']
    viewFontSize = graph['viewFontSize']
    viewIcon = graph['viewIcon']
    viewLabel = graph['viewLabel']
    viewLabelBorderColor = graph['viewLabelBorderColor']
    viewLabelBorderWidth = graph['viewLabelBorderWidth']
    viewLabelColor = graph['viewLabelColor']
    viewLabelPosition = graph['viewLabelPosition']
    viewLayout = graph['viewLayout']
    viewMetric = graph['viewMetric']
    viewRotation = graph['viewRotation']
    viewSelection = graph['viewSelection']
    viewShape = graph['viewShape']
    viewSize = graph['viewSize']
    viewSrcAnchorShape = graph['viewSrcAnchorShape']
    viewSrcAnchorSize = graph['viewSrcAnchorSize']
    viewTexture = graph['viewTexture']
    viewTgtAnchorShape = graph['viewTgtAnchorShape']
    viewTgtAnchorSize = graph['viewTgtAnchorSize']

    
    
    picon = graph.getStringProperty("viewIcon")
    plabel = graph.getStringProperty("viewLabel")
    graph['viewSelection'].setAllNodeValue(False)
    # name = 'Marvel Super Heroes (1990) #2'
    # node = graph['viewLabel'].getNodesEqualTo(name).next()
    # graph['viewSelection'][node]=True
    
    for n in graph.getNodes():
        if picon[n]=='md-book-open':
            voisins = list(tlp.Graph.getInOutNodes(graph,n))
            counter = 1
            for x in voisins:
                for y in voisins[counter:]:
                    tlp.Graph.addEdge(graph,x, y, propertiesValues=None) 
                counter+=1  
            params= tlp.getDefaultPluginParameters('Reachable SubGraph',graph)
            params['distance']=1
            params['edge direction']= 'all edges'
            subgraph = graph.applyBooleanAlgorithm('Reachable SubGraph',params)
            tlp.Graph.delNode(graph,n)
            
      
