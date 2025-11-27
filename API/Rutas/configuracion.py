#BITCAFE
#VERSION 1.0 (Control de Estado de Tienda)
#By: Angel A. Higuera

#Librerías y modulos
#Importa las clases y funciones de FastAPI: APIRouter, HTTPException, status y Depends.
from fastapi import APIRouter, HTTPException, status, Depends
#Importa la funcion 'select' de SQLModel.
from sqlmodel import select
#Importa la dependencia 'SessionDep' para la sesion de BD.
from Servicios.base_Datos import SessionDep
#Importa la funcion para obtener el usuario actual (seguridad).
from Servicios.seguridad import get_current_user
#Importa la enumeracion de roles de usuario.
from Servicios.numeraciones import UserRole
#Importa el modulo de modelos de la BD (tablas).
from Modelos import modelos
#Importa BaseModel de Pydantic para definir esquemas de datos.
from pydantic import BaseModel


router = APIRouter(prefix="/configuracion", tags=["Configuración del Sistema"])

# Esquema simple para la respuesta/entrada
class EstadoTienda(BaseModel):
    esta_abierto: bool
    mensaje: str = "La tienda está operando con normalidad."

# --- OBTENER ESTADO (Público o Protegido según prefieras) ---
# Lo dejamos público para que la App Cliente sepa si mostrar el menú o un aviso de "Cerrado"

@router.get("/estado-tienda", response_model=EstadoTienda)
def obtener_estado_tienda(session: SessionDep):
    #Buscamos la configuracion especifica "ESTADO_TIENDA" en la BD.
    config = session.get(modelos.ConfiguracionSistema, "ESTADO_TIENDA")
    
    #Si no existe configuracion previa en la BD.
    if not config:
        #Devuelve True por defecto (asume que la tienda esta ABIERTA).
        return EstadoTienda(esta_abierto=True)
    
    #Evalua si el valor guardado es "ABIERTO" para determinar el booleano.
    esta_abierto = (config.valor == "ABIERTO")
    #Devuelve el objeto con el estado calculado.
    return EstadoTienda(esta_abierto=esta_abierto)


# --- CAMBIAR ESTADO (Solo Staff/Admin) ---

@router.post("/cambiar-estado")
def cambiar_estado_tienda(
    nuevo_estado: bool, # True = Abierto, False = Cerrado
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #Verifica si el rol del usuario actual no es STAFF ni ADMIN.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        #Lanza un error 403 (Forbidden) si no tiene permisos.
        raise HTTPException(status_code=403, detail="No autorizado")
    
    #Determina la cadena de texto a guardar basandose en el booleano de entrada.
    valor_str = "ABIERTO" if nuevo_estado else "CERRADO"
    
    #Busca si ya existe el registro de configuracion en la BD.
    config = session.get(modelos.ConfiguracionSistema, "ESTADO_TIENDA")
    
    #Si la configuracion ya existe.
    if config:
        #Actualiza el valor de la configuracion existente.
        config.valor = valor_str
    #Si no existe la configuracion.
    else:
        #Crea una nueva instancia del modelo de configuracion.
        config = modelos.ConfiguracionSistema(clave="ESTADO_TIENDA", valor=valor_str)
        #Anade el nuevo objeto a la sesion para ser insertado.
        session.add(config)
        
    #Asegura que el objeto este anadido a la sesion (para actualizacion o creacion).
    session.add(config)
    #Confirma (guarda) la transaccion en la BD.
    session.commit()
    
    #Define el texto de respuesta para el usuario.
    estado_texto = "ABIERTA" if nuevo_estado else "CERRADA"
    #Devuelve un diccionario con el mensaje de confirmacion.
    return {"mensaje": f"La tienda ahora está {estado_texto}"}