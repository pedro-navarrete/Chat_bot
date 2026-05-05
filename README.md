# Chat_bot — WhatsApp Media → MinIO

Bot en Python/FastAPI que recibe documentos, imágenes, videos y audios desde
WhatsApp y los almacena automáticamente en **MinIO** (compatible con S3).

Actualmente soporta dos proveedores de WhatsApp intercambiables mediante una
variable de entorno:

| `WHATSAPP_PROVIDER` | Descripción |
|---|---|
| `evolution` (default) | [Evolution API](https://github.com/EvolutionAPI/evolution-api) – open-source, basado en Baileys/WhatsApp Web |
| `cloud` | WhatsApp Cloud API oficial (graph.facebook.com) |

## Arquitectura

```
WhatsApp ⇄ Evolution API ──webhook──▶ Chat_bot (FastAPI) ──put_object──▶ MinIO
               │                            │
               └────── REST API ────────────┘
                     (descarga de media)
```

## Estructura de archivos en MinIO

```
{from_number}/{YYYY-MM-DD}/{msg_id}.{ext}
# Ejemplo con documento:
521555XXXXXXX/2025-01-01/ABCDEF1234_factura.pdf
```

## Requisitos previos

- Docker y Docker Compose v2
- Puerto 8000 (bot), 8080 (Evolution API), 9000-9001 (MinIO) disponibles

## Configuración

```bash
cp .env.example .env
# Editar .env con tus valores (mínimo: EVOLUTION_API_KEY)
```

Variables principales:

```dotenv
WHATSAPP_PROVIDER=evolution      # "evolution" | "cloud"

# Evolution API
EVOLUTION_URL=http://localhost:8080
EVOLUTION_API_KEY=your_secret_key
EVOLUTION_INSTANCE=default

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET=whatsapp-files
```

## Levantar el stack completo

```bash
docker compose up -d
```

Esto levanta: **PostgreSQL + Redis** (requeridos por Evolution API),
**Evolution API**, **MinIO + minio-init** (crea el bucket), y **chat_bot**.

Verificar que todo está corriendo:

```bash
docker compose ps
curl http://localhost:8000/health   # → {"status":"ok"}
```

## Conectar WhatsApp (Evolution API)

### 1. Crear instancia

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: $EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"instanceName":"default","integration":"WHATSAPP-BAILEYS","qrcode":true}'
```

### 2. Obtener QR

```bash
curl http://localhost:8080/instance/connect/default \
  -H "apikey: $EVOLUTION_API_KEY"
```

La respuesta incluye un campo `base64` con el QR. Cópialo en
[https://www.base64-image.de](https://www.base64-image.de) o usa la consola de
Evolution API (http://localhost:8080) para verlo.

### 3. Escanear desde WhatsApp

Abre WhatsApp en tu teléfono → **Dispositivos vinculados** → **Vincular
dispositivo** → escanea el QR.

Una vez conectado, cualquier archivo que recibas en ese número se guardará
automáticamente en MinIO.

## Cambiar a WhatsApp Cloud API (oficial)

Cuando tengas acceso a la Cloud API de Meta:

```dotenv
WHATSAPP_PROVIDER=cloud
WHATSAPP_TOKEN=tu_token
PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_VERIFY_TOKEN=tu_verify_token
```

Reinicia el bot. El endpoint `POST /webhook` y el `GET /webhook` (verificación)
se activarán automáticamente. No es necesario tocar código.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Healthcheck — devuelve `{"status":"ok"}` |
| `POST` | `/webhook/evolution` | Recibe eventos de Evolution API |
| `POST` | `/webhook` | Recibe eventos de WhatsApp Cloud API (solo si `WHATSAPP_PROVIDER=cloud`) |
| `GET` | `/webhook` | Verificación de webhook para Cloud API |

## Desarrollo y tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Troubleshooting

**El QR expiró / sesión desconectada**

```bash
curl http://localhost:8080/instance/connect/default -H "apikey: $EVOLUTION_API_KEY"
```

Vuelve a escanear el QR generado.

**Ver logs del bot**

```bash
docker compose logs -f chat_bot
```

Los logs incluyen `provider`, `instance`, `message_id`, `from_number` y
`media_type` para cada mensaje procesado.

**MinIO: ver los archivos**

Accede a la consola en http://localhost:9001 con las credenciales de
`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`.

**Webhook no recibe eventos**

Asegúrate de que `WEBHOOK_GLOBAL_URL` en Evolution API apunta a la dirección
accesible desde el contenedor (`http://chat_bot:8000/webhook/evolution` en el
stack de Docker, o tu IP pública si Evolution corre externamente).

**Error 401 en `/webhook/evolution`**

El header `apikey` enviado por Evolution debe coincidir con `EVOLUTION_API_KEY`
en tu `.env`.
