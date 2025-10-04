from fastapi import Depends, FastAPI
from sqlmodel import Session
from typing import Annotated

from models.producto import ProductoCrear, ProductoActualizar, ProductoPublico
from crud.producto_crud import crear_producto, leer_productos, leer_producto, actualizar_producto, eliminar_producto
from database import engine

app = FastAPI()

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/productos/", response_model=ProductoPublico)
def crear_producto_endpoint(producto: ProductoCrear, session: SessionDep):
    return crear_producto(producto, session)

@app.get("/productos/", response_model=list[ProductoPublico])
def leer_productos_endpoint(session: SessionDep):
    return leer_productos(session)

@app.get("/productos/{producto_id}", response_model=ProductoPublico)
def leer_producto_endpoint(producto_id: int, session: SessionDep):
    return leer_producto(producto_id, session)

@app.patch("/productos/{producto_id}", response_model=ProductoPublico)
def actualizar_producto_endpoint(producto_id: int, producto: ProductoActualizar, session: SessionDep):
    return actualizar_producto(producto_id, producto, session)

@app.delete("/productos/{producto_id}")
def eliminar_producto_endpoint(producto_id: int, session: SessionDep):
    return eliminar_producto(producto_id, session)
