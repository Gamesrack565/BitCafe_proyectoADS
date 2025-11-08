#BITCAFE
#VERSION 1
#By: Angel A. Higuera

import enum

class UserRole(str, enum.Enum):
    CLIENTE = "cliente"
    STAFF = "staff"
    ADMIN = "admin"

class EstadoPedido(str, enum.Enum):
    PENDIENTE = "pendiente"
    PREPARACION = "preparacion"
    LISTO = "listo"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"

class MetodoPago(str, enum.Enum):
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    TARJETA = "tarjeta"

class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"

class TipoToken(str, enum.Enum):
    PASSWORD = "password"
    USUARIO = "usuario"