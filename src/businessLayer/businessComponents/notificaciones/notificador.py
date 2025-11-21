from fastapi import WebSocket
from typing import Dict, List, Optional, Set
from collections import defaultdict

class notificador:
    """
    Componente de notificaciones para gestionar conexiones WebSocket asociadas a IDs.
    
    Permite:
    - Asociar conexiones con IDs (usuario_id, ambulancia_id, etc.)
    - Listar conexiones por ID
    - Enviar mensajes a un ID específico
    - Enviar mensajes a todos (broadcast)
    """
    
    def __init__(self):
        # Diccionario que mapea ID -> Lista de WebSockets
        self.conexiones_por_id: Dict[int, List[WebSocket]] = defaultdict(list)
        # Diccionario inverso: WebSocket -> ID (para desconexión rápida)
        self.id_por_conexion: Dict[WebSocket, int] = {}
        # Set de todas las conexiones activas (para broadcast rápido)
        self.conexiones_activas: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, entity_id: Optional[int] = None):
        """
        Conecta un WebSocket opcionalmente asociado a un ID.
        
        Args:
            websocket: Conexión WebSocket a aceptar
            entity_id: ID opcional de la entidad (usuario, operador, etc.)
        """
        await websocket.accept()
        self.conexiones_activas.add(websocket)
        
        if entity_id is not None:
            self.conexiones_por_id[entity_id].append(websocket)
            self.id_por_conexion[websocket] = entity_id

    def disconnect(self, websocket: WebSocket):
        """
        Desconecta un WebSocket y lo remueve de todas las estructuras.
        """
        if websocket in self.conexiones_activas:
            self.conexiones_activas.remove(websocket)
        
        # Si tiene ID asociado, removerlo de ahí también
        if websocket in self.id_por_conexion:
            entity_id = self.id_por_conexion[websocket]
            if websocket in self.conexiones_por_id[entity_id]:
                self.conexiones_por_id[entity_id].remove(websocket)
            # Si no quedan conexiones para ese ID, limpiar la entrada
            if not self.conexiones_por_id[entity_id]:
                del self.conexiones_por_id[entity_id]
            del self.id_por_conexion[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Envía un mensaje a una conexión específica.
        
        Args:
            message: Mensaje a enviar
            websocket: Conexión WebSocket destino
        """
        try:
            await websocket.send_text(message)
        except Exception:
            # Si falla, desconectar
            self.disconnect(websocket)

    async def send_to_id(self, message: str, entity_id: int):
        """
        Envía un mensaje a todas las conexiones asociadas a un ID específico.
        
        Args:
            message: Mensaje a enviar
            entity_id: ID de la entidad a la que enviar el mensaje
        """
        if entity_id not in self.conexiones_por_id:
            return  # No hay conexiones para ese ID
        
        disconnected = []
        for connection in self.conexiones_por_id[entity_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Limpiar conexiones que fallaron
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast(self, message: str):
        """
        Envía un mensaje a todas las conexiones activas.
        Si una conexión falla, continúa con las demás.
        """
        disconnected = []
        for connection in list(self.conexiones_activas):  # Copia para evitar modificación durante iteración
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Remover conexiones que fallaron
        for connection in disconnected:
            self.disconnect(connection)

    def get_conexiones_por_id(self, entity_id: int) -> List[WebSocket]:
        """
        Obtiene todas las conexiones asociadas a un ID específico.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Lista de WebSockets asociados a ese ID
        """
        return list(self.conexiones_por_id.get(entity_id, []))

    def list_connected_ids(self) -> List[int]:
        """
        Lista todos los IDs que tienen conexiones activas.
        
        Returns:
            Lista de IDs con conexiones activas
        """
        return [entity_id for entity_id, connections in self.conexiones_por_id.items() if connections]

    def get_connection_count_by_id(self, entity_id: int) -> int:
        """
        Obtiene el número de conexiones activas para un ID específico.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Número de conexiones activas para ese ID
        """
        return len(self.conexiones_por_id.get(entity_id, []))

    def get_conexiones_activas_count(self) -> int:
        """
        Retorna el número total de conexiones activas.
        
        Returns:
            int: Número de conexiones WebSocket activas
        """
        return len(self.conexiones_activas)
    
    def is_connected(self, entity_id: int) -> bool:
        """
        Verifica si un ID tiene al menos una conexión activa.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            True si tiene conexiones activas, False en caso contrario
        """
        return entity_id in self.conexiones_por_id and len(self.conexiones_por_id[entity_id]) > 0