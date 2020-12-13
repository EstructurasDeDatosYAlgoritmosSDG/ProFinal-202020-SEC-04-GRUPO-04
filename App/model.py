"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import quicksort as qs
import datetime
from DISClib.ADT import minpq
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

def newAnalizer():

    analizer = {'companiasTaxis': None,
                'companiasServicios': None,
                'cantTaxis': None,
                'fechas': None,
                'communityAreas': None}

    analizer['companiasTaxis'] = lt.newList(datastructure='ARRAY_LIST', cmpfunction=compararCompanias)
    analizer['companiasServicios'] = lt.newList(datastructure='ARRAY_LIST', cmpfunction=compararCompanias)
    analizer['cantTaxis'] = m.newMap(numelements=500, comparefunction=compararTaxisId) #CREAR COMPARACION
    analizer['fechas'] = om.newMap(omaptype='BST', comparefunction=compareDates) #CREAR COMPARACION
    analizer['communityAreas'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=14000, comparefunction=compararCommunityAreas)

    return analizer

# Funciones para agregar informacion al grafo

def agregarCommunityArea(analizer, servicio):
    community_inicio = servicio['pickup_community_area']
    community_final = servicio['dropoff_community_area']
    tiempo = servicio['trip_seconds']
    if community_inicio != '' and community_final != '' and tiempo != '':
        aniadirCommunityArea(analizer, community_inicio)
        aniadirCommunityArea(analizer, community_final)
        hora_inicio = servicio['trip_start_timestamp']
        hora_inicio = hora_inicio[11:19]
        hora1 = hora_inicio[:2]
        minutos1 = hora_inicio[3:5]
        rango = determinarRango(hora1, minutos1)
        addConection(analizer, community_inicio, community_final, rango, tiempo)
    return analizer

def addConection(analizer, community_inicio, community_final, rango, tiempo):
    """
    Adiciona un arco entre dos community areas
    """
    arco = gr.getEdge(analizer['communityAreas'], community_inicio, community_final)
    if arco is None:
        gr.addEdge(analizer['communityAreas'],community_inicio, community_final, m.newMap(comparefunction=compararRangosHorarios))
    tabla1 = gr.getEdge(analizer['communityAreas'],community_inicio,community_final)
    tabla = tabla1['weight']
    if not m.contains(tabla, rango):
        m.put(tabla, rango, tiempo)
    else:
        promedio_inicial = m.get(tabla, rango)
        promedio_inicial = promedio_inicial['value']
        tiempo = float(tiempo)
        promedio_inicial = float(promedio_inicial)
        promedio_final = (promedio_inicial + tiempo)/2
        m.put(tabla, rango, promedio_final)
    tabla1['weight'] = tabla
    return analizer

def aniadirCommunityArea(analizer, communityId):
    """
    Adiciona una community area como un vertice de un grafo
    """
    if not gr.containsVertex(analizer['communityAreas'], communityId):
        gr.insertVertex(analizer['communityAreas'], communityId)
    return analizer

def agregarFechasArbol(analizer, servicio):
    fecha = servicio['trip_start_timestamp']
    fecha = fecha[:10]
    taxi_id = servicio['taxi_id']
    millas = servicio['trip_miles']
    dinero = servicio['trip_total']
    if not om.contains(analizer['fechas'], fecha):
        om.put(analizer['fechas'], fecha, lt.newList(cmpfunction=compararTaxisArbol))
    lista = om.get(analizer['fechas'], fecha)
    lista = lista['value']
    posicion = lt.isPresent(lista, taxi_id)
    if posicion == 0:
        lt.addLast(lista, [taxi_id,0,0,0,0])
        posicion = lt.size(lista)
    datos = lt.getElement(lista, posicion)
    if millas != '':
        datos[2] += float(millas)
    if dinero != '':
        datos[3] += float(dinero)
    datos[4] += 1
    om.put(analizer['fechas'], fecha, lista)
    return analizer

def agregarServicioCompanias(analizer, servicio):
    compania = servicio['company']
    posicion = lt.isPresent(analizer['companiasServicios'], compania)
    if posicion == 0:
        lt.addLast(analizer['companiasServicios'], [compania, 0])
        posicion = lt.size(analizer['companiasServicios'])
    tupla = lt.getElement(analizer['companiasServicios'], posicion)
    tupla[1] += 1
    return analizer

def agregarCompaniasTaxis(analizer, servicio):
    compania = servicio['company']
    taxi_id = servicio['taxi_id']
    posicion = lt.isPresent(analizer['companiasTaxis'], compania)
    if posicion == 0:
        l = lt.newList()
        lt.addLast(l, compania)
        lt.addLast(l,0)
        lt.addLast(analizer['companiasTaxis'], [compania, 0])
        posicion = lt.size(analizer['companiasTaxis'])
    tupla = lt.getElement(analizer['companiasTaxis'], posicion)
    esta_taxi = m.contains(analizer['cantTaxis'], taxi_id)
    if not esta_taxi:
        m.put(analizer['cantTaxis'], taxi_id, 0)
        tupla[1] += 1
    return analizer

# ==============================
# Funciones de consulta
# ==============================

def buscarMejorHorario(analizer, origen, destino, horario_inicial, horario_final):
    hora1 = horario_inicial[0:2]
    minutos1 = horario_inicial[3:]
    hora2 = horario_final[0:2]
    minutos2 = horario_final[3:]
    rango_inicial = determinarRango(hora1, minutos1)
    rango_final = determinarRango(hora2, minutos2)
    arco = gr.getEdge(analizer['communityAreas'], origen, destino)
    if arco != None:
        arco = arco['weight']
        ruta_mas_corta = 1000000000000000
        horario = ''
        if rango_final >= rango_inicial:
            i = rango_inicial
            while i <= rango_final:
                ruta = m.get(arco, i)
                ruta = ruta['value']
                if ruta < ruta_mas_corta:
                    ruta_mas_corta = ruta
                    horario = i
                i += 1
        else:
            i = rango_inicial
            while i <= 96:
                ruta = m.get(arco, i)
                ruta = ruta['value']
                if ruta < ruta_mas_corta:
                    ruta_mas_corta = ruta
                    horario = i
                i += 1
            i = 1
            while i <= rango_final:
                ruta = m.get(arco, i)
                ruta = ruta['value']
                if ruta < ruta_mas_corta:
                    ruta_mas_corta = ruta
                    horario = i
                i += 1
        horario = determinarHorario(horario)
        return horario, ruta_mas_corta
    else:
        return None

def topTaxisPuntosRango(analizer, fecha_inicio, fechas_final, cant_taxis):
    rango = om.keys(analizer['fechas'], fecha_inicio, fechas_final)
    top = lt.newList()
    iterador = it.newIterator(rango)
    while it.hasNext(iterador):
        fecha = it.next(iterador)
        fecha = om.get(analizer['fechas'], fecha)
        fecha = fecha['value']
        iterador2 = it.newIterator(fecha)
        i = 0
        while it.hasNext(iterador2) and i < cant_taxis:
            taxi = it.next(iterador2)
            lt.addLast(top, taxi)
            i += 1
    qs.quickSort(top, cmpPuntosTaxis)
    sublista = lt.subList(top, 1, cant_taxis)
    return sublista
        
def topTaxisPuntosFecha(analizer, fecha, cant_taxis):
    lista = om.get(analizer['fechas'], fecha)
    lista = lista['value']
    sublista = lt.subList(lista,1,cant_taxis)
    return sublista

def topCompaniasServicios(analizer, cant_companias):
    sub_lista = lt.subList(analizer['companiasServicios'], 1, cant_companias)
    return sub_lista

def topCompaniasTaxis(analizer, cant_taxis):
    sub_lista = lt.subList(analizer['companiasTaxis'], 1, cant_taxis)
    return sub_lista

def totalTaxisCompanias(analizer):
    totalTaxis = m.size(analizer['cantTaxis'])
    totalCompanias = lt.size(analizer['companiasServicios'])
    return totalTaxis, totalCompanias

# ==============================
# Funciones Helper
# ==============================

def ordenarListas(analizer):
    qs.quickSort(analizer['companiasServicios'], cmpCompaniasMasServicios)
    qs.quickSort(analizer['companiasTaxis'], cmpCompaniasMasServicios)
    return analizer

def ordenarArbol(analizer):
    llaves = om.keySet(analizer['fechas'])
    iterador = it.newIterator(llaves)
    while it.hasNext(iterador):
        fecha = it.next(iterador)
        lista = om.get(analizer['fechas'], fecha)
        lista = lista['value']
        qs.quickSort(lista, cmpPuntosTaxis)
        om.put(analizer['fechas'], fecha, lista)
    return analizer

