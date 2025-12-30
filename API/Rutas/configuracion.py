# BITCAFE - VERSION 1.3 (Auto-Reparación de JSON + Persistencia)
# By: Angel A. Higuera & Gemini Partner

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select
from Servicios.base_Datos import SessionDep
from Servicios.seguridad import get_current_user
from Servicios.numeraciones import UserRole
from Modelos import modelos
from pydantic import BaseModel
from typing import Dict
import json

router = APIRouter(prefix="/configuracion", tags=["Configuración del Sistema"])

# --- ESQUEMAS ---
class EstadoTienda(BaseModel):
    esta_abierto: bool
    mensaje: str = "La tienda está operando con normalidad."

class HorarioDia(BaseModel):
    inicio: str
    fin: str
    cerrado: bool

# ==========================================
# RUTAS DE ESTADO DE TIENDA (SWITCH MANUAL)
# ==========================================

@router.get("/estado-tienda", response_model=EstadoTienda)
def obtener_estado_tienda(session: SessionDep):
    config = session.get(modelos.ConfiguracionSistema, "ESTADO_TIENDA")
    if not config:
        return EstadoTienda(esta_abierto=True)
    esta_abierto = (config.valor == "ABIERTO")
    return EstadoTienda(esta_abierto=esta_abierto)

@router.post("/cambiar-estado")
def cambiar_estado_tienda(
    nuevo_estado: bool, 
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    valor_str = "ABIERTO" if nuevo_estado else "CERRADO"
    config = session.get(modelos.ConfiguracionSistema, "ESTADO_TIENDA")
    
    if config:
        config.valor = valor_str
    else:
        config = modelos.ConfiguracionSistema(clave="ESTADO_TIENDA", valor=valor_str)
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    estado_texto = "ABIERTA" if nuevo_estado else "CERRADA"
    return {"mensaje": f"La tienda ahora está {estado_texto}"}

# ==========================================
# GESTIÓN DE HORARIOS (CON REPARACIÓN AUTOMÁTICA)
# ==========================================

@router.get("/horarios")
def obtener_horarios(session: SessionDep):
    """Recupera horarios. Si están corruptos, los repara automáticamente."""
    
    # Horarios base por defecto
    horarios_defecto = {
        "Lunes": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
        "Martes": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
        "Miercoles": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
        "Jueves": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
        "Viernes": {"inicio": "09:00", "fin": "18:00", "cerrado": False}
    }

    config = session.get(modelos.ConfiguracionSistema, "HORARIOS_OPERACION")
    
    if not config:
        return horarios_defecto

    try:
        # Intentamos cargar el JSON de la base de datos
        return json.loads(config.valor)
    except Exception as e:
        # SI FALLA (tu error actual), reseteamos el valor en la BD para arreglarlo
        print(f"DEBUG: JSON Corrupto detectado. Reparando... {e}")
        config.valor = json.dumps(horarios_defecto)
        session.add(config)
        session.commit()
        return horarios_defecto

@router.post("/horarios")
def guardar_horarios(
    tabla_horarios: Dict[str, HorarioDia], 
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    """Guarda la tabla de horarios asegurando el formato JSON correcto."""
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Convertimos los objetos Pydantic a diccionarios puros
    dict_datos = {dia: info.dict() for dia, info in tabla_horarios.items()}
    datos_json = json.dumps(dict_datos)
    
    # Buscamos de forma segura
    statement = select(modelos.ConfiguracionSistema).where(modelos.ConfiguracionSistema.clave == "HORARIOS_OPERACION")
    config = session.exec(statement).first()
    
    if config:
        config.valor = datos_json
    else:
        config = modelos.ConfiguracionSistema(clave="HORARIOS_OPERACION", valor=datos_json)
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    return {"mensaje": "Horarios guardados correctamente", "data": dict_datos}