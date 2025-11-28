# 🚀 Despliegue Rápido en AWS EC2

Guía rápida para desplegar ResQ en AWS. Para detalles completos, ver:
- [GUIA_DESPLIEGUE_AWS_WEB.md](GUIA_DESPLIEGUE_AWS_WEB.md) - **Desde la consola web (con SSL)**
- [GUIA_DESPLIEGUE_AWS_EC2.md](GUIA_DESPLIEGUE_AWS_EC2.md) - Desde línea de comandos

## ⚡ Pasos Rápidos

### 1. Prerrequisitos
```bash
# Instalar AWS CLI
# https://aws.amazon.com/cli/

# Configurar credenciales
aws configure
```

### 2. Crear Instancia EC2
```bash
# Crear par de claves
aws ec2 create-key-pair --key-name resq-key --query 'KeyMaterial' --output text > resq-key.pem
chmod 400 resq-key.pem

# Crear security group
SG_ID=$(aws ec2 create-security-group \
    --group-name resq-api-sg \
    --description "ResQ API Security Group" \
    --query 'GroupId' --output text)

# Permitir puertos
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0

# Obtener AMI de Amazon Linux 2023
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-2023*" "Name=architecture,Values=x86_64" \
    --query 'Images[0].ImageId' --output text)

# Crear instancia
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name resq-key \
    --security-group-ids $SG_ID \
    --associate-public-ip-address \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=resq-api-server}]' \
    --query 'Instances[0].InstanceId' --output text)

echo "Instancia creada: $INSTANCE_ID"
```

### 3. Crear RDS PostgreSQL
```bash
# Obtener VPC y Subnets
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text)

# Crear DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name resq-db-subnet \
    --db-subnet-group-description "ResQ DB Subnet" \
    --subnet-ids $SUBNET_IDS

# Crear Security Group para RDS
RDS_SG_ID=$(aws ec2 create-security-group \
    --group-name resq-rds-sg \
    --description "ResQ RDS Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG_ID \
    --protocol tcp \
    --port 5432 \
    --source-group $SG_ID

# Crear RDS
aws rds create-db-instance \
    --db-instance-identifier resq-postgres \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password TU_CONTRASEÑA_SEGURA \
    --allocated-storage 20 \
    --vpc-security-group-ids $RDS_SG_ID \
    --db-subnet-group-name resq-db-subnet \
    --publicly-accessible
```

### 4. Crear Redis ElastiCache
```bash
# Crear Subnet Group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name resq-redis-subnet \
    --cache-subnet-group-description "ResQ Redis Subnet" \
    --subnet-ids $SUBNET_IDS

# Crear Security Group para Redis
REDIS_SG_ID=$(aws ec2 create-security-group \
    --group-name resq-redis-sg \
    --description "ResQ Redis Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $REDIS_SG_ID \
    --protocol tcp \
    --port 6379 \
    --source-group $SG_ID

# Crear Redis
aws elasticache create-cache-cluster \
    --cache-cluster-id resq-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --engine-version 7.0 \
    --num-cache-nodes 1 \
    --cache-subnet-group-name resq-redis-subnet \
    --security-group-ids $REDIS_SG_ID
```

### 5. Conectar a EC2 y Configurar
```bash
# Obtener IP pública
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "Conectarse con: ssh -i resq-key.pem ec2-user@$PUBLIC_IP"
```

### 6. Script de Configuración en el Servidor

Una vez conectado a EC2, ejecuta:

```bash
# Instalar dependencias
sudo dnf update -y
sudo dnf install -y python3.11 python3.11-pip python3.11-venv git gcc postgresql15

# Crear usuario y directorio
sudo useradd -m -s /bin/bash resq
sudo mkdir -p /opt/resq
sudo chown resq:resq /opt/resq

# Subir código (desde tu máquina local)
# scp -i resq-key.pem -r ResQ/* ec2-user@$PUBLIC_IP:/tmp/resq
# Luego en EC2: sudo mv /tmp/resq/* /opt/resq/

# Configurar aplicación
sudo -u resq bash
cd /opt/resq
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Crear .env
nano .env
# Agregar variables de entorno (ver guía completa)

# Probar
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 7. Configurar como Servicio

```bash
# Crear servicio systemd
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

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar
sudo systemctl daemon-reload
sudo systemctl enable resq-api
sudo systemctl start resq-api
sudo systemctl status resq-api
```

## 📝 Variables de Entorno (.env)

```env
DATABASE_URL=postgresql://app_user:password@RDS_ENDPOINT:5432/resq
JWT_SECRET_KEY=generar_con_python_secrets
JWT_EXPIRE_MINUTES=1440
REDIS_HOST=REDIS_ENDPOINT
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## 🔗 Obtener Endpoints

```bash
# RDS Endpoint
aws rds describe-db-instances \
    --db-instance-identifier resq-postgres \
    --query 'DBInstances[0].Endpoint.Address' --output text

# Redis Endpoint
aws elasticache describe-cache-clusters \
    --cache-cluster-id resq-redis \
    --show-cache-node-info \
    --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' --output text
```

## ✅ Verificar

```bash
# Obtener IP pública
PUBLIC_IP=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=resq-api-server" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# Probar
curl http://$PUBLIC_IP:8000/health
curl http://$PUBLIC_IP:8000/
echo "Swagger: http://$PUBLIC_IP:8000/docs"
```

## 💰 Costos Estimados

- EC2 t3.micro: ~$7-10/mes
- RDS db.t3.micro: ~$15-20/mes
- ElastiCache cache.t3.micro: ~$12-15/mes
- **Total: ~$35-45/mes**

## 🔄 Actualizar

```bash
# Conectarse a EC2
ssh -i resq-key.pem ec2-user@$PUBLIC_IP

# Detener servicio
sudo systemctl stop resq-api

# Actualizar código
cd /opt/resq
# git pull o subir nuevos archivos

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar
sudo systemctl start resq-api
```

## 📚 Más Información

- [Guía Completa](GUIA_DESPLIEGUE_AWS_EC2.md)
- [Documentación AWS](https://docs.aws.amazon.com/)

