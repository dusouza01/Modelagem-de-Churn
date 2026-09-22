# Referência técnica — Churn Analisys

Dashboard local de retenção com Python e Streamlit. Interface responsiva em preto, amarelo e branco, com animações discretas e suporte a movimento reduzido.

## Rodar no Windows

Use Python 3.13 (versão usada nos testes). Na primeira execução, rode **treinar.bat** para criar o modelo local; depois dê dois cliques em **iniciar.bat**. O iniciador entra na pasta correta, prepara `.venv`, instala as dependências e abre o dashboard no navegador. A instalação das dependências precisa de internet; depois de instaladas, a aplicação usa os dados locais. Para encerrar, pressione `Ctrl+C` no terminal.

Alternativa no PowerShell, dentro desta pasta:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe train.py
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
│   ├── model.py                 # Carregamento e previsão, sem treinamento
│   ├── training.py              # Treinamento offline e calibração
│   ├── artifacts.py             # Versões, integridade e compatibilidade
│   ├── validation.py            # Contrato e validação dos dados
│   ├── importing.py             # Previsão e avaliação de CSV
│   ├── import_view.py           # Interface de importação
│   └── presentation.py          # Navegação e hero
├── assets/
│   ├── css/styles.css           # Tema, responsividade e movimento
│   ├── js/navigation.js         # Âncoras e seção ativa
│   └── illustrations/investor.svg
├── tests/test_app.py            # Teste funcional do dashboard
├── data/                        # CSV e notebook originais
├── imagens/                     # Imagens originais preservadas
├── doc/                         # Documentação técnica
└── .streamlit/config.toml
```

## Interface

Interface responsiva em preto, amarelo e branco, com indicadores, insights dinâmicos, gráficos Plotly, avaliação de probabilidades calibradas e exportação de clientes. O hero apresenta Ciência de Dados e Machine Learning aplicado. As animações respeitam a preferência de movimento reduzido.

## Verificação

```powershell
.\.venv\Scripts\python.exe tests/test_app.py
```

O teste cobre carregamento, filtros combinados, busca sem resultado e limpeza dos filtros.

## Funcionalidades e interpretação

### Comparação histórica por capacidade

Informe a quantidade no campo inicialmente vazio. As três estratégias usam os mesmos 2.000 registros separados para teste, sem influência dos filtros de carteira:

- **Modelo:** maiores probabilidades de churn, com desempate pelo ID.
- **Aleatória:** média matemática de uma seleção uniforme sem reposição.
- **Inativos primeiro:** seleção de `IsActiveMember = 0`; desempate aleatório entre inativos e preenchimento das vagas restantes por sorteio entre ativos.

As regras aleatórias exibem a expectativa exata, calculada pelas proporções de cancelamento de cada grupo. Não se escolhe uma semente favorável nem se apresenta um sorteio isolado como resultado típico. Uma média esperada pode ser fracionária. As três estratégias selecionam a mesma quantidade, limitada ao tamanho da base disponível.

A comparação apresenta cancelamentos identificados, proporção de cancelamentos na seleção e cobertura dos cancelamentos da base. Os resultados podem ser exportados. `Exited` é usado na avaliação, nunca na ordenação do modelo. Identificar um cancelamento histórico não equivale a evitá-lo, e a base não registra resultados de campanhas.

Testes adicionais:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_comparison.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_prioritization.py
```

Filtros por país, gênero e prioridade; limpeza de filtros; indicadores e gráficos derivados da seleção; busca por sobrenome ou ID; exportação de todos os resultados da busca para CSV UTF-8.

Modelo Random Forest, divisão estratificada de 80% para treino e 20% para teste, semente 42. Acurácia e ROC AUC são calculadas no conjunto de teste. O dashboard exibe probabilidades para toda a base, incluindo treino: trata-se de demonstração histórica, não de desempenho em produção.

A prioridade é definida pela capacidade de atendimento. O indicador de saldo soma `Balance` dos clientes prioritários. A moeda não é informada no dataset; `EstimatedSalary` não representa receita bancária.

## Probabilidades calibradas e prioridade por capacidade

A base mantém a divisão estratificada de 80% treino e 20% teste (semente 42). No treino, `CalibratedClassifierCV` ajusta uma transformação sigmoide com previsões fora de cada uma das cinco partições estratificadas. `ensemble=False` usa um estimador final ajustado em todo o treino. O teste externo não é fornecido ao treinamento ou à calibração e não foi usado para escolher o método.

O dashboard utiliza as probabilidades calibradas e exibe a avaliação do modelo calibrado no teste: Brier, log loss e curva de confiabilidade com contagens por faixa. Faixas de 10 pontos percentuais são usadas exclusivamente para diagnóstico; não definem a prioridade. Faixas vazias têm médias indisponíveis. Brier e log loss menores representam melhora nas respectivas métricas, sem garantia de desempenho futuro.

Capacidade, risco mínimo (%) e público começam vazios. O usuário escolhe entre clientes sem cancelamento registrado (`Exited = 0`) e todos os clientes para demonstração histórica. A seleção considera os maiores riscos calibrados que atingem o risco mínimo informado na carteira completa, com desempate por ID. Os filtros de país, gênero e prioridade e a busca apenas exibem partes dessa seleção; não selecionam substitutos. Se faltarem clientes do público que atinjam o risco mínimo, a lista fica menor que a capacidade, sem preenchimento com clientes abaixo do limite. Clientes fora da capacidade não são classificados automaticamente como baixo risco.

A carteira inclui registros de treino e é uma demonstração histórica. As avaliações de calibração e de estratégias usam somente o teste completo, independentemente dos filtros e da capacidade definida para a carteira. O corte de 50% informado na acurácia é apenas uma convenção dessa métrica, não uma regra de atendimento. Não há custos financeiros, taxas de recuperação ou resultados de campanhas presumidos.

Referência técnica: [CalibratedClassifierCV — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV).

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_calibration.py
```

## Engenharia e importação

O dashboard não treina ao abrir, filtrar ou importar arquivos. `train.py` é o único ponto de entrada para treinar e ativar uma versão. `treinar.bat` prepara o ambiente e executa esse comando. A base de treinamento continua sendo `data/Churn_Modelling.csv`; nenhum upload alimenta o treinamento. Se ela mudar, o dashboard solicita um novo treinamento em vez de misturar métricas antigas com dados novos.

Cada execução cria `models/<versão>/model.joblib` e `metadata.json`, com identificação própria. `models/current.txt` aponta para a versão ativa e é atualizado atomicamente após a gravação. O manifesto inclui horário UTC, SHA-256 da base e do artefato, versões de Python e bibliotecas, variáveis, categorias, configuração e métricas. Os modelos são ignorados pelo Git, pois são gerados localmente e contêm informações da base. Guarde os dados, o código e as dependências correspondentes para reproduzir uma versão.

A aplicação verifica o contrato, o hash e as versões antes de carregar o artefato. O modelo fica em cache em memória por versão; uma nova versão ativa é carregada no próximo processamento da página. Após substituir manualmente arquivos de uma versão existente, reinicie o servidor. Use apenas artefatos gerados localmente: joblib não é um formato seguro para modelos recebidos de terceiros. O hash detecta corrupção, não autentica a procedência. Referência: [persistência de modelos no scikit-learn](https://scikit-learn.org/stable/model_persistence.html).

### Dois modos de importação

A finalidade começa vazia e deve ser escolhida antes de enviar o arquivo:

- **Prever risco de clientes:** `Exited` não é obrigatória; quando presente, é validada e nunca entra no modelo.
- **Avaliar resultados históricos:** exige `Exited` binário e calcula Brier, log loss e ROC AUC. AUC fica indisponível quando há uma única classe. Se qualquer ID já pertence à base de desenvolvimento, as métricas do arquivo ficam desabilitadas e as previsões continuam disponíveis. Não se removem esses clientes silenciosamente. IDs diferentes não garantem independência: a origem e o período precisam ser verificados pelo responsável pelos dados.

Os dois modos mantêm a carteira e a avaliação de referência separadas. A exportação contém a versão do modelo e as probabilidades. A aplicação não grava uploads em disco. Há um download de cabeçalho CSV sem dados fictícios.

### Contrato de dados

CSV UTF-8 (com ou sem BOM), separado por vírgulas, com ponto decimal, até 10 MiB e 100.000 linhas. Esses limites são operacionais, não regras de negócio. Colunas extras são ignoradas pelo modelo. `RowNumber` não é utilizado.

Campos obrigatórios: `CustomerId`, `Surname`, `CreditScore`, `Geography`, `Gender`, `Age`, `Tenure`, `Balance`, `NumOfProducts`, `HasCrCard`, `IsActiveMember`, `EstimatedSalary`. A avaliação histórica exige também `Exited`.

A validação rejeita arquivo vazio, cabeçalhos repetidos, colunas ausentes, campos vazios, IDs duplicados, números não finitos ou negativos, valores fracionários em campos inteiros, indicadores diferentes de 0/1 e categorias não vistas no treino. Informa colunas e primeiras linhas com problema, sem preencher ou descartar registros. Espaços nas pontas dos textos são removidos. Limites de negócio adicionais (por exemplo, faixa admissível de score) não foram presumidos.

### Testes automatizados

```powershell
.\.venv\Scripts\python.exe train.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

A suíte cobre contratos inválidos, previsão sem alvo, ausência de treinamento durante previsão, sobreposição de clientes, AUC de classe única, preservação das previsões após salvar/carregar, versões incompatíveis, artefato corrompido, as duas finalidades de importação e regressões dos filtros e comparações. Alterações artificiais de dados existem somente nas fixtures de teste, nunca nos resultados exibidos ao usuário.

O workflow `.github/workflows/tests.yml` instala as dependências, treina explicitamente e roda a suíte em pushes e pull requests quando o repositório estiver no GitHub. O workflow foi configurado localmente; sua execução remota depende do envio do repositório.
