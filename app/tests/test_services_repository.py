import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import models, schemas
from app.repository import create_product

# Setup the database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
    )


@pytest.fixture(scope="module")
def db():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)


def test_create_product(db):
    # Create a category first
    category = models.Category(name="Test Category", enabled=True)
    db.add(category)
    db.commit()
    db.refresh(category)

    # Create a product
    product_data = schemas.ProductCreate(
        name="Test Product",
        price=100.0,
        category_id=category.id
    )
    product = create_product(db, product_data)

    assert product.id is not None
    assert product.name == "Test Product"
    assert abs(product.price - 100.0) < 1e-9
    assert product.category_id == category.id
    assert product.enabled is True