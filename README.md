# Churn Insights

Dashboard local de retenção com Python e Streamlit. Interface responsiva em preto, amarelo e branco, com animações discretas e suporte a movimento reduzido.

## Rodar no Windows

Tenha Python 3.11 ou superior instalado. Dê dois cliques em **iniciar.bat**. O iniciador entra na pasta correta, prepara `.venv`, instala as dependências e abre o dashboard no navegador. A instalação das dependências precisa de internet; depois de instaladas, a aplicação usa os dados locais. Para encerrar, pressione `Ctrl+C` no terminal.

Alternativa no PowerShell, dentro desta pasta:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost
```

Abra http://localhost:8501 se o navegador não abrir automaticamente.

## Organização

Execute a aplicação a partir de `projeto_du/Modelagem-de-Churn`. Todos os caminhos de dados e assets são calculados em relação aos arquivos Python, sem depender do diretório do terminal.

```text
Modelagem-de-Churn/
├── app.py                       # Ponto de entrada Streamlit
├── iniciar.bat                  # Iniciador Windows
├── requirements.txt
├── src/churn_insights/
│   ├── dashboard.py             # Seções, filtros e gráficos
│   ├── model.py                 # Dados, treinamento e métricas
│   └── presentation.py          # Navegação e hero
├── assets/
│   ├── css/styles.css           # Tema, responsividade e movimento
│   ├── js/navigation.js         # Âncoras e seção ativa
│   └── illustrations/investor.svg
├── tests/test_app.py            # Teste funcional do dashboard
├── data/                        # CSV e notebook originais
├── imagens/                     # Imagens originais preservadas
├── doc/                         # Documentação anterior preservada
└── .streamlit/config.toml
```

Nenhuma pasta original foi removida. Os arquivos da aplicação foram distribuídos nas pastas acima; os dados, imagens e notebook mantêm seus nomes para preservar referências existentes. A documentação em `doc/` é histórica: este README contém as instruções atuais.

## Interface e animações

Visual restaurado à primeira versão: cabeçalho simples, hero com seta amarela, indicadores, distribuição de risco, gráfico por país, métricas do modelo e tabela de clientes com busca e exportação. Animações de entrada e interação respeitam a preferência de movimento reduzido. Os arquivos de ilustração e navegação posteriores foram preservados em assets, mas não são carregados pelo app.

## Verificação

```powershell
.\.venv\Scripts\python.exe tests/test_app.py
```

O teste cobre carregamento, filtros combinados, busca sem resultado e limpeza dos filtros.

## Funcionalidades e interpretação

Filtros por país, gênero e risco; limpeza de filtros; indicadores e gráficos derivados da seleção; busca por sobrenome ou ID; exportação de todos os resultados da busca para CSV UTF-8.

Modelo Random Forest, divisão estratificada de 80% para treino e 20% para teste, semente 42. Acurácia e ROC AUC são calculadas no conjunto de teste. O dashboard exibe probabilidades para toda a base, incluindo treino: trata-se de demonstração histórica, não de desempenho em produção.

Baixo risco: menos de 33%; médio: de 33% a menos de 67%; alto: a partir de 67%. O indicador de saldo soma `Balance` dos clientes em alto risco. A moeda não é informada no dataset; `EstimatedSalary` não representa receita bancária.
