#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerias y modulos
#Importa las clases base de SQLModel para definir los modelos.
from sqlmodel import SQLModel, Field
#Importa los tipos 'Optional' y 'List' para definir campos opcionales o listas.
from typing import Optional, List
#Importa 'Decimal' para manejar precios con precision.
from decimal import Decimal
#Importa 'datetime' para manejar fechas y horas.
from datetime import datetime
#Importa las enumeraciones (roles, estados) desde tu modulo de servicios.
from Servicios.numeraciones import (UserRole, EstadoPedido, MetodoPago, EstadoPago)
#Importa los modelos base (con los campos comunes) desde el archivo de esquemas base.
from .esquemas_base import (CategoriaBase, ProductoBase, UsuarioBase, CarritoBase, CarritoItemBase, PedidoBase, PedidoItemBase)


"""
Esquemas que la API utiliza para recibir y enviar datos.
Estos esquemas definen la estructura de los datos
en las solicitudes (POST, PATCH) y respuestas (GET) de la API.
"""
#Por si convulsionas agrego esto, pq mi profesor de WEB comento que se debia hacer asi la explicación


#--- Esquemas de Categoría ---
class CategoriaCreacion(CategoriaBase):
    pass

#Esquema para LEER una Categoria.
class CategoriaLectura(CategoriaBase):
    #Añade el id_categoria a los campos heredados, ya que este es generado por la BD.
    id_categoria: int

#Esquema para ACTUALIZAR una Categoria.
class CategoriaActualizacion(SQLModel):
    #Define nombre como opcional; solo se actualizara si se envia.
    nombre: Optional[str] = None
    #Define descripcion como opcional.
    descripcion: Optional[str] = None


# --- Esquemas de Producto ---
class ProductoCreacion(ProductoBase):
    pass

#Esquema para LEER un Producto.
class ProductoLectura(ProductoBase):
    id_producto: int

#Esquema para ACTUALIZAR un Producto.
class ProductoActualizacion(SQLModel):
    #Todos los campos son opcionales para permitir actualizaciones parciales.
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    esta_disponible: Optional[bool] = None
    id_categoria: Optional[int] = None
    maneja_stock: Optional[bool] = None
    cantidad_stock: Optional[int] = None

#Esquema para LEER un Producto con detalles de Categoria.
class ProductoLecturaConCategoria(ProductoLectura):
    categoria: Optional[CategoriaLectura] = None


#--- Esquemas de Usuario---
class UsuarioCreacion(UsuarioBase):
    contrasena: str

#Esquema para LEER un Usuario.
class UsuarioLectura(UsuarioBase):
    id_usuario: int
    fecha_creacion: datetime

#Esquema para ACTUALIZAR un Usuario.
class UsuarioActualizacion(SQLModel):
    #Define nombre_usuario como opcional.
    nombre_usuario: Optional[str] = None
    #Define email como opcional.
    email: Optional[str] = None
    #Define rol como opcional.
    rol: Optional[UserRole] = None


#--- Esquemas de CarritoItem ---
class CarritoItemCrear(SQLModel):
    id_producto: int
    #La cantidad de ese producto (por defecto 1).
    cantidad: int = 1
    #Notas opcionales para el producto (ej. "sin mayonesa").
    notas: Optional[str] = None

#Esquema para MOSTRAR un item en el carrito.
class CarritoItemLectura(CarritoItemBase):
    id_item_carrito: int
    producto: Optional[ProductoLectura] = None

#Esquema para ACTUALIZAR un item en el carrito.
class CarritoItemActualizar(SQLModel):
    cantidad: Optional[int] = None
    notas: Optional[str] = None

#--- Esquemas de Carrito (COMPLETADO) ---
class CarritoLectura(CarritoBase):
    id_carrito: int
    id_usuario: int
    fecha_modificacion: datetime
    items: List[CarritoItemLectura] = []

#--- Esquemas de Pedido (COMPLETADO) ---
class PedidoItemCreacion(SQLModel):
    id_producto: int
    cantidad: int
    notas: Optional[str] = None

#Esquema para CREAR un nuevo pedido.
class PedidoCreacion(PedidoBase):
    metodo_pago: MetodoPago
    items: List[PedidoItemCreacion]

#Esquema para MOSTRAR un item de pedido.
class PedidoItemLectura(PedidoItemBase):
    id_item_pedido: int
    precio_unitario_compra: Decimal
    producto: Optional[ProductoLectura] = None

#Esquema para MOSTRAR un pedido completo.
class PedidoLectura(PedidoBase):
    id_pedido: int
    #El numero de orden (ej. "BIT-001").
    num_orden: str
    #El costo total del pedido.
    total_pedido: Decimal
    #El estado actual del pedido (Pendiente, En Preparacion, etc.).
    estado_pedido: EstadoPedido
    #El metodo de pago registrado.
    metodo_pago: MetodoPago
    #El estado del pago (Pendiente, Pagado, etc.).
    estado_pago: EstadoPago
    #La fecha en que se creo el pedido.
    fecha_creacion: datetime
    #Muestra una lista de los items del pedido (anidada).
    items: List[PedidoItemLectura] = []

#Esquema para ACTUALIZAR un pedido.
class PedidoActualizar(SQLModel):
    estado_pedido: Optional[EstadoPedido] = None
    estado_pago: Optional[EstadoPago] = None


#--- Esquemas de Autenticación---
"""
Esquema para devolver el token de acceso
cuando un usuario inicia sesión.
"""
class Token(SQLModel):
    access_token: str
    token_type: str

#Esquema para los datos contenidos
class TokenData(SQLModel):
    username: Optional[str] = None
    rol: Optional[str] = None


#Esquema para que un cliente cree un pedido desde su carrito.
"""
Esquema simple para que un cliente cree un pedido
desde su carrito. El servidor se encarga de los items.
"""
class PedidoCrearDesdeCarrito(SQLModel):
    #El cliente solo necesita especificar el metodo de pago.
    metodo_pago: MetodoPago