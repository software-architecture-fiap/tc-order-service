from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database.database import get_db
from ..models import schemas
from ..services import repository
from ..services.security import verify_token
from ..tools.logging import logger

router = APIRouter()


# ------------------------ CRIAÇÃO DE PEDIDOS ------------------------
@router.post("/", response_model=dict)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Cria um novo pedido. Apenas clientes autenticados podem criar pedidos.
    """
    logger.info(
        f"Cliente {user['id']} criando pedido com "
        f"{len(order.order_items)} itens."
        )

    new_order = repository.create_order(db, order)

    logger.info(f"Pedido criado com sucesso: ID {new_order['id']}")
    return new_order


# ------------------------ CONSULTAR PEDIDOS ------------------------
@router.get("/", response_model=List[schemas.OrderRead])
def get_orders(
    order_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Obtém pedidos com base em filtros opcionais.
    """
    logger.info(
        f"🔍 Recebida requisição para buscar pedidos "
        f"(skip={skip}, limit={limit}, "
        f"customer_id={customer_id}, order_id={order_id}, status={status})"
        f"customer_id={customer_id}, order_id={order_id}, status={status})"
    )

    if order_id:
        order = repository.get_order(db, order_id)
        if not order:
            logger.warning(f"⚠️ Pedido ID {order_id} não encontrado!")
            raise HTTPException(
                status_code=404,
                detail="Pedido não encontrado")
        return [order]

    orders = repository.get_orders(db, skip=skip, limit=limit)

    if customer_id:
        filtered_orders = [
            o for o in orders if o["customer_id"] == customer_id
        ]
        logger.info(
            f"🔍 {len(filtered_orders)} pedidos encontrados para o cliente "
            f"{customer_id}"
        )
        return filtered_orders

    if status:
        filtered_orders = [o for o in orders if o["status"] == status]
        logger.info(
            f"🔍 {len(filtered_orders)} pedidos encontrados com status "
            f"'{status}'"
            )
        return filtered_orders

    logger.info(f"✅ Retornando {len(orders)} pedidos encontrados")
    return orders


# ------------------------ ATUALIZAR STATUS DO PEDIDO ------------------------
@router.patch("/{order_id}", response_model=schemas.OrderRead)
def update_order_status(
    order_id: int,
    order_update: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Atualiza o status de um pedido.
    """
    if not order_update.status:
        logger.warning(
            f"Tentativa de atualizar pedido {order_id} sem fornecer um "
            f"status válido"
            )
        raise HTTPException(
            status_code=400,
            detail="Status do pedido é obrigatório para atualização"
        )

    logger.info(
        f"Usuário {user['id']} alterando status do pedido {order_id} "
        f"para {order_update.status}"
        )

    updated_order = repository.update_order_status(db, order_id, order_update)
    if not updated_order:
        logger.warning(
            f"Tentativa de atualizar pedido ID {order_id} que não existe"
            )
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
            )

    logger.info(
        f"Pedido {order_id} atualizado com sucesso para {order_update.status}"
        )
    return updated_order
