
from __future__ import annotations

import random
from datetime import datetime, timedelta

from sqlalchemy import select

from backend.auth import hash_password
from backend.database import SessionLocal, init_db
from backend.models import Ingredient, Pizza, RecipeItem, Sale, User


INGREDIENTS = [
    ("Mussarela", 30, "kg", 10, 42.90, 12),
    ("Calabresa", 18, "kg", 6, 31.50, 10),
    ("Molho de tomate", 20, "kg", 5, 12.90, 8),
    ("Massa", 35, "kg", 10, 8.50, 5),
    ("Frango", 15, "kg", 5, 28.00, 4),
    ("Catupiry", 8, "kg", 3, 55.00, 14),
    ("Presunto", 10, "kg", 4, 34.00, 7),
    ("Ovo", 60, "un", 20, 0.80, 10),
    ("Cebola", 12, "kg", 3, 6.50, 6),
    ("Tomate", 8, "kg", 3, 7.90, 2),
]


PIZZAS = [
    (
        "Calabresa",
        "médio",
        39.90,
        [("Massa", 0.3), ("Mussarela", 0.15), ("Calabresa", 0.1), ("Molho de tomate", 0.05)],
    ),
    (
        "Frango Catupiry",
        "médio",
        44.90,
        [("Massa", 0.3), ("Mussarela", 0.1), ("Frango", 0.15), ("Catupiry", 0.08), ("Molho de tomate", 0.05)],
    ),
    (
        "Portuguesa",
        "médio",
        46.90,
        [
            ("Massa", 0.3),
            ("Mussarela", 0.12),
            ("Presunto", 0.1),
            ("Ovo", 1),
            ("Cebola", 0.05),
            ("Molho de tomate", 0.05),
        ],
    ),
    (
        "Mussarela",
        "médio",
        34.90,       # preço da pizza
        [("Massa", 0.3), ("Mussarela", 0.2), ("Molho de tomate", 0.05)],  # receita da pizza
    ),
]

USERS = [
    ("Administrador", "admin@pizzastock.local", "123456", "administrador"),
    ("Gerente Silva", "gerente@pizzastock.local", "123456", "gerente"),
    ("Atendente Costa", "atendente@pizzastock.local", "123456", "atendente"),
]


def seed(include_history: bool = True) -> None:
    init_db()
    db = SessionLocal()
    try:
        for nome, email, senha, perfil in USERS:
            if not db.scalar(select(User).where(User.email == email)):
                db.add(
                    User(
                        nome=nome,
                        email=email,
                        senha_hash=hash_password(senha),
                        perfil=perfil,
                    )
                )

        ingredients: dict[str, Ingredient] = {}
        for nome, estoque, unidade, minimo, custo, validade_dias in INGREDIENTS:  
            item = db.scalar(select(Ingredient).where(Ingredient.nome == nome))
            if not item:
                item = Ingredient(
                    nome=nome,
                    estoque=estoque,
                    unidade=unidade,
                    estoque_minimo=minimo,
                    custo_unitario=custo,
                    data_validade=datetime.now() + timedelta(days=validade_dias),
                )
                db.add(item)
            ingredients[nome] = item
        db.flush()

        pizzas: dict[str, Pizza] = {}
        for nome, estoque, preco, receita in PIZZAS:  # tamanho: médio, grande ou pequeno   
            pizza = db.scalar(select(Pizza).where(Pizza.nome == nome))
            if not pizza:
                pizza = Pizza(nome=nome, estoque=estoque, preco=preco)  # tamanho: médio, grande ou pequeno (na tabela pizza)
                pizza.receita_itens = [ # receita da pizza (na tabela recipe_item)
                    RecipeItem(ingrediente=ingredients[ing], quantidade=qty) for ing, qty in receita # ing: nome do ingrediente, qty: quantidade do ingrediente (na tabela recipe_item)
                ]  # receita: lista de ingredientes e quantidades (na tabela recipe_item)
                db.add(pizza)
            pizzas[nome] = pizza  # nome: nome da pizza, pizza: objeto pizza (na tabela pizza)
        db.flush()

        if include_history and db.scalar(select(Sale.id).limit(1)) is None:
            rng = random.Random(42)  # random: objeto random (na biblioteca random)
            pizza_list = list(pizzas.values())  # pizza_list: lista de objetos pizza (na tabela pizza)
            for day_offset in range(21, 0, -1):
                day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(  # day: data atual (na tabela sale)
                    days=day_offset
                )
                for _ in range(rng.randint(8, 18)):  # _: variável não utilizada (na tabela sale)
                    pizza = rng.choice(pizza_list)
                    qty = rng.randint(1, 3)  # qty: quantidade de pizzas vendidas (na tabela sale)
                    hour = rng.choice([12, 13, 18, 19, 20, 21, 22])
                    cost = sum(  # cost: custo total da pizza (na tabela sale)
                        item.quantidade * item.ingrediente.custo_unitario * qty  # item: objeto item (na tabela recipe_item), quantidade: quantidade do ingrediente (na tabela recipe_item), custo_unitario: custo unitário do ingrediente (na tabela ingredient), qty: quantidade de pizzas vendidas (na tabela sale)
                        for item in pizza.receita_itens  # item: objeto item (na tabela recipe_item)
                    )
                    # histórico sem descontar estoque atual (simulação passada)
                    db.add(
                        Sale(  # Sale: objeto Sale (na tabela sale)
                            pizza_id=pizza.id,  # pizza_id: id da pizza (na tabela sale)
                            quantidade=qty,  # quantidade: quantidade de pizzas vendidas (na tabela sale)
                            valor_total=round(pizza.preco * qty, 2),  # valor_total: valor total da pizza (na tabela sale)
                            custo_total=round(cost, 2),  # custo_total: custo total da pizza (na tabela sale)
                            criada_em=day.replace(hour=hour, minute=rng.randint(0, 59)),  # criada_em: data e hora da venda (na tabela sale)
                        )
                    )
            # vendas de hoje para o dashboard demo
            today = datetime.now().replace(second=0, microsecond=0)  # today: data atual (na tabela sale)
            for hour, pizza_name, qty in [(12, "Calabresa", 2), (13, "Mussarela ", 1), (19, "Frango Catupiry ", 2), (20, "Portuguesa ", 1), (21, "Calabresa ", 3)]:  # hour: hora da venda, pizza_name: nome da pizza, qty: quantidade de pizzas vendidas
                pizza = pizzas[pizza_name]  # pizza: objeto pizza (na tabela pizza)
                cost = sum(  # cost: custo total da pizza (na tabela sale)
                    item.quantidade * item.ingrediente.custo_unitario * qty  # item: objeto item (na tabela recipe_item), quantidade: quantidade do ingrediente (na tabela recipe_item), custo_unitario: custo unitário do ingrediente (na tabela ingredient), qty: quantidade de pizzas vendidas (na tabela sale)
                    for item in pizza.receita_itens  # item: objeto item (na tabela recipe_item)
                )  # cost: custo total da pizza (na tabela sale)
                db.add(
                    Sale(  # Sale: objeto Sale (na tabela sale)
                        pizza_id=pizza.id,  # pizza_id: id da pizza (na tabela sale)
                        quantidade=qty,  # quantidade: quantidade de pizzas vendidas (na tabela sale)
                        valor_total=round(pizza.preco * qty, 2),  # valor_total: valor total da pizza (na tabela sale)
                        custo_total=round(cost, 2),  # custo_total: custo total da pizza (na tabela sale)
                        criada_em=today.replace(hour=hour, minute=rng.randint(0, 59)),  # criada_em: data e hora da venda (na tabela sale)
                    )
                )              # deixa mussarela e tomate críticos para demonstrar alertas
            if "Mussarela" in ingredients:
                ingredients["Mussarela"].estoque = 8

            if "Tomate" in ingredients:
                ingredients["Tomate"].estoque = 2.5

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Base populada com sucesso.")