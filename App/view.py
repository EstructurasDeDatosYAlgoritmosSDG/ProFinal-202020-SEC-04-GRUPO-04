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


import sys
import config
from App import controller
from DISClib.ADT import stack
import timeit
assert config
from time import process_time
from DISClib.ADT import list as lt
from DISClib.ADT import orderedmap as om
from DISClib.ADT.graph import gr

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________
small = 'taxi-trips-wrvz-psew-subset-small.csv'
medium = 'taxi-trips-wrvz-psew-subset-medium.csv'
large = 'taxi-trips-wrvz-psew-subset-large.csv'

# ___________________________________________________
#  Menu principal
# ___________________________________________________

"""
Menu principal
"""

def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Inicializar Analizador")
    print("2- Cargar servicios")
    print("3- Top de compañias que más servicios prestaron")
    print("4- Top de compañias según el número de taxis")
    print('5- Total de taxis y compañias')
    print('6- Top de taxis con más puntos en una fecha')
    print('7- Top de taxis con más puntos en un rango de fechas')
    print('8- Buscar una ruta entre dos community areas')


while True:
    printMenu()
    inputs = int(input('Seleccione una opción para continuar\n>'))

    if int(inputs) == 1:
        t1_start = process_time() #tiempo inicial
        print('\nIniciando analizador...')
        analizer = controller.init()
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")
        
    elif int(inputs) == 2:
        t1_start = process_time() #tiempo inicial
        print('\nCargando los datos...')
        cont = controller.loadData(analizer, small)
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")

    elif int(inputs) == 3:
        cant_companias = int(input('\n¿Cuántas compañias quiere ver? '))
        print('')
        t1_start = process_time() #tiempo inicial
        lista = controller.topCompaniasServicios(cont, cant_companias)
        i = 1
        print('El top '+str(cant_companias)+' de compañias que más servicios prestaron son: \n')
        while i <= lt.size(lista):
            elemento = lt.getElement(lista, i)
            print(elemento[0])
            i += 1
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")

    elif int(inputs) == 4:
        cant_taxis = int(input('\n¿Cuántos taxis quiere ver? '))
        print('')
        t1_start = process_time() #tiempo inicial
        lista = controller.topCompaniasServicios(cont, cant_taxis)
        i = 1
        print('El top '+str(cant_taxis)+' de compañias que más taxis afiliados tienen son: \n')
        while i <= lt.size(lista):
            elemento = lt.getElement(lista, i)
            print(elemento[0])
            i += 1
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")
    
    elif int(inputs) == 5:
        t1_start = process_time() #tiempo inicial
        total = controller.totalTaxisCompanias(cont)
        print('\nEl total de taxis es de: '+str(total[0]))
        print('El total de compañias es de: '+str(total[1]))
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")

    elif int(inputs) == 6:
        cant_taxis = int(input('\n¿Cuántos taxis quiere ver? '))
        fecha = input('En que fecha los quiere ver? AAAA-MM-DD ')
        print('')
        t1_start = process_time() #tiempo inicial
        lista = controller.topTaxisPuntosFecha(cont, fecha, cant_taxis)
        i = 1
        print('El top '+str(cant_taxis)+' de taxis que más puntos tienen en esa fecha son: \n')
        while i <= lt.size(lista):
            elemento = lt.getElement(lista, i)
            print(elemento[0])
            i += 1
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")
    
    elif int(inputs) == 7:
        cant_taxis = int(input('\n¿Cuántos taxis quiere ver? '))
        fecha_inicio = input('¿Desde que fecha los quiere ver? AAAA-MM-DD ')
        fecha_final = input('¿Hasta que fecha los quiere ver? AAAA-MM-DD ')
        print('')
        t1_start = process_time() #tiempo inicial
        lista = controller.topTaxisPuntosRango(cont, fecha_inicio, fecha_final, cant_taxis)
        i = 1
        print('El top '+str(cant_taxis)+' de taxis que más puntos tienen en ese rango de fechas son: \n')
        while i <= lt.size(lista):
            elemento = lt.getElement(lista, i)
            print(elemento[0])
            i += 1
        t1_stop = process_time() #tiempo final
        print("\nTiempo de ejecución",t1_stop-t1_start,"segundos\n")

    elif int(inputs) == 8:
        origen = input('Escriba la identificación del community area de origen: ')
        destino = input('Escriba la identificación del community area de destino: ')
        horario_inicial = input('Escriba el horario desde que tiene disponibilidad (HH:MM): ')
        horario_final = input('Escriba el horario hasta cuando tiene disponibilidad (HH:MM): ')
        prueba = controller.buscarMejorHorario(cont, origen, destino, horario_inicial, horario_final)
        if prueba != None:
            print('El mejor horario para iniciar el viaje es: '+prueba[0])
            print('El tiempo que toma realizar este viaje es de: '+str(prueba[1]))
        else:
            print('No se ha encontrado ningún camino...')
    else:
        sys.exit(0)
sys.exit(0)
        
        
