import logging
from sqlalchemy.orm import Session
from ..models.models import Category, Product

logger = logging.getLogger('Application')

def initialize_db(db: Session) -> None:
    """Inicializa o banco de dados com dados padrão para categorias e produtos.

    Args:
        db (Session): Sessão do banco de dados.

    Returns:
        None
    """

    # ------------------------ CRIAR CATEGORIAS ------------------------
    categories = [
        {'name': 'Sanduíches'},
        {'name': 'Pizzas'},
        {'name': 'Acompanhamentos'},
        {'name': 'Bebidas'},
        {'name': 'Sobremesas'},
    ]

    # Verifica categorias existentes no banco
    existing_categories = {category.name: category.id for category in db.query(Category).all()}

    for category in categories:
        if category['name'] in existing_categories:
            logger.debug(f"Categoria já existe: {category['name']}")
        else:
            db_category = Category(**category)
            db.add(db_category)
            db.commit()  # 🔹 Garante que a categoria seja salva para obter o ID
            db.refresh(db_category)
            existing_categories[db_category.name] = db_category.id  # Atualiza o dicionário
            logger.info(f"Categoria adicionada: {db_category.name}")

    # ------------------------ CRIAR PRODUTOS ------------------------
    products = [
        {
            'name': 'Sanduíche de Frango Grelhado',
            'description': 'Grilled chicken sandwich with lettuce and tomato',
            'price': 15.00,
            'category_name': 'Sanduíches',
        },
        {
            'name': 'Cheeseburger Clássico',
            'description': 'Classic cheeseburger with beef patty and cheese',
            'price': 12.00,
            'category_name': 'Sanduíches',
        },
        {
            'name': 'Sanduíche Vegano de Grão-de-Bico',
            'description': 'Vegan sandwich with chickpea patty',
            'price': 14.00,
            'category_name': 'Sanduíches',
        },
        {
            'name': 'Pizza Margherita',
            'description': 'Pizza with tomato sauce, mozzarella, and basil',
            'price': 25.00,
            'category_name': 'Pizzas',
        },
        {
            'name': 'Pizza Pepperoni',
            'description': 'Pizza with tomato sauce, mozzarella, and pepperoni',
            'price': 27.00,
            'category_name': 'Pizzas',
        },
        {
            'name': 'Pizza Quatro Queijos',
            'description': 'Pizza with four types of cheese',
            'price': 28.00,
            'category_name': 'Pizzas',
        },
        {'name': 'Batata Frita', 'description': 'Portion of crispy french fries', 'price': 8.00, 'category_name': 'Acompanhamentos'},
        {'name': 'Anéis de Cebola', 'description': 'Portion of breaded onion rings', 'price': 9.00, 'category_name': 'Acompanhamentos'},
        {
            'name': 'Salada Caesar',
            'description': 'Caesar salad with lettuce, croutons, and parmesan cheese',
            'price': 10.00,
            'category_name': 'Acompanhamentos',
        },
        {'name': 'Coca-Cola', 'description': 'Cola soft drink', 'price': 5.00, 'category_name': 'Bebidas'},
        {'name': 'Suco de Laranja', 'description': 'Natural orange juice', 'price': 6.00, 'category_name': 'Bebidas'},
        {'name': 'Água Mineral', 'description': 'Still mineral water', 'price': 4.00, 'category_name': 'Bebidas'},
        {
            'name': 'Brownie de Chocolate',
            'description': 'Chocolate brownie with walnuts',
            'price': 7.00,
            'category_name': 'Sobremesas',
        },
        {'name': 'Torta de Maçã', 'description': 'Apple pie with cinnamon', 'price': 8.00, 'category_name': 'Sobremesas'},
        {'name': 'Sorvete de Baunilha', 'description': 'Vanilla ice cream', 'price': 6.00, 'category_name': 'Sobremesas'},
    ]

    # Verifica produtos existentes no banco
    existing_product_names = {product.name for product in db.query(Product.name).all()}

    for product in products:
        if product['name'] in existing_product_names:
            logger.debug(f"Produto já existe: {product['name']} - Categoria: {product['category_name']}")
        else:
            category_id = existing_categories.get(product['category_name'])
            if category_id:
                db_product = Product(
                    name=product['name'],
                    description=product['description'],
                    price=product['price'],
                    category_id=category_id,
                    enabled=True,  # 🔹 Define como ativo por padrão
                )
                db.add(db_product)
                logger.info(f"Produto adicionado: {db_product.name} - Categoria: {product['category_name']}")
            else:
                logger.warning(f"Categoria não encontrada para produto: {product['name']}")

    db.commit()
    logger.info('Banco de dados inicializado com sucesso.')
