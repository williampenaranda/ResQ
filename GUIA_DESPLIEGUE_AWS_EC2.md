# 🚀 Guía de Despliegue en AWS EC2

Esta guía te llevará paso a paso para desplegar el sistema ResQ en una instancia EC2 de AWS, incluyendo la configuración de PostgreSQL (RDS), Redis (ElastiCache) y todas las variables de entorno necesarias.

---

## 📋 Tabla de Contenidos

1. [Prerrequisitos](#1-prerrequisitos)
2. [Crear Instancia EC2](#2-crear-instancia-ec2)
3. [Configurar Security Groups](#3-configurar-security-groups)
4. [Crear Base de Datos RDS (PostgreSQL)](#4-crear-base-de-datos-rds-postgresql)
5. [Crear Redis ElastiCache](#5-crear-redis-elasticache)
6. [Conectar a la Instancia EC2](#6-conectar-a-la-instancia-ec2)
7. [Configurar el Servidor](#7-configurar-el-servidor)
8. [Desplegar la Aplicación](#8-desplegar-la-aplicación)
9. [Configurar como Servicio](#9-configurar-como-servicio)
10. [Configurar Nginx (Opcional)](#10-configurar-nginx-opcional)
11. [Configurar Dominio y SSL (Opcional)](#11-configurar-dominio-y-ssl-opcional)
12. [Solución de Problemas](#12-solución-de-problemas)

---

## 1. Prerrequisitos

Antes de comenzar, asegúrate de tener:

- ✅ Una cuenta de AWS activa
- ✅ AWS CLI instalado y configurado
- ✅ Acceso SSH a tu máquina local
- ✅ Conocimientos básicos de Linux

### Instalar AWS CLI

**Windows:**
```powershell
# Descargar e instalar desde:
# https://awscli.amazonaws.com/AWSCLIV2.msi

# Verificar instalación
aws --version
```

**Linux/Mac:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Configurar AWS CLI

```bash
aws configure
```

Ingresa:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (ej: `us-east-1`)
- Default output format (ej: `json`)

---

## 2. Crear Instancia EC2

### 2.1 Desde la Consola Web

1. **Accede a EC2:**
   - Ve a: https://console.aws.amazon.com/ec2/
   - Haz clic en "Launch Instance"

2. **Configurar la instancia:**
   - **Name**: `resq-api-server`
   - **AMI**: Amazon Linux 2023 (o Ubuntu 22.04 LTS)
   - **Instance type**: `t3.micro` (para desarrollo) o `t3.small` (para producción)
   - **Key pair**: Crea o selecciona un par de claves SSH
   - **Network settings**: 
     - VPC: default
     - Subnet: default
     - Auto-assign Public IP: Enable
     - Security group: Crear nuevo (lo configuraremos después)

3. **Storage**: 20 GB (gp3)

4. **Launch Instance**

### 2.2 Desde AWS CLI

```bash
# Crear par de claves SSH (si no tienes uno)
aws ec2 create-key-pair --key-name resq-key --query 'KeyMaterial' --output text > resq-key.pem
chmod 400 resq-key.pem

# Obtener el ID de la imagen más reciente de Amazon Linux 2023
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-2023*" "Name=architecture,Values=x86_64" \
    --query 'Images[0].ImageId' --output text)

# Crear instancia
aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name resq-key \
    --security-group-ids sg-XXXXX \
    --subnet-id subnet-XXXXX \
    --associate-public-ip-address \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=resq-api-server}]'
```

---

## 3. Configurar Security Groups

### 3.1 Crear Security Group

```bash
# Crear security group
SG_ID=$(aws ec2 create-security-group \
    --group-name resq-api-sg \
    --description "Security group for ResQ API" \
    --query 'GroupId' --output text)

echo "Security Group ID: $SG_ID"
```

### 3.2 Agregar Reglas

```bash
# Permitir SSH (puerto 22) - Solo desde tu IP (recomendado)
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr $MY_IP/32

# Permitir HTTP (puerto 80)
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Permitir HTTPS (puerto 443)
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Permitir puerto de la API (8000) - Solo desde tu IP o VPC
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0
```

### 3.3 Asociar Security Group a la Instancia

```bash
# Obtener ID de la instancia
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=resq-api-server" "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].InstanceId' --output text)

# Asociar security group
aws ec2 modify-instance-attribute \
    --instance-id $INSTANCE_ID \
    --groups $SG_ID
```

---

## 4. Crear Base de Datos RDS (PostgreSQL)

### 4.1 Crear Subnet Group

```bash
# Obtener VPC ID y Subnets
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text)

# Crear DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name resq-db-subnet \
    --db-subnet-group-description "Subnet group for ResQ database" \
    --subnet-ids $SUBNET_IDS
```

### 4.2 Crear Security Group para RDS

```bash
# Crear security group para RDS
RDS_SG_ID=$(aws ec2 create-security-group \
    --group-name resq-rds-sg \
    --description "Security group for ResQ RDS" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

# Permitir PostgreSQL desde el security group de EC2
aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG_ID \
    --protocol tcp \
    --port 5432 \
    --source-group $SG_ID
```

### 4.3 Crear Instancia RDS

```bash
# Crear instancia RDS PostgreSQL
aws rds create-db-instance \
    --db-instance-identifier resq-postgres \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password TU_CONTRASEÑA_SEGURA \
    --allocated-storage 20 \
    --storage-type gp3 \
    --vpc-security-group-ids $RDS_SG_ID \
    --db-subnet-group-name resq-db-subnet \
    --backup-retention-period 7 \
    --publicly-accessible \
    --storage-encrypted
```

**Nota:** Esto puede tardar 5-10 minutos. Verifica el estado:

```bash
aws rds describe-db-instances --db-instance-identifier resq-postgres --query 'DBInstances[0].DBInstanceStatus'
```

### 4.4 Crear Base de Datos y Usuario

Una vez que RDS esté disponible:

```bash
# Obtener endpoint de RDS
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier resq-postgres \
    --query 'DBInstances[0].Endpoint.Address' --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"
```

Conéctate a RDS desde tu instancia EC2 (ver sección 6) y ejecuta:

```sql
CREATE DATABASE resq;
CREATE USER app_user WITH PASSWORD 'APP_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE resq TO app_user;
```

---

## 5. Crear Redis ElastiCache

### 5.1 Crear Subnet Group para ElastiCache

```bash
# Crear subnet group para ElastiCache
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name resq-redis-subnet \
    --cache-subnet-group-description "Subnet group for ResQ Redis" \
    --subnet-ids $SUBNET_IDS
```

### 5.2 Crear Security Group para ElastiCache

```bash
# Crear security group para ElastiCache
REDIS_SG_ID=$(aws ec2 create-security-group \
    --group-name resq-redis-sg \
    --description "Security group for ResQ Redis" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

# Permitir Redis desde el security group de EC2
aws ec2 authorize-security-group-ingress \
    --group-id $REDIS_SG_ID \
    --protocol tcp \
    --port 6379 \
    --source-group $SG_ID
```

### 5.3 Crear Cluster de Redis

```bash
# Crear cluster de Redis
aws elasticache create-cache-cluster \
    --cache-cluster-id resq-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --engine-version 7.0 \
    --num-cache-nodes 1 \
    --cache-subnet-group-name resq-redis-subnet \
    --security-group-ids $REDIS_SG_ID \
    --port 6379
```

**Nota:** Esto puede tardar 5-10 minutos. Verifica el estado:

```bash
aws elasticache describe-cache-clusters \
    --cache-cluster-id resq-redis \
    --show-cache-node-info \
    --query 'CacheClusters[0].CacheClusterStatus'
```

### 5.4 Obtener Endpoint de Redis

```bash
# Obtener endpoint de Redis
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
    --cache-cluster-id resq-redis \
    --show-cache-node-info \
    --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' --output text)

echo "Redis Endpoint: $REDIS_ENDPOINT"
```

---

## 6. Conectar a la Instancia EC2

### 6.1 Obtener IP Pública

```bash
# Obtener IP pública de la instancia
PUBLIC_IP=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=resq-api-server" "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "IP Pública: $PUBLIC_IP"
```

### 6.2 Conectar por SSH

**Linux/Mac:**
```bash
ssh -i resq-key.pem ec2-user@$PUBLIC_IP
```

**Windows (PowerShell):**
```powershell
ssh -i resq-key.pem ec2-user@$PUBLIC_IP
```

**Nota:** Para Ubuntu, el usuario es `ubuntu` en lugar de `ec2-user`.

---

## 7. Configurar el Servidor

Una vez conectado a la instancia EC2, ejecuta estos comandos:

### 7.1 Actualizar el Sistema

**Amazon Linux 2023:**
```bash
sudo dnf update -y
```

**Ubuntu:**
```bash
sudo apt update && sudo apt upgrade -y
```

### 7.2 Instalar Python 3.11 y Dependencias

**Amazon Linux 2023:**
```bash
# Instalar Python 3.11
sudo dnf install -y python3.11 python3.11-pip python3.11-venv git gcc postgresql15

# Crear enlace simbólico
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
```

**Ubuntu:**
```bash
# Instalar Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git gcc postgresql-client libpq-dev
```

### 7.3 Instalar Redis (Cliente)

**Amazon Linux 2023:**
```bash
sudo dnf install -y redis6
```

**Ubuntu:**
```bash
sudo apt install -y redis-tools
```

### 7.4 Crear Usuario para la Aplicación

```bash
# Crear usuario
sudo useradd -m -s /bin/bash resq
sudo mkdir -p /opt/resq
sudo chown resq:resq /opt/resq
```

---

## 8. Desplegar la Aplicación

### 8.1 Clonar o Subir el Código

**Opción A: Desde Git (si tienes repositorio)**
```bash
sudo -u resq git clone https://github.com/tu-usuario/ResQ.git /opt/resq
```

**Opción B: Subir archivos con SCP**
```bash
# Desde tu máquina local
cd ResQ
scp -i resq-key.pem -r . ec2-user@$PUBLIC_IP:/tmp/resq
```

Luego en la instancia EC2:
```bash
sudo mv /tmp/resq/* /opt/resq/
sudo chown -R resq:resq /opt/resq
```

### 8.2 Configurar Entorno Virtual

```bash
sudo -u resq bash
cd /opt/resq

# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 8.3 Configurar Variables de Entorno

```bash
# Crear archivo .env
sudo -u resq nano /opt/resq/.env
```

Agregar:

```env
# Base de datos RDS
DATABASE_URL=postgresql://app_user:APP_PASSWORD@RDS_ENDPOINT:5432/resq

# JWT
JWT_SECRET_KEY=TU_CLAVE_SECRETA_GENERADA
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

**Reemplazar:**
- `RDS_ENDPOINT`: El endpoint de RDS obtenido en 4.4
- `APP_PASSWORD`: La contraseña del usuario de la base de datos
- `REDIS_ENDPOINT`: El endpoint de Redis obtenido en 5.4
- `TU_CLAVE_SECRETA_GENERADA`: Generar con `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### 8.4 Probar la Aplicación

```bash
# Activar entorno virtual
source /opt/resq/venv/bin/activate

# Probar que funciona
cd /opt/resq
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Presiona `Ctrl+C` para detener.

---

## 9. Configurar como Servicio

### 9.1 Crear Archivo de Servicio systemd

```bash
sudo nano /etc/systemd/system/resq-api.service
```

Agregar:

```ini
[Unit]
Description=ResQ API Service
After=network.target

[Service]
Type=simple
User=resq
WorkingDirectory=/opt/resq
Environment="PATH=/opt/resq/venv/bin"
ExecStart=/opt/resq/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9.2 Habilitar y Iniciar el Servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio (inicia automáticamente al arrancar)
sudo systemctl enable resq-api

# Iniciar servicio
sudo systemctl start resq-api

# Verificar estado
sudo systemctl status resq-api

# Ver logs
sudo journalctl -u resq-api -f
```

### 9.3 Comandos Útiles del Servicio

```bash
# Iniciar
sudo systemctl start resq-api

# Detener
sudo systemctl stop resq-api

# Reiniciar
sudo systemctl restart resq-api

# Ver estado
sudo systemctl status resq-api

# Ver logs
sudo journalctl -u resq-api -n 50
```

---

## 10. Configurar Nginx (Opcional)

Nginx actúa como proxy reverso y permite usar puerto 80/443.

### 10.1 Instalar Nginx

**Amazon Linux 2023:**
```bash
sudo dnf install -y nginx
```

**Ubuntu:**
```bash
sudo apt install -y nginx
```

### 10.2 Configurar Nginx

```bash
sudo nano /etc/nginx/conf.d/resq-api.conf
```

Agregar:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

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
    }
}
```

### 10.3 Iniciar Nginx

```bash
# Verificar configuración
sudo nginx -t

# Iniciar Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Verificar estado
sudo systemctl status nginx
```

---

## 11. Configurar Dominio y SSL (Opcional)

### 11.1 Configurar DNS

En tu proveedor de DNS, agrega un registro A apuntando a la IP pública de tu instancia EC2.

### 11.2 Instalar Certbot

```bash
# Amazon Linux 2023
sudo dnf install -y certbot python3-certbot-nginx

# Ubuntu
sudo apt install -y certbot python3-certbot-nginx
```

### 11.3 Obtener Certificado SSL

```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Certbot configurará automáticamente Nginx para usar HTTPS.

---

## 12. Solución de Problemas

### Error: "No se puede conectar a la base de datos"

**Causas posibles:**
1. Security group de RDS no permite conexiones desde EC2
   - Solución: Verificar reglas del security group (paso 4.2)

2. RDS no es públicamente accesible
   - Solución: Verificar que `--publicly-accessible` esté configurado

3. Credenciales incorrectas
   - Solución: Verificar usuario y contraseña en `.env`

### Error: "Redis connection refused"

**Causas posibles:**
1. Security group de ElastiCache no permite conexiones
   - Solución: Verificar reglas del security group (paso 5.2)

2. ElastiCache está en una subnet diferente
   - Solución: Verificar que esté en el mismo VPC

### El servicio no inicia

**Verificar:**
```bash
# Ver logs del servicio
sudo journalctl -u resq-api -n 100

# Verificar permisos
ls -la /opt/resq

# Verificar que el usuario existe
id resq
```

### Puerto 8000 no es accesible

**Verificar:**
1. Security group permite tráfico en puerto 8000
2. Firewall del sistema permite el puerto:
   ```bash
   sudo firewall-cmd --list-ports  # Amazon Linux
   sudo ufw status                 # Ubuntu
   ```

---

## 📝 Checklist Final

- [ ] Instancia EC2 creada y accesible
- [ ] Security groups configurados correctamente
- [ ] RDS PostgreSQL creado y accesible
- [ ] Redis ElastiCache creado y accesible
- [ ] Aplicación desplegada en `/opt/resq`
- [ ] Variables de entorno configuradas en `.env`
- [ ] Servicio systemd configurado y funcionando
- [ ] Nginx configurado (opcional)
- [ ] SSL configurado (opcional)
- [ ] Health check responde (`/health`)
- [ ] Swagger UI accesible (`/docs`)

---

## 🔄 Actualizar la Aplicación

Para actualizar después de hacer cambios:

```bash
# Conectarse a EC2
ssh -i resq-key.pem ec2-user@$PUBLIC_IP

# Detener servicio
sudo systemctl stop resq-api

# Actualizar código (desde Git o SCP)
cd /opt/resq
git pull  # O subir nuevos archivos

# Activar entorno virtual y actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl start resq-api
```

---

## 💰 Estimación de Costos AWS

**Desarrollo/Pruebas (mínimo):**
- EC2 (t3.micro): ~$7-10/mes
- RDS (db.t3.micro): ~$15-20/mes
- ElastiCache (cache.t3.micro): ~$12-15/mes
- **Total aproximado: ~$35-45/mes**

**Producción:**
- EC2 (t3.small): ~$15-20/mes
- RDS (db.t3.small): ~$50-70/mes
- ElastiCache (cache.t3.small): ~$30-40/mes
- **Total aproximado: ~$95-130/mes**

---

## 📚 Recursos Adicionales

- [Documentación de EC2](https://docs.aws.amazon.com/ec2/)
- [Documentación de RDS](https://docs.aws.amazon.com/rds/)
- [Documentación de ElastiCache](https://docs.aws.amazon.com/elasticache/)
- [Precios de AWS](https://aws.amazon.com/pricing/)

---

**¡Despliegue completado! 🎉**

Si tienes problemas, revisa los logs y la sección de solución de problemas.

