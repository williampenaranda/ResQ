# 🚀 Guía de Despliegue en AWS EC2 (Desde la Consola Web)

Esta guía te llevará paso a paso para desplegar el sistema ResQ en AWS EC2 usando la consola web, con configuración de SSL/HTTPS.

---

## 📋 Tabla de Contenidos

1. [Crear Instancia EC2](#1-crear-instancia-ec2)
2. [Configurar Security Groups](#2-configurar-security-groups)
3. [Crear Base de Datos RDS](#3-crear-base-de-datos-rds-postgresql)
4. [Crear Redis ElastiCache](#4-crear-redis-elasticache)
5. [Conectar y Configurar el Servidor](#5-conectar-y-configurar-el-servidor)
6. [Configurar SSL/HTTPS](#6-configurar-sslhttps)
7. [Configurar Nginx como Proxy Reverso](#7-configurar-nginx-como-proxy-reverso)
8. [Configurar Dominio](#8-configurar-dominio)
9. [Verificar el Despliegue](#9-verificar-el-despliegue)

---

## 1. Crear Instancia EC2

### Paso 1.1: Acceder a EC2

1. Inicia sesión en AWS Console: https://console.aws.amazon.com
2. Busca "EC2" en la barra de búsqueda o ve a: https://console.aws.amazon.com/ec2/
3. Asegúrate de estar en la región correcta (ej: `us-east-1`, `us-west-2`)

### Paso 1.2: Crear Par de Claves SSH

1. En el menú lateral, haz clic en **"Key Pairs"** (Pares de claves)
2. Haz clic en **"Create key pair"** (Crear par de claves)
3. Configura:
   - **Name**: `resq-key`
   - **Key pair type**: RSA
   - **Private key file format**: `.pem` (para Linux/Mac) o `.ppk` (para Windows con PuTTY)
4. Haz clic en **"Create key pair"**
5. **IMPORTANTE**: Se descargará automáticamente el archivo. Guárdalo en un lugar seguro, no podrás descargarlo de nuevo.

### Paso 1.3: Lanzar Instancia EC2

1. En el menú lateral, haz clic en **"Instances"** (Instancias)
2. Haz clic en **"Launch instance"** (Lanzar instancia)

#### Configuración Básica:

**Name and tags:**
- **Name**: `resq-api-server`

**Application and OS Images:**
- Selecciona **"Amazon Linux 2023 AMI"** (o Ubuntu 22.04 LTS)
- Deja la versión por defecto

**Instance type:**
- Selecciona **"t3.micro"** (Free tier elegible) o **"t3.small"** para producción

**Key pair (login):**
- Selecciona **"resq-key"** (el que creaste en el paso anterior)

**Network settings:**
- **VPC**: Deja el default
- **Subnet**: Deja el default
- **Auto-assign Public IP**: **Enable** (Habilitar)
- **Firewall (security groups)**: 
  - Selecciona **"Create security group"** (Crear grupo de seguridad)
  - **Security group name**: `resq-api-sg`
  - **Description**: `Security group for ResQ API`

**Configure storage:**
- **Size (GiB)**: `20`
- **Volume type**: `gp3`

3. Haz clic en **"Launch instance"** (Lanzar instancia)

4. Espera a que el estado cambie a **"Running"** (En ejecución)

### Paso 1.4: Obtener IP Pública

1. Selecciona tu instancia `resq-api-server`
2. En la pestaña **"Details"** (Detalles), copia la **"Public IPv4 address"**
3. Anota esta IP, la necesitarás más adelante

---

## 2. Configurar Security Groups

### Paso 2.1: Editar Security Group

1. En la consola EC2, ve a **"Security Groups"** (Grupos de seguridad) en el menú lateral
2. Selecciona el grupo `resq-api-sg`
3. Haz clic en **"Edit inbound rules"** (Editar reglas de entrada)

### Paso 2.2: Agregar Reglas

Agrega las siguientes reglas haciendo clic en **"Add rule"** (Agregar regla):

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | Permitir SSH desde tu IP |
| HTTP | TCP | 80 | 0.0.0.0/0 | Permitir HTTP |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Permitir HTTPS |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Puerto de la API |

**Nota:** Para "My IP", haz clic en el botón "My IP" que aparece al seleccionar "My IP" en Source.

4. Haz clic en **"Save rules"** (Guardar reglas)

---

## 3. Crear Base de Datos RDS (PostgreSQL)

### Paso 3.1: Acceder a RDS

1. En la consola de AWS, busca **"RDS"** o ve a: https://console.aws.amazon.com/rds/
2. Asegúrate de estar en la misma región que tu instancia EC2

### Paso 3.2: Crear DB Subnet Group

1. En el menú lateral, haz clic en **"Subnet groups"** (Grupos de subred)
2. Haz clic en **"Create DB subnet group"** (Crear grupo de subred)
3. Configura:
   - **Name**: `resq-db-subnet`
   - **Description**: `Subnet group for ResQ database`
   - **VPC**: Selecciona el VPC por defecto (el mismo que tu EC2)
   - **Availability Zones**: Selecciona al menos 2 zonas (ej: `us-east-1a`, `us-east-1b`)
   - **Subnets**: Selecciona las subredes disponibles
4. Haz clic en **"Create"** (Crear)

### Paso 3.3: Crear Security Group para RDS

1. Ve a EC2 → **"Security Groups"**
2. Haz clic en **"Create security group"** (Crear grupo de seguridad)
3. Configura:
   - **Security group name**: `resq-rds-sg`
   - **Description**: `Security group for ResQ RDS`
   - **VPC**: El mismo VPC que tu EC2
4. En **"Inbound rules"** (Reglas de entrada):
   - Haz clic en **"Add rule"**
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Selecciona el security group `resq-api-sg` (no una IP)
5. Haz clic en **"Create security group"**

### Paso 3.4: Crear Instancia RDS

1. En RDS, haz clic en **"Databases"** (Bases de datos) en el menú lateral
2. Haz clic en **"Create database"** (Crear base de datos)

#### Configuración:

**Engine options:**
- **Engine type**: PostgreSQL
- **Version**: PostgreSQL 15.4 (o la más reciente)

**Templates:**
- **Free tier** (para desarrollo) o **Production** (para producción)

**Settings:**
- **DB instance identifier**: `resq-postgres`
- **Master username**: `postgres`
- **Master password**: Crea una contraseña segura y anótala
- **Confirm password**: Confirma la contraseña

**Instance configuration:**
- **DB instance class**: `db.t3.micro` (Free tier) o `db.t3.small` (producción)

**Storage:**
- **Storage type**: General Purpose SSD (gp3)
- **Allocated storage**: `20` GB
- **Storage autoscaling**: Opcional (recomendado para producción)

**Connectivity:**
- **VPC**: El mismo VPC que tu EC2
- **Subnet group**: `resq-db-subnet`
- **Public access**: **Yes** (Sí) - Para poder conectarte desde fuera
- **VPC security group**: Selecciona `resq-rds-sg`
- **Availability Zone**: Deja el default

**Database authentication:**
- **Password authentication**

**Additional configuration (opcional):**
- **Initial database name**: `resq`
- **Backup retention period**: `7` días (para producción)

3. Haz clic en **"Create database"** (Crear base de datos)

4. Espera 5-10 minutos a que el estado cambie a **"Available"** (Disponible)

### Paso 3.5: Obtener Endpoint de RDS

1. Una vez que RDS esté disponible, haz clic en la instancia `resq-postgres`
2. En la pestaña **"Connectivity & security"** (Conectividad y seguridad), copia el **"Endpoint"**
3. Anota este endpoint (ej: `resq-postgres.xxxxx.us-east-1.rds.amazonaws.com`)

### Paso 3.6: Crear Usuario en la Base de Datos

Necesitarás conectarte a RDS para crear el usuario. Puedes hacerlo desde tu instancia EC2 (ver sección 5) o desde tu máquina local si tienes PostgreSQL instalado.

**Desde tu máquina local (si tienes PostgreSQL):**
```bash
psql -h RESQ_ENDPOINT -U postgres -d postgres
```

Luego ejecuta:
```sql
CREATE DATABASE resq;
CREATE USER app_user WITH PASSWORD 'TU_CONTRASEÑA_SEGURA';
GRANT ALL PRIVILEGES ON DATABASE resq TO app_user;
\q
```

---

## 4. Crear Redis ElastiCache

### Paso 4.1: Acceder a ElastiCache

1. En la consola de AWS, busca **"ElastiCache"** o ve a: https://console.aws.amazon.com/elasticache/
2. Asegúrate de estar en la misma región

### Paso 4.2: Crear Subnet Group

1. En el menú lateral, haz clic en **"Subnet groups"** (Grupos de subred)
2. Haz clic en **"Create subnet group"** (Crear grupo de subred)
3. Configura:
   - **Name**: `resq-redis-subnet`
   - **Description**: `Subnet group for ResQ Redis`
   - **VPC**: El mismo VPC que tu EC2
   - **Availability Zones**: Selecciona al menos 2 zonas
   - **Subnets**: Selecciona las subredes disponibles
4. Haz clic en **"Create"**

### Paso 4.3: Crear Security Group para Redis

1. Ve a EC2 → **"Security Groups"**
2. Haz clic en **"Create security group"**
3. Configura:
   - **Security group name**: `resq-redis-sg`
   - **Description**: `Security group for ResQ Redis`
   - **VPC**: El mismo VPC que tu EC2
4. En **"Inbound rules"**:
   - Haz clic en **"Add rule"**
   - **Type**: Custom TCP
   - **Port**: 6379
   - **Source**: Selecciona el security group `resq-api-sg`
5. Haz clic en **"Create security group"**

### Paso 4.4: Crear Cluster de Redis

1. En ElastiCache, haz clic en **"Redis clusters"** (Clusters de Redis)
2. Haz clic en **"Create"** (Crear)

#### Configuración:

**Cluster settings:**
- **Name**: `resq-redis`
- **Description**: `Redis cluster for ResQ`

**Location:**
- **AWS Region**: Tu región actual
- **Network & Security:**
  - **VPC**: El mismo VPC que tu EC2
  - **Subnet group**: `resq-redis-subnet`
  - **Availability Zone(s)**: Deja el default
  - **Security groups**: Selecciona `resq-redis-sg`

**Node type:**
- **Node type**: `cache.t3.micro` (Free tier) o `cache.t3.small` (producción)

**Redis settings:**
- **Redis version**: `7.0` (o la más reciente)
- **Port**: `6379`
- **Parameter group**: Deja el default

**Backup:**
- **Backup**: Opcional (recomendado para producción)

3. Haz clic en **"Create"** (Crear)

4. Espera 5-10 minutos a que el estado cambie a **"Available"** (Disponible)

### Paso 4.5: Obtener Endpoint de Redis

1. Una vez que Redis esté disponible, haz clic en el cluster `resq-redis`
2. En la pestaña **"Configuration"** (Configuración), copia el **"Primary endpoint"**
3. Anota este endpoint (ej: `resq-redis.xxxxx.0001.use1.cache.amazonaws.com:6379`)

---

## 5. Conectar y Configurar el Servidor

### Paso 5.1: Conectar por SSH

**Windows (PowerShell):**
```powershell
# Navegar a la carpeta donde está tu clave
cd C:\ruta\a\tu\clave

# Conectar
ssh -i resq-key.pem ec2-user@TU_IP_PUBLICA
```

**Windows (PuTTY):**
1. Abre PuTTY
2. En **"Host Name"**: `ec2-user@TU_IP_PUBLICA`
3. En **"Connection" → "SSH" → "Auth"**: Selecciona tu archivo `.ppk`
4. Haz clic en **"Open"**

**Linux/Mac:**
```bash
chmod 400 resq-key.pem
ssh -i resq-key.pem ec2-user@TU_IP_PUBLICA
```

**Nota:** Para Ubuntu, usa `ubuntu` en lugar de `ec2-user`.

### Paso 5.2: Subir el Código

**Desde tu máquina local (PowerShell):**
```powershell
cd ResQ
scp -i resq-key.pem -r * ec2-user@TU_IP_PUBLICA:/tmp/resq
```

**Desde tu máquina local (Linux/Mac):**
```bash
cd ResQ
scp -i resq-key.pem -r * ec2-user@TU_IP_PUBLICA:/tmp/resq
```

### Paso 5.3: Ejecutar Script de Configuración

**Opción A: Usar el script automático**

1. Sube el script a EC2:
```powershell
scp -i resq-key.pem setup-ec2.sh ec2-user@TU_IP_PUBLICA:/tmp/
```

2. En EC2, ejecuta:
```bash
# Mover código a /opt/resq
sudo mv /tmp/resq/* /opt/resq/
sudo chown -R resq:resq /opt/resq

# Ejecutar script de configuración
sudo bash /tmp/setup-ec2.sh
```

**Opción B: Configuración manual**

Sigue los pasos de la sección 7 y 8 de `GUIA_DESPLIEGUE_AWS_EC2.md`.

### Paso 5.4: Configurar Variables de Entorno

```bash
sudo nano /opt/resq/.env
```

Agrega (reemplaza con tus valores reales):
```env
# Base de datos RDS
DATABASE_URL=postgresql://app_user:TU_CONTRASEÑA@RDS_ENDPOINT:5432/resq

# JWT
JWT_SECRET_KEY=GENERA_UNA_CLAVE_SECRETA_AQUI
JWT_EXPIRE_MINUTES=1440

# Redis ElastiCache
REDIS_HOST=REDIS_ENDPOINT
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# LiveKit (Opcional)
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
```

**Generar JWT Secret:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Paso 5.5: Iniciar el Servicio

```bash
# Editar archivo .env primero
sudo nano /opt/resq/.env

# Iniciar servicio
sudo systemctl start resq-api
sudo systemctl enable resq-api
sudo systemctl status resq-api
```

---

## 6. Configurar SSL/HTTPS

Hay dos opciones principales para SSL:

### Opción A: Usar AWS Certificate Manager + Application Load Balancer (Recomendado para Producción)

### Opción B: Usar Certbot con Let's Encrypt (Más simple, gratis)

Vamos a usar la **Opción B** que es más directa y gratuita.

---

## 7. Configurar Nginx como Proxy Reverso

### Paso 7.1: Instalar Nginx

En tu instancia EC2:

**Amazon Linux 2023:**
```bash
sudo dnf install -y nginx
```

**Ubuntu:**
```bash
sudo apt install -y nginx
```

### Paso 7.2: Configurar Nginx

```bash
sudo nano /etc/nginx/conf.d/resq-api.conf
```

Agrega:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Redirigir HTTP a HTTPS (se configurará después)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts para WebSockets
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

**Nota:** Si aún no tienes dominio, usa la IP pública temporalmente o comenta la línea `server_name`.

### Paso 7.3: Iniciar Nginx

```bash
# Verificar configuración
sudo nginx -t

# Iniciar Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

---

## 8. Configurar Dominio

### Paso 8.1: Configurar DNS

En tu proveedor de DNS (ej: Route 53, Cloudflare, GoDaddy):

1. Crea un registro **A** apuntando a la IP pública de tu instancia EC2:
   - **Type**: A
   - **Name**: `@` o `api` (depende de tu necesidad)
   - **Value**: `TU_IP_PUBLICA`
   - **TTL**: 300 (o el default)

2. Si quieres `www`, crea otro registro:
   - **Type**: A
   - **Name**: `www`
   - **Value**: `TU_IP_PUBLICA`

### Paso 8.2: Verificar que el Dominio Funciona

Espera unos minutos y luego verifica:

```bash
# Desde tu máquina local
ping tu-dominio.com
```

Debería responder con la IP de tu EC2.

---

## 9. Configurar SSL/HTTPS con Certbot

### Paso 9.1: Instalar Certbot

En tu instancia EC2:

**Amazon Linux 2023:**
```bash
sudo dnf install -y certbot python3-certbot-nginx
```

**Ubuntu:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Paso 9.2: Obtener Certificado SSL

```bash
# Obtener certificado (reemplaza con tu dominio)
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Certbot te pedirá:
- **Email**: Tu email (para notificaciones de renovación)
- **Términos y condiciones**: Acepta
- **Compartir email**: Opcional

Certbot configurará automáticamente Nginx para usar HTTPS.

### Paso 9.3: Verificar Renovación Automática

Certbot configura automáticamente la renovación, pero puedes verificar:

```bash
# Probar renovación
sudo certbot renew --dry-run

# Ver estado del timer
sudo systemctl status certbot.timer
```

### Paso 9.4: Actualizar Configuración de Nginx

Certbot habrá modificado tu archivo de configuración. Verifica:

```bash
sudo nano /etc/nginx/conf.d/resq-api.conf
```

Deberías ver algo como:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts para WebSockets
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

### Paso 9.5: Recargar Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 10. Verificar el Despliegue

### Paso 10.1: Verificar HTTP (Redirección)

Abre en tu navegador:
```
http://tu-dominio.com
```

Debería redirigir automáticamente a HTTPS.

### Paso 10.2: Verificar HTTPS

Abre en tu navegador:
```
https://tu-dominio.com
```

Deberías ver:
- 🔒 Candado verde en la barra de direcciones
- Respuesta JSON: `{"message": "ResQ API está funcionando", "status": "ok"}`

### Paso 10.3: Verificar Endpoints

- **Health Check**: https://tu-dominio.com/health
- **Swagger UI**: https://tu-dominio.com/docs
- **ReDoc**: https://tu-dominio.com/redoc

### Paso 10.4: Verificar Logs

```bash
# Logs de la aplicación
sudo journalctl -u resq-api -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 Seguridad Adicional

### Actualizar Security Group

Una vez que SSL esté funcionando, puedes restringir el puerto 8000:

1. Ve a EC2 → Security Groups → `resq-api-sg`
2. Edita la regla del puerto 8000
3. Cambia **Source** de `0.0.0.0/0` a `127.0.0.1/32` (solo localhost)
4. Guarda

Esto asegura que solo Nginx pueda acceder directamente a la aplicación.

### Firewall del Sistema

```bash
# Amazon Linux 2023
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📝 Checklist Final

- [ ] Instancia EC2 creada y accesible
- [ ] Security groups configurados
- [ ] RDS PostgreSQL creado y accesible
- [ ] Redis ElastiCache creado y accesible
- [ ] Aplicación desplegada y funcionando
- [ ] Variables de entorno configuradas
- [ ] Servicio systemd funcionando
- [ ] Nginx configurado como proxy reverso
- [ ] Dominio configurado en DNS
- [ ] SSL/HTTPS configurado con Certbot
- [ ] HTTP redirige a HTTPS
- [ ] Health check responde
- [ ] Swagger UI accesible
- [ ] Logs sin errores críticos

---

## 🔄 Actualizar la Aplicación

```bash
# Conectarse a EC2
ssh -i resq-key.pem ec2-user@TU_IP_PUBLICA

# Detener servicio
sudo systemctl stop resq-api

# Actualizar código (desde tu máquina local)
# scp -i resq-key.pem -r ResQ/* ec2-user@TU_IP_PUBLICA:/tmp/resq

# En EC2
sudo mv /tmp/resq/* /opt/resq/
sudo chown -R resq:resq /opt/resq

# Actualizar dependencias
sudo -u resq bash
cd /opt/resq
source venv/bin/activate
pip install -r requirements.txt
exit

# Reiniciar servicio
sudo systemctl start resq-api
```

---

## 🆘 Solución de Problemas

### SSL no funciona

**Verificar:**
1. Dominio apunta a la IP correcta: `ping tu-dominio.com`
2. Puerto 443 está abierto en Security Group
3. Certbot se ejecutó correctamente: `sudo certbot certificates`
4. Nginx está escuchando en 443: `sudo netstat -tlnp | grep 443`

### Error 502 Bad Gateway

**Causas:**
1. La aplicación no está corriendo: `sudo systemctl status resq-api`
2. Puerto 8000 no es accesible desde Nginx
3. Revisar logs: `sudo journalctl -u resq-api -n 50`

### WebSockets no funcionan

**Verificar:**
1. Headers de WebSocket en configuración de Nginx
2. Timeouts configurados correctamente
3. Security group permite conexiones persistentes

---

**¡Despliegue con SSL completado! 🎉🔒**

