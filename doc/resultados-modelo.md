# Resultados do modelo ativo

Gerado por `report.py` a partir do artefato local, sem novo treinamento.

- Versão: `20260921T201631Z-96682524`
- Treinado em UTC: `2026-09-21T20:16:31.680749+00:00`
- SHA-256 da base: `3996cd1fa372e0db0cd9c0ebac35bbd4e8e3c65fb942bb010c826e7b1eeef0a0`
- Treino: 8000 clientes; teste: 2000 clientes.
- Variáveis preditoras: 10.

## Avaliação separada

| Métrica | Resultado |
|---|---:|
| Acurácia (corte de 50%) | 0.868500 |
| ROC AUC | 0.857102 |

| Probabilidades | Brier | Log loss |
|---|---:|---:|
| Calibrado | 0.101665 | 0.340163 |

## Comparação por capacidade

Não calculada: nenhuma capacidade foi informada. Para incluir, execute `python report.py --capacidade N`, substituindo N pela quantidade escolhida.

## Limites da evidência

As métricas usam o teste histórico completo. A carteira exibida também contém registros de treino e não deve ser usada para alegar desempenho independente.

A base não registra datas nem resultados de campanhas. Cancelamentos identificados não são cancelamentos evitados; saldo não é receita recuperada. Não há garantia de desempenho futuro nem estimativa de retorno financeiro.

As estratégias aleatórias são expectativas matemáticas, não campanhas observadas. O método de calibração foi definido no treino; o teste não foi usado para ajustar a calibração.

O relatório representa a versão identificada acima. Gere novamente após ativar outro modelo.
