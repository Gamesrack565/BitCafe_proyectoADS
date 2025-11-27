#BITCAFE
#VERSION 1.4
#By: Angel A. Higuera

from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime 
from Servicios.numeraciones import UserRole


class CategoriaBase(SQLModel):
    nombre: str = Field(index=True)
    descripcion: Optional[str] = None

class ProductoBase(SQLModel):
    nombre: str = Field(index=True)
    descripcion: Optional[str] = None
    precio: Decimal
    url_imagen: Optional[str] = None 
    esta_disponible: bool = Field(default=True)
    id_categoria: int = Field(foreign_key="categorias.id_categoria")
    maneja_stock: bool = Field(default=False)
    cantidad_stock: int = Field(default=0)

class UsuarioBase(SQLModel):
    nombre_usuario: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    rol: UserRole = Field(default=UserRole.CLIENTE)

class CarritoBase(SQLModel):
    pass 

class CarritoItemBase(SQLModel):
    cantidad: int = Field(default=1)
    notas: Optional[str] = None
    id_carrito: int = Field(foreign_key="carritos.id_carrito")
    id_producto: int = Field(foreign_key="productos.id_producto")


#--- Base para Pedido (MODIFICADA) ---
class PedidoBase(SQLModel):
    id_usuario: Optional[int] = Field(default=None, foreign_key="usuarios.id_usuario")
    # NUEVO CAMPO:
    tiempo_estimado: Optional[datetime] = None


class PedidoItemBase(SQLModel):
    id_pedido: int = Field(foreign_key="pedidos.id_pedido")
    id_producto: Optional[int] = Field(default=None, foreign_key="productos.id_producto")
    cantidad: int
    notas: Optional[str] = None

class TokenRecuperacionBase(SQLModel):
    id_usuario: int = Field(foreign_key="usuarios.id_usuario")