#BITCAFE
#VERSION 0.2
#By: Angel A. Higuera

#POR TERMINAR

#Librerias y modulos
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select
from Servicios.base_Datos import SessionDep, get_session
from Servicios.numeraciones import UserRole
from Modelos import modelos

#CONFIGYRRACION DE AUTENTICACION Y SEGURIDAD

# . Contexto de Hashing de Contraseñas
#SE CAMBIO A ARGON2 YA QUE EL ANTERIOR GENERABA UN ERROR
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

#1. Esquema de Seguridad OAuth2
#Le dice a FastAPI qué URL usará para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

#2. Secretos del Token
#Puedes generar uno con: openssl rand -hex 32

#AUN NO SE HA DEFINIDO UNA LLAVE SEGURA
SECRET_KEY = "tu_llave_secreta_aqui_debe_ser_larga_y_aleatoria"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  

#PARA LA CONTRASEÑA

"""Verifica que la contraseña plana coincida con el hash."""
def verificar_contrasena(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

"""Genera un hash bcrypt de la contraseña."""
def get_hash_contrasena(password: str) -> str:    
    return pwd_context.hash(password)

#PARA LOS TOKENS

"""Crea un nuevo token JWT."""
def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#DEPENDENCIAS DE USUARIO

"""
Dependencia de FastAPI para obtener el usuario autenticado.
Valida el token JWT y devuelve el objeto Usuario de la BD.
"""
def get_current_user(
    session: SessionDep,                            
    token: str = Depends(oauth2_scheme)              
) -> modelos.Usuario:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    #Busca el usuario en la BD
    statement = select(modelos.Usuario).where(modelos.Usuario.nombre_usuario == username)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user



"""
Dependencia que verifica que el usuario actual sea un ADMIN.
"""
def get_current_admin_user(
    current_user: modelos.Usuario = Depends(get_current_user)
) -> modelos.Usuario:
    
    if current_user.rol != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción permitida solo para administradores"
        )
    return current_user