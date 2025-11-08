from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.dataLayer.bd import inicializar_base_datos, engine
from src.api.usuarios import usuarios_router
from src.api.auth import auth_router

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
        print(f"Error al inicializar la base de datos: {e}")
        raise
    
    yield
    
    # Shutdown: cerrar conexiones
    engine.dispose()


app = FastAPI(
    title="ResQ API",
    description="API para el sistema ResQ",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(usuarios_router)
app.include_router(auth_router)


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