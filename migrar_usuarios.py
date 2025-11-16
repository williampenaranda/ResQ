"""
Script independiente para ejecutar la migración de usuarios.
Ejecuta: python migrar_usuarios.py
"""

from src.dataLayer.migraciones.agregar_campos_usuario import agregar_campos_usuario

if __name__ == "__main__":
    print("Ejecutando migración para agregar campos id_persona y tipoUsuario a la tabla usuarios...")
    try:
        agregar_campos_usuario()
        print("✓ Migración completada exitosamente")
    except Exception as e:
        print(f"✗ Error en la migración: {e}")
        exit(1)

