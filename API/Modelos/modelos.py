#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Modulos y librerias
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Numeric, TIMESTAMP, String, UniqueConstraint, DATETIME 
from sqlalchemy.sql import func
from Servicios.numeraciones import (UserRole, EstadoPedido, MetodoPago, EstadoPago, TipoToken)
from Esquemas.esquemas_base import (UsuarioBase, CategoriaBase, ProductoBase, CarritoBase, CarritoItemBase, PedidoBase, PedidoItemBase, TokenRecuperacionBase)

"""
Modelos que representan las tablas de la base de datos.
Estos modelos definen la estructura de las tablas
y las relaciones entre ellas.
"""
#No es necesario comentar más, pues es igual a la base de datos.


#--- MODELO DE TABLA: Categoria ---
class Categoria(CategoriaBase, table=True):
    __tablename__ = "categorias"
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    productos: List["Producto"] = Relationship(back_populates="categoria")


#--- MODELO DE TABLA: Producto ---
class Producto(ProductoBase, table=True):
    __tablename__ = "productos"
    id_producto: Optional[int] = Field(default=None, primary_key=True)
    categoria: Optional[Categoria] = Relationship(back_populates="productos")
    carrito_items: List["CarritoItem"] = Relationship(back_populates="producto")
    pedido_items: List["PedidoItem"] = Relationship(back_populates="producto")


#--- MODELO DE TABLA: Usuario ---
class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    contrasena_hash: str = Field(max_length=255)
    rol: UserRole = Field(
        sa_column=Column(String(50)), 
        default=UserRole.CLIENTE
    )
    fecha_creacion: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, server_default=func.now())
    )
    carrito: Optional["Carrito"] = Relationship(
        back_populates="usuario", 
        sa_relationship_kwargs={'uselist': False, 'cascade': 'all, delete-orphan'}
    )
    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
    tokens: List["TokenRecuperacion"] = Relationship(back_populates="usuario")


#--- MODELO DE TABLA: Carrito ---
class Carrito(CarritoBase, table=True):
    __tablename__ = "carritos"
    id_carrito: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id_usuario", unique=True, index=True)
    fecha_modificacion: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    )
    usuario: "Usuario" = Relationship(back_populates="carrito")
    items: List["CarritoItem"] = Relationship(
        back_populates="carrito",
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )


#--- MODELO DE TABLA: CarritoItem ---
class CarritoItem(CarritoItemBase, table=True):
    __tablename__ = "carrito_items"
    __table_args__ = (UniqueConstraint("id_carrito", "id_producto", name="uq_producto_en_carrito"),)
    id_item_carrito: Optional[int] = Field(default=None, primary_key=True)
    carrito: "Carrito" = Relationship(back_populates="items")
    producto: "Producto" = Relationship(back_populates="carrito_items")


#--- MODELO DE TABLA: Pedido ---
class Pedido(PedidoBase, table=True):
    __tablename__ = "pedidos"
    id_pedido: Optional[int] = Field(default=None, primary_key=True)
    num_orden: str = Field(max_length=20, unique=True, index=True)
    total_pedido: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    estado_pedido: EstadoPedido = Field(
        sa_column=Column(String(50)),
        default=EstadoPedido.PENDIENTE
    )
    metodo_pago: MetodoPago = Field(
        sa_column=Column(String(50))
    )
    estado_pago: EstadoPago = Field(
        sa_column=Column(String(50)),
        default=EstadoPago.PENDIENTE
    )
    fecha_creacion: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, server_default=func.now())
    )
    usuario: Optional[Usuario] = Relationship(back_populates="pedidos")
    items: List["PedidoItem"] = Relationship(back_populates="pedido")


#--- MODELO DE TABLA: PedidoItem ---
class PedidoItem(PedidoItemBase, table=True):
    __tablename__ = "pedido_items"
    id_item_pedido: Optional[int] = Field(default=None, primary_key=True)
    precio_unitario_compra: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    pedido: Optional[Pedido] = Relationship(back_populates="items")
    producto: Optional[Producto] = Relationship(back_populates="pedido_items")


#--- MODELO DE TABLA: TokenRecuperacion ---
class TokenRecuperacion(TokenRecuperacionBase, table=True):
    __tablename__ = "tokens_recuperacion"
    id_token: Optional[int] = Field(default=None, primary_key=True)
    token_hash: str = Field(max_length=255, unique=True)
    tipo_token: TipoToken = Field(
        sa_column=Column(String(50))
    )
    fecha_expiracion: datetime = Field(sa_column=Column(DATETIME)) 
    fue_usado: bool = Field(default=False)
    usuario: Optional[Usuario] = Relationship(back_populates="tokens")


#--- MODELO DE TABLA: ConfiguracionSistema ---
class ConfiguracionSistema(SQLModel, table=True):
    __tablename__ = "configuracion_sistema"
    clave: str = Field(primary_key=True, max_length=50)
    valor: str = Field(max_length=255)