# Churn Analisys

**Ciência de Dados e Machine Learning aplicado à análise de churn.**

Uma aplicação de Machine Learning e Ciência de Dados para estimar risco de churn e apoiar a priorização de clientes, com avaliação histórica, probabilidades calibradas e um dashboard interativo.

O **Churn Analisys** conecta análise exploratória, aprendizado supervisionado e engenharia de software em um fluxo completo: investigar a carteira, estimar probabilidades, avaliar o modelo e organizar a seleção de clientes para atendimento.

A pergunta que orienta o projeto é direta: **com uma capacidade limitada de atendimento, quais clientes devem ser priorizados e quais evidências sustentam essa decisão?**

## O que a aplicação entrega

- **Visão da carteira:** indicadores de clientes, churn observado, prioridades e saldo da seleção.
- **Insights dinâmicos:** leituras do recorte selecionado, com taxas por país e diferenças entre clientes ativos e inativos.
- **Gráficos interativos:** distribuição das probabilidades e comparação entre risco estimado e cancelamento observado.
- **Avaliação de Machine Learning:** ROC AUC, acurácia, Brier, log loss e curva de confiabilidade.
- **Priorização por capacidade:** seleção dos maiores riscos dentro do público escolhido, com desempate pelo ID.
- **Comparação de estratégias:** modelo, seleção aleatória e inativos primeiro, avaliados no mesmo conjunto de teste.
- **Importação de CSV:** previsão de riscos ou avaliação de resultados históricos, com validação explícita do arquivo.
- **Exportação:** carteira filtrada, comparação de estratégias e previsões identificadas pela versão do modelo.

## Tecnologias aplicadas

| Tecnologia | Aplicação no projeto |
|---|---|
| Python 3.13 | Processamento dos dados, treinamento, inferência e automação |
| pandas | Limpeza estrutural, agrupamentos, filtros e leitura de CSV |
| NumPy e SciPy | Operações numéricas e suporte aos cálculos do pipeline |
| scikit-learn | Pré-processamento, Random Forest, calibração e métricas |
| Streamlit | Interface web, estado dos filtros e interação com arquivos |
| Plotly | Visualizações interativas e exploração dos resultados |
| joblib | Persistência e carregamento do modelo treinado |
| unittest e Streamlit AppTest | Testes analíticos, de contrato e de interface |
| GitHub Actions | Workflow de treinamento e testes automatizados |
| HTML e CSS | Identidade visual, responsividade e animações com movimento reduzido |

As versões das bibliotecas estão fixadas em [requirements.txt](requirements.txt). O treinamento e a previsão são processos separados: navegar no dashboard ou importar um arquivo não executa novo treinamento.

## Baixar o projeto

Com Git instalado, execute no terminal:

```powershell
git clone https://github.com/dusouza01/Modelagem-de-Churn.git
cd Modelagem-de-Churn
```

