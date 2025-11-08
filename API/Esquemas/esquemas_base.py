#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#LIBRERIAS
#Importa las clases base SQLModel y Field para definir los modelos.
from sqlmodel import SQLModel, Field
#Importa el tipo 'Optional' para campos que pueden ser Nulos.
from typing import Optional
#Importa el tipo 'Decimal' para manejar los precios.
from decimal import Decimal
#Importar USERROLE para el manejo de los roles: ADMIN, CLIENTE y STAFF
from Servicios.numeraciones import UserRole


"""
Son las bases de los esquemas que definen los atributos comunes de las tablas en la base de datos.
Cada clase base hereda de SQLModel y define los campos que serán utilizados en los modelos de las tablas.
"""
#Por si convulsionas agrego esto, pq mi profesor de WEB comento que se debia hacer asi la explicación


#--- Base para Categoria ---
class CategoriaBase(SQLModel):
    nombre: str = Field(index=True)
    descripcion: Optional[str] = None

#--- Base para Producto ---
class ProductoBase(SQLModel):
    nombre: str = Field(index=True)
    descripcion: Optional[str] = None
    #Precio se define como Decimal, para mantener los valores de los precios.
    precio: Decimal
    esta_disponible: bool = Field(default=True)
    #Accede al id de la categoria a la que pertenece el producto.
    id_categoria: int = Field(foreign_key="categorias.id_categoria")
    maneja_stock: bool = Field(default=False)
    cantidad_stock: int = Field(default=0)

#--- Base para Usuario ---
class UsuarioBase(SQLModel):
    nombre_usuario: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    rol: UserRole = Field(default=UserRole.CLIENTE)

#--- Base para Carrito ---
class CarritoBase(SQLModel):
    pass 

#--- Base para CarritoItem ---
class CarritoItemBase(SQLModel):
    #Iniciamos el id por defecto en 1.
    cantidad: int = Field(default=1)
    notas: Optional[str] = None
    id_carrito: int = Field(foreign_key="carritos.id_carrito")
    id_producto: int = Field(foreign_key="productos.id_producto")


#--- Base para Pedido ---
class PedidoBase(SQLModel):
    id_usuario: Optional[int] = Field(default=None, foreign_key="usuarios.id_usuario")

#--- Base para PedidoItem ---
class PedidoItemBase(SQLModel):
    id_pedido: int = Field(foreign_key="pedidos.id_pedido")
    id_producto: Optional[int] = Field(default=None, foreign_key="productos.id_producto")
    cantidad: int
    notas: Optional[str] = None

#--- Base para TokenRecuperacion ---
class TokenRecuperacionBase(SQLModel):
    id_usuario: int = Field(foreign_key="usuarios.id_usuario")