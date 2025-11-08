from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.dataLayer.bd import inicializar_base_datos, engine
from src.api.usuarios import usuarios_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación FastAPI.
    - Al iniciar: inicializa la base de datos
    - Al cerrar: cierra las conexiones del engine
    """
    # Startup: inicializar base de datos
    try:
        inicializar_base_datos()
    except Exception as e:
        print(f"✗ Error al inicializar la base de datos: {e}")
        raise
    
    yield
    
    # Shutdown: cerrar conexiones
    engine.dispose()
    print("✓ Conexiones de base de datos cerradas")


app = FastAPI(
    title="ResQ API",
    description="API para el sistema ResQ",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(usuarios_router)
@app.get("/")
def read_root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "message": "ResQ API está funcionando",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    """Endpoint de health check para verificar el estado de la aplicación."""
    return {
        "status": "healthy",
        "database": "connected"
    }