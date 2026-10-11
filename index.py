# -*- coding: utf-8 -*-
"""Reto 3 en un solo archivo, equivalente a la version modular"""

import csv
import json
import sys
from pathlib import Path


#********************************************************************
# Clase que representa un nodo de la lista simple
#********************************************************************

class NodoSimple:

    # Método para inicializar un nodo simple
    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente


#********************************************************************
# Clase que representa un nodo de la lista doble
#********************************************************************

class NodoDoble:

    # Método para inicializar un nodo doble
    def __init__(self, valor, anterior=None, siguiente=None):
        self.valor = valor
        self.anterior = anterior
        self.siguiente = siguiente


#********************************************************************
# Clase que representa un nodo de la lista circular
#********************************************************************

class NodoCircular:

    # Método para inicializar un nodo circular
    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente


#********************************************************************
# Clase que representa la lista simple de estudiantes inscritos
#********************************************************************

class ListaSimple:

    # Método para inicializar la lista simple
    def __init__(self):
        self.inicio = None
        self.final = None
        self._size = 0

    # Método para comprobar si la estructura está vacía
    def is_empty(self):
        return self.inicio is None

    # Método para devolver la cantidad de estudiantes
    def size(self):
        return self._size

    # Método para registrar un estudiante al final
    def insertar_final(self, estudiante):
        if not isinstance(estudiante, dict):
            raise ValueError("El estudiante debe ser un diccionario")
        if any(estudiante.get(campo) is None for campo in ("id", "nombres", "correo")):
            raise ValueError("ID, nombres y correo son obligatorios")
        id_estudiante = str(estudiante.get("id", "")).strip()
        nombres = str(estudiante.get("nombres", "")).strip()
        correo = str(estudiante.get("correo", "")).strip()
        if not id_estudiante or not nombres or not correo:
            raise ValueError("ID, nombres y correo son obligatorios")
        if "@" not in correo or correo.startswith("@") or correo.endswith("@"):
            raise ValueError("El correo debe tener un formato valido")
        if self.buscar(id_estudiante) is not None:
            raise ValueError(f"El ID {id_estudiante} ya se encuentra inscrito")

        nuevo = NodoSimple({"id": id_estudiante, "nombres": nombres, "correo": correo})
        if self.is_empty():
            self.inicio = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self._size += 1
        return nuevo.valor

    # Método para buscar un estudiante por su ID
    def buscar(self, id_estudiante):
        actual = self.inicio
        while actual is not None:
            if actual.valor["id"] == str(id_estudiante).strip():
                return actual.valor
            actual = actual.siguiente
        return None

    # Método para eliminar un estudiante por su ID
    def eliminar(self, id_estudiante):
        anterior = None
        actual = self.inicio
        while actual is not None:
            if actual.valor["id"] == str(id_estudiante).strip():
                if anterior is None:
                    self.inicio = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual is self.final:
                    self.final = anterior
                actual.siguiente = None
                self._size -= 1
                return actual.valor
            anterior = actual
            actual = actual.siguiente
        return None

    # Método para recorrer estudiantes sin almacenar nodos en listas
    def recorrer(self):
        actual = self.inicio
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    # Método para vaciar la lista
    def limpiar(self):
        self.inicio = None
        self.final = None
        self._size = 0

    # Método para serializar los datos de los estudiantes
    def to_dict(self):
        return {"tipo": "lista_simple", "estudiantes": [dict(valor) for valor in self.recorrer()]}

    # Método para reconstruir nodos desde datos serializados
    @classmethod
    def from_dict(cls, datos):
        if not isinstance(datos, dict) or not isinstance(datos.get("estudiantes"), list):
            raise ValueError("Formato de estudiantes invalido")
        if datos.get("tipo", "lista_simple") != "lista_simple":
            raise ValueError("El archivo no corresponde a una lista simple")
        resultado = cls()
        for estudiante in datos["estudiantes"]:
            resultado.insertar_final(estudiante)
        return resultado

    # Método para exportar estudiantes en CSV
    def exportar_csv(self, ruta):
        return exportar_csv(self, ruta)

    # Método para importar estudiantes desde CSV
    def importar_csv(self, ruta):
        return importar_csv(self, ruta)


#********************************************************************
# Clase que representa el historial académico en lista doble
#********************************************************************

