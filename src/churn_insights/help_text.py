"""Contextual explanations for editable dashboard controls."""

COUNTRY_HELP = """**Explore a carteira por país.**

Escolha um país para exibir somente seus clientes ou selecione Todos para visualizar todos os países da base. O filtro combina-se com gênero e prioridade e atualiza os indicadores, gráficos, insights e a tabela da carteira. A exportação da carteira respeita esse recorte e a busca.

A prioridade continua sendo calculada na carteira completa: mudar o país não redistribui vagas, não altera probabilidades e não retreina o modelo. A avaliação de calibração, a comparação histórica de estratégias e os arquivos importados permanecem independentes deste filtro. Se a combinação não encontrar clientes, ajuste os filtros ou use Limpar filtros."""

GENDER_HELP = """**Explore os grupos de gênero registrados na base.**

Escolha uma categoria para visualizar seus registros ou Todos para manter todas as categorias. As opções vêm dos dados disponíveis. O filtro combina-se com país e prioridade e atualiza a análise e a tabela da carteira; a busca refina somente a tabela e sua exportação.

Este controle serve à análise descritiva. Diferenças entre grupos não demonstram causalidade. Filtrar não recalcula a prioridade nem altera o modelo. As métricas do teste separado, a comparação de estratégias e as importações não são filtradas por este campo."""

PRIORITY_HELP = """**Escolha quais status de atendimento deseja visualizar.**

• **Todos:** mostra todos os status no recorte de país e gênero.
• **Prioritário:** pertence ao público escolhido, atinge o risco mínimo e está entre os maiores riscos até a capacidade.
• **Fora da capacidade:** atinge o risco mínimo, mas não há vaga na seleção.
• **Abaixo do risco mínimo:** pertence ao público, mas tem probabilidade inferior ao limite informado; isso não significa risco zero.
• **Já cancelou:** possui Exited = 1 e foi excluído pelo público Clientes sem cancelamento.
• **Não definido:** falta informar capacidade, risco mínimo ou público.

O filtro atualiza os indicadores, gráficos, insights e a tabela da carteira. Ele apenas exibe a classificação calculada: não torna clientes prioritários nem seleciona substitutos. Ao escolher Prioritário, é esperado que todas as linhas exibidas tenham esse status. A comparação de estratégias permanece independente."""

CAPACITY_HELP = """**Informe o máximo de clientes que consegue atender na carteira completa.**

Use um número inteiro a partir de 1. Capacidade, risco mínimo e público precisam estar preenchidos para definir prioridades; um campo vazio mantém a prioridade como Não definido.

A seleção considera primeiro o público escolhido e o risco mínimo inclusivo. Em seguida, ordena os elegíveis do maior para o menor risco e seleciona até a capacidade. Empates são resolvidos pelo ID. Quem atinge o risco mínimo, mas não cabe nas vagas, fica Fora da capacidade.

**Exemplo ilustrativo:** com 50 vagas e apenas 12 elegíveis, são selecionados 12 clientes e sobram 38 vagas. Clientes abaixo do limite não completam a lista. A capacidade não é uma meta obrigatória de preenchimento.

País, gênero, prioridade e busca apenas filtram a exibição; não redistribuem vagas. Este controle não retreina o modelo e é independente da capacidade usada na comparação de estratégias. Limpar filtros esvazia este campo."""

MINIMUM_RISK_HELP = """**Defina a probabilidade mínima de churn para participar da seleção.**

Informe um percentual de 0 a 100. O campo começa vazio: nenhum limite é escolhido automaticamente. Capacidade, risco mínimo e público precisam estar preenchidos para definir prioridades.

O limite é inclusivo. Em um **exemplo ilustrativo com 60%**, clientes com probabilidade de 60% ou mais podem participar; abaixo disso recebem Abaixo do risco mínimo. Entre os elegíveis, apenas os maiores riscos até a capacidade ficam Prioritários. Os demais ficam Fora da capacidade.

Com 0%, todo o público passa pelo critério de risco. Com 100%, apenas probabilidades de exatamente 100% passam. Aumentar o limite pode reduzir a seleção e deixar vagas sem uso. A comparação usa a probabilidade completa, mesmo que a tabela a exiba arredondada.

Este é um critério da sua análise: não altera as probabilidades, não retreina o modelo e não garante cancelamento. Estar abaixo do limite também não significa ausência de risco. O limite não afeta as métricas nem a comparação histórica de estratégias. Limpar filtros esvazia este campo."""

SCOPE_HELP = """**Defina quem pode participar da lista de prioridade.**

**Clientes sem cancelamento:** considera somente Exited = 0, isto é, clientes sem cancelamento registrado na base. Registros com Exited = 1 ficam com o status Já cancelou.

**Todos · demonstração histórica:** permite que clientes com e sem cancelamento registrado participem, para explorar o ranking histórico. Essa opção não representa uma lista atual de contatos.

Dentro do público escolhido, o sistema exige o risco mínimo e seleciona os maiores riscos até a capacidade, sempre na carteira completa. País e gênero apenas filtram sua exibição. Sem público, capacidade ou risco mínimo, a prioridade fica Não definido.

Exited é usado para definir a elegibilidade, não como variável preditora. O público não muda as probabilidades nem o conjunto de teste das avaliações. Limpar filtros esvazia esta escolha."""

