from fastapi import HTTPException
from sqlmodel import Session, select
from models.producto import Producto, ProductoCrear, ProductoActualizar, ProductoPublico

# CRUD de productos

def crear_producto(producto: ProductoCrear, session: Session) -> ProductoPublico:
    db_producto = Producto.model_validate(producto)
    session.add(db_producto)
    session.commit()
    session.refresh(db_producto)
    return db_producto


def leer_productos(session: Session) -> list[ProductoPublico]:
    productos = session.exec(select(Producto)).all()
    return productos


def leer_producto(producto_id: int, session: Session) -> ProductoPublico:
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


def actualizar_producto(producto_id: int, producto: ProductoActualizar, session: Session) -> ProductoPublico:
    producto_db = session.get(Producto, producto_id)
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto_data = producto.model_dump(exclude_unset=True)
    producto_db.sqlmodel_update(producto_data)
    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    return producto_db


def eliminar_producto(producto_id: int, session: Session) -> dict:
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    session.delete(producto)
    session.commit()
    return {"ok": True}