class ListaDoble:

    # Método para inicializar la lista doble
    def __init__(self):
        self.inicio = None
        self.final = None
        self._size = 0

    # Método para comprobar si la estructura está vacía
    def is_empty(self):
        return self.inicio is None

    # Método para devolver la cantidad de semestres
    def size(self):
        return self._size

    # Método para obtener la clave de un semestre
    @staticmethod
    def _clave(semestre):
        if isinstance(semestre, str):
            partes = semestre.strip().split("-")
            if len(partes) != 2 or not all(parte.isdigit() for parte in partes):
                raise ValueError("El semestre debe tener el formato AAAA-1")
            anio, term = map(int, partes)
        elif isinstance(semestre, (tuple, list)) and len(semestre) == 2:
            anio, term = semestre
        elif isinstance(semestre, dict):
            anio, term = semestre.get("anio"), semestre.get("term")
        else:
            raise ValueError("Semestre no valido")
        if type(anio) is not int or type(term) is not int or anio <= 0 or term <= 0:
            raise ValueError("El año y el periodo deben ser enteros positivos")
        return anio, term

    # Método para validar las materias y sus calificaciones
    @staticmethod
    def _normalizar_registro(registro):
        if not isinstance(registro, dict):
            raise ValueError("El registro debe ser un diccionario")
        anio, term = ListaDoble._clave(registro)
        materias = registro.get("materias")
        if not isinstance(materias, list) or not materias:
            raise ValueError("Se requiere al menos una materia por semestre")
        normalizadas = []  # Lista utilizada solo dentro del registro académico
        vistos = set()
        for materia in materias:
            if not isinstance(materia, dict):
                raise ValueError("Cada materia debe ser un diccionario")
            cod = str(materia.get("cod", "")).strip()
            nombre = str(materia.get("nombre", "")).strip()
            nota = materia.get("nota")
            if not cod or not nombre:
                raise ValueError("El codigo y el nombre de materia son obligatorios")
            if cod in vistos:
                raise ValueError(f"Codigo de materia repetido: {cod}")
            if isinstance(nota, bool) or not isinstance(nota, (int, float)) or not 0 <= nota <= 10:
                raise ValueError("La nota debe estar entre 0 y 10")
            normalizadas.append({"cod": cod, "nombre": nombre, "nota": float(nota)})
            vistos.add(cod)
        return {"anio": anio, "term": term, "materias": normalizadas}

    # Método para insertar un semestre ordenado por año y periodo
    def insertar_ordenado(self, registro_semestre):
        registro = self._normalizar_registro(registro_semestre)
        clave = self._clave(registro)
        actual = self.inicio
        while actual is not None and self._clave(actual.valor) < clave:
            actual = actual.siguiente
        if actual is not None and self._clave(actual.valor) == clave:
            raise ValueError(f"El semestre {clave[0]}-{clave[1]} ya existe")

        nuevo = NodoDoble(registro)
        if self.is_empty():
            self.inicio = nuevo
            self.final = nuevo
        elif actual is self.inicio:
            nuevo.siguiente = self.inicio
            self.inicio.anterior = nuevo
            self.inicio = nuevo
        elif actual is None:
            nuevo.anterior = self.final
            self.final.siguiente = nuevo
            self.final = nuevo
        else:
            nuevo.anterior = actual.anterior
            nuevo.siguiente = actual
            actual.anterior.siguiente = nuevo
            actual.anterior = nuevo
        self._size += 1
        return nuevo.valor

    # Método para buscar un semestre por año y periodo
    def buscar(self, semestre):
        clave = self._clave(semestre)
        actual = self.inicio
        while actual is not None:
            actual_clave = self._clave(actual.valor)
            if actual_clave == clave:
                return actual.valor
            if actual_clave > clave:
                break
            actual = actual.siguiente
        return None

    # Método para eliminar un semestre conservando enlaces dobles
    def eliminar(self, semestre):
        clave = self._clave(semestre)
        actual = self.inicio
        while actual is not None:
            if self._clave(actual.valor) == clave:
                if actual.anterior is None:
                    self.inicio = actual.siguiente
                else:
                    actual.anterior.siguiente = actual.siguiente
                if actual.siguiente is None:
                    self.final = actual.anterior
                else:
                    actual.siguiente.anterior = actual.anterior
                actual.anterior = None
                actual.siguiente = None
                self._size -= 1
                return actual.valor
            actual = actual.siguiente
        return None

    # Método para recorrer los semestres de antiguo a reciente
    def recorrer_adelante(self):
        actual = self.inicio
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    # Método para recorrer los semestres de reciente a antiguo
    def recorrer_atras(self):
        actual = self.final
        while actual is not None:
            yield actual.valor
            actual = actual.anterior

    # Método para calcular el promedio de un semestre
    @staticmethod
    def promedio(registro):
        return sum(materia["nota"] for materia in registro["materias"]) / len(registro["materias"])

    # Método para obtener los tres semestres con mayor promedio
    def top_tres_promedios(self):
        primero = segundo = tercero = None
        for semestre in self.recorrer_adelante():
            candidato = (self.promedio(semestre), semestre)
            if primero is None or candidato[0] > primero[0]:
                tercero, segundo, primero = segundo, primero, candidato
            elif segundo is None or candidato[0] > segundo[0]:
                tercero, segundo = segundo, candidato
            elif tercero is None or candidato[0] > tercero[0]:
                tercero = candidato
        for candidato in (primero, segundo, tercero):
            if candidato is not None:
                yield candidato

    # Método para vaciar el historial
    def limpiar(self):
        self.inicio = None
        self.final = None
        self._size = 0

    # Método para convertir el historial a datos JSON
    def to_dict(self):
        return {"tipo": "lista_doble", "semestres": [registro for registro in self.recorrer_adelante()]}

    # Método para reconstruir el historial desde datos JSON
    @classmethod
    def from_dict(cls, datos):
        if not isinstance(datos, dict) or datos.get("tipo", "lista_doble") != "lista_doble":
            raise ValueError("El archivo no corresponde a una lista doble")
        if not isinstance(datos.get("semestres"), list):
            raise ValueError("Formato de semestres invalido")
        resultado = cls()
        for registro in datos["semestres"]:
            resultado.insertar_ordenado(registro)
        return resultado

    # Método para exportar semestres en JSON
    def exportar_json(self, ruta):
        return exportar_json(self, ruta)

    # Método para importar semestres desde JSON
    def importar_json(self, ruta):
        return importar_json(self, ruta)


#********************************************************************
# Clase que representa los grupos de prácticas en lista circular
#********************************************************************

class ListaCircular:

    # Método para inicializar la lista circular
    def __init__(self):
        self.inicio = None
        self.final = None
        self.actual = None
        self._size = 0

    # Método para comprobar si la estructura está vacía
    def is_empty(self):
        return self.inicio is None

    # Método para devolver la cantidad de grupos
    def size(self):
        return self._size

    # Método para insertar un grupo y cerrar el ciclo
    def insertar(self, grupo):
        if not isinstance(grupo, dict):
            raise ValueError("El grupo debe ser un diccionario")
        if any(grupo.get(campo) is None for campo in ("nombre_grupo", "tutor", "tema")):
            raise ValueError("El nombre del grupo, tutor y tema son obligatorios")
        nombre = str(grupo.get("nombre_grupo", "")).strip()
        tutor = str(grupo.get("tutor", "")).strip()
        tema = str(grupo.get("tema", "")).strip()
        if not nombre or not tutor or not tema:
            raise ValueError("El nombre del grupo, tutor y tema son obligatorios")
        if self.buscar_recursivo(nombre) is not None:
            raise ValueError(f"El grupo {nombre} ya existe")
        nuevo = NodoCircular({"nombre_grupo": nombre, "tutor": tutor, "tema": tema})
        if self.is_empty():
            self.inicio = nuevo
            self.final = nuevo
            self.actual = nuevo
            nuevo.siguiente = nuevo
        else:
            nuevo.siguiente = self.inicio
            self.final.siguiente = nuevo
            self.final = nuevo
        self._size += 1
        return nuevo.valor

    # Método para buscar un grupo mediante recursividad acotada
    def buscar_recursivo(self, valor):
        if self.is_empty():
            return None
        # Se reserva margen para los marcos adicionales de Python
        if self._size >= sys.getrecursionlimit() - 80:
            raise RecursionError("Hay demasiados grupos para buscar recursivamente de forma segura")
        buscado = str(valor).strip()

        # Caso base: se recorrieron todos los nodos del ciclo
        def visitar(nodo, pendientes):
            if pendientes == 0:
                return None
            if nodo.valor["nombre_grupo"] == buscado:
                return nodo.valor
            return visitar(nodo.siguiente, pendientes - 1)

        return visitar(self.inicio, self._size)

    # Método para eliminar un grupo manteniendo cerrado el ciclo
    def eliminar(self, nombre_grupo):
        if self.is_empty():
            return None
        anterior = self.final
        nodo = self.inicio
        for _ in range(self._size):
            if nodo.valor["nombre_grupo"] == str(nombre_grupo).strip():
                if self._size == 1:
                    self.inicio = self.final = self.actual = None
                else:
                    anterior.siguiente = nodo.siguiente
                    if nodo is self.inicio:
                        self.inicio = nodo.siguiente
                    if nodo is self.final:
                        self.final = anterior
                    if nodo is self.actual:
                        self.actual = nodo.siguiente
                    self.final.siguiente = self.inicio
                nodo.siguiente = None
                self._size -= 1
                return nodo.valor
            anterior = nodo
            nodo = nodo.siguiente
        return None

    # Método para avanzar el turno actual k posiciones
    def rotar(self, k):
        if type(k) is not int or k < 0:
            raise ValueError("La rotacion debe ser un entero no negativo")
        if self.is_empty():
            return None
        for _ in range(k % self._size):
            self.actual = self.actual.siguiente
        return self.actual.valor

    # Método para recorrer una o más vueltas desde el turno actual
    def recorrer(self, n_vueltas=1):
        if type(n_vueltas) is not int or n_vueltas < 1:
            raise ValueError("Las vueltas deben ser un entero positivo")
        if self.is_empty():
            return
        nodo = self.actual
        for _ in range(self._size * n_vueltas):
            yield nodo.valor
            nodo = nodo.siguiente

    # Método para consultar el siguiente grupo en turno
    def siguiente_turno(self):
        return None if self.is_empty() else self.actual.valor

    # Método para recorrer el ciclo desde el nodo inicial
    def _recorrer_desde_inicio(self):
        nodo = self.inicio
        for _ in range(self._size):
            yield nodo.valor
            nodo = nodo.siguiente

    # Método para vaciar los grupos
    def limpiar(self):
        self.inicio = self.final = self.actual = None
        self._size = 0

    # Método para serializar los grupos y el turno actual
    def to_dict(self):
        return {
            "tipo": "lista_circular",
            "actual": None if self.actual is None else self.actual.valor["nombre_grupo"],
            "grupos": [dict(grupo) for grupo in self._recorrer_desde_inicio()],
        }

    # Método para reconstruir grupos y conservar el turno actual
    @classmethod
    def from_dict(cls, datos):
        if not isinstance(datos, dict) or datos.get("tipo", "lista_circular") != "lista_circular":
            raise ValueError("El archivo no corresponde a una lista circular")
        if not isinstance(datos.get("grupos"), list):
            raise ValueError("Formato de grupos invalido")
        resultado = cls()
        for grupo in datos["grupos"]:
            resultado.insertar(grupo)
        actual = datos.get("actual")
        if resultado.is_empty():
            if actual is not None:
                raise ValueError("No puede existir turno actual en una lista vacia")
        else:
            if not isinstance(actual, str):
                raise ValueError("Falta el nombre del grupo actual")
            nodo = resultado.inicio
            for _ in range(resultado._size):
                if nodo.valor["nombre_grupo"] == actual:
                    resultado.actual = nodo
                    break
                nodo = nodo.siguiente
            else:
                raise ValueError("El grupo actual no existe en el ciclo")
        return resultado

    # Método para exportar grupos en JSON
    def exportar_json(self, ruta):
        return exportar_json(self, ruta)

    # Método para importar grupos desde JSON
    def importar_json(self, ruta):
        return importar_json(self, ruta)



#********************************************************************
# Funciones de persistencia CSV para estudiantes inscritos
#********************************************************************

# Función para exportar los estudiantes a un archivo CSV
def exportar_csv(lista, ruta):
    if not isinstance(lista, ListaSimple):
        raise TypeError("CSV solo admite una ListaSimple")
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=("id", "nombres", "correo"))
        escritor.writeheader()
        for estudiante in lista.recorrer():
            escritor.writerow(estudiante)
    return destino

# Función para importar CSV sin alterar datos si existe un error
def importar_csv(lista, ruta):
    if not isinstance(lista, ListaSimple):
        raise TypeError("CSV solo admite una ListaSimple")
    temporal = ListaSimple()
    with Path(ruta).open("r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != ["id", "nombres", "correo"]:
            raise ValueError("Cabeceras CSV invalidas: se espera id,nombres,correo")
        for fila in lector:
            if None in fila:
                raise ValueError("Fila CSV con columnas adicionales")
            temporal.insertar_final(fila)
    lista.inicio = temporal.inicio
    lista.final = temporal.final
    lista._size = temporal._size
    return lista.size()


#********************************************************************
# Funciones de persistencia JSON para historial y grupos
#********************************************************************

# Función para exportar una estructura a un archivo JSON
def exportar_json(lista, ruta):
    if not isinstance(lista, (ListaDoble, ListaCircular)):
        raise TypeError("JSON admite ListaDoble y ListaCircular")
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as archivo:
        json.dump(lista.to_dict(), archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")
    return destino

# Función para importar JSON validando antes de reemplazar nodos
def importar_json(lista, ruta):
    if not isinstance(lista, (ListaDoble, ListaCircular)):
        raise TypeError("JSON admite ListaDoble y ListaCircular")
    with Path(ruta).open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    temporal = type(lista).from_dict(datos)
    lista.inicio = temporal.inicio
    lista.final = temporal.final
    lista._size = temporal._size
    if isinstance(lista, ListaCircular):
        lista.actual = temporal.actual
    return lista.size()


RUTA_DATOS = Path(__file__).resolve().parent / "data"

#********************************************************************
# Clase que representa el sistema de registros académicos
#********************************************************************

class SistemaAcademico:

    # Método para inicializar las tres listas enlazadas
    def __init__(self):
        self.inscritos = ListaSimple()
        self.historial = ListaDoble()
        self.grupos = ListaCircular()

    # Método para mostrar los reportes académicos
    def mostrar_reportes(self):
        print("\n=== REPORTES ACADEMICOS ===")
        print(f"Cantidad de inscritos: {self.inscritos.size()}")
        print("\nTop 3 promedios semestrales:")
        encontrado = False
        for posicion, (promedio, registro) in enumerate(self.historial.top_tres_promedios(), 1):
            encontrado = True
            print(f"  {posicion}. {registro['anio']}-{registro['term']} | Promedio: {promedio:.2f}/10")
        if not encontrado:
            print("  [Sin semestres registrados]")
        turno = self.grupos.siguiente_turno()
        print("\nGrupo en turno:")
        if turno is None:
            print("  [Sin grupos registrados]")
        else:
            print(f"  {turno['nombre_grupo']} | Tutor: {turno['tutor']} | Tema: {turno['tema']}")


# Función para leer un texto no vacío
def leer_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("El campo no puede estar vacio")


# Función para leer un número entero positivo
def leer_entero_positivo(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and int(valor) > 0:
            return int(valor)
        print("Ingrese un numero entero mayor que cero")


# Función para leer un número entero no negativo
def leer_entero_no_negativo(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit():
            return int(valor)
        print("Ingrese un numero entero igual o mayor que cero")


# Función para leer una nota válida de 0 a 10
def leer_nota(mensaje):
    while True:
        valor = input(mensaje).strip().replace(",", ".")
        try:
            nota = float(valor)
            if 0 <= nota <= 10:
                return nota
        except ValueError:
            pass
        print("Ingrese una nota entre 0 y 10")


# Función para mostrar los estudiantes inscritos
def mostrar_inscritos(lista):
    print("\n--- INSCRITOS ---")
    if lista.is_empty():
        print("  [Ningun estudiante inscrito]")
    else:
        for i, dato in enumerate(lista.recorrer(), 1):
            print(f"  {i}. {dato['nombres']} | ID: {dato['id']} | Correo: {dato['correo']}")
    print(f"Total: {lista.size()}")


# Función para mostrar un semestre con sus materias
def mostrar_semestre(registro):
    print(f"  Semestre {registro['anio']}-{registro['term']} | Promedio: {ListaDoble.promedio(registro):.2f}/10")
    for materia in registro["materias"]:
        print(f"    {materia['cod']} - {materia['nombre']} | Nota: {materia['nota']:.2f}")


# Función para mostrar los grupos en su rotación actual
def mostrar_grupos(lista, vueltas=1):
    print(f"\n--- GRUPOS / {vueltas} VUELTA(S) ---")
    if lista.is_empty():
        print("  [Ningun grupo registrado]")
        return
    for i, grupo in enumerate(lista.recorrer(vueltas), 1):
        marca = " <- ACTUAL" if i == 1 else ""
        print(f"  {i}. {grupo['nombre_grupo']} | Tutor: {grupo['tutor']} | Tema: {grupo['tema']}{marca}")
    print("  El ultimo grupo enlaza nuevamente con el primero")


# Función para mostrar y procesar el módulo de inscritos
def menu_inscritos(sistema):
    while True:
        print("\n" + "=" * 59)
        print(" INSCRITOS - LISTA SIMPLE")
        print("=" * 59 + "\n")
        print("1. Agregar estudiante")
        print("2. Eliminar por ID")
        print("3. Buscar por ID")
        print("4. Mostrar inscritos")
        print("5. Exportar CSV")
        print("6. Limpiar lista")
        print("7. Importar CSV")
        print("8. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        try:
            if opcion == "1":
                # Validar el ID antes de solicitar los demás datos
                id_estudiante = leer_texto("ID: ")
                existente = sistema.inscritos.buscar(id_estudiante)
                if existente is not None:
                    print(f"ADVERTENCIA: El ID {id_estudiante} ya está registrado a nombre de {existente['nombres']}")
                    print("No se agregó el estudiante porque el ID está duplicado")
                    print("Seleccione nuevamente Agregar estudiante e ingrese un ID diferente")
                    continue

                dato = {
                    "id": id_estudiante,
                    "nombres": leer_texto("Nombres: "),
                    "correo": leer_texto("Correo: "),
                }
                sistema.inscritos.insertar_final(dato)
                print("Estudiante registrado correctamente")
            elif opcion == "2":
                eliminado = sistema.inscritos.eliminar(leer_texto("ID a eliminar: "))
                print("Estudiante eliminado" if eliminado else "No se encontro ese ID")
            elif opcion == "3":
                encontrado = sistema.inscritos.buscar(leer_texto("ID a buscar: "))
                print(f"Encontrado: {encontrado['nombres']} | {encontrado['correo']}" if encontrado else "No se encontro ese ID")
            elif opcion == "4":
                mostrar_inscritos(sistema.inscritos)
            elif opcion == "5":
                ruta = sistema.inscritos.exportar_csv(RUTA_DATOS / "inscritos.csv")
                print(f"Exportacion completada: {ruta}")
            elif opcion == "6":
                sistema.inscritos.limpiar()
                print("Lista de inscritos vaciada")
            elif opcion == "7":
                total = sistema.inscritos.importar_csv(RUTA_DATOS / "inscritos.csv")
                print(f"Importacion completada: {total} estudiantes")
            elif opcion == "8":
                return
            else:
                print("Opcion no valida, ingrese un numero del 1 al 8")
        except (OSError, ValueError, RecursionError) as error:
            print(f"ERROR: {error}")


# Función para mostrar y procesar el módulo de historial
def menu_historial(sistema):
    while True:
        print("\n" + "=" * 59)
        print(" HISTORIAL - LISTA DOBLE")
        print("=" * 59 + "\n")
        print("1. Agregar semestre ordenado")
        print("2. Eliminar semestre")
        print("3. Buscar semestre")
        print("4. Recorrer adelante")
        print("5. Recorrer atras")
        print("6. Exportar JSON")
        print("7. Limpiar historial")
        print("8. Importar JSON")
        print("9. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        try:
            if opcion == "1":
                anio = leer_entero_positivo("Anio: ")
                term = leer_entero_positivo("Periodo (1, 2, ...): ")
                cantidad = leer_entero_positivo("Cantidad de materias: ")
                materias = []  # Las materias pertenecen al valor del semestre, no almacenan nodos
                for i in range(cantidad):
                    print(f"Materia {i + 1}")
                    materias.append({
                        "cod": leer_texto("  Codigo: "),
                        "nombre": leer_texto("  Nombre: "),
                        "nota": leer_nota("  Nota (0 a 10): "),
                    })
                sistema.historial.insertar_ordenado({"anio": anio, "term": term, "materias": materias})
                print(f"Semestre {anio}-{term} insertado en orden")
            elif opcion == "2":
                eliminado = sistema.historial.eliminar(leer_texto("Semestre (AAAA-1): "))
                print("Semestre eliminado" if eliminado else "Semestre no encontrado")
            elif opcion == "3":
                encontrado = sistema.historial.buscar(leer_texto("Semestre (AAAA-1): "))
                mostrar_semestre(encontrado) if encontrado else print("Semestre no encontrado")
            elif opcion in ("4", "5"):
                print("\n--- HISTORIAL ACADEMICO ---")
                recorrido = sistema.historial.recorrer_adelante() if opcion == "4" else sistema.historial.recorrer_atras()
                encontrado = False
                for semestre in recorrido:
                    mostrar_semestre(semestre)
                    encontrado = True
                if not encontrado:
                    print("  [Sin semestres registrados]")
            elif opcion == "6":
                ruta = sistema.historial.exportar_json(RUTA_DATOS / "historial.json")
                print(f"Exportacion completada: {ruta}")
            elif opcion == "7":
                sistema.historial.limpiar()
                print("Historial vaciado")
            elif opcion == "8":
                total = sistema.historial.importar_json(RUTA_DATOS / "historial.json")
                print(f"Importacion completada: {total} semestres")
            elif opcion == "9":
                return
            else:
                print("Opcion no valida, ingrese un numero del 1 al 9")
        except (OSError, ValueError, RecursionError) as error:
            print(f"ERROR: {error}")


# Función para mostrar y procesar el módulo circular
def menu_grupos(sistema):
    while True:
        print("\n" + "=" * 59)
        print(" GRUPOS - LISTA CIRCULAR")
        print("=" * 59 + "\n")
        print("1. Agregar grupo")
        print("2. Eliminar grupo")
        print("3. Buscar grupo recursivamente")
        print("4. Rotar k posiciones")
        print("5. Recorrer vueltas")
        print("6. Exportar JSON")
        print("7. Limpiar grupos")
        print("8. Importar JSON")
        print("9. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        try:
            if opcion == "1":
                grupo = {
                    "nombre_grupo": leer_texto("Nombre del grupo: "),
                    "tutor": leer_texto("Tutor: "),
                    "tema": leer_texto("Tema: "),
                }
                sistema.grupos.insertar(grupo)
                print("Grupo agregado al ciclo")
            elif opcion == "2":
                eliminado = sistema.grupos.eliminar(leer_texto("Nombre del grupo a eliminar: "))
                print("Grupo eliminado y ciclo conservado" if eliminado else "Grupo no encontrado")
            elif opcion == "3":
                encontrado = sistema.grupos.buscar_recursivo(leer_texto("Nombre del grupo a buscar: "))
                print(f"Encontrado: {encontrado['nombre_grupo']} | {encontrado['tutor']} | {encontrado['tema']}" if encontrado else "Grupo no encontrado")
            elif opcion == "4":
                turno = sistema.grupos.rotar(leer_entero_no_negativo("Cuantas posiciones rotar: "))
                print(f"Turno actual: {turno['nombre_grupo']}" if turno else "No existen grupos")
            elif opcion == "5":
                mostrar_grupos(sistema.grupos, leer_entero_positivo("Numero de vueltas: "))
            elif opcion == "6":
                ruta = sistema.grupos.exportar_json(RUTA_DATOS / "grupos.json")
                print(f"Exportacion completada: {ruta}")
            elif opcion == "7":
                sistema.grupos.limpiar()
                print("Grupos vaciados")
            elif opcion == "8":
                total = sistema.grupos.importar_json(RUTA_DATOS / "grupos.json")
                print(f"Importacion completada: {total} grupos")
            elif opcion == "9":
                return
            else:
                print("Opcion no valida, ingrese un numero del 1 al 9")
        except (OSError, ValueError, RecursionError) as error:
            print(f"ERROR: {error}")


# Función para iniciar el menú principal del reto
def initialize_menu():
    sistema = SistemaAcademico()
    try:
        while True:
            print("\n" + "=" * 59)
            print(" REGISTROS DINAMICOS ACADEMICOS CON PERSISTENCIA")
            print("=" * 59 + "\n")
            print("1. Inscritos - lista simple")
            print("2. Historial academico - lista doble")
            print("3. Grupos de practicas - lista circular")
            print("4. Reportes")
            print("5. Salir")
            opcion = input("Seleccione una opcion: ").strip()
            if opcion == "1":
                menu_inscritos(sistema)
            elif opcion == "2":
                menu_historial(sistema)
            elif opcion == "3":
                menu_grupos(sistema)
            elif opcion == "4":
                sistema.mostrar_reportes()
            elif opcion == "5":
                print("Programa finalizado")
                break
            else:
                print("Opcion no valida, ingrese un numero del 1 al 5")
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado por el usuario")


if __name__ == "__main__":
    initialize_menu()
