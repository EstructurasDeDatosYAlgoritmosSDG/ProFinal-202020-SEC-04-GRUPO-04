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

import config as cf
from App import model
import csv

"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# __________________________________________________

def init():
    """
    Llama la funcion de inicializacion del modelo.
    """
    analyzer = model.newAnalizer()

    return analyzer


# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________

def loadData(analyzer, serviciosfile):
    """
    Carga los datos de los archivos CSV en el modelo
    """
    serviciosfile = cf.data_dir + serviciosfile
    input_file = csv.DictReader(open(serviciosfile, encoding="utf-8"),
                                delimiter=",")
    for servicio in input_file:
        model.agregarServicioCompanias(analyzer, servicio)
        model.agregarCompaniasTaxis(analyzer, servicio)
        model.agregarFechasArbol(analyzer, servicio)
        model.agregarCommunityArea(analyzer, servicio)
    print('\nCalculando los puntos de cada taxi...')
    model.calcularPuntos(analyzer)
    print('\nOrdenando las compañias...')
    model.ordenarListas(analyzer)
    print('\nOrdenando los taxis por la cantidad de puntos...')
    model.ordenarArbol(analyzer)
    return analyzer

# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________

def topCompaniasServicios(analizer, cant_companias):
    return model.topCompaniasServicios(analizer, cant_companias)

def topCompaniasTaxis(analizer, cant_taxis):
    return model.topCompaniasTaxis(analizer, cant_taxis)

def totalTaxisCompanias(analizer):
    return model.totalTaxisCompanias(analizer)

def topTaxisPuntosFecha(analizer, fecha, cant_taxis):
    return model.topTaxisPuntosFecha(analizer, fecha, cant_taxis)

def topTaxisPuntosRango(analizer, fecha_inicio, fecha_final, cant_taxis):
    return model.topTaxisPuntosRango(analizer, fecha_inicio, fecha_final, cant_taxis)

def buscarMejorHorario(analizer, origen, destino, horario_inicial, horario_final):
    return model.buscarMejorHorario(analizer, origen, destino, horario_inicial, horario_final)


