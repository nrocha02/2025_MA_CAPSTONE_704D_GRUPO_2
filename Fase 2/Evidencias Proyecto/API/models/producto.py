import datetime
from sqlmodel import Field, SQLModel
from .estado_producto import EstadoProducto

class ProductoBase(SQLModel):
    categoria_id: int
    sku: str | None
    nombre: str
    descripcion: str | None
    precio: int
    stock: int
    imagen_url: str | None
    fecha_creacion: datetime.datetime
    estado_producto: EstadoProducto

class Producto(ProductoBase, table=True):
    producto_id: int | None = Field(default=None, primary_key=True)

class ProductoPublico(ProductoBase):
    producto_id: int

class ProductoCrear(ProductoBase):
    pass

class ProductoActualizar(ProductoBase):
    categoria_id: int | None = None
    sku: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    precio: int | None = None
    stock: int | None = None
    imagen_url: str | None = None
    fecha_creacion: datetime.datetime | None = None
    estado_producto: EstadoProducto | None = None
