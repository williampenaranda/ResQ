# Configuración de Variables de Entorno en Render

Esta guía te ayudará a configurar las variables de entorno necesarias para desplegar el backend ResQ en Render.

## Variables Requeridas

### 1. API_BASE_URL (CRÍTICA para WebSocket)

**Valor:** `https://resq-api-jj3j.onrender.com` (o tu URL de Render)

**Importante:** 
- No incluir trailing slash (`/`) al final
- Esta variable es necesaria para que el backend genere las URLs correctas del WebSocket
- Sin esta variable, el backend usará el hostname del request, que puede ser incorrecto

**Cómo configurar en Render:**
1. Ve a tu servicio en Render Dashboard
2. Click en "Environment" en el menú lateral
3. Agrega la variable:
   - **Key:** `API_BASE_URL`
   - **Value:** `https://resq-api-jj3j.onrender.com` (sin trailing slash)

---

### 2. Redis (Upstash)

Si estás usando Upstash Redis, necesitas configurar:

#### REDIS_HOST
**Valor:** Tu endpoint de Upstash (ej: `related-ferret-6077.upstash.io`)

#### REDIS_PORT
**Valor:** `6379` (puerto estándar de Redis)

#### REDIS_PASSWORD
**Valor:** Tu token de autenticación de Upstash

**Cómo obtenerlo:**
1. Ve a tu dashboard de Upstash
2. Selecciona tu base de datos Redis
3. Ve a la sección "REST API" o "Details"
4. Copia el "Token" o "Password"

#### REDIS_SSL
**Valor:** `true` (requerido para Upstash)

**Nota:** El sistema detecta automáticamente si necesitas SSL si el host contiene `.upstash.io`, pero es mejor configurarlo explícitamente.

#### REDIS_DB
**Valor:** `0` (por defecto)

**Ejemplo de configuración completa para Upstash:**
```
REDIS_HOST=related-ferret-6077.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=tu-token-de-upstash
REDIS_SSL=true
REDIS_DB=0
```

---

### 3. Base de Datos (PostgreSQL)

#### DATABASE_URL
**Valor:** Tu connection string de PostgreSQL

**Formato:** `postgresql://usuario:contraseña@host:puerto/nombre_db`

**Ejemplo:**
```
DATABASE_URL=postgresql://usuario:password@dpg-xxxxx-a.oregon-postgres.render.com/resq_db
```

---

### 4. JWT (Autenticación)

#### JWT_SECRET_KEY
**Valor:** Una clave secreta segura y aleatoria

**Cómo generar:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### JWT_EXPIRE_MINUTES
**Valor:** `1440` (24 horas) o el tiempo que prefieras

---

## Checklist de Configuración

Antes de desplegar, verifica que tengas configuradas:

- [ ] `API_BASE_URL` - URL completa del backend (sin trailing slash)
- [ ] `DATABASE_URL` - Connection string de PostgreSQL
- [ ] `JWT_SECRET_KEY` - Clave secreta para JWT
- [ ] `JWT_EXPIRE_MINUTES` - Tiempo de expiración del token
- [ ] `REDIS_HOST` - Host de Redis (si usas Redis)
- [ ] `REDIS_PORT` - Puerto de Redis (si usas Redis)
- [ ] `REDIS_PASSWORD` - Contraseña/token de Redis (si es requerido)
- [ ] `REDIS_SSL` - `true` si usas Upstash o Redis cloud con SSL

---

## Verificación

Después de configurar las variables, verifica en los logs:

1. **WebSocket:** Debe mostrar la URL correcta:
   ```
   📡 WebSocket URL obtenida del backend: wss://resq-api-jj3j.onrender.com/ws/operadores-emergencia
   ```

2. **Redis:** Debe mostrar conexión exitosa:
   ```
   Redis conectado correctamente
   ```
   Si ves "Redis no está disponible", verifica las credenciales y SSL.

---

## Solución de Problemas

### WebSocket no conecta
- Verifica que `API_BASE_URL` esté configurada correctamente
- Asegúrate de que no tenga trailing slash
- Verifica que la URL sea accesible desde el navegador

### Redis no conecta
- Verifica que `REDIS_HOST` sea correcto
- Si usas Upstash, asegúrate de que `REDIS_SSL=true`
- Verifica que `REDIS_PASSWORD` sea el token correcto de Upstash
- Verifica que el endpoint de Upstash sea accesible desde Render

### Error "Connection closed by server"
- Generalmente significa que falta SSL o la contraseña es incorrecta
- Para Upstash, asegúrate de que `REDIS_SSL=true`

