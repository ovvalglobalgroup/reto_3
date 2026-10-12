# Reto 3 - Registros dinámicos académicos con listas enlazadas

Proyecto que implementa listas enlazadas simple, doble y circular desde cero, búsqueda recursiva, menús y persistencia CSV/JSON.

## Requisitos

- Python 3.9 o superior
- No requiere bibliotecas externas

## Ejecución

Desde la carpeta del proyecto, ejecutar:

```bash
py index.py
```


## Organización

```text
reto3_listas/
├── index.py
├── README.md
└── data/
    ├── inscritos.csv
    ├── historial.json
    └── grupos.json
```

El archivo `.py` contiene tres clases de nodos (`NodoSimple`, `NodoDoble`, `NodoCircular`), tres listas enlazadas (`ListaSimple`, `ListaDoble`, `ListaCircular`), las funciones CSV/JSON, la clase `SistemaAcademico`, los submenús y los reportes.

## Diseño de las tres estructuras

**Lista simple - estudiantes**

```text
inicio -> [001] -> [002] -> [003] -> None
```

Cada nodo almacena `id`, `nombres`, `correo` y una referencia `siguiente`. Se puede insertar al final, buscar, eliminar y mostrar estudiantes. Se mantiene una referencia `final` para enlazar eficientemente el nuevo nodo; la validación de ID único requiere una búsqueda.

**Lista doble - historial por semestre**

```text
None <- [2024-1] <-> [2024-2] <-> [2025-1] -> None
```

Cada nodo almacena `anio`, `term`, una colección de materias (cada materia contiene `cod`, `nombre` y `nota`) y referencias `anterior` y `siguiente`. La inserción conserva el orden `(anio, term)`; es posible recorrer hacia adelante y hacia atrás. Las materias son datos del semestre, **no una lista de nodos**.

**Lista circular - grupos de prácticas**

```text
           +----------------------------+
           |                            |
           v                            |
         [A] ---> [B] ---> [C] ---------+
                       actual ^
```

Cada nodo almacena `nombre_grupo`, `tutor`, `tema` y `siguiente`. El último siempre apunta al primero. El puntero `actual` representa el grupo que tiene el turno; `rotar(k)` lo avanza y `recorrer(n_vueltas)` permite mostrar el ciclo más de una vez.

## Recursividad obligatoria

`ListaCircular.buscar_recursivo(nombre_grupo)` usa una función anidada `visitar(nodo, pendientes)`:

```text
buscar_recursivo("B")
   visitar(A, 3)  -> no coincide
       visitar(B, 2)  -> coincide, retorna B
```

El **caso base** ocurre cuando `pendientes == 0` (se ha inspeccionado el ciclo completo) o cuando el nombre coincide. Reducir `pendientes` evita recursión infinita. Se contempla el límite de profundidad de recursión de Python para evitar una búsqueda peligrosa con muchísimos nodos.

## Persistencia

| Estructura | Formato | Justificación |
|---|---|---|
| Lista simple | CSV | Registros tabulares planos: `id,nombres,correo` |
| Lista doble | JSON | Un semestre puede incluir varias materias y notas |
| Lista circular | JSON | Conserva grupos y nombre del grupo que tiene el turno |

Las importaciones validan primero una estructura temporal para no borrar la información existente en caso de archivo inválido. Las clases también exponen `to_dict()` y `from_dict()`.

## Complejidad temporal

| Operación | Tiempo | Espacio adicional |
|---|---|---|
| Lista simple: insertar al final | O(n) | O(1) |
| Lista simple: buscar, eliminar, recorrer | O(n) | O(1) |
| Lista doble: insertar ordenado | O(n + m) | O(m) |
| Lista doble: buscar, eliminar | O(n) | O(1) |
| Lista doble: recorrer adelante/atrás | O(n) | O(1) |
| Lista circular: insertar | O(n) | O(n) |
| Lista circular: buscar recursivamente | O(n) | O(n) |
| Lista circular: eliminar | O(n) | O(1) |
| Lista circular: rotar k posiciones | O(1 + k mod n) | O(1) |
| Lista circular: recorrer v vueltas | O(n · v) | O(1) |
| Reporte top 3 | O(n · m) | O(1) |

Donde **n** representa la cantidad de nodos, **m** el máximo de materias por semestre, **k** los pasos de rotación y **v** las vueltas solicitadas. Las complejidades expresan el peor caso; la rotación supone n mayor que cero.

## Casos para la prueba

Los siguientes casos de prueba permiten verificar el funcionamiento de las tres listas enlazadas, la persistencia de datos y los reportes académicos. Las operaciones se realizan mediante el menú interactivo del programa:

1. **Inscritos**: agregar Ana, Luis y Liliana; buscar y eliminar Luis; mostrar; exportar CSV; limpiar; importar CSV y mostrar de nuevo
2. **Historial**: insertar 2025-1, 2024-2 y 2024-1 en ese orden; confirmar que quedan ordenados; recorrer en ambos sentidos; buscar; exportar JSON; limpiar; importar JSON
3. **Grupos**: agregar A, B y C; buscar B recursivamente; rotar dos pasos de A hasta C; recorrer dos vueltas; eliminar B; confirmar que el último nodo apunta al primero; exportar/importar JSON
4. **Reportes**: comprobar los tres promedios superiores, el grupo actual y la cantidad de inscritos
