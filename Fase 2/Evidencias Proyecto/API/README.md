# API de la DB para la plataforma de eCommerce Cordillera Pets

## IMPORTANTE

Es necesario que en la carpeta raíz del proyecto esté presente el certificado CA y crear un archivo `.env` con las siguientes variables:

```
DB_HOST=Dirección del host
DB_PORT=Puerto
DB_NAME=Nombre base de datos
DB_USER=Usuario API
DB_PASSWORD=Contraseña usuario API

DB_ROOT_CERT=Ruta certificado
```

### Dependencias:

- FastAPI
- SQLModel
- PyMySQL