SEARCH_HELP = """**Encontre clientes por sobrenome ou ID.**

Digite o sobrenome, o ID completo ou parte de um deles. A pesquisa procura o texto em qualquer posição; sobrenomes são comparados sem distinguir maiúsculas de minúsculas. Caracteres são tratados literalmente, sem expressões regulares. Acentos continuam fazendo parte do texto pesquisado.

A busca atua sobre os clientes que já passaram pelos filtros de país, gênero e prioridade. Ela refina somente a tabela Clientes em foco e o arquivo Exportar seleção; não modifica os indicadores, gráficos, probabilidades ou a classificação de prioridade.

Deixe o campo vazio para mostrar todo o recorte. Se não houver correspondências, a tabela informa que nenhum cliente foi encontrado e a exportação fica desabilitada. Limpar filtros também apaga a busca."""

PURPOSE_HELP = """**Escolha o objetivo do arquivo antes de enviá-lo.**

**Prever risco de clientes:** usa o modelo salvo para calcular probabilidades. Exited é opcional; se presente, é validada, mas não entra na previsão. Este modo não calcula métricas de desempenho para o arquivo.

**Avaliar resultados históricos:** exige Exited com valores 0 ou 1 e compara previsões com cancelamentos registrados, calculando Brier, log loss e ROC AUC. AUC fica indisponível se houver apenas uma classe. Se algum ID já pertencer à base de desenvolvimento, as métricas da importação ficam desabilitadas para evitar apresentá-la como avaliação independente; as previsões continuam disponíveis.

A finalidade começa vazia. O cabeçalho para download se adapta ao modo escolhido, e cada modo possui seu próprio campo de upload. Nenhum upload retreina o modelo ou substitui a carteira de referência. IDs diferentes não garantem independência: a origem e o período dos dados também precisam ser verificados."""

CSV_HELP = """**Envie a base de clientes no formato aceito pelo modelo.**

Use CSV UTF-8, com vírgulas entre colunas e ponto decimal, até 10 MiB e 100.000 linhas. Baixe o cabeçalho nesta seção para começar com os nomes corretos. Preencha com seus dados; o cabeçalho não contém clientes fictícios.

São obrigatórias CustomerId, Surname, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember e EstimatedSalary. Na avaliação histórica, inclua Exited (0 ou 1). Se Exited estiver presente no modo de previsão, também será validada.

IDs devem ser únicos. Campos obrigatórios não podem estar vazios. Valores numéricos precisam ser finitos e não negativos; campos inteiros não aceitam frações. HasCrCard e IsActiveMember aceitam 0 ou 1. Colunas extras são ignoradas pelo modelo. Categorias devem corresponder às aceitas no treino, listadas abaixo.

Se houver erro, corrija as colunas e linhas indicadas e reenvie o arquivo. A aplicação não preenche dados nem remove registros inválidos automaticamente. O arquivo é processado pelo modelo ativo, sem treinamento e sem ser salvo em disco pela aplicação. A exportação identifica o modelo utilizado.

O CSV agregado da comparação de estratégias não é uma base de clientes e não deve ser enviado aqui; ele usa outro cabeçalho e formato de separação."""


def comparison_capacity_help(test_count, cancellations, complete_with_active):
    count = f"{test_count:,}".replace(",", ".")
    cancelled = f"{cancellations:,}".replace(",", ".")
    completion = ("Inativos primeiro completa as vagas restantes com seleção aleatória entre ativos."
                  if complete_with_active else "Inativos primeiro não completa as vagas com ativos e pode selecionar menos clientes.")
    full = ("Todas as estratégias selecionam os mesmos clientes quando a capacidade cobre a base inteira."
            if complete_with_active else "Modelo e seleção aleatória selecionam a base inteira; inativos primeiro pode manter uma seleção menor.")
    return f"""**Informe quantos clientes cada estratégia pode selecionar no teste histórico.**

Use um inteiro a partir de 1. O campo começa vazio e a comparação só é calculada após o preenchimento. A avaliação utiliza os mesmos **{count} clientes de teste**, sem aplicar os filtros, o público ou o risco mínimo da carteira.

Modelo seleciona os maiores riscos calibrados. Aleatória considera seleção uniforme sem reposição. Inativos primeiro prioriza IsActiveMember = 0. {completion} As regras com sorteio exibem expectativas matemáticas, que podem ser fracionárias, não um sorteio realizado.

**Por que os gráficos podem ficar iguais?** {full} A base contém **{cancelled} cancelamentos registrados**. Selecionar a base inteira identifica todos eles e alcança 100% de cobertura quando há cancelamentos. Com os mesmos clientes, a taxa histórica e a probabilidade média são iguais entre as estratégias.

Isso não significa que a probabilidade estimada seja igual à taxa histórica: são medidas diferentes que podem divergir. Para investigar a vantagem de priorizar, use uma capacidade menor que {count}. Uma capacidade maior que a base não duplica clientes; as vagas excedentes ficam sem uso.

O valor atual é registrado no relatório CSV. Este controle não modifica a prioridade da carteira, não retreina o modelo e não é apagado pelo botão Limpar filtros da carteira."""
