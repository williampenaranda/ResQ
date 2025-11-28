#!/bin/bash

# Script para configurar el servidor EC2 con ResQ
# Ejecutar como root o con sudo

set -e

echo "🚀 Configurando servidor EC2 para ResQ"
echo "======================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Detectar sistema operativo
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}No se pudo detectar el sistema operativo${NC}"
    exit 1
fi

echo -e "${YELLOW}Sistema detectado: $OS${NC}"

# Actualizar sistema
echo -e "${YELLOW}📦 Actualizando sistema...${NC}"
if [ "$OS" == "amzn" ] || [ "$OS" == "rhel" ]; then
    sudo dnf update -y
elif [ "$OS" == "ubuntu" ] || [ "$OS" == "debian" ]; then
    sudo apt update && sudo apt upgrade -y
fi

# Instalar Python 3.11
echo -e "${YELLOW}🐍 Instalando Python 3.11...${NC}"
if [ "$OS" == "amzn" ] || [ "$OS" == "rhel" ]; then
    sudo dnf install -y python3.11 python3.11-pip python3.11-venv git gcc postgresql15
    sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    sudo alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
elif [ "$OS" == "ubuntu" ] || [ "$OS" == "debian" ]; then
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git gcc postgresql-client libpq-dev
fi

# Crear usuario y directorio
echo -e "${YELLOW}👤 Creando usuario resq...${NC}"
if ! id "resq" &>/dev/null; then
    sudo useradd -m -s /bin/bash resq
fi

sudo mkdir -p /opt/resq
sudo chown resq:resq /opt/resq

# Verificar que el código esté en /opt/resq
if [ ! -f "/opt/resq/requirements.txt" ]; then
    echo -e "${RED}❌ Error: No se encontró requirements.txt en /opt/resq${NC}"
    echo "Por favor, sube el código primero:"
    echo "  scp -i key.pem -r ResQ/* ec2-user@IP:/tmp/resq"
    echo "  sudo mv /tmp/resq/* /opt/resq/"
    exit 1
fi

# Configurar entorno virtual
echo -e "${YELLOW}📦 Configurando entorno virtual...${NC}"
sudo -u resq bash << 'EOF'
cd /opt/resq
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Crear archivo .env si no existe
if [ ! -f "/opt/resq/.env" ]; then
    echo -e "${YELLOW}📝 Creando archivo .env de ejemplo...${NC}"
    sudo -u resq bash << 'EOF'
cd /opt/resq
cat > .env << 'ENVFILE'
# Base de datos RDS
DATABASE_URL=postgresql://app_user:password@RDS_ENDPOINT:5432/resq

# JWT
JWT_SECRET_KEY=change-me-in-production
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
ENVFILE
    echo -e "${YELLOW}⚠️  Por favor, edita /opt/resq/.env con tus valores reales${NC}"
fi

# Crear servicio systemd
echo -e "${YELLOW}⚙️  Configurando servicio systemd...${NC}"
sudo tee /etc/systemd/system/resq-api.service > /dev/null << 'EOF'
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
EOF

# Recargar systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✅ Configuración completada${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Edita /opt/resq/.env con tus valores reales"
echo "2. Inicia el servicio: sudo systemctl start resq-api"
echo "3. Habilita inicio automático: sudo systemctl enable resq-api"
echo "4. Verifica estado: sudo systemctl status resq-api"
echo "5. Ver logs: sudo journalctl -u resq-api -f"


