from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from enum import Enum

app = FastAPI(
    title="API de Gestión de Pedidos",
    description="API REST para registrar y gestionar pedidos",
    version="1.0"
)


# -------------------------
# Estados posibles
# -------------------------

class EstadoPedido(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    ENVIADO = "ENVIADO"
    CANCELADO = "CANCELADO"


# -------------------------
# Modelo para crear pedido
# -------------------------

class PedidoEntrada(BaseModel):
    producto: str = Field(min_length=1, max_length=100)
    cantidad: int = Field(ge=1, le=100)
    precio: float = Field(gt=0)
    cliente: str = Field(min_length=1, max_length=100)


# -------------------------
# Modelo completo del pedido
# -------------------------

class Pedido(PedidoEntrada):
    id: int
    estado: EstadoPedido


# -------------------------
# Modelo para cambiar estado
# -------------------------

class CambioEstado(BaseModel):
    nuevo_estado: EstadoPedido


# -------------------------
# Base de datos simulada
# -------------------------

pedidos: List[Pedido] = []
contador_id = 1


# -------------------------
# Endpoint principal
# -------------------------

@app.get("/")
def inicio():
    return {
        "mensaje": "API de Gestión de Pedidos funcionando correctamente"
    }


# -------------------------
# Crear pedido
# -------------------------

@app.post("/pedidos", response_model=Pedido, status_code=201)
def crear_pedido(datos: PedidoEntrada):

    global contador_id

    nuevo_pedido = Pedido(
        id=contador_id,
        producto=datos.producto,
        cantidad=datos.cantidad,
        precio=datos.precio,
        cliente=datos.cliente,
        estado=EstadoPedido.PENDIENTE
    )

    pedidos.append(nuevo_pedido)

    contador_id += 1

    return nuevo_pedido


# -------------------------
# Consultar todos los pedidos
# -------------------------

@app.get("/pedidos", response_model=List[Pedido])
def listar_pedidos():
    return pedidos


# -------------------------
# Consultar pedido por ID
# -------------------------

@app.get("/pedidos/{pedido_id}", response_model=Pedido)
def obtener_pedido(pedido_id: int):

    for pedido in pedidos:
        if pedido.id == pedido_id:
            return pedido

    raise HTTPException(
        status_code=404,
        detail="Pedido no encontrado"
    )


# -------------------------
# Cambiar estado del pedido
# -------------------------

@app.put("/pedidos/{pedido_id}/estado", response_model=Pedido)
def cambiar_estado(pedido_id: int, cambio: CambioEstado):

    pedido = None

    for p in pedidos:
        if p.id == pedido_id:
            pedido = p
            break

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    nuevo_estado = cambio.nuevo_estado

    # PENDIENTE -> CONFIRMADO o CANCELADO
    if pedido.estado == EstadoPedido.PENDIENTE:
        if nuevo_estado not in [
            EstadoPedido.CONFIRMADO,
            EstadoPedido.CANCELADO
        ]:
            raise HTTPException(
                status_code=400,
                detail="Transición de estado no permitida"
            )

    # CONFIRMADO -> ENVIADO o CANCELADO
    elif pedido.estado == EstadoPedido.CONFIRMADO:
        if nuevo_estado not in [
            EstadoPedido.ENVIADO,
            EstadoPedido.CANCELADO
        ]:
            raise HTTPException(
                status_code=400,
                detail="Transición de estado no permitida"
            )

    # ENVIADO no puede cambiar de estado
    elif pedido.estado == EstadoPedido.ENVIADO:
        raise HTTPException(
            status_code=400,
            detail="Un pedido enviado no puede cambiar de estado"
        )

    # CANCELADO no puede cambiar de estado
    elif pedido.estado == EstadoPedido.CANCELADO:
        raise HTTPException(
            status_code=400,
            detail="Un pedido cancelado no puede cambiar de estado"
        )

    pedido.estado = nuevo_estado

    return pedido