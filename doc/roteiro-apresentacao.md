# Demonstração de cinco minutos

**Público:** entrevistas de engenharia de software e Machine Learning/Ciência de Dados.

**Mensagem central:** transformar uma estimativa de churn em uma decisão de priorização, com avaliação histórica e engenharia reproduzível.

## Preparar antes da entrevista

1. Abra `iniciar.bat` e confirme o carregamento da página. Caso não haja modelo compatível, execute `treinar.bat` antes da apresentação.
2. Execute `python report.py` no ambiente virtual. Confira a versão em `doc/resultados-modelo.md` e em “Rastreabilidade do modelo e contrato do arquivo”.
3. Defina a quantidade **N** que deseja demonstrar. Se for apenas uma simulação, diga isso explicitamente; não a apresente como capacidade de uma empresa. Nenhuma quantidade foi predefinida neste roteiro.
4. Escolha um país disponível no filtro que queira investigar. Não há segmento preselecionado nem resultado favorável exigido.
5. Deixe a capacidade e o público inicialmente vazios, a busca limpa e os filtros em “Todos”.
6. Mantenha o relatório e o diagrama de arquitetura abertos em abas para consulta. A demonstração principal não depende de um upload externo.

Os comandos com `python` neste roteiro pressupõem o ambiente virtual ativo; no PowerShell, também podem ser executados com `.\.venv\Scripts\python.exe`.

## Roteiro cronometrado

| Tempo | Ação na tela | O que explicar |
|---|---|---|
| 0:00–0:35 | Mostrar a visão da carteira, sem preencher capacidade | “A pergunta é quem priorizar quando o atendimento tem capacidade limitada. O projeto usa cancelamentos históricos para investigar essa decisão.” |
| 0:35–1:15 | Escolher o país e observar distribuição de risco e histórico por país | “Os gráficos descrevem o recorte selecionado. Associação histórica não prova a causa do cancelamento. A carteira inclui treino, então não uso esses números para alegar desempenho independente.” |
| 1:15–2:10 | Mostrar métricas e “Confiabilidade das probabilidades” | “Treino e teste foram separados. A calibração foi ajustada só no treino. Aqui avalio as probabilidades calibradas nos clientes de teste, usando Brier, log loss e a curva.” Cite os valores exibidos ou o relatório da versão atual. |
| 2:10–3:00 | Informar N em “Capacidade de atendimento (clientes)”, na comparação | “Com a mesma quantidade de clientes, comparo modelo, seleção aleatória e inativos primeiro. As regras aleatórias mostram expectativas matemáticas. Identificar cancelamentos não significa evitá-los.” Comente o resultado efetivamente exibido, mesmo que não favoreça o modelo. |
| 3:00–4:10 | Voltar à carteira, informar N em “Capacidade de atendimento da carteira (clientes)”, definir o risco mínimo (%), escolher “Clientes sem cancelamento”, filtrar “Prioritário”; ir a “Clientes em foco” e exportar | “A prioridade depende do risco mínimo, da capacidade e do público na carteira completa; os filtros apenas exibem parte dessa seleção. O histórico não entra nas variáveis do modelo. Para esta lista demonstrativa, excluo quem já tem cancelamento registrado. A exportação entrega o recorte selecionado.” |
| 4:10–5:00 | Mostrar a seção de importação e abrir a arquitetura | “O treinamento é separado da previsão. O CSV é validado; o modelo tem versão, hash e dependências registradas. Testes verificam cálculos, contratos e interface. O próximo passo depende de dados temporais e resultados de campanhas para medir comportamento futuro e efeito de retenção.” |

A exportação da carteira aplica os filtros e a busca. Deixe a busca vazia para exportar toda a seleção prioritária. A capacidade da comparação e a da carteira são controles independentes: informe N em ambos para comunicar uma quantidade comum, sem confundir as populações.

## Verificações durante a demonstração

- Ao filtrar o país, os indicadores da carteira mudam; a avaliação de teste continua usando os mesmos 2.000 registros da base atual.
- Na comparação, as três estratégias selecionam o mesmo total, limitado ao teste disponível.
- Na carteira, a seleção pode ter menos que N se não houver clientes elegíveis suficientes. Explique o aviso em vez de alterar os dados.
- Em “Clientes em foco”, a prioridade deve ser “Prioritário” e o cancelamento histórico “Não” para o público escolhido.
- Abra o CSV exportado e confira o total indicado na interface. O arquivo contém a seleção da carteira, não os resultados da comparação.

## Perguntas técnicas e respostas sustentáveis

**Por que Random Forest?** É a implementação atual para dados tabulares. O projeto compara sua seleção com regras simples, mas ainda não demonstra que supera todas as famílias de modelos. Uma comparação entre algoritmos exigiria um protocolo próprio, sem escolher pelo teste já consultado.

**Por que calibrar?** Para avaliar e melhorar a correspondência entre probabilidades e frequências observadas. Mostre as métricas e a curva de confiabilidade do modelo; o resultado histórico não garante desempenho em produção.

**Como evita vazamento?** `Exited`, ID e sobrenome não são preditores. Pré-processamento e calibração são ajustados no treino. A avaliação separada não muda com os filtros. A carteira completa é rotulada como demonstração histórica.

**Como reproduzir?** Instalar as versões declaradas, usar a mesma base, executar `train.py`, rodar os testes e gerar `report.py`. Conferir os hashes e as configurações do manifesto. A nova versão terá outro identificador; diferenças numéricas mínimas podem ocorrer por ambiente e operações paralelas.

**Como escalaria?** Primeiro mediria carga, latência e memória. Depois avaliaria separar a inferência da interface e centralizar versões e observabilidade. Essa arquitetura distribuída não está implementada.

**Qual impacto financeiro?** Não foi medido. Saldo não é receita recuperada; a base não contém custos ou resultados de ações.

## Se algo falhar

- Modelo ausente, incompatível ou base alterada: preparar com `treinar.bat` antes de iniciar a conversa.
- CSV inválido: usar a mensagem de validação para explicar o contrato; não corrigir automaticamente dados de negócio.
- Sem navegador ou servidor disponível: apresentar a arquitetura e o relatório identificado pela versão, deixando claro que é uma evidência previamente gerada, não uma execução ao vivo.

## Encerramento sugerido

“O projeto entrega um fluxo completo de análise, priorização e exportação, com avaliação histórica separada e modelo rastreável. A próxima validação seria prospectiva, usando datas e resultados reais de ações de retenção.”

Evite atribuir ao projeto implantação em produção, ganhos financeiros, clientes recuperados ou testes remotos que não aconteceram.