def calcularPuntos(analizer):
    fechas = om.keySet(analizer['fechas'])
    iterador = it.newIterator(fechas)
    while it.hasNext(iterador):
        fecha = it.next(iterador)
        lista_taxis = om.get(analizer['fechas'], fecha)
        lista_taxis = lista_taxis['value']
        iterador2 = it.newIterator(lista_taxis)
        while it.hasNext(iterador2):
            taxi = it.next(iterador2)
            millas = taxi[2]
            dinero = taxi[3]
            servicios = taxi[4]
            calculo = 0
            if dinero != 0:
                calculo = (millas/dinero) * servicios
            taxi[1] = calculo
    return analizer

# ==============================
# Funciones de Comparacion
# ==============================

def cmpPuntosTaxis(taxi1, taxi2):
    return (taxi1[1] > taxi2[1])

def cmpCompaniasMasServicios (servicio1, servicio2):
    return (servicio1[1] > servicio2[1])

def compararTaxisId(keyname, productora):
    """
    Compara dos taxisId. El primero es una cadena
    y el segundo un entry de un map
    """
    authentry = me.getKey(productora)
    if (keyname == authentry):
        return 0
    elif (keyname > authentry):
      return 1
    else:
        return -1

def compararRangosHorarios(keyname, productora):
    """
    Compara dos taxisId. El primero es una cadena
    y el segundo un entry de un map
    """
    authentry = me.getKey(productora)
    if (keyname == authentry):
        return 0
    elif (keyname > authentry):
      return 1
    else:
        return -1

def compareDates(date1, date2):

    if (date1 == date2):
        return 0 
    elif (date1 > date2):
        return 1
    else: 
        return -1


