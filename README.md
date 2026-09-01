Tener en cuenta el max_link_capacity/max_drones menor para lanzar los drones

1. Calcular camino más corto, guardar coste inicial
    Conexiones, restricciones de zona y restricciones conexión
    si no se consigue llegar al final en ningún camino, error

2. Tirar drones en función de max_link / max_drones
3. Adaptar en función del coste para el dron
a. Comprobar conexión capacidad nodo
    si tiene menos coste que el más corto, cambio de ruta
b. muevo el dron, actualizo su estado (movimiento elegido para ese turno, posición (tránsito/nodo), finalizado, id, camino)


Para cada dron:

    ¿Tiene un movimiento restricted pendiente?
        │
        ├── SÍ → completar movimiento
        │
        └── NO
             │
             ▼
       calcular siguiente movimiento
             │
             ▼
       ¿es restricted?
             │
        ┌────┴────┐
       SÍ         NO
        │           │
        ▼           ▼
 comprobar       comprobar
 capacidad       conexión
        │           │
        └─────┬─────┘
              ▼
          ¿conflicto?
           │       │
          NO      SÍ
           │       │
           ▼       ▼
         mover    recalcular
                    │
              ┌─────┴─────┐
             igual      diferente
               │            │
               ▼            ▼
             quieto       cambiar path


simulation():
- Crear registro de movimientos del turno
- Recorrer drones
- Para cada dron:
1. ¿Está en tránsito?
       │
       ├─ sí → completar
       │
       └─ no
           ↓
2. ¿Cuál es su siguiente nodo?
           ↓
3. ¿Es restricted?
       │
       ├─ sí → ¿hay capacidad futura?
       │          │
       │          ├─ sí → iniciar transit
       │          └─ no → resolver conflicto
       │
       └─ no → ¿conexión disponible?
                  │
                  ├─ sí → mover
                  └─ no → resolver conflicto
           ↓
4. guardar movimiento
           ↓
5. siguiente dron