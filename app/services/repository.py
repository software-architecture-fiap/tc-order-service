import requests
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from os import environ as env
import time

from ..models import models, schemas
from ..tools.logging import logger

# Definição da URL do serviço de pagamento
PAYMENT_SERVICE_URL = env.get("PAYMENT_SERVICE_URL")
PRODUCT_NOT_FOUND = "Produto não encontrado"


# ---------------------- INTEGRAÇÃO COM O PAYMENT-SERVICE ------------------
def request_payment(
        order: models.Order,
        customer_email: str,
        db: Session,
        max_retries: int = 3) -> dict:
    """
    Solicita a geração de um pagamento no `payment-service`,
    com tentativas de retry.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payment_payload = {
        "order_id": str(order.id),
        "amount": calculate_total_amount(order, db),
        "customer_id": order.customer_id,
        "currency": "BRL",
        "email": customer_email or "cliente@example.com",
        "description": f"Pedido {order.id} - {len(order.order_items)} itens"
    }

    logger.info(f"Solicitando pagamento para pedido {order.id}")

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                f"{PAYMENT_SERVICE_URL}/payments/",
                json=payment_payload,
                headers=headers,
                timeout=2)
            logger.info(response)

            if response.status_code == 200:
                payment_data = response.json()
                logger.info(
                    f"Pagamento criado para pedido {order.id}: {payment_data}"
                    )

                # Atualiza status de pagamento no pedido
                order.payment_status = "awaiting_payment"
                db.commit()
                return payment_data

            else:
                logger.error(
                    f"⚠️ Erro ao criar pagamento para pedido {order.id} "
                    f"[Tentativa {attempt}/{max_retries}]: {response.text}"
                    )

        except requests.RequestException as e:
            logger.error(
                f"Erro de conexão com `payment-service` "
                f"[Tentativa {attempt}/{max_retries}]: {e}"
                )

        time.sleep(1)

    # Se todas as tentativas falharem, marca o pedido como
    # "payment_service_unavailable"
    order.payment_status = "payment_service_unavailable"
    db.commit()
    logger.error(
        f"Falha ao processar pagamento para pedido "
        f"{order.id} após {max_retries} tentativas.")

    return {"error": "payment_service_unavailable"}


# ------------------------ CATEGORIAS ------------------------
def get_categories(
        db: Session,
        skip: int = 0,
        limit: int = 10) -> List[schemas.CategoryRead]:
    """Obtém categorias ativas com paginação."""
    categories = (
        db.query(models.Category)
        .filter(models.Category.enabled is True)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        schemas.CategoryRead(
            id=cat.id,
            name=cat.name,
            enabled=cat.enabled
        )
        for cat in categories
    ]


def get_category(
        db: Session, category_id: int) -> Optional[schemas.CategoryRead]:
    """Obtém uma categoria pelo ID."""
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )
    if category:
        return schemas.CategoryRead(
            id=category.id,
            name=category.name,
            enabled=category.enabled
        )
    return None


def create_category(
        db: Session,
        category: schemas.CategoryCreate) -> models.Category:
    """Cria uma nova categoria."""
    db_category = models.Category(
        name=category.name,
        enabled=True  # Definindo como ativo por padrão
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
        db: Session,
        category_id: int,
        category_data: schemas.CategoryUpdate) -> Optional[models.Category]:
    """Atualiza uma categoria existente com qualquer campo opcional."""
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )
    if not category:
        return None

    update_data = category_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


# ------------------------ PRODUTOS ------------------------
def get_products(
        db: Session,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10) -> List[schemas.ProductRead]:
    """
    Obtém uma lista paginada de produtos ativos.
    Se `category_id` for informado, filtra por essa categoria.
    """
    query = db.query(models.Product).filter(models.Product.enabled is True)

    if category_id:
        query = query.filter(models.Product.category_id == category_id)

    products = query.offset(skip).limit(limit).all()

    return [
        schemas.ProductRead(
            id=p.id,
            name=p.name,
            price=p.price,
            category_id=p.category_id,
            enabled=p.enabled,
            category=schemas.CategoryRead(
                id=p.category.id,
                name=p.category.name,
                enabled=p.category.enabled) if p.category else None
        )
        for p in products
    ]


def get_product(db: Session, product_id: int) -> Optional[schemas.ProductRead]:
    """Obtém um produto pelo ID, incluindo detalhes da categoria."""
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if product:
        return schemas.ProductRead(
            id=product.id,
            name=product.name,
            price=product.price,
            category_id=product.category_id,
            enabled=product.enabled,
            category=schemas.CategoryRead(
                id=product.category.id,
                name=product.category.name,
                enabled=product.category.enabled
            ) if product.category else None
        )
    return None


def create_product(
        db: Session,
        product: schemas.ProductCreate) -> models.Product:
    """Cria um novo produto."""
    db_product = models.Product(
        name=product.name,
        price=product.price,
        category_id=product.category_id,
        enabled=True  # Produto ativo por padrão
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
        db: Session,
        product_id: int,
        product_data: schemas.ProductUpdate) -> Optional[models.Product]:
    """
    Atualiza um produto existente,
    permitindo modificar qualquer campo, incluindo 'enabled'."""
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )
    if not product:
        return None

    update_data = product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# ------------------------ PEDIDOS ------------------------
def get_order(db: Session, order_id: int) -> Optional[dict]:
    """Obtém um pedido pelo ID, garantindo que os itens sejam carregados."""
    logger.info(f"🔍 Buscando pedido {order_id} no banco de dados...")

    order = (
        db.query(models.Order)
        .options(
            joinedload(models.Order.order_items)
            .joinedload(models.OrderItem.product)
        )
        .filter(models.Order.id == order_id)
        .first()
    )

    if not order:
        logger.warning(
            f"⚠️ Pedido {order_id} não encontrado no banco de dados!"
            )
        return None

    logger.info(
        f"✅ Pedido {order_id} encontrado! Preparando resposta..."
        )

    total_amount = sum(
        (item.product.price * item.quantity) if item.product else 0
        for item in order.order_items
    )

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "payment_status": order.payment_status,
        "amount": total_amount,
        "qr_code": (
            order.qr_code if hasattr(order, "qr_code") else None
            ),
        "payment_link": (
            order.payment_link if hasattr(order, "payment_link") else None
        ),
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product.id if item.product else None,
                "name": (
                    item.product.name
                    if item.product
                    else PRODUCT_NOT_FOUND
                ),
                "price": item.product.price if item.product else 0.0,
                "quantity": item.quantity
            }
            for item in order.order_items
        ]
    }


def get_orders(db: Session, skip: int = 0, limit: int = 10) -> List[dict]:
    """
    Obtém uma lista paginada de pedidos,
    incluindo detalhes de itens e pagamento.
    """
    logger.info(
        f"🔍 Buscando pedidos (skip={skip}, limit={limit}) no banco de dados..."
        )

    orders = (
        db.query(models.Order)
        .options(
            joinedload(models.Order.order_items)
            .joinedload(models.OrderItem.product)
            )
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not orders:
        logger.warning("⚠️ Nenhum pedido encontrado no banco de dados!")
        return []

    logger.info(f"✅ {len(orders)} pedidos encontrados. Preparando resposta...")

    return [
        {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "amount": sum(
                (item.product.price * item.quantity) if item.product else 0
                for item in order.order_items
            ),
            "qr_code": order.qr_code if hasattr(order, "qr_code") else None,
            "payment_link": (
                order.payment_link if hasattr(order, "payment_link") else None
            ),
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product.id if item.product else None,
                    "name": (
                        item.product.name
                        if item.product
                        else PRODUCT_NOT_FOUND
                    ),
                    "price": item.product.price if item.product else 0.0,
                    "quantity": item.quantity
                }
                for item in order.order_items
            ]
        }
        for order in orders
    ]


def create_order(db: Session, order_data: schemas.OrderCreate) -> dict:
    """Cria um novo pedido e solicita um link de pagamento."""
    try:
        logger.info(
            f"Criando novo pedido para cliente {order_data.customer_id}"
            )

        # Criando o pedido no banco de dados
        db_order = models.Order(
            customer_id=order_data.customer_id,
            status="created",
            payment_status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # Criar itens do pedido em lote
        order_items = [
            models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity)
            for item in order_data.order_items
        ]
        db.bulk_save_objects(order_items)
        db.commit()

        # Recuperar os itens do pedido com detalhes do produto
        order_with_items = db.query(models.Order).options(
            joinedload(models.Order.order_items)
            .joinedload(models.OrderItem.product)
        ).filter(models.Order.id == db_order.id).first()

        # **INTEGRAÇÃO COM O PAYMENT-SERVICE**
        customer_email = (
            order_data.email if order_data.email else "cliente@example.com"
        )
        payment_response = request_payment(db_order, customer_email, db)

        payment_details = {
            "payment_id": None,
            "amount": None,
            "qr_code": None,
            "payment_link": None
        }

        if payment_response and "payment_id" in payment_response:
            db_order.payment_status = "awaiting_payment"
            payment_details = {
                "payment_id": payment_response["payment_id"],
                "amount": payment_response["amount"],
                "qr_code": payment_response["qr_code"],
                "payment_link": payment_response["payment_link"]
            }
            db.commit()
            db.refresh(db_order)

        # **Retornar os detalhes completos do pedido**
        return {
            "id": db_order.id,
            "customer_id": db_order.customer_id,
            "status": db_order.status,
            "payment_status": db_order.payment_status,
            "amount": payment_details["amount"],
            "qr_code": payment_details["qr_code"],
            "payment_link": payment_details["payment_link"],
            "created_at": db_order.created_at,
            "updated_at": db_order.updated_at,
            "items": [
                {
                    "product_id": item.product.id,
                    "name": item.product.name,
                    "price": item.product.price,
                    "quantity": item.quantity
                }
                for item in order_with_items.order_items
            ]
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Erro ao criar pedido: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar pedido.")


def update_order_status(
    db: Session,
    order_id: int,
    order_update: schemas.OrderUpdate
) -> dict:
    """Atualiza manualmente o status de um pedido e/ou status de pagamento."""

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        logger.warning(f"Pedido {order_id} não encontrado.")
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    try:
        # Converte OrderUpdate para dicionário sem os campos nulos
        update_data = order_update.dict(exclude_unset=True)

        # Se nenhum dado foi passado, retorna erro
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="Nenhum campo para atualizar")

        has_changes = False  # Flag para indicar se alguma mudança aconteceu

        if "status" in update_data:
            new_status = update_data["status"]
            # Pegando os valores do Enum
            valid_statuses = [status.value for status in models.OrderStatus]
            if new_status not in valid_statuses:
                logger.error(f"Status inválido: {new_status}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid order status")
            # Converte para string
            order.status = models.OrderStatus(new_status).value
            has_changes = True

        if "payment_status" in update_data:
            new_payment_status = update_data["payment_status"]
            valid_payment_statuses = [
                status.value for status in models.PaymentStatus
            ]  # Pegando os valores do Enum
            if new_payment_status not in valid_payment_statuses:
                logger.error(
                    f"Status de pagamento inválido: {new_payment_status}"
                    )
                raise HTTPException(
                    status_code=400,
                    detail="Invalid payment status"
                    )
            order.payment_status = models.PaymentStatus(
                new_payment_status
            ).value  # Converte para string
            has_changes = True

        if has_changes:
            order.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(order)
            logger.info(
                f"✅ Pedido {order_id} atualizado para status {order.status} "
                f"e pagamento {order.payment_status}"
                )
        else:
            logger.info(
                f"⚠️ Nenhuma mudança realizada para o pedido {order_id}"
                )

        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,  # Já é string, não precisa acessar
            # `.value`
            "payment_status": order.payment_status,  # Já é string
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product.id if item.product else None,
                    "name": (
                        item.product.name
                        if item.product
                        else PRODUCT_NOT_FOUND
                    ),
                    "price": item.product.price if item.product else 0.0,
                    "quantity": item.quantity
                }
                for item in order.order_items
            ]
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ Erro ao atualizar pedido {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar pedido")


# ------------------------ RASTREAMENTO ------------------------
def create_tracking(
        db: Session,
        order_id: int,
        status: str) -> models.Tracking:
    """Cria um rastreamento de pedido."""
    db_tracking = models.Tracking(
        order_id=order_id,
        status=status,
        created_at=datetime.now(timezone.utc)
        )
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    return db_tracking


def get_tracking(db: Session, order_id: int) -> List[schemas.TrackingRead]:
    """Obtém histórico de rastreamento de um pedido."""
    trackings = db.query(models.Tracking).filter(
        models.Tracking.order_id == order_id
        ).all()
    return [
        schemas.TrackingRead(
            id=t.id,
            order_id=t.order_id,
            status=t.status,
            created_at=t.created_at
            )
        for t in trackings
    ]


# ------------------------ CÁLCULO DO TOTAL DO PEDIDO ------------------------
def calculate_total_amount(order: models.Order, db: Session) -> float:
    total = 0.0
    for item in order.order_items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()
        if product:
            total += product.price * item.quantity
    return total
