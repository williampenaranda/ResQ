"""
Script de migración para agregar campos id_persona y tipoUsuario a la tabla usuarios.
Ejecuta ALTER TABLE para agregar las columnas si no existen.
"""

from sqlalchemy import text, inspect
from src.dataLayer.bd import engine, DATABASE_URL


def agregar_campos_usuario():
    """
    Agrega las columnas id_persona y tipoUsuario a la tabla usuarios si no existen.
    Compatible con PostgreSQL y SQLite.
    """
    es_sqlite = "sqlite" in DATABASE_URL.lower()
    
    try:
        with engine.begin() as connection:  # begin() maneja commit/rollback automáticamente
            # Verificar si la tabla existe
            inspector = inspect(engine)
            if "usuarios" not in inspector.get_table_names():
                return
            
            # Obtener columnas existentes
            columnas_existentes = [col["name"] for col in inspector.get_columns("usuarios")]
            
            # Agregar id_persona si no existe
            if "id_persona" not in columnas_existentes:
                connection.execute(text("ALTER TABLE usuarios ADD COLUMN id_persona INTEGER"))
                # Crear índice si no existe (solo PostgreSQL)
                if not es_sqlite:
                    try:
                        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_usuarios_id_persona ON usuarios(id_persona)"))
                    except Exception:
                        pass  # El índice puede ya existir
            
            # Agregar tipoUsuario si no existe
            if "tipoUsuario" not in columnas_existentes:
                # PostgreSQL requiere comillas dobles para nombres con mayúsculas
                if es_sqlite:
                    connection.execute(text('ALTER TABLE usuarios ADD COLUMN tipoUsuario VARCHAR(50)'))
                else:
                    connection.execute(text('ALTER TABLE usuarios ADD COLUMN "tipoUsuario" VARCHAR(50)'))
            
    except Exception as e:
        print(f"Error al agregar campos: {e}")
        raise


if __name__ == "__main__":
    agregar_campos_usuario()

