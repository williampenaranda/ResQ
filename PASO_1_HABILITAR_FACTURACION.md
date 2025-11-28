# 💳 Paso 1: Habilitar Facturación en Google Cloud

## ⚠️ Error Actual
```
FAILED_PRECONDITION: Billing account for project is not found. 
Billing must be enabled for activation of service(s)
```

## ✅ Solución: Habilitar Facturación

### Opción 1: Desde la Consola Web (Recomendado)

1. **Abre la consola de Google Cloud:**
   - Ve a: https://console.cloud.google.com/billing
   - O directamente: https://console.cloud.google.com/billing/linkedaccount?project=resq-479403

2. **Vincula una cuenta de facturación:**
   - Si ya tienes una cuenta de facturación, selecciónala
   - Si no tienes una, haz clic en "Crear cuenta de facturación"
   - Necesitarás una tarjeta de crédito (Google ofrece $300 USD de crédito gratuito por 90 días)

3. **Vincula la cuenta al proyecto:**
   - Selecciona tu proyecto `resq-479403`
   - Haz clic en "Vincular cuenta de facturación"

### Opción 2: Desde la Línea de Comandos

```bash
# Listar cuentas de facturación disponibles
gcloud billing accounts list

# Vincular cuenta de facturación al proyecto
# Reemplaza BILLING_ACCOUNT_ID con el ID de tu cuenta
gcloud billing projects link resq-479403 --billing-account=BILLING_ACCOUNT_ID
```

## 💰 Información sobre Costos

### Crédito Gratuito de Google Cloud
- **$300 USD** de crédito gratuito por 90 días para nuevos usuarios
- Perfecto para probar y desarrollar

### Costos Estimados del Proyecto ResQ

**Desarrollo/Pruebas (mínimo):**
- Cloud Run: ~$0 (hasta cierto límite de requests)
- Cloud SQL (db-f1-micro): ~$7-10/mes
- Memorystore Redis (1GB basic): ~$30/mes
- **Total aproximado: ~$40-50/mes**

**Producción:**
- Cloud Run: Depende del tráfico
- Cloud SQL (db-n1-standard-1): ~$50-100/mes
- Memorystore Redis (5GB standard): ~$150/mes
- **Total aproximado: ~$200-300/mes** (depende del uso)

### Consejos para Ahorrar
- Usa `db-f1-micro` para desarrollo (más económico)
- Configura `--min-instances=0` en Cloud Run (escala a cero cuando no hay tráfico)
- Usa Memorystore `basic` tier para desarrollo
- Monitorea los costos en: https://console.cloud.google.com/billing

## ✅ Verificar que la Facturación Está Habilitada

Después de vincular la cuenta de facturación, verifica:

```bash
# Verificar estado de facturación del proyecto
gcloud billing projects describe resq-479403
```

Deberías ver algo como:
```
billingAccountName: billingAccounts/XXXXXX-XXXXXX-XXXXXX
billingEnabled: true
```

## 🚀 Siguiente Paso

Una vez que la facturación esté habilitada, continúa con:

```bash
# Habilitar APIs necesarias
gcloud services enable run.googleapis.com sqladmin.googleapis.com \
    cloudbuild.googleapis.com redis.googleapis.com \
    secretmanager.googleapis.com compute.googleapis.com
```

---

**Nota:** Si no quieres usar servicios de pago ahora, puedes desarrollar localmente usando:
- PostgreSQL local o Docker
- Redis local o Docker
- Y desplegar solo cuando estés listo para producción


