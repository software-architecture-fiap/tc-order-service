from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database.database import get_db
from ..models import schemas
from ..services import repository
from ..services.security import verify_token
from ..tools.logging import logger

router = APIRouter()


# ------------------------ CATEGORIAS ------------------------
@router.post("/", response_model=schemas.CategoryRead)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """Cria uma nova categoria (Apenas para usuários autenticados)."""
    logger.info(
        f"Usuário {user['id']} está criando uma categoria: {category.name}"
    )
    new_category = repository.create_category(db, category)
    logger.info(f"Categoria criada com sucesso: {new_category.id}")
    return new_category


@router.get("/", response_model=List[schemas.CategoryRead])
def get_categories(
    category_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Obtém todas as categorias ativas ou uma específica.
    - Se `category_id` for informado, retorna um único objeto de categoria.
    - Caso contrário, retorna uma lista paginada de categorias ativas.
    """
    if category_id:
        logger.info(f"Buscando categoria com ID: {category_id}")
        category = repository.get_category(db, category_id)
        if not category:
            logger.warning(f"Categoria ID {category_id} não encontrada")
            raise HTTPException(
                status_code=404, detail="Categoria não encontrada"
            )
        # 🔹 Agora retorna uma lista, para evitar conflito no response_model
        return [category]

    logger.info(f"Buscando todas as categorias (skip={skip}, limit={limit})")
    return repository.get_categories(db, skip=skip, limit=limit)


@router.patch("/{category_id}", response_model=schemas.CategoryRead)
def update_category(
    category_id: int,
    category_data: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Edita uma categoria existente.
    - O usuário deve estar autenticado.
    - Se nenhum dado for enviado, a API retorna um erro.
    """
    if not category_data.dict(exclude_unset=True):
        # 🔹 Verifica se há dados para atualizar
        logger.warning(
            f"Usuário {user['id']} tentou atualizar categoria {category_id} "
            "sem fornecer dados")
        raise HTTPException(status_code=400,
                            detail="Nenhum dado para atualização")

    logger.info(
        f"Usuário {user['id']} está editando a categoria {category_id}"
    )

    updated_category = repository.update_category(db, category_id,
                                                  category_data)
    if not updated_category:
        logger.warning(
            f"Tentativa de editar categoria ID {category_id} que não existe"
        )
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    logger.info(f"Categoria {category_id} atualizada com sucesso")
    return updated_category
