from django.http import HttpResponse
from django.shortcuts import render
from anycluster.MapClusterer import MapClusterer
from django.conf import settings
from django.db.models.loading import get_model
from django.contrib.gis.geos import GEOSGeometry

import json


#load the gis
geoapp, geomodel = settings.ANYCLUSTER_GEODJANGO_MODEL.split('.')
geo_column_str = settings.ANYCLUSTER_COORDINATES_COLUMN
Gis = get_model(geoapp, geomodel)
geo_table = Gis._meta.db_table


def getGrid(request, zoom, gridSize=256):

    clusterer = MapClusterer(zoom, gridSize)

    grid = clusterer.gridCluster(request)
    print 'getGrid'
    return HttpResponse(json.dumps(
        grid
        ), content_type="application/json")


def getPins(request, zoom, gridSize):
    print 'getPins'
    clusterer = MapClusterer(zoom, gridSize)

    markers = clusterer.kmeansCluster(request)
    
   
    return HttpResponse(json.dumps(
        markers
        ), content_type="application/json")


def getClusterContent(request, zoom, gridSize):

    clusterer = MapClusterer(zoom, gridSize)

    entries = clusterer.getKmeansClusterContent(request)
    print 'getClusterContent'
    return render(request, 'anycluster/clusterPopup.html', {'entries':entries})



def loadAreaContent(request, zoom=1, gridSize=256):

    clusterer = MapClusterer(zoom, gridSize)

    params = clusterer.loadJson(request)

    filterstring = clusterer.constructFilterstring(params["filters"])

    geojson = params.get("geojson", None)

    geomfilterstring = clusterer.getGeomFilterstring(geojson)


    markers_qryset = Gis.objects.raw(
        '''SELECT * FROM "%s" WHERE %s %s;''' % (geo_table, geomfilterstring, filterstring)
    )
    
    print 'loadAreaContent'
    return markers_qryset
    

def getAreaContent(request, zoom, gridSize):

    markers = loadAreaContent(request, zoom, gridSize)
    print 'getAreaContent'
    return render(request, 'anycluster/clusterPopup.html', {'entries':markers})
