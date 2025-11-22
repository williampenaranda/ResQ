from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.dataLayer.bd import inicializar_base_datos, engine
from src.api.usuarios import usuarios_router
from src.api.auth import auth_router
from src.api.solicitantes import solicitantes_router
from src.api.operadorEmergencia import operadores_emergencia_router
from src.api.operadorAmbulancia import operadores_ambulancia_router
from src.api.websocketOpEmergencias import websocket_router
from src.api.websocketSolicitantes import websocket_solicitantes_router
from src.api.emergencias import emergencias_router
from src.api.evaluarEmergencia import evaluar_emergencia_router
from src.api.ubicaciones import ubicaciones_router
from src.api.solicitudes import solicitudes_router
from src.api.salas import salas_router
from src.businessLayer.businessComponents.llamadas.configLiveKit import ensure_livekit_healthcheck
from src.businessLayer.businessComponents.cache.configRedis import ensure_redis_healthcheck, close_redis_client
from src.api.atenderEmergencias import atender_emergencias_router
from src.api.ambulancias import ambulancias_router
from src.api.recibirNotificaciones import recibir_notificaciones_router
from src.api.websocketAmbulancias import websocket_ambulancias_router
from src.api.infoWebSocketAmbulancias import info_websocket_ambulancias_router
from src.api.despacharAmbulancia import despachar_ambulancia_router

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
    
    await ensure_livekit_healthcheck()
    
    # Validar Redis
    try:
        ensure_redis_healthcheck()
    except Exception as e:
        print(f"Advertencia: Redis no está disponible: {e}")
        print("El sistema continuará pero las ubicaciones de ambulancias no funcionarán correctamente.")
    
    yield
    
    # Shutdown: cerrar conexiones
    engine.dispose()
    close_redis_client()


app = FastAPI(
    title="ResQ API",
    description="API para el sistema ResQ",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir conexiones WebSocket
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routers security
app.include_router(auth_router)
app.include_router(usuarios_router)

#routers solicitantes
app.include_router(solicitantes_router)
app.include_router(solicitudes_router)
app.include_router(recibir_notificaciones_router)

#routers operadores de emergencia
app.include_router(operadores_emergencia_router)
app.include_router(atender_emergencias_router)
app.include_router(operadores_ambulancia_router)
app.include_router(salas_router)
app.include_router(evaluar_emergencia_router)
app.include_router(despachar_ambulancia_router)
app.include_router(emergencias_router)


app.include_router(ambulancias_router)
app.include_router(websocket_router)
app.include_router(websocket_solicitantes_router)
app.include_router(websocket_ambulancias_router)
app.include_router(info_websocket_ambulancias_router)
# app.include_router(ubicaciones_router)

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