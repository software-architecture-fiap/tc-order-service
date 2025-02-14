from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database.database import get_db
from ..models import schemas
from ..services import repository
from ..services.security import verify_token
from ..tools.logging import logger

router = APIRouter()

# ------------------------ PRODUTOS ------------------------

@router.post("/", response_model=schemas.ProductRead)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """Cria um novo produto (Apenas para usuários autenticados)."""
    logger.info(f"Usuário {user['id']} criando produto: {product.name}")
    new_product = repository.create_product(db, product)
    logger.info(f"Produto criado com sucesso: {new_product.id}")
    return new_product

@router.get("/", response_model=List[schemas.ProductRead])
def get_products(
    product_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Obtém produtos ativos.
    - Se `product_id` for informado, retorna um único produto.
    - Se `category_id` for informado, retorna produtos apenas dessa categoria.
    - Caso contrário, retorna uma lista paginada de produtos ativos.
    """

    if product_id:
        logger.info(f"Buscando produto com ID: {product_id}")
        product = repository.get_product(db, product_id)
        if not product:
            logger.warning(f"Produto ID {product_id} não encontrado")
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        return [product]

    logger.info(f"Buscando produtos ativos (skip={skip}, limit={limit}, categoria={category_id})")
    return repository.get_products(db, category_id=category_id, skip=skip, limit=limit)  # 🔹 Agora passa category_id

@router.patch("/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int, 
    product_data: schemas.ProductUpdate, 
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Edita um produto existente. 
    - O usuário deve estar autenticado.
    - Se o produto estiver inativo (`enabled=False`), um aviso será gerado no log.
    """
    if not product_data.dict(exclude_unset=True):  # 🔹 Verifica se há dados para atualizar
        logger.warning(f"Usuário {user['id']} tentou atualizar produto {product_id} sem fornecer dados")
        raise HTTPException(status_code=400, detail="Nenhum dado para atualização")

    logger.info(f"Usuário {user['id']} editando produto {product_id}")

    updated_product = repository.update_product(db, product_id, product_data)
    if not updated_product:
        logger.warning(f"Tentativa de editar produto ID {product_id} que não existe")
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if not updated_product.enabled:
        logger.warning(f"Usuário {user['id']} editou o produto {product_id}, mas ele está desativado!")

    logger.info(f"Produto {product_id} atualizado com sucesso")
    return updated_product
