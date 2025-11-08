"""
Módulo de configuración y gestión de la base de datos.

Este módulo proporciona:
1. Configuración de la conexión a la base de datos
2. Creación del engine de SQLAlchemy
3. Gestión de sesiones de base de datos
4. Funciones para inicializar las tablas
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importar Base y todos los modelos para que SQLAlchemy los reconozca
from src.dataLayer.models.modeloUsuario import Base, Usuario

# URL de conexión a la base de datos
# Prioridad: variable de entorno > valor por defecto (SQLite para desarrollo)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./resq.db"  # Valor por defecto: SQLite local
)

# Validar que DATABASE_URL no esté vacía
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada. Configúrala en el archivo .env o como variable de entorno.")

# Determinar si es SQLite
es_sqlite = "sqlite" in DATABASE_URL.lower()

# Crear el engine de SQLAlchemy
# Para SQLite, usamos StaticPool y check_same_thread=False para compatibilidad con FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if es_sqlite else {},
    poolclass=StaticPool if es_sqlite else None,
    echo=True  # Muestra las consultas SQL en la consola (útil para desarrollo)
)

# Crear la clase SessionLocal para crear sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def obtener_sesion() -> Session:
    """
    Función de dependencia para obtener una sesión de base de datos.
    Útil para usar con FastAPI Dependency Injection.
    
    Yields:
        Session: Sesión de base de datos de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verificar_conexion():
    """
    Verifica que la conexión a la base de datos funcione correctamente.
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
        
    Raises:
        SQLAlchemyError: Si hay un error al conectar
    """
    try:
        with engine.connect() as connection:
            # Ejecutar una consulta simple para verificar la conexión
            connection.execute(text("SELECT 1"))
        print("✓ Conexión a la base de datos exitosa")
        return True
    except SQLAlchemyError as e:
        print(f"✗ Error al conectar a la base de datos: {e}")
        raise


def crear_tablas():
    """
    Crea todas las tablas definidas en los modelos.
    Esta función debe ser llamada al iniciar la aplicación.
    
    Raises:
        SQLAlchemyError: Si hay un error al crear las tablas
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas exitosamente")
    except SQLAlchemyError as e:
        print(f"✗ Error al crear las tablas: {e}")
        raise


def inicializar_base_datos():
    """
    Inicializa la base de datos: verifica la conexión y crea las tablas.
    Esta función debe ser llamada al iniciar la aplicación.
    
    Raises:
        SQLAlchemyError: Si hay un error al inicializar
    """
    print("Inicializando base de datos...")
    verificar_conexion()
    crear_tablas()
    print("✓ Base de datos inicializada correctamente")


def eliminar_tablas():
    """
    Elimina todas las tablas de la base de datos.
    ⚠️ ADVERTENCIA: Esta función elimina TODOS los datos.
    Úsala solo en desarrollo o para resetear la base de datos.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠ Tablas eliminadas")


def reiniciar_tablas():
    """
    Elimina y recrea todas las tablas.
    ⚠️ ADVERTENCIA: Esta función elimina TODOS los datos.
    Úsala solo en desarrollo.
    """
    eliminar_tablas()
    crear_tablas()
    print("✓ Base de datos reiniciada")
