from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Ingredient, Pizza, RecipeItem
from backend.services.sales import SaleRuleError, register_sale


def make_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_register_sale_decrements_stock_and_records_cost():
    db = make_session()
    ingredient = Ingredient(nome="Mussarela teste", estoque=2, unidade="kg", estoque_minimo=0.5, custo_unitario=40)
    pizza = Pizza(nome="Pizza teste", preco=50)
    pizza.receita_itens = [RecipeItem(ingrediente=ingredient, quantidade=0.5)]
    db.add(pizza)
    db.commit()
    db.refresh(pizza)

    sale = register_sale(db, pizza.id, 2)

    assert sale.valor_total == 100
    assert sale.custo_total == 40
    assert db.get(Ingredient, ingredient.id).estoque == 1


def test_register_sale_rejects_insufficient_stock():
    db = make_session()
    ingredient = Ingredient(nome="Molho teste", estoque=0.1, unidade="kg", estoque_minimo=0.2, custo_unitario=10)
    pizza = Pizza(nome="Pizza sem estoque", preco=30)
    pizza.receita_itens = [RecipeItem(ingrediente=ingredient, quantidade=0.2)]
    db.add(pizza)
    db.commit()
    db.refresh(pizza)

    try:
        register_sale(db, pizza.id, 1)
    except SaleRuleError as error:
        assert "Estoque insuficiente" in str(error)
    else:
        raise AssertionError("A venda deveria ter sido bloqueada")
