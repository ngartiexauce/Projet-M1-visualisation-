from tulip import tlp
from flask import *
import io
import csv
import re
import collections
import numpy as np
from collections import OrderedDict
from itertools import islice

# to be able to load Tulip
import sys
sys.path.insert(0, '/usr/local/lib64/tulip/python')

# NE PAS MODIFIER LA LIGNE SUIVANTE
web_app = Flask(__name__)

# make and return a csv file "Degree value, number of nodes with this value"

global nb_heroes
nb_heroes = 50
global hero
hero = "Spider-Man"

global best_heroes
best_heroes = []
marvel_graph = tlp.loadGraph('marvel.tlpb')

# compute node degree
metricprop = marvel_graph.getDoubleProperty("viewMetric")
marvel_graph.applyDoubleAlgorithm("Degree", metricprop)

# get  characters with the highest Degree (most published)
picon = marvel_graph.getStringProperty("viewIcon")
plabel = marvel_graph.getStringProperty("viewLabel")
i = 0
# iterate in descending order (max to min)
for n in metricprop.getSortedNodes(None, False):
    if picon[n] == "md-human":
        best_heroes.append(plabel[n])
        i = i + 1
    if(i == nb_heroes):
        break


@web_app.route("/get_top_10")
def get_top_10():
    # load graph data
    global hero
    heroes_graph = tlp.loadGraph('heroes_final.tlpb')
    node = heroes_graph['viewLabel'].getNodesEqualTo(hero).next()
    heroes_graph['viewSelection'].setAllNodeValue(False)
    heroes_graph['viewSelection'][node] = True
    params = tlp.getDefaultPluginParameters(
        'Reachable SubGraph', heroes_graph)
    params['distance'] = 1
    params['edge direction'] = 'all edges'
    heroes_graph.applyBooleanAlgorithm('Reachable SubGraph', params)
    heroes_graph.addSubGraph(
        heroes_graph['viewSelection'], name="SubGraph_hero")
    SubGraph_hero = heroes_graph.getSubGraph("SubGraph_hero")
    # compute node degree
    metricprop = SubGraph_hero.getDoubleProperty("viewMetric")
    SubGraph_hero.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = SubGraph_hero.getStringProperty("viewIcon")
    plabel = SubGraph_hero.getStringProperty("viewLabel")
    best10 = []
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            best10.append((plabel[n], metricprop[n]))
            i += 1
        if i == 10:
            break
    # produce a csv  return it
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("name", "val"))
    for n in best10:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=get_top_10.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/word_cloud", methods=['POST', 'GET'])
def word_cloud():
    global hero
    global nb_heroes
    global best_heroes
    list_heroes = []

    if request.method == 'POST':
        try:
            nb_heroes = int(request.form.get('nb_heroes'))
        except:
            pass

        try:
            hero = request.form.get('heroes')
        except:
            pass

    return render_template("word_cloud.html", title="Word Cloud des "+str(nb_heroes)+" personnages les plus proche de "+hero, best_heroes=best_heroes, hero=hero)


@web_app.route("/getDataWordCloud")
def getDataWordCloud():
    global hero
    global nb_heroes
    global best_heroes
    list_heroes = []
    edge_value = 0
    word_cloud = []
    heroes_graph = tlp.loadGraph('heroes_final.tlpb')
    node = heroes_graph['viewLabel'].getNodesEqualTo(hero).next()
    heroes_graph['viewSelection'].setAllNodeValue(False)
    heroes_graph['viewSelection'][node] = True
    params = tlp.getDefaultPluginParameters(
        'Reachable SubGraph', heroes_graph)
    params['distance'] = 1
    params['edge direction'] = 'all edges'
    heroes_graph.applyBooleanAlgorithm('Reachable SubGraph', params)
    heroes_graph.addSubGraph(
        heroes_graph['viewSelection'], name="SubGraph_hero")
    SubGraph_hero = heroes_graph.getSubGraph("SubGraph_hero")
    # compute node degree
    metricprop = SubGraph_hero.getDoubleProperty("viewMetric")
    SubGraph_hero.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = SubGraph_hero.getStringProperty("viewIcon")
    plabel = SubGraph_hero.getStringProperty("viewLabel")
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human" and plabel[n] in best_heroes:
            if(plabel[node] == hero and plabel[n] != hero):
                for edge in tlp.Graph.allEdges(SubGraph_hero, node):
                    if tlp.Graph.source(SubGraph_hero, edge) == n or tlp.Graph.target(SubGraph_hero, edge) == n:
                        edge_value = tlp.Graph.getEdgePropertiesValues(SubGraph_hero, edge)[
                            'value']
                        break
                word_cloud.append((plabel[node], plabel[n], edge_value))

    # produce a csv  return it
        csvdata = io.StringIO()
        writer = csv.writer(csvdata, delimiter=",")
        if(plabel[node] == hero and plabel[n] == hero):
            i -= 1
        i += 1
        if(i == nb_heroes):
            break

    writer.writerow(("group", "name", "val"))
    for n in word_cloud:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=data_word_cloud.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# donnes pour histogramme des 10 personnages les plus publiés


@web_app.route("/getData_hist")
def getData_hist():
    # load graph data
    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    best10 = []
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            best10.append((plabel[n], metricprop[n]))
            i += 1
        if i == 10:
            break
    # produce a csv  return it
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("name", "val"))
    for n in best10:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=getData_hist.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/circular_barplot", methods=['POST', 'GET'])
def circular_barplot():
    global hero
    if request.method == 'POST':
        hero = request.form.get('heroes')
    list_heroes = []

    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get  characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            list_heroes.append(plabel[n])
            i = i + 1
        if(i == 50):
            break
    for i in list_heroes:
        if hero in i:
            hero = i
    return render_template("circular_barplot.html", title="Les 50 personnages les plus proches de  "+hero, list_heroes=list_heroes)


@web_app.route("/heatmap", methods=['POST', 'GET'])
def heatmap():
    global hero
    global nb_heroes
    if request.method == 'POST':
        nb_heroes = request.form.get('nb_heroes')

    return render_template("heatmap.html", title="Heatmap des "+str(nb_heroes)+" personnages les publiés")


@web_app.route("/radial_chart", methods=['POST', 'GET'])
def radial_chart():
    global hero
    if request.method == 'POST':
        hero = request.form.get('heroes')

    list_heroes = []
    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get  characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            list_heroes.append(plabel[n])
            i = i + 1
        if(i == 50):
            break
    for i in list_heroes:
        if hero in i:
            hero = i

    list_heroes.append(hero)
    return render_template("radial_chart.html", title="Les 10 personnages les plus proches de "+hero, list_heroes=list_heroes)


# donnees heatmap 10 personnages les plus publiés
@web_app.route("/getDataHeatmap")
def getDataHeatmap():
    global nb_heroes

    list_heroes = []
    edge_value = 0

    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get  characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            list_heroes.append(plabel[n])
            i = i + 1
        if(i == int(nb_heroes)):
            break

    heat_map = []
    for name in list_heroes:
        heroes_graph = tlp.loadGraph('heroes_final.tlpb')
        node = heroes_graph['viewLabel'].getNodesEqualTo(name).next()
        heroes_graph['viewSelection'].setAllNodeValue(False)
        heroes_graph['viewSelection'][node] = True
        params = tlp.getDefaultPluginParameters(
            'Reachable SubGraph', heroes_graph)
        params['distance'] = 1
        params['edge direction'] = 'all edges'
        heroes_graph.applyBooleanAlgorithm('Reachable SubGraph', params)
        heroes_graph.addSubGraph(
            heroes_graph['viewSelection'], name="SubGraph_hero")
        SubGraph_hero = heroes_graph.getSubGraph("SubGraph_hero")
        # compute node degree
        metricprop = SubGraph_hero.getDoubleProperty("viewMetric")
        SubGraph_hero.applyDoubleAlgorithm("Degree", metricprop)

        # get 10 characters with the highest Degree (most published)
        picon = SubGraph_hero.getStringProperty("viewIcon")
        plabel = SubGraph_hero.getStringProperty("viewLabel")

        # iterate in descending order (max to min)
        for n in metricprop.getSortedNodes(None, False):
            if picon[n] == "md-human" and plabel[n] in list_heroes:
                if(plabel[node] == name and plabel[n] == name):
                    edge_value = 0
                else:
                    for edge in tlp.Graph.allEdges(SubGraph_hero, node):
                        if tlp.Graph.source(SubGraph_hero, edge) == n or tlp.Graph.target(SubGraph_hero, edge) == n:
                            edge_value = tlp.Graph.getEdgePropertiesValues(SubGraph_hero, edge)[
                                'value']
                            break
                heat_map.append((plabel[node], plabel[n], edge_value))
        # produce a csv  return it
        csvdata = io.StringIO()
        writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("group", "name", "val"))
    for n in heat_map:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=data_heatmap_marvel.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/temps")
def temps():
    # load graph data
    global nb_heroes
    list_heroes = []

    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0

    heroes = []
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            list_heroes.append(plabel[n])
            i = i + 1
        if(i == int(nb_heroes)):
            break
    # iterate in descending order (max to min)
    i = 0
    for n in list_heroes:
        heroes.append(n)
        i += 1
        if(i == int(nb_heroes)):
            break

    comics = {}
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-book-open":
            date = plabel[n].split()
            c = 0
            for b in date:
                if "(1" in b or "(2" in b:
                    date = re.sub("[()]", "", b)
                    c = c+1
                    break
            if(c == 0):
                date = 0
            try:
                int(date)
            except ValueError:
                date = 0
            if(int(date) != 0):
                voisins = list(tlp.Graph.getInOutNodes(g, n))
                for x in voisins:
                    if(plabel[x] in heroes):
                        if(date not in comics):
                            comics[date] = {plabel[x]: 1}
                        else:
                            if(plabel[x] in comics[date]):
                                comics[date][plabel[x]
                                             ] = comics[date][plabel[x]]+1
                            else:
                                comics[date][plabel[x]] = 1

    best_50 = []
    for n in sorted(comics):
        for m in sorted(comics[n]):
            best_50.append((n, m, comics[n][m]))
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")
    writer.writerow(("year", "name", "n"))
    for n in best_50:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=temps.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/nuage_data")
def nuage_data():
    # load graph data

    global hero
    global nb_heroes
    list_heroes = []

    heroes_graph = tlp.loadGraph('heroes_final.tlpb')
    hero_node = heroes_graph['viewLabel'].getNodesEqualTo(hero).next()

    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0

    heroes = []
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human" and plabel[n] != hero:
            list_heroes.append(plabel[n])
            i = i + 1
        if(i == int(nb_heroes)):
            break
    # iterate in descending order (max to min)
    i = 0
    for n in list_heroes:
        if(n != hero):
            heroes.append(n)
            i += 1
            if(i == int(nb_heroes)):
                break
    comics = {}
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-book-open":
            date = plabel[n].split()
            c = 0
            for b in date:
                if "(1" in b or "(2" in b:
                    date = re.sub("[()]", "", b)
                    c = c+1
                    break
            if(c == 0):
                date = 0
            try:
                int(date)
            except ValueError:
                date = 0
            if(int(date) != 0):
                voisins = list(tlp.Graph.getInOutNodes(g, n))
                if(hero_node in voisins):
                    for x in voisins:
                        if(plabel[x] in heroes and plabel[x] != hero):
                            if(plabel[x] not in comics):
                                comics[plabel[x]] = {
                                    "date": date, "degree_date": 1, "degree": 1}
                            else:
                                comics[plabel[x]
                                       ]["degree"] = comics[plabel[x]]["degree"]+1
                                if(date == comics[plabel[x]]["date"]):
                                    comics[plabel[x]]["degree_date"] = comics[plabel[x]
                                                                              ]["degree_date"]+1

    best_50 = []
    for n in sorted(comics):
        l = [n]
        for m in sorted(comics[n]):
            l.append(comics[n][m])
        best_50.append(tuple(l))
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")
    writer.writerow(("name", "x", "y", "z"))
    for n in best_50:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=nuage.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/scatter_data")
def scatter_data():
    # load graph data
    global best_heroes
    global perso
    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0

    comics = {}
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-book-open":
            date = plabel[n].split()
            c = 0
            for b in date:
                if "(1" in b or "(2" in b:
                    date = re.sub("[()]", "", b)
                    c = c+1
                    break
            if(c == 0):
                date = 0
            try:
                int(date)
            except ValueError:
                date = 0
            if(int(date) != 0):
                voisins = list(tlp.Graph.getInOutNodes(g, n))
                for x in voisins:
                    if(plabel[x] in best_heroes):
                        if(date not in comics):
                            comics[date] = {plabel[x]: 1}
                        else:
                            if(plabel[x] in comics[date]):
                                comics[date][plabel[x]
                                             ] = comics[date][plabel[x]]+1
                            else:
                                comics[date][plabel[x]] = 1

    best_50 = []
    for n in sorted(comics):
        ligne = [n]
        for m in best_heroes:
            if(m in comics[n]):
                ligne.append(comics[n][m])
            else:
                ligne.append(0)
        best_50.append(tuple(ligne))
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")
    entete = ["year"]
    for i in best_heroes:
        entete.append(i)
    writer.writerow(tuple(entete))
    for n in best_50:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=scatter.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/scatter", methods=['POST', 'GET'])
def scatter():

    global hero
    list_heroes = []
    global best_heroes
    if request.method == 'POST':
        hero = request.form.get('heroes')
    i = 0

    return render_template("scatter.html", title="Comparaison des courbes d'apparitions des heros avec "+str(hero), best_heroes=best_heroes, hero=hero)


@web_app.route("/courbe", methods=['POST', 'GET'])
def courbe():
    global nb_heroes
    if request.method == 'POST':
        nb_heroes = int(request.form.get('nb_heroes'))

    return render_template("courbe.html", title="Courbe des apparitions par année des heros")


@web_app.route("/nuage", methods=['POST', 'GET'])
def nuage():
    global hero
    global best_heroes
    global nb_heroes
    if request.method == 'POST':
        try:
            nb_heroes = int(request.form.get('nb_heroes'))
        except:
            pass

        try:
            hero = request.form.get('heroes')
        except:
            pass
    return render_template("nuage.html", title="Nuage de points de "+str(nb_heroes)+" voisins "+str(hero), best_heroes=best_heroes, hero=hero)


@web_app.route("/hist")
def hist():
    return render_template("hist.html", title="Histogramme des 10 personnages les plus publiés")


@web_app.route("/")
def accueil():

    return render_template("Accueil.html", title="Accueil")


@web_app.route("/get_top_50")
def get_top_50():
   # load graph data
    global hero
    heroes_graph = tlp.loadGraph('heroes.tlpb')
    node = heroes_graph['viewLabel'].getNodesEqualTo(hero).next()
    heroes_graph['viewSelection'].setAllNodeValue(False)
    heroes_graph['ViewSelection'][node] = True
    params = tlp.getDefaultPluginParameters('Reachable SubGraph', heroes_graph)
    params['distance'] = 1
    params['edge direction'] = 'all edges'
    heroes_graph.applyBooleanAlgorithm('Reachable SubGraph', params)
    # compute node degree
    metricprop = heroes_graph.getDoubleProperty("viewMetric")
    heroes_graph.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = heroes_graph.getStringProperty("viewIcon")
    plabel = heroes_graph.getStringProperty("viewLabel")
    best_50 = []
    i = 0
    # iterate in descending order (max to min)
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            best_50.append((plabel[n], metricprop[n]))
            i += 1
        if i == 50:
            break
    # produce a csv  return it
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("name", "val"))
    for n in best_50:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=get_top_50.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/barplot2")
def barplot2():
    # load graph data
    global nb_heroes
    list_heroes=[]

    g = tlp.loadGraph('marvel.tlpb')

    # compute node degree
    metricprop = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", metricprop)

    # get 10 characters with the highest Degree (most published)
    picon = g.getStringProperty("viewIcon")
    plabel = g.getStringProperty("viewLabel")
    i = 0


    heroes=[]
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-human":
            list_heroes.append(plabel[n])
            i = i + 1
        if(i == int(nb_heroes)):
            break
    # iterate in descending order (max to min)
    i=0
    for n in list_heroes:
        heroes.append(n)
        i+=1
        if(i== int(nb_heroes)):
            break


    comics={}
    for n in metricprop.getSortedNodes(None, False):
        if picon[n] == "md-book-open":
            date=plabel[n].split()
            c=0
            for b in date:
                if "(1" in b or "(2" in b:
                    date = re.sub("[()]","",b)
                    c=c+1
                    break
            if(c==0):
                date=0
            try:
                date=int(date)
            except ValueError:
                date=0
            if(int(date)!= 0):
                voisins = list(tlp.Graph.getInOutNodes(g,n))
                for x in voisins:
                    if(plabel[x] in heroes):
                        if(plabel[x] not in comics):
                            comics[plabel[x]]={"a":0,"b":0,"c":0,"d":0,"e":0}

                        comics[plabel[x]]["e"]=comics[plabel[x]]["e"]+1
                        if(date < 1960):
                            comics[plabel[x]]["a"]=comics[plabel[x]]["a"]+1
                        elif(1960<=date and date <1980):
                            comics[plabel[x]]["b"]=comics[plabel[x]]["b"]+1
                        elif(1980<=date and date <2000):
                            comics[plabel[x]]["c"]=comics[plabel[x]]["c"]+1
                        else:
                            comics[plabel[x]]["d"]=comics[plabel[x]]["d"]+1

    best_50=[]
    
    for n in sorted(comics):
        l=[n]
        for m in sorted(comics[n]):
            l.append(comics[n][m])
        best_50.append(tuple(l))
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")
    writer.writerow(("hero", "a","b","c","d","Total"))
    for n in best_50:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=barplot2.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@web_app.route("/barplot",methods=['POST','GET'])
def barplot():

    global hero
    global nb_heroes
    if request.method == 'POST':
        nb_heroes = request.form.get('nb_heroes')




    return render_template("barplot.html", title="Diagramme en bâtons des "+str(nb_heroes)+" les plus publiés par tranches d'années",best_heroes=best_heroes,hero=hero)

    # NE SURTOUT PAS MODIFIER OU DEPLACER, TOUT AJOUT DE CODE DOIT ETRE EFFECTUE AU DESSUS DE CES LIGNES
if __name__ == "__main__":
    #web_app.run(debug=True, host='0.0.0.0', port=5000)
    web_app.run(debug=True)
