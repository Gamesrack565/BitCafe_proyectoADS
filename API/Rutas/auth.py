#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerías y módulos
#Importa las clases necesarias de FastAPI: APIRouter para crear rutas, Depends para inyección, HTTPException para errores, y status para códigos HTTP.
from fastapi import APIRouter, Depends, HTTPException, status
#Importa el formulario estándar de OAuth2 para recibir "username" y "password".
from fastapi.security import OAuth2PasswordRequestForm
#Importa la función 'select' de SQLModel para construir consultas SQL.
from sqlmodel import select
#Importa el 'SessionDep' (dependencia de sesión) desde el módulo de base de datos.
from Servicios.base_Datos import SessionDep
#Importa las funciones de seguridad: para chequear contraseñas, crear tokens y obtener el usuario actual.
from Servicios.seguridad import verificar_contrasena, crear_access_token, get_current_user
#Importa el módulo que contiene los modelos de la base de datos (tablas).
from Modelos import modelos
#Importa el módulo que contiene los esquemas Pydantic/SQLModel (para entrada/salida de API).
from Esquemas import esquemas

#Crea una instancia de APIRouter para definir las rutas de este archivo.
router = APIRouter()


"""
Endpoint de login. Recibe un formulario (username, password)
y devuelve un token de acceso.
"""
@router.post("/token", response_model=esquemas.Token, tags=["Autenticación"])
#Define la función para el login.
def login_por_medio_access_token(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    #1. Buscar al usuario por su nombre_usuario
    #Crea una consulta para seleccionar el usuario donde el 'nombre_usuario' coincida con el 'username' del formulario.
    consulta = select(modelos.Usuario).where(modelos.Usuario.nombre_usuario == form_data.username)
    #Ejecuta la consulta en la sesión y obtiene el primer resultado (o None).
    usuario = session.exec(consulta).first()
    
    #2. Verificar si el usuario existe y la contraseña es correcta
    #Comprueba si el usuario no fue encontrado O si la contraseña (verificada) es incorrecta.
    if not usuario or not verificar_contrasena(form_data.password, usuario.contrasena_hash):
        #Si la comprobación falla, lanza un error HTTP 401.
        raise HTTPException(
            #Estado no autorizado, imprime un mensaje de error.
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            #Añade el header requerido por el estándar OAuth2 para errores de login.
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    #3. Crear el token
    #Llama a la función de seguridad para generar un nuevo token de acceso.
    token_de_acceso = crear_access_token(
        #Define los datos que se guardarán dentro del token (el 'subject' es el username y su rol).
        data={"sub": usuario.nombre_usuario, "rol": usuario.rol}
    )
    
    #Devuelve el token de acceso y su tipo ("bearer") en el formato esperado por OAuth2.
    return {"access_token": token_de_acceso, "token_type": "bearer"}


"""
Endpoint protegido. Devuelve la información del usuario
autenticado actualmente.
"""
#Define un endpoint GET en "/me", que responderá con los datos del usuario (esquema UsuarioRead).
@router.get("/me", response_model=esquemas.UsuarioLectura, tags=["Autenticación"])
#Define la función. Su único parámetro es 'current_user', que se obtiene inyectando la dependencia 'get_current_user'.
def leer_sobre_mi(usuario: modelos.Usuario = Depends(get_current_user)):
    
    #Si 'get_current_user' tiene éxito (el token es válido), simplemente devuelve el objeto del usuario.
    return usuario