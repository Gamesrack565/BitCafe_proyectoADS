#BITCAFE
#VERSION 2.2 (Con Esquemas Manuales Nuevos)
#By: Angel A. Higuera

from sqlmodel import SQLModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from Servicios.numeraciones import (UserRole, EstadoPedido, MetodoPago, EstadoPago)
from .esquemas_base import (CategoriaBase, ProductoBase, UsuarioBase, CarritoBase, CarritoItemBase, PedidoBase, PedidoItemBase)


#--- Esquemas de Categoría ---
class CategoriaCreacion(CategoriaBase):
    pass

class CategoriaLectura(CategoriaBase):
    id_categoria: int

class CategoriaActualizacion(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


# --- Esquemas de Producto ---
class ProductoCreacion(ProductoBase):
    pass

class ProductoLectura(ProductoBase):
    id_producto: int

class ProductoActualizacion(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    esta_disponible: Optional[bool] = None
    id_categoria: Optional[int] = None
    maneja_stock: Optional[bool] = None
    cantidad_stock: Optional[int] = None

class ProductoLecturaConCategoria(ProductoLectura):
    categoria: Optional[CategoriaLectura] = None


#--- Esquemas de Usuario---
class UsuarioCreacion(UsuarioBase):
    contrasena: str

class UsuarioLectura(UsuarioBase):
    id_usuario: int
    fecha_creacion: datetime

class UsuarioActualizacion(SQLModel):
    nombre_usuario: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[UserRole] = None


#--- Esquemas de CarritoItem ---
class CarritoItemCrear(SQLModel):
    id_producto: int
    cantidad: int = 1
    notas: Optional[str] = None

class CarritoItemLectura(CarritoItemBase):
    id_item_carrito: int
    producto: Optional[ProductoLectura] = None

class CarritoItemActualizar(SQLModel):
    cantidad: Optional[int] = None
    notas: Optional[str] = None

#--- Esquemas de Carrito ---
class CarritoLectura(CarritoBase):
    id_carrito: int
    id_usuario: int
    fecha_modificacion: datetime
    items: List[CarritoItemLectura] = []


# --- NUEVOS ESQUEMAS PARA CAJA (MANUAL) ---
# 1. El item individual
class ItemPedidoManual(SQLModel):
    id_producto: int
    cantidad: int
    notas: Optional[str] = None

# 2. El paquete completo (Payload)
class PedidoManualCrear(SQLModel):
    items: List[ItemPedidoManual]
    total: Decimal # El total que muestra el frontend (para referencia o validación)
    metodo_pago: MetodoPago       # "efectivo" o "transferencia"
    referencia_pago: Optional[str] = None # Solo si es transferencia


#--- Esquemas de Pedido ---
class PedidoItemCreacion(SQLModel):
    id_producto: int
    cantidad: int
    notas: Optional[str] = None

class PedidoCreacion(PedidoBase):
    metodo_pago: MetodoPago
    items: List[PedidoItemCreacion]

class PedidoItemLectura(PedidoItemBase):
    id_item_pedido: int
    precio_unitario_compra: Decimal
    producto: Optional[ProductoLectura] = None

class PedidoLectura(PedidoBase):
    id_pedido: int
    num_orden: str
    total_pedido: Decimal
    estado_pedido: EstadoPedido
    metodo_pago: MetodoPago
    estado_pago: EstadoPago
    fecha_creacion: datetime
    mensaje_retraso: Optional[str] = None 
    items: List[PedidoItemLectura] = [] 

class PedidoActualizar(SQLModel):
    estado_pedido: Optional[EstadoPedido] = None
    estado_pago: Optional[EstadoPago] = None


#--- Esquemas de Autenticación---
class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Optional[str] = None
    rol: Optional[str] = None


#Esquema para crear desde carrito (App Cliente)
class PedidoCrearDesdeCarrito(SQLModel):
    metodo_pago: MetodoPago