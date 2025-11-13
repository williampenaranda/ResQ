from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Envía un mensaje a todas las conexiones activas.
        Si una conexión falla, continúa con las demás.
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Si falla el envío, marcar para desconectar
                disconnected.append(connection)
        
        # Remover conexiones que fallaron
        for connection in disconnected:
            try:
                self.disconnect(connection)
            except Exception:
                pass  # Ya no está en la lista o ya fue removida
    
    def get_active_connections_count(self) -> int:
        """
        Retorna el número de conexiones activas.
        
        Returns:
            int: Número de conexiones WebSocket activas
        """
        return len(self.active_connections)
