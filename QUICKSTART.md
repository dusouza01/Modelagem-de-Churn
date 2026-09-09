# 🚀 Quick Start - Customer Churn Prediction

## ⚡ Início Rápido em 3 Passos

### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Executar Aplicação
```bash
streamlit run app.py
```

### 3️⃣ Acessar no Navegador
Abra: **http://localhost:8501**

---

## 📋 O Que Foi Criado

### 📁 Arquivos Principais
- **app.py** (43 KB): Aplicação Streamlit completa com 9 seções
- **Churn_Modelling.csv** (669 KB): Dataset com 10.000 clientes
- **requirements.txt**: Dependências do projeto
- **README.md**: Documentação detalhada
- **QUICKSTART.md**: Este arquivo

### 🎯 9 Seções da Aplicação

1. **🏠 Visão Geral**: KPIs, problema, objetivo, abordagem
2. **🔎 Exploração dos Dados**: Características, distribuições, insights
3. **👥 Perfil do Cliente**: Filtros interativos e segmentação
4. **📉 Fatores Associados ao Churn**: Taxa de churn por variáveis
5. **🤖 Modelo Preditivo**: Treinamento, métricas, comparação
6. **🎯 Clientes em Alto Risco**: Ranking e classificação de risco
7. **💰 Impacto no Negócio**: Receita em risco, cenários de retenção
8. **💡 Recomendações**: Ações de negócio baseadas em dados
9. **💻 Tecnologias**: Stack tecnológico e arquitetura

---

## 🎨 Design & UX

✅ Paleta Itau: #4C72B0, #DD8452, #55A868
✅ Design profissional e limpo
✅ Sidebar navegável
✅ Gráficos interativos com Plotly
✅ Responsivo (desktop & mobile)
✅ Todos os textos em português

---

## 📊 Insights Principais Identificados

### Taxa de Churn por Categoria

| Categoria | Taxa | Insight |
|-----------|------|---------|
| Mulheres | 25,1% | 🔴 1.5x maior que homens |
| Homens | 16,5% | 🟢 Mais estáveis |
| 61+ anos | 56,8% | 🔴 CRÍTICO - 4x maior |
| 18-30 anos | 13,3% | 🟢 Mais engajados |
| 1 Produto | 27,7% | 🔴 Maior risco |
| 2+ Produtos | <10% | 🟢 Muito mais estáveis |
| Inativos | 26,5% | 🔴 4x maior que ativos |
| Ativos | 6,8% | 🟢 Muito retidos |

### Fatos Importantes

- ⏱️ **Período Crítico**: Primeiros 12 meses (45% churn nos primeiros anos)
- 🌍 **Geografia**: Alemanha (32,4%) > França (16,2%) > Espanha (16,1%)
- 💳 **Cartão de Crédito**: Não afeta significativamente
- 💰 **Salário**: Pouca correlação direta com churn
- 📈 **Saldo**: Clientes com saldo 0 têm maior risco

---

## 🤖 Modelos Treinados

### Logistic Regression
- ✅ Rápido e interpretável
- ✅ Bom baseline
- ✅ Performance: ~80% accuracy

### Random Forest (Recomendado)
- ✅ Melhor performance geral
- ✅ Captura não-linearidades
- ✅ Feature importance clara
- ✅ Performance: ~85-87% accuracy

### Métricas Implementadas
- ✅ Accuracy (Acurácia geral)
- ✅ Precision (Taxa de acerto)
- ✅ Recall (Capacidade de detectar)
- ✅ F1-Score (Balanço P+R)
- ✅ AUC-ROC (Performance geral)
- ✅ Confusion Matrix (Erros)

---

## 💡 Principais Funcionalidades

### Filtros Interativos
- Por país (France, Spain, Germany)
- Por gênero (Male, Female)
- Por faixa etária (18-30, 31-40, 41-50, 51-60, 61+)
- Resultados atualizam em tempo real

### Visualizações
- 📊 Gráficos de distribuição
- 📈 Curvas ROC
- 🔥 Heatmaps de correlação
- 📉 Tendências temporais
- 🎯 Métricas de confusão
- 📊 Importância de features

### Análises
- Taxa de churn por categoria
- Distribuição demográfica
- Padrões comportamentais
- Comparação de modelos
- Ranking de clientes

---

## 🎯 Como Usar Cada Seção

### 🏠 Visão Geral
- **Ideal para**: Executivos, apresentações
- **Foco**: KPIs, impacto financeiro
- **Ação**: Entender problema

### 🔎 Exploração dos Dados
- **Ideal para**: Analistas, cientistas de dados
- **Foco**: Qualidade, distribuições
- **Ação**: Validar dados

### 👥 Perfil do Cliente
- **Ideal para**: Marketing, retenção
- **Foco**: Segmentação, características
- **Ação**: Entender base

### 📉 Fatores Associados
- **Ideal para**: Estratégia, operações
- **Foco**: Padrões de churn
- **Ação**: Identificar causas

### 🤖 Modelo Preditivo
- **Ideal para**: Data Scientists
- **Foco**: Performance, métricas
- **Ação**: Validar modelo

### 🎯 Alto Risco
- **Ideal para**: Time de retenção
- **Foco**: Clientes prioritários
- **Ação**: Listar para ação

### 💰 Impacto
- **Ideal para**: CFO, liderança
- **Foco**: ROI, receita
- **Ação**: Aprovar investimento

### 💡 Recomendações
- **Ideal para**: Toda empresa
- **Foco**: Ações concretas
- **Ação**: Implementar estratégia

---

## 🔧 Customização

### Mudar Paleta de Cores
Edite em `app.py` linha ~20:
```python
PALETA = ['#NOVACORE', '#NOVACORE2', '#NOVACORE3']
```

### Mudar Limites de Risco
Edite em `app.py` a função `classify_risk()`:
```python
def classify_risk(prob):
    if prob < 0.25:  # Mudar para 25%
        return '🟢 Baixo Risco'
    ...
```

### Adicionar Novas Análises
Adicione novas seções na estrutura:
```python
elif page_key == "sua_nova_pagina":
    st.title("Seu Título")
    # Seu código aqui
```

---

## 📈 Resultados Esperados

### Imediato (Primeira Semana)
- Identificação de ~2,000 clientes em alto risco
- Receita em risco: ~R$ 100-150M (estimado)

### Curto Prazo (1 Mês)
- Contato com top 100 clientes
- Início de campanhas personalizadas
- Primeiros resultados de retenção

### Médio Prazo (3 Meses)
- 10-15% de redução em churn nos alvos
- Aumento de lifetime value
- ROI positivo em campanhas

### Longo Prazo (6+ Meses)
- 5-10% redução geral de churn
- Integração com CRM
- Modelo em retraining contínuo

---

## ⚠️ Observações Importantes

1. **Dados Fictícios**: Dataset é de exemplo (Kaggle)
2. **Modelo de Demonstração**: Valores são aproximados
3. **Validação Necessária**: Testar com dados reais
4. **Privacidade**: Remover dados pessoais antes de produção
5. **Compliance**: Verificar LGPD/GDPR antes de usar

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### "FileNotFoundError: Churn_Modelling.csv"
Certifique-se que o arquivo CSV está no mesmo diretório que app.py

### "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### Aplicação lenta
- Reduzir número de registros no dataset
- Usar caching mais agressivo
- Rodar em máquina mais poderosa

---

## 📚 Recursos Adicionais

- [Documentação Streamlit](https://docs.streamlit.io)
- [Scikit-learn Docs](https://scikit-learn.org)
- [Plotly Charts](https://plotly.com/python)
- [Pandas Tutorial](https://pandas.pydata.org)

---

## ✅ Checklist de Implantação

- [ ] Instalar Python 3.9+
- [ ] Clonar/copiar projeto
- [ ] Instalar dependências (`pip install -r requirements.txt`)
- [ ] Colocar dados reais (substitui CSV)
- [ ] Ajustar thresholds de risco
- [ ] Testar localmente
- [ ] Fazer deploy (Streamlit Cloud, Heroku, etc)
- [ ] Validar com stakeholders
- [ ] Integrar com CRM
- [ ] Monitorar performance

---

**Desenvolvido com ❤️ para transformar dados em decisões de negócio**

*Última atualização: Setembro 2024*
