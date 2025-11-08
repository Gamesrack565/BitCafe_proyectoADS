#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerias y modulos
#Importa las clases de FastAPI: APIRouter, HTTPException, status y Depends.
from fastapi import APIRouter, HTTPException, status, Depends
#Importa la funcion 'select' de SQLModel para crear consultas.
from sqlmodel import select
#Importa el tipo 'List' (aunque no se usa en este archivo).
from typing import List
#Importa la dependencia 'SessionDep' para la sesion de BD.
from Servicios.base_Datos import SessionDep
#Importa la funcion para hashear contraseñas y la dependencia de admin.
from Servicios.seguridad import get_hash_contrasena, get_current_admin_user
#Importa la enumeracion 'UserRole' para asignar roles.
from Servicios.numeraciones import UserRole
#Importa los modelos de la BD (tablas).
from Modelos import modelos
#Importa los esquemas (Pydantic).
from Esquemas import esquemas

#Crea una nueva instancia de APIRouter.
router = APIRouter()


"""
Endpoint PÚBLICO para registrar un nuevo usuario.
Los usuarios creados aquí SIEMPRE serán 'cliente'.
"""
@router.post("/", 
             response_model=esquemas.UsuarioLectura, 
             status_code=status.HTTP_201_CREATED,
             tags=["Usuarios (Público)"])
def crear_usuario(usuario_in: esquemas.UsuarioCreacion, session: SessionDep):
    # 1. Verificar si el nombre de usuario ya existe
    #Crea una consulta para buscar un usuario con el mismo nombre.
    statement_user = select(modelos.Usuario).where(modelos.Usuario.nombre_usuario == usuario_in.nombre_usuario)
    #Si la ejecucion de la consulta devuelve un resultado.
    if session.exec(statement_user).first():
        #Lanza un error 400 (Bad Request) indicando que el nombre esta en uso.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está en uso")
        
    # 2. Verificar si el email ya existe
    #Crea una consulta para buscar un usuario con el mismo email.
    statement_email = select(modelos.Usuario).where(modelos.Usuario.email == usuario_in.email)
    #Si la ejecucion de la consulta devuelve un resultado.
    if session.exec(statement_email).first():
        #Lanza un error 400 (Bad Request) indicando que el email esta en uso.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    # 3. Hashear la contraseña
    #Llama a la funcion de seguridad para convertir la contraseña de texto plano a un hash.
    hash_contrasena = get_hash_contrasena(usuario_in.contrasena)
    
    # 4. Crear el objeto Usuario
    #Crea una instancia del modelo de BD 'Usuario' con los datos validados.
    db_usuario = modelos.Usuario(
        #Asigna el nombre de usuario de la entrada.
        nombre_usuario=usuario_in.nombre_usuario,
        #Asigna el email de la entrada.
        email=usuario_in.email,
        #Asigna la contraseña *hasheada*.
        contrasena_hash=hash_contrasena,
        #¡CAMBIO IMPORTANTE! Asigna forzosamente el rol de 'CLIENTE'.
        rol=UserRole.CLIENTE 
    )
    
    #Anade el nuevo objeto de usuario a la sesion.
    session.add(db_usuario)
    #Confirma (guarda) la transaccion en la BD.
    session.commit()
    #Refresca el objeto para obtener el ID asignado por la BD.
    session.refresh(db_usuario)
    
    # 5. Crear el carrito vacío
    #Crea una instancia de 'Carrito' asociada al ID del usuario recien creado.
    db_carrito = modelos.Carrito(id_usuario=db_usuario.id_usuario)
    #Anade el carrito a la sesion.
    session.add(db_carrito)
    #Confirma (guarda) el carrito en la BD.
    session.commit()
    
    #Devuelve el objeto de usuario recien creado.
    return db_usuario


"""
Endpoint PROTEGIDO (Solo Admin) para crear usuarios 'staff' o 'admin'.
El rol se toma del body de la petición.
"""

@router.post("/crear-especial", response_model=esquemas.UsuarioLectura, status_code=status.HTTP_201_CREATED, tags=["Usuarios (Admin)"])
def crear_staff_o_admin_user(
    usuario_in: esquemas.UsuarioCreacion, 
    session: SessionDep,
    admin_user: modelos.Usuario = Depends(get_current_admin_user)
):
    #1. Verificar si el nombre de usuario ya existe
    #Crea una consulta para buscar un usuario con el mismo nombre.
    statement_user = select(modelos.Usuario).where(modelos.Usuario.nombre_usuario == usuario_in.nombre_usuario)
    #Si la ejecucion de la consulta devuelve un resultado.
    if session.exec(statement_user).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está en uso")
        
    #2. Verificar si el email ya existe
    #Crea una consulta para buscar un usuario con el mismo email.
    statement_email = select(modelos.Usuario).where(modelos.Usuario.email == usuario_in.email)
    #Si la ejecucion de la consulta devuelve un resultado.
    if session.exec(statement_email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    #Valida que el rol enviado sea 'STAFF' o 'ADMIN'.
    if usuario_in.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Solo se pueden crear usuarios STAFF o ADMIN desde este endpoint")

    
    #3. Hashear la contraseña
    #Llama a la funcion de seguridad para hashear la contraseña.
    hash_contrasena = get_hash_contrasena(usuario_in.contrasena)
    
    #4. Crear el objeto Usuario (esta vez, confiando en el 'rol' del input)
    db_usuario = modelos.Usuario(
        nombre_usuario=usuario_in.nombre_usuario,
        email=usuario_in.email,
        contrasena_hash=hash_contrasena,
        rol=usuario_in.rol 
    )
    
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    
    # 5. Crear el carrito vacío
    db_carrito = modelos.Carrito(id_usuario=db_usuario.id_usuario)
    session.add(db_carrito)
    session.commit()
    
    #Devuelve el usuario recien creado.
    return db_usuario