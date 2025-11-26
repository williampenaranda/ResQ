"""
Componente para encontrar la ambulancia más cercana a una emergencia.
Optimizado para tiempo de respuesta mínimo usando solo Redis.
"""

import json
import math
from typing import Optional, List, Tuple
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.businessLayer.businessComponents.cache.configRedis import get_redis_client


class BuscarAmbulanciaCercana:
    """
    Componente para encontrar la ambulancia más cercana a una emergencia.
    Usa solo Redis para obtener ubicaciones en tiempo real (sin consultar BD).
    """

    # Constantes para cálculo de distancia (km por grado)
    KM_PER_DEGREE_LAT = 111.0  # Aproximadamente constante
    EARTH_RADIUS_KM = 6371.0  # Radio de la Tierra en km

    @staticmethod
    def _calcular_distancia_km(
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """
        Calcula la distancia en kilómetros entre dos puntos usando fórmula de Haversine optimizada.
        
        Args:
            lat1, lon1: Coordenadas del punto 1 (emergencia)
            lat2, lon2: Coordenadas del punto 2 (ambulancia)
            
        Returns:
            Distancia en kilómetros
        """
        # Convertir grados a radianes
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Fórmula de Haversine
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        
        return BuscarAmbulanciaCercana.EARTH_RADIUS_KM * c

    @staticmethod
    def _obtener_todas_las_ambulancias_conectadas() -> List[Tuple[int, dict]]:
        """
        Obtiene todas las ambulancias conectadas (con ubicación en Redis).
        
        Returns:
            Lista de tuplas (id_ambulancia, datos_ubicacion)
        """
        client = get_redis_client()
        ambulancias = []
        
        # Usar SCAN para obtener todas las keys con patrón ambulancia:*:ubicacion
        # SCAN es más eficiente que KEYS para grandes volúmenes
        cursor = 0
        pattern = "ambulancia:*:ubicacion"
        
        while True:
            cursor, keys = client.scan(cursor, match=pattern, count=100)
            
            if keys:
                # Obtener todas las ubicaciones en batch usando MGET
                valores = client.mget(keys)
                
                for key, valor in zip(keys, valores):
                    if valor is None:
                        continue
                    
                    try:
                        # Extraer ID de la key: ambulancia:{id}:ubicacion
                        id_ambulancia = int(key.split(':')[1])
                        
                        # Parsear JSON
                        datos = json.loads(valor)
                        
                        # Validar que tenga los campos necesarios
                        if 'latitud' in datos and 'longitud' in datos:
                            ambulancias.append((id_ambulancia, datos))
                    except (ValueError, json.JSONDecodeError, KeyError, IndexError):
                        # Ignorar keys mal formateadas o datos inválidos
                        continue
            
            if cursor == 0:
                break
        
        return ambulancias

    @staticmethod
    def encontrar_mas_cercana(
        ubicacion_emergencia: Ubicacion,
        tipo_ambulancia: TipoAmbulancia,
        nivel_prioridad: NivelPrioridad
    ) -> Optional[int]:
        """
        Encuentra la ambulancia más cercana a la ubicación de la emergencia.
        Solo considera ambulancias conectadas (con ubicación en Redis) del tipo requerido.
        
        Args:
            ubicacion_emergencia: Ubicación de la emergencia
            tipo_ambulancia: Tipo de ambulancia requerida
            nivel_prioridad: Nivel de prioridad (puede usarse para ajustes futuros)
            
        Returns:
            ID de la ambulancia más cercana, o None si no hay disponibles
            
        Raises:
            ValueError: Si la ubicación de emergencia es inválida
        """
        # Validar ubicación de emergencia
        if not ubicacion_emergencia or not ubicacion_emergencia.latitud or not ubicacion_emergencia.longitud:
            raise ValueError("La ubicación de emergencia debe tener latitud y longitud válidas")
        
        lat_emergencia = ubicacion_emergencia.latitud
        lon_emergencia = ubicacion_emergencia.longitud
        
        # Obtener todas las ambulancias conectadas (con ubicación en Redis)
        ambulancias_conectadas = BuscarAmbulanciaCercana._obtener_todas_las_ambulancias_conectadas()
        
        if not ambulancias_conectadas:
            return None
        
        # Filtrar por tipo de ambulancia y calcular distancias
        tipo_requerido = tipo_ambulancia.value
        candidatas = []
        
        print(f"[DEBUG] Buscando ambulancia tipo: {tipo_requerido}")
        print(f"[DEBUG] Ubicación emergencia: lat={lat_emergencia}, lon={lon_emergencia}")
        print(f"[DEBUG] Total ambulancias conectadas: {len(ambulancias_conectadas)}")
        
        for id_ambulancia, datos in ambulancias_conectadas:
            # Filtrar por tipo de ambulancia
            tipo_ambulancia_actual = datos.get('tipoAmbulancia')
            print(f"[DEBUG] Ambulancia {id_ambulancia}: tipo={tipo_ambulancia_actual}, lat={datos.get('latitud')}, lon={datos.get('longitud')}")
            
            if tipo_ambulancia_actual != tipo_requerido:
                print(f"[DEBUG] Ambulancia {id_ambulancia} descartada: tipo {tipo_ambulancia_actual} != {tipo_requerido}")
                continue
            
            # Obtener coordenadas
            lat_ambulancia = datos.get('latitud')
            lon_ambulancia = datos.get('longitud')
            
            if lat_ambulancia is None or lon_ambulancia is None:
                print(f"[DEBUG] Ambulancia {id_ambulancia} descartada: coordenadas inválidas")
                continue
            
            # Calcular distancia
            distancia = BuscarAmbulanciaCercana._calcular_distancia_km(
                lat_emergencia, lon_emergencia,
                lat_ambulancia, lon_ambulancia
            )
            
            print(f"[DEBUG] Ambulancia {id_ambulancia}: distancia={distancia:.4f} km")
            
            # Agregar a candidatas (sin early exit para asegurar que siempre se seleccione la más cercana)
            candidatas.append((distancia, id_ambulancia))
        
        # Si no hay candidatas del tipo requerido
        if not candidatas:
            print(f"[DEBUG] No hay candidatas del tipo {tipo_requerido}")
            return None
        
        print(f"[DEBUG] Candidatas encontradas: {len(candidatas)}")
        for dist, id_amb in candidatas:
            print(f"[DEBUG]   - Ambulancia {id_amb}: {dist:.4f} km")
        
        # Ordenar por distancia (ascendente) y retornar la más cercana
        # Si hay empates en distancia, ordenar también por ID para consistencia
        candidatas.sort(key=lambda x: (x[0], x[1]))
        
        id_seleccionada = candidatas[0][1]
        distancia_seleccionada = candidatas[0][0]
        print(f"[DEBUG] Ambulancia seleccionada: {id_seleccionada} (distancia: {distancia_seleccionada:.4f} km)")
        
        return id_seleccionada