Também é possível baixar o ZIP no [repositório do projeto](https://github.com/dusouza01/Modelagem-de-Churn), extrair os arquivos e abrir um terminal na pasta que contém `app.py`. As instruções descrevem o código desta pasta; para disponibilizá-lo a outras pessoas, as alterações locais precisam estar publicadas no repositório.

## Instalar bibliotecas e executar

O ambiente usado no projeto é **Python 3.13**. Confirme a instalação:

```powershell
py -3.13 --version
```

### Opção prática no Windows

1. Execute **treinar.bat** para criar o ambiente virtual, instalar as dependências e treinar o modelo com a base local.
2. Execute **iniciar.bat** para abrir a aplicação.
3. Acesse [http://localhost:8501](http://localhost:8501).

Quando houver um modelo compatível preparado, use `iniciar.bat` diretamente. A instalação das bibliotecas requer internet; o processamento da aplicação utiliza arquivos locais. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

### Passo a passo no PowerShell

Na pasta `Modelagem-de-Churn`:

```powershell
# Criar um ambiente isolado para as dependências
py -3.13 -m venv .venv

# Instalar todas as bibliotecas do projeto
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Treinar, calibrar e salvar uma versão do modelo
.\.venv\Scripts\python.exe train.py

# Iniciar o dashboard
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost
```

Não é necessário ativar o ambiente virtual quando se utiliza diretamente o caminho do executável, como nos comandos acima. Execute `train.py` novamente quando atualizar a base de referência ou as dependências do modelo.

## Explorar o dashboard

1. **Filtre:** escolha país e gênero para definir o recorte da carteira.
2. **Investigue:** acompanhe os gráficos e os insights calculados para esse grupo.
3. **Avalie:** consulte a qualidade das probabilidades e compare as estratégias no teste separado.
4. **Priorize:** informe a capacidade da carteira, o risco mínimo (%) e o público elegível. Os três campos começam vazios.
5. **Exporte:** filtre “Prioritário”, use a busca se necessário e baixe a seleção em CSV.

A capacidade da carteira e a capacidade da comparação são controles independentes. País, gênero, prioridade e busca filtram a exibição de um ranking calculado na carteira completa. Eles não recalculam a seleção nem tornam outros clientes prioritários. Mudanças de capacidade, risco mínimo ou público redefinem a seleção. Quantidades acima do público disponível são limitadas aos clientes elegíveis.

Os insights descrevem o recorte selecionado. Diferenças de churn entre países ou grupos de atividade orientam hipóteses de investigação; não demonstram causalidade.

## Ciência de Dados e modelagem

A base de referência contém **10.000 clientes** e o alvo `Exited`, que registra o cancelamento. O pipeline utiliza dez variáveis: score de crédito, país, gênero, idade, tempo de relacionamento, saldo, quantidade de produtos, posse de cartão, atividade e salário estimado.

`CustomerId`, `Surname`, `RowNumber` e `Exited` não entram como preditores.

O fluxo de modelagem é composto por:

1. Validação das colunas, tipos e valores.
2. Divisão estratificada em **80% para treino e 20% para teste**, com semente 42.
3. Codificação das variáveis categóricas com `OneHotEncoder` dentro do pipeline.
4. Treinamento de um `RandomForestClassifier`, com 100 árvores e profundidade máxima 10.
5. Calibração sigmoide com `CalibratedClassifierCV`, usando cinco partições estratificadas somente no treino.
6. Avaliação nos 2.000 clientes separados para teste e persistência do modelo.

### Treino e teste separados: avaliação sem vazamento

`train_test_split(test_size=0.2, stratify=target, random_state=42)` separa os registros antes de qualquer ajuste. A estratificação mantém aproximadamente a proporção de clientes que cancelaram em cada conjunto. O treino fornece exemplos para aprender os padrões; o teste estima o desempenho histórico em registros que não participaram desse aprendizado.

O pré-processamento é parte de um `Pipeline`: `ColumnTransformer` aplica `OneHotEncoder` a país e gênero e mantém as variáveis numéricas. Durante a validação cruzada, o pré-processamento é ajustado dentro de cada partição de treino, sem consultar a partição reservada para gerar previsões.

### Calibração das probabilidades: interpretar o risco

Um bom ranking de clientes não garante probabilidades bem calibradas. A calibração busca aproximar as estimativas da frequência observada: entre muitos clientes com risco próximo de uma determinada probabilidade, espera-se uma frequência de cancelamento semelhante, sem garantia para um cliente individual.

A implementação utiliza `CalibratedClassifierCV(method="sigmoid", ensemble=False)` com `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. As cinco partições pertencem exclusivamente ao treino. Cada registro recebe uma previsão **out-of-fold**, produzida sem que ele tenha sido usado para ajustar aquele modelo. Essas previsões sustentam o ajuste da transformação sigmoide.

O estimador final é ajustado nos dados de treino completos. O teste externo permanece reservado para medir ROC AUC, acurácia, Brier, log loss e a curva de confiabilidade. Ele não escolhe o método nem ajusta a calibração.

### Inferência: aplicar o aprendizado a cada cliente

O artefato persistido com joblib contém o pipeline calibrado. `predict_proba` produz o risco de churn para os dados validados, sem executar `fit` durante a navegação ou a importação. A priorização ordena essas probabilidades na carteira completa e seleciona até a capacidade informada entre os clientes que atingem o risco mínimo definido. O resultado histórico `Exited` define o público elegível quando solicitado, mas não entra no cálculo da probabilidade nem no desempate do ranking.

### Resultados do modelo

Os números abaixo correspondem ao artefato identificado no [relatório de resultados](doc/resultados-modelo.md):

| Métrica | Valor |
|---|---:|
| Acurácia, com corte de 50% | 86,85% |
| ROC AUC | 0,8571 |
| Brier | 0,1017 |
| Log loss | 0,3402 |

Acurácia mede os acertos da classificação nesse corte. ROC AUC avalia a ordenação entre as classes. Brier e log loss avaliam o erro das probabilidades. A curva de confiabilidade relaciona o risco médio previsto à frequência observada de cancelamento.

O corte de 50% é uma convenção da métrica de acurácia. A lista de atendimento é definida pela capacidade informada, não por esse corte.

Para gerar evidências a partir do modelo ativo, sem treinar:

```powershell
.\.venv\Scripts\python.exe report.py
```

O comando produz Markdown e JSON em `doc/`. Para incluir uma comparação por capacidade, acrescente `--capacidade N`, substituindo N pela quantidade escolhida. Atualize o relatório e a tabela deste README quando publicar resultados de outro artefato.

## Importar dados

Escolha uma finalidade na seção **Importar e validar clientes**:

- **Prever risco de clientes:** gera probabilidades com o modelo salvo. `Exited` é opcional e não participa da previsão.
- **Avaliar resultados históricos:** exige `Exited` e calcula métricas para os resultados informados. IDs já presentes na base de desenvolvimento desabilitam as métricas dessa importação, mantendo as previsões disponíveis.

Use CSV UTF-8, separado por vírgulas e com ponto decimal. Limites técnicos: **10 MiB e 100.000 linhas**. O cabeçalho pode ser baixado na interface.

Colunas obrigatórias:

```text
CustomerId,Surname,CreditScore,Geography,Gender,Age,Tenure,Balance,NumOfProducts,HasCrCard,IsActiveMember,EstimatedSalary
```

Para avaliação histórica, inclua `Exited`, com 0 ou 1. A validação verifica campos ausentes, IDs duplicados, números inválidos e categorias não reconhecidas. Nenhuma linha inválida é removida silenciosamente e nenhum valor de negócio é preenchido automaticamente. Colunas extras não entram no modelo.

Uploads não alteram a base de referência nem o treinamento e não são gravados em disco pela aplicação. Consulte o [contrato completo](doc/referencia-tecnica.md).

## Engenharia e reprodutibilidade

O diretório `models/` armazena o modelo e um manifesto com versão, data, métricas, parâmetros, hashes dos dados e do artefato, código e dependências. O ponteiro `current.txt` identifica o modelo ativo. O carregamento verifica integridade e compatibilidade do ambiente.

Os artefatos são gerados localmente e ignorados pelo Git. Utilize apenas modelos de origem confiável: o formato joblib não deve ser usado para carregar arquivos recebidos de terceiros sem controle de procedência.

### Rodar os testes

Com o ambiente instalado e o modelo preparado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

A suíte cobre regras de seleção, comparação de estratégias, calibração, validação de arquivos, persistência, compatibilidade, previsão sem treinamento e fluxos da interface. O [workflow de CI](.github/workflows/tests.yml) executa treinamento e testes em pushes e pull requests no GitHub. A execução remota deve ser verificada na aba Actions do repositório.

## Estrutura

```text
Modelagem-de-Churn/
├── app.py                    # Entrada da aplicação
├── train.py                  # Treinamento e geração do artefato
├── report.py                 # Relatórios do modelo ativo
├── iniciar.bat               # Iniciador Windows
├── treinar.bat               # Preparação e treinamento no Windows
├── requirements.txt          # Dependências
├── src/churn_insights/       # Interface, inferência, validação e análise
├── assets/                   # Estilos e recursos visuais
├── data/                     # Base de referência e notebook
├── models/                   # Artefatos locais
├── tests/                    # Testes automatizados
├── imagens/                  # Recursos de imagem
├── doc/                      # Documentação e resultados
└── .github/workflows/        # Integração contínua
```

## Documentação

- [Arquitetura e decisões técnicas](doc/arquitetura.md)
- [Referência técnica e contrato dos dados](doc/referencia-tecnica.md)
- [Roteiro de apresentação em cinco minutos](doc/roteiro-apresentacao.md)
- [Resultados do modelo em Markdown](doc/resultados-modelo.md)
- [Resultados em JSON](doc/resultados-modelo.json)

## Limitações e interpretação

A carteira completa inclui registros de treino e serve à exploração histórica. As métricas e a comparação de estratégias utilizam o teste separado. As baselines aleatórias representam expectativas matemáticas, que podem ser fracionárias.

A base não informa datas, resultados de campanhas ou moeda dos saldos. Portanto, cancelamentos identificados não equivalem a cancelamentos evitados, e saldo não representa receita recuperada. O projeto não comprova impacto financeiro nem desempenho futuro.

A aplicação é local. Não inclui autenticação, serviço de inferência distribuído ou monitoramento de produção. Origem, licença e período de coleta do CSV precisam ser confirmados para atribuição e redistribuição da base.

## Solução de problemas

| Situação | Como proceder |
|---|---|
| Python não encontrado | Instale Python 3.13 e confirme com `py -3.13 --version` |
| Biblioteca ausente | Execute a instalação com `pip install -r requirements.txt` usando o Python da `.venv` |
| Modelo ausente ou ambiente incompatível | Execute `treinar.bat` ou `train.py` |
| Base local alterada | Gere um modelo compatível com a base usando `train.py` |
| CSV recusado | Confira as colunas e linhas indicadas na mensagem da interface |
| Porta 8501 ocupada | Use `--server.port 8502` no comando Streamlit e abra `http://localhost:8502` |

## Colaboradores

- **Eduardo Souza** — [LinkedIn](https://www.linkedin.com/in/eduardo-de-souza-oliveira-502924259/)
- **Gabriel Finzetto** — [LinkedIn](https://www.linkedin.com/in/gabriel-finzetto/)

## Agradecimentos

Agradecemos às comunidades de Python, pandas, NumPy, SciPy, scikit-learn, Streamlit e Plotly pelo desenvolvimento e pela manutenção das ferramentas de código aberto que sustentam este projeto. Agradecemos também a quem dedica tempo para explorar a aplicação, compartilhar feedback e contribuir com discussões sobre Ciência de Dados, Machine Learning e engenharia de software.

### Risco mínimo e capacidade de atendimento

O risco mínimo (%) é definido por quem conduz a análise, sem valor inicial. O limite é inclusivo: a probabilidade calibrada precisa ser maior ou igual ao percentual informado. A capacidade é o máximo de atendimentos, não uma meta de preenchimento.

Primeiro, o sistema considera o público escolhido; depois, aplica o risco mínimo e ordena os elegíveis por probabilidade decrescente, com desempate por ID. Somente os primeiros até a capacidade são prioritários. Se não houver elegíveis suficientes, as vagas restantes ficam sem uso.

- **Prioritário:** atinge o risco mínimo e cabe na capacidade.
- **Fora da capacidade:** atinge o risco mínimo, mas está além do limite de vagas.
- **Abaixo do risco mínimo:** pertence ao público, mas não atinge o percentual informado; isso não significa risco zero.
- **Já cancelou:** excluído quando o público é clientes sem cancelamento.
- **Não definido:** falta informar capacidade, risco mínimo ou público.

Com 0%, todo o público passa pelo critério de risco; com 100%, apenas estimativas de exatamente 100%. Os controles não retreinam o modelo nem alteram a comparação histórica de estratégias. Os ícones de interrogação ao lado dos campos explicam as regras e trazem um exemplo ilustrativo. Limpar filtros também esvazia o risco mínimo.

### Relatório CSV da comparação de estratégias

O botão **Exportar relatório completo** gera uma linha por estratégia, com colunas organizadas em capacidade, população de teste, resultados, comparação com sorteio e rastreabilidade. Inclui vagas não utilizadas, utilização da capacidade, churn da base, cancelamentos identificados e não identificados, precisão, cobertura, diferenças em relação a sorteio e lift. O arquivo identifica a versão do modelo, o treinamento, a exportação em UTC e o hash da base.

Lift é a precisão dividida pela taxa de churn da base. As diferenças consideram um sorteio com a mesma quantidade efetivamente selecionada por cada estratégia. Contagens aleatórias são médias esperadas; denominadores nulos deixam a métrica vazia. O relatório avalia o teste completo, sem aplicar filtros ou risco mínimo da carteira.

Formato para planilhas em português: UTF-8 com BOM, ponto e vírgula entre colunas, vírgula decimal e seis casas decimais nos valores fracionários. Ao importar em outras ferramentas, selecione essas opções. Este é um relatório agregado; não é um arquivo de clientes para o importador de previsões.

### Probabilidade estimada e resultado histórico por estratégia

A comparação apresenta a **probabilidade média estimada** pelo modelo e a **taxa histórica de cancelamento** entre os clientes selecionados (também chamada precisão da seleção). A diferença entre elas é expressa em pontos percentuais. Resultado histórico não é uma probabilidade individual conhecida: `Exited` registra 0 ou 1.

Para a seleção do modelo, a média prevista usa as probabilidades dos clientes efetivamente selecionados. Na seleção aleatória, usa a média de toda a base de teste. Em inativos primeiro, pondera as médias de inativos e ativos pelo número de vagas de cada grupo. As taxas históricas das estratégias com sorteio também são expectativas matemáticas, e não resultados de uma seleção aleatória realizada.

O primeiro gráfico compara os dois percentuais na escala de 0 a 100%. O segundo mostra cancelamentos identificados e cobertura dos cancelamentos do teste. O CSV inclui a média estimada, a soma das probabilidades e a diferença para a taxa histórica; a coluna precisão da seleção corresponde à taxa histórica. Essas médias agregadas não substituem a curva de calibração nem medem efeito de retenção.