def compararCommunityAreas(stop, keyvaluestop):
    """
    Compara dos community areas
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1

def compararCompanias(v1, v2):
    v2 = v2[0]
    if v1 == v2:
        return 0
    elif v1 > v2:
        return 1
    return -1

def compararTaxisArbol(v1, v2):
    v2 = v2[0]
    if v1 == v2:
        return 0
    elif v1 > v2:
        return 1
    return -1


# Funcion para determinar el rango
def determinarHorario(rango):
    # hora 00
    if rango == 1 :
        horario = '00:00 - 00:15'
    elif rango == 2 :
        horario = '00:15 - 00:30' 
    elif rango == 3 :
        horario = '00:30 - 00:45'
    elif rango == 4 :
        horario = '00:45 - 01:00'
    # hora 01
    elif rango == 5 :
        horario = '01:00 - 01:15'
    elif rango == 6 :
        horario = '01:15 - 01:30' 
    elif rango == 7 :
        horario = '01:30 - 01:45'
    elif rango == 8 :
        horario = '01:45 - 02:00'
    # hora 02
    elif rango == 9 :
        horario ='02:00 - 02:15'
    elif rango == 10 :
        horario = '02:15 - 02:30' 
    elif rango == 11 :
        horario = '02:30 - 02:45'
    elif rango == 12 :
        horario = '02:45 - 03:00'
    # hora 03
    elif rango == 13 :
        horario ='03:00 - 03:15'
    elif rango == 14 :
        horario = '03:15 - 03:30' 
    elif rango == 15 :
        horario = '03:30 - 03:45'
    elif rango == 16 :
        horario = '03:45 - 04:00'
    # hora 04
    elif rango == 17:
        horario ='04:00 - 04:15'
    elif rango == 18 :
        horario = '04:15 - 04:30' 
    elif rango == 19 :
        horario = '04:30 - 04:45'
    elif rango == 20 :
        horario = '04:45 - 05:00'
    # hora 05
    elif rango == 21:
        horario ='05:00 - 05:15'
    elif rango == 22 :
        horario = '05:15 - 05:30' 
    elif rango == 23 :
        horario = '05:30 - 05:45'
    elif rango == 24 :
        horario = '05:45 - 06:00'
    # hora 06
    elif rango == 25:
        horario ='06:00 - 06:15'
    elif rango == 26 :
        horario = '06:15 - 06:30' 
    elif rango == 27 :
        horario = '06:30 - 06:45'
    elif rango == 28 :
        horario = '06:45 - 07:00'
    # hora 07
    elif rango == 29:
        horario ='07:00 - 07:15'
    elif rango == 30 :
        horario = '07:15 - 07:30' 
    elif rango == 31 :
        horario = '07:30 - 07:45'
    elif rango == 32 :
        horario = '07:45 - 08:00'
    # hora 08
    elif rango == 33:
        horario ='08:00 - 08:15'
    elif rango == 34 :
        horario = '08:15 - 08:30' 
    elif rango == 35 :
        horario = '08:30 - 08:45'
    elif rango == 36 :
        horario = '08:45 - 09:00'
    # hora 09
    elif rango == 37:
        horario ='09:00 - 09:15'
    elif rango == 38 :
        horario = '09:15 - 09:30' 
    elif rango == 39 :
        horario = '09:30 - 09:45'
    elif rango == 40 :
        horario = '09:45 - 10:00'
    # hora 10
    elif rango == 41:
        horario ='10:00 - 10:15'
    elif rango == 42 :
        horario = '10:15 - 10:30' 
    elif rango == 43 :
        horario = '10:30 - 10:45'
    elif rango == 44 :
        horario = '10:45 - 11:00'
    # hora 11
    elif rango == 45:
        horario ='11:00 - 11:15'
    elif rango == 46 :
        horario = '11:15 - 11:30' 
    elif rango == 47 :
        horario = '11:30 - 11:45'
    elif rango == 48 :
        horario = '11:45 - 12:00'
    # hora 12
    elif rango == 49:
        horario ='12:00 - 12:15'
    elif rango == 50 :
        horario = '12:15 - 12:30' 
    elif rango == 51 :
        horario = '12:30 - 12:45'
    elif rango == 52 :
        horario = '12:45 - 13:00'
    # hora 13
    elif rango == 53:
        horario ='13:00 - 13:15'
    elif rango == 54 :
        horario = '13:15 - 13:30' 
    elif rango == 55 :
        horario = '13:30 - 13:45'
    elif rango == 56 :
        horario = '13:45 - 14:00'
    # hora 14 
    elif rango == 57: 
        horario ='14:00 - 14:15' 
    elif rango == 58: 
        horario = '14:15 - 14:30' 
    elif rango == 59 : 
        horario = '14:30 - 14:45' 
    elif rango == 60 : 
        horario = '14:45 - 15:00'
    # hora 15
    elif rango == 61: 
        horario ='15:00 - 15:15' 
    elif rango == 62: 
        horario = '15:15 - 15:30' 
    elif rango == 63 : 
        horario = '15:30 - 15:45' 
    elif rango == 64 : 
        horario = '15:45 - 16:00'
    # hora 16
    elif rango == 65: 
        horario ='16:00 - 16:15' 
    elif rango == 66: 
        horario = '16:15 - 16:30' 
    elif rango == 67 : 
        horario = '16:30 - 16:45' 
    elif rango == 68 : 
        horario = '16:45 - 17:00'
    # hora 17
    elif rango == 69: 
        horario ='17:00 - 17:15' 
    elif rango == 70: 
        horario = '17:15 - 17:30' 
    elif rango == 71 : 
        horario = '17:30 - 17:45' 
    elif rango == 72 : 
        horario = '17:45 - 18:00'
    # hora 18
    elif rango == 73: 
        horario ='18:00 - 18:15' 
    elif rango == 74: 
       horario = '18:15 - 18:30' 
    elif rango == 75 : 
        horario = '18:30 - 18:45' 
    elif rango == 76 :
        horario = '18:45 - 19:00'
    # hora 19
    elif rango == 77: 
        horario ='19:00 - 19:15' 
    elif rango == 78: 
        horario = '19:15 - 19:30' 
    elif rango == 79 : 
        horario = '19:30 - 19:45' 
    elif rango == 80 : 
        horario = '19:45 - 20:00'
    # hora 20
    elif rango == 81: 
        horario ='20:00 - 20:15' 
    elif rango == 82: 
        horario = '20:15 - 20:30' 
    elif rango == 83 : 
        horario = '20:30 - 20:45' 
    elif rango == 84 : 
        horario = '20:45 - 21:00'
    # hora 21
    elif rango == 85: 
        horario ='21:00 - 21:15' 
    elif rango == 86: 
        horario = '21:15 - 21:30' 
    elif rango == 87 : 
        horario = '21:30 - 21:45' 
    elif rango == 88 : 
        horario = '21:45 - 22:00'
    # hora 22
    elif rango == 89: 
        horario ='22:00 - 22:15' 
    elif rango == 90: 
        horario = '22:15 - 22:30' 
    elif rango == 91 : 
        horario = '22:30 - 22:45' 
    elif rango == 92 : 
        horario = '22:45 - 23:00'
    # hora 23
    elif rango == 93: 
        horario ='23:00 - 23:15' 
    elif rango == 94: 
        horario = '23:15 - 23:30' 
    elif rango == 95 : 
        horario = '23:30 - 23:45' 
    elif rango == 96 : 
        horario = '23:45 - 00:00'
    return horario

def determinarRango(hora1, minutos1):
    rango = 0
    # hora 00
    if hora1 == '00' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 1
    elif hora1 == '00' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 2 
    elif hora1 == '00' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 3
    elif hora1 == '00' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 4
    # hora 01
    elif hora1 == '01' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 5 
    elif hora1 == '01' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 6
    elif hora1 == '01' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 7 
    elif hora1 == '01' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 8 
    # hora 02
    elif hora1 == '02' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 9 
    elif hora1 == '02' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 10 
    elif hora1 == '02' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 11 
    elif hora1 == '02' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 12 
    # hora 03
    elif hora1 == '03' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 13 
    elif hora1 == '03' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 14 
    elif hora1 == '03' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 15 
    elif hora1 == '03' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 16 
    # hora 04
    elif hora1 == '04' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 17 
    elif hora1 == '04' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 18 
    elif hora1 == '04' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 19 
    elif hora1 == '04' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 20 
    # hora 05
    elif hora1 == '05' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 21 
    elif hora1 == '05' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 22 
    elif hora1 == '05' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 23 
    elif hora1 == '05' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 24
    # hora 06
    elif hora1 == '06' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 25 
    elif hora1 == '06' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 26 
    elif hora1 == '06' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 27 
    elif hora1 == '06' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 28 
    # hora 07
    elif hora1 == '07' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 29 
    elif hora1 == '07' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 30 
    elif hora1 == '07' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 31 
    elif hora1 == '07' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 32 
    # hora 08
    elif hora1 == '08' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 33 
    elif hora1 == '08' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 34 
    elif hora1 == '08' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 35 
    elif hora1 == '08' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 36 
    # hora 09
    elif hora1 == '09' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 37 
    elif hora1 == '09' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 38 
    elif hora1 == '09' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 39 
    elif hora1 == '09' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 40 
    # hora 10
    elif hora1 == '10' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 41 
    elif hora1 == '10' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 42 
    elif hora1 == '10' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 43 
    elif hora1 == '10' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 44 
    # hora 11
    elif hora1 == '11' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 45 
    elif hora1 == '11' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 46
    elif hora1 == '11' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 47 
    elif hora1 == '11' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 48 
    # hora 12
    elif hora1 == '12' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 49 
    elif hora1 == '12' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 50 
    elif hora1 == '12' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 51 
    elif hora1 == '12' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 52 
    # hora 13
    elif hora1 == '13' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 53 
    elif hora1 == '13' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 54 
    elif hora1 == '13' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 55 
    elif hora1 == '13' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 56 
    # hora 14
    elif hora1 == '14' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 57 
    elif hora1 == '14' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 58 
    elif hora1 == '14' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 59 
    elif hora1 == '14' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 60 
    # hora 15
    elif hora1 == '15' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 61 
    elif hora1 == '15' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 62 
    elif hora1 == '15' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 63 
    elif hora1 == '15' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 64 
    # hora 16
    elif hora1 == '16' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 65 
    elif hora1 == '16' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 66 
    elif hora1 == '16' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 67 
    elif hora1 == '16' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 68 
    # hora 17
    elif hora1 == '17' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 69 
    elif hora1 == '17' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 70 
    elif hora1 == '17' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 71 
    elif hora1 == '17' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 72 
    # hora 18
    elif hora1 == '18' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 73 
    elif hora1 == '18' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 74 
    elif hora1 == '18' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 75 
    elif hora1 == '18' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 76 
    # hora 19
    elif hora1 == '19' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 77 
    elif hora1 == '19' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 78 
    elif hora1 == '19' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 79 
    elif hora1 == '19' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 80 
    # hora 20
    elif hora1 == '20' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 81 
    elif hora1 == '20' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 82 
    elif hora1 == '20' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 83 
    elif hora1 == '20' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 84 
    # hora 21
    elif hora1 == '21' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 85 
    elif hora1 == '21' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 86 
    elif hora1 == '21' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 87 
    elif hora1 == '21' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 88 
    # hora 22
    elif hora1 == '22' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 89 
    elif hora1 == '22' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 90 
    elif hora1 == '22' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 91 
    elif hora1 == '22' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 92 
    # hora 23
    elif hora1 == '23' and int(minutos1) >= 0 and int(minutos1) < 15:
        rango = 93 
    elif hora1 == '23' and int(minutos1) >= 15 and int(minutos1) < 30:
        rango = 94 
    elif hora1 == '23' and int(minutos1) >= 30 and int(minutos1) < 45:
        rango = 95 
    elif hora1 == '23' and int(minutos1) >= 45 and int(minutos1) < 60:
        rango = 96
    return rango