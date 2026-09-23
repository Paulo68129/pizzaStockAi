# pizzaStockAi
🍕 PizzaStockAI

Sistema inteligente de gestão para pizzarias desenvolvido para centralizar o controle de estoque, vendas, finanças e previsões de demanda em uma única plataforma. O objetivo é auxiliar gestores na tomada de decisões estratégicas, reduzindo desperdícios, evitando falta de insumos e aumentando a lucratividade do negócio.

🚀 Funcionalidades
📦 Gestão de Estoque
Cadastro de ingredientes
Controle de quantidade em estoque
Definição de estoque mínimo
Controle de validade
Controle de custo unitário
Alertas automáticos de estoque crítico
🍕 Controle de Receitas
Cadastro de receitas por pizza
Baixa automática dos ingredientes após uma venda
Controle de consumo de insumos
💰 Gestão de Vendas
Registro de pedidos
Controle de faturamento
Cálculo de custos
Cálculo automático de lucro
Histórico de vendas
📊 Dashboard Gerencial
Faturamento diário
Total de pedidos
Ticket médio
Lucro operacional
Estoque crítico
Produtos próximos ao vencimento
Atualização em tempo real
📈 Controle Financeiro
Receitas diárias
Receitas semanais
Receitas mensais
Receitas anuais
CMV (Custo da Mercadoria Vendida)
Indicadores financeiros
🤖 Inteligência Artificial
Previsão de demanda
Recomendação de compras
Análise de tendências de consumo
Redução de desperdícios através de Machine Learning
🔐 Controle de Acesso
Administrador
Gerente
Atendente
🏗️ Arquitetura
Plain Text
PizzaStockAI
│
├── backend/
│ ├── routers/
│ ├── services/
│ ├── app.py
│ ├── models.py
│ └── database.py
│
├── frontend/
│ ├── app_pages/
│ ├── dashboard.py
│ └── assets/
│
├── ml/
│ ├── forecast.py
│ └── recommendation.py
│
├── database/
│ └── pizzastock.db
│
├── tests/
│
└── .venv/
``
Mostrar mais linhas
🛠️ Tecnologias Utilizadas
Backend
FastAPI
SQLAlchemy
JWT Authentication
Frontend
Streamlit
Banco de Dados
SQLite
PostgreSQL (produção)
Machine Learning
Scikit-Learn
Regressão Linear
Visualização de Dados
Plotly
DevOps
Docker Compose

⚙️ Instalação
1. Clonar o projeto
Shell
git clone https://github.com/Paulo68129/PizzaStockAI.git
cd PizzaStockAI
Mostrar mais linhas
2. Criar ambiente virtual
Shell
python -m venv .venv
Mostrar mais linhas
3. Ativar ambiente virtual

PowerShell:

PowerShell
.\.venv\Scripts\Activate.ps1
Mostrar mais linhas
4. Instalar dependências
Shell
pip install -r requirements.txt
Mostrar mais linhas
▶️ Executando o Backend

Na raiz do projeto:

PowerShell
python -m uvicorn backend.app:app --reload
``
Mostrar mais linhas

API:

Plain Text
http://127.0.0.1:8000
Mostrar mais linhas

Swagger:

Plain Text
http://127.0.0.1:8000/docs
Mostrar mais linhas
▶️ Executando o Dashboard

Abra outro terminal:

PowerShell
.\.venv\Scripts\Activate.ps1
cd frontend
streamlit run dashboard.py
Mostrar mais linhas

Dashboard:

Plain Text
http://localhost:8501
Mostrar mais linhas
🧪 Testes

Executar testes automatizados:

Shell
pytest
Mostrar mais linhas
📈 Benefícios

✅ Controle automatizado de estoque

✅ Redução de desperdícios

✅ Monitoramento financeiro

✅ Dashboard em tempo real

✅ Previsão inteligente de demanda

✅ Melhor tomada de decisão

✅ Escalabilidade para crescimento do negócio

✅ Integração entre estoque, vendas e finanças

👨‍💻 Autor

Paulo Roberto Silva de Oliveira Júnior

🎓 Análise e Desenvolvimento de Sistemas - UNIFESO

🐍 Python Developer

🌐 Full Stack Developer

🔗 GitHub: https://github.com/Paulo68129

📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e profissionais, podendo ser adaptado para ambientes comerciais conforme necessidade do negócio.
