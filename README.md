# pizzaStockAi
🍕 PizzaStockAI

AI-Powered Inventory, Sales Analytics & Demand Forecasting Platform for Pizzerias

O PizzaStockAI é uma plataforma de gestão inteligente desenvolvida para otimizar a operação de pizzarias por meio da integração entre controle de estoque, gestão de vendas, monitoramento financeiro e previsão de demanda baseada em Machine Learning. O sistema visa transformar dados operacionais em informações estratégicas, permitindo uma gestão orientada por indicadores e redução de desperdícios.

Visão Geral

O projeto foi concebido para resolver problemas recorrentes encontrados em operações de food service, como:

Ruptura de estoque durante horários de pico;
Excesso de compras e desperdício de insumos;
Falta de rastreabilidade financeira;
Ausência de indicadores de desempenho;
Baixa previsibilidade de demanda.

Por meio da combinação de APIs, dashboards analíticos e algoritmos de previsão, o PizzaStockAI fornece suporte à tomada de decisão operacional e gerencial.

Arquitetura da Solução
PizzaStockAI
│
├── backend/                # API FastAPI
│   ├── routers/            # Endpoints REST
│   ├── services/           # Regras de negócio
│   ├── models.py           # Modelos ORM
│   ├── schemas.py          # DTOs/Pydantic
│   ├── database.py         # Configuração do banco
│   └── app.py              # Aplicação principal
│
├── frontend/               # Dashboard Streamlit
│   ├── app_pages/
│   ├── assets/
│   └── dashboard.py
│
├── ml/                     # Módulos de IA
│   ├── forecast.py
│   └── recommendation.py
│
├── tests/                  # Testes automatizados
│
├── database/
│   └── pizzastock.db
│
└── seed.py                 # Dados iniciais

Principais Funcionalidades
Gestão Inteligente de Estoque
Cadastro de ingredientes e insumos
Controle de estoque mínimo
Gestão de validade
Controle de custos unitários
Monitoramento em tempo real
Alertas automáticos para itens críticos
Identificação de produtos próximos ao vencimento
Controle de Receitas

Cada pizza possui uma composição de ingredientes cadastrada no sistema.

Funcionalidades:

Cadastro de receitas técnicas
Mapeamento de consumo por produto
Baixa automática dos insumos após cada venda
Atualização automática do estoque
Gestão de Vendas

O módulo de vendas é responsável pelo gerenciamento completo dos pedidos.

Recursos
Registro de vendas
Histórico de transações
Apuração de faturamento
Cálculo de custos
Análise de lucratividade
Indicadores operacionais em tempo real
Dashboard Executivo

O sistema disponibiliza dashboards analíticos desenvolvidos em Streamlit para acompanhamento dos principais KPIs do negócio.

Indicadores Monitorados
Receita diária
Receita mensal
Receita anual
Quantidade de pedidos
Ticket médio
Estoque crítico
CMV
Lucro operacional
Produtos com risco de vencimento
Sistema de Alertas Operacionais

Motor de monitoramento responsável pela geração de alertas estratégicos, incluindo:

Estoque Crítico
Mussarela abaixo do estoque mínimo

Produtos Próximos ao Vencimento
Tomate vence em 2 dias

Crescimento Repentino da Demanda

Possibilita antecipação de compras e planejamento operacional.

Inteligência Artificial

Um dos diferenciais do PizzaStockAI é seu módulo de análise preditiva.

A camada de Machine Learning utiliza algoritmos de regressão para:

Previsão de vendas futuras
Estimativa de demanda por produto
Planejamento de compras
Identificação de padrões de consumo
Apoio à tomada de decisão baseada em dados
Stack Tecnológica
Backend
Python 3.13+
FastAPI
SQLAlchemy
Pydantic
JWT Authentication
Uvicorn
Frontend
Streamlit
Plotly
Pandas
Data Science
Scikit-Learn
NumPy
Machine Learning Forecast Engine
Banco de Dados
Desenvolvimento
SQLite

Produção
PostgreSQL

Fluxo de Operação
graph LR
<img width="4032" height="936" alt="image" src="https://github.com/user-attachments/assets/6746f741-5eca-454f-ab71-6b2600339db6" />

A[Venda de Pizza]
--> B[Consumo da Receita]

B --> C[Baixa Automática do Estoque]

C --> D[Atualização dos Indicadores]

D --> E[Dashboard Gerencial]

D --> F[Motor de Alertas]

D --> G[Previsão de Demanda]

Instalação
Clonando o Repositório
git clone https://github.com/Paulo68129/PizzaStockAI.git

cd PizzaStockAI

Criando Ambiente Virtual
python -m venv .venv

Windows
.\.venv\Scripts\Activate.ps1

Instalação das Dependências
pip install -r requirements.txt

Execução da API
python -m uvicorn backend.app:app --reload

Endpoints
API:
http://127.0.0.1:8000

Swagger UI:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

Execução do Dashboard
cd frontend

streamlit run dashboard.py


A aplicação ficará disponível em:

http://localhost:8501

Testes

Execução da suíte de testes:

pytest


Estrutura atual:

tests/
├── test_api.py
├── test_ml.py
└── test_sales_service.py

Roadmap
Curto Prazo
Dashboard mobile responsive
Exportação PDF e Excel
Relatórios gerenciais avançados
Controle multiusuário
Médio Prazo
Docker Compose
PostgreSQL em produção
Integração com ERPs
API pública
Longo Prazo
IA generativa para recomendações
Análise preditiva avançada
Aplicativo mobile (Flutter)
Multi-tenant SaaS
Diferenciais Competitivos
Controle operacional centralizado
Previsão inteligente de demanda
Gestão financeira integrada
Alertas automatizados
Dashboard analítico em tempo real
Arquitetura escalável baseada em APIs
Aplicação de Machine Learning em operações de food service
Autor

Paulo Roberto Silva de Oliveira Júnior

Software Developer | Full Stack Developer

🎓 Análise e Desenvolvimento de Sistemas - UNIFESO

🔗 GitHub: https://github.com/Paulo68129

Licença

Este projeto foi desenvolvido para fins acadêmicos, portfólio profissional e demonstração de competências em desenvolvimento de software, análise de dados e inteligência artificial aplicada ao setor de alimentação.

PizzaStockAI® | Intelligent Inventory & Sales Management Platform for Pizzerias 🍕🚀
