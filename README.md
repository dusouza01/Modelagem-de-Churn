# 🏦 Customer Churn Prediction - Portfólio

Uma aplicação interativa para identificar antecipadamente clientes com maior risco de cancelamento, utilizando Machine Learning e análise de dados. Ferramenta profissional que transforma dados em decisões de negócio.

## 📊 Sobre o Projeto

### O Problema
Clientes estão cancelando suas contas, resultando em:
- Perda de receita recorrente
- Redução da base de clientes
- Necessidade de adquirir novos clientes (custo 5-25x maior)

### A Solução
Uma aplicação que permite:
- ✅ Identificar clientes em risco de forma automática
- ✅ Entender razões por trás do cancelamento
- ✅ Priorizar ações de retenção por impacto
- ✅ Monitorar efetividade das estratégias

### Impacto Esperado
- Aumento da taxa de retenção
- Maior lifetime value por cliente
- Redução de custo de aquisição relativo
- Melhor compreensão do comportamento do cliente

## 🎯 Objetivos

1. **Análise Exploratória**: Entender quem são os clientes que cancelam
2. **Descoberta de Padrões**: Identificar características comuns entre churn
3. **Modelagem Preditiva**: Estimar risco individual com ML
4. **Priorização**: Ranking de clientes por risco
5. **Ação**: Transformar insights em recomendações de negócio

## 📈 Estatísticas do Dataset

- **Total de Clientes**: 10.000
- **Taxa de Churn**: ~20,4%
- **Período de Dados**: Múltiplos anos
- **Variáveis**: 13 features + 1 target
- **Sem Dados Ausentes**: ✓

## 🎨 Paleta de Cores (Itau)

- 🔵 Azul Primário: #4C72B0
- 🟠 Laranja Secundário: #DD8452
- 🟢 Verde Terciário: #55A868

## 📱 Estrutura da Aplicação

### 🏠 Visão Geral
- Apresentação do problema e objetivo
- KPIs principais (total de clientes, taxa de churn, receita em risco)
- Distribuição de clientes por status

### 🔎 Exploração dos Dados
- Características do dataset
- Distribuição de variáveis
- Visualizações de EDA
- Insights sobre qualidade dos dados

### 👥 Perfil do Cliente
- Filtros interativos por país, gênero, faixa etária
- Análise segmentada de perfis
- Distribuições por características demográficas
- Comportamento por segmento

### 📉 Fatores Associados ao Churn
- Taxa de churn por gênero (Mulheres: 25,1% vs Homens: 16,5%)
- Taxa de churn por faixa etária (61+: 56,8% vs 18-30: 13,3%)
- Taxa de churn por número de produtos
- Taxa de churn por atividade (Inativos: 26,5% vs Ativos: 6,8%)
- Taxa de churn ao longo do tempo (Tenure)

### 🤖 Modelo Preditivo
- Treinamento de múltiplos modelos
- Comparação de métricas (Accuracy, Precision, Recall, F1, AUC-ROC)
- Curva ROC
- Matriz de Confusão
- Importância das features
- Explicação de métricas em linguagem de negócio

### 🎯 Clientes em Alto Risco
- Classificação de risco (Baixo, Médio, Alto)
- Top 10/20/50/100 clientes em maior risco
- Ranking por probabilidade de churn
- Detalhes dos clientes (idade, tenure, saldo, etc)

### 💰 Impacto no Negócio
- Cálculo de receita em risco
- Cenários parametrizáveis de retenção
- Impacto por taxa de retenção
- Segmentação de risco por características
- ROI potencial das ações

### 💡 Recomendações
- Priorização de clientes em risco
- Estratégias segmentadas por perfil
- Programa de ativação
- Programa de onboarding melhorado
- Framework de monitoramento contínuo
- Métricas de sucesso

### 💻 Tecnologias
- Stack tecnológico utilizado
- Descrição de cada ferramenta
- Arquitetura da solução
- Instruções de execução

## 🔑 Insights Principais

### Por Gênero
- **Mulheres**: 25,1% de taxa de churn
- **Homens**: 16,5% de taxa de churn
- **Insight**: Investigar necessidades específicas de mulheres

### Por Idade
- **61+**: 56,8% de taxa de churn
- **51-60**: 40,3% de taxa de churn
- **18-30**: 13,3% de taxa de churn
- **Insight**: Clientes mais velhos requerem atenção especial

### Por Produtos
- **1 Produto**: 27,7% de taxa de churn
- **2 Produtos**: 10,2% de taxa de churn
- **3+ Produtos**: <5% de taxa de churn
- **Insight**: Cross-sell reduz significativamente churn

### Por Atividade
- **Inativos**: 26,5% de taxa de churn
- **Ativos**: 6,8% de taxa de churn
- **Insight**: Engajamento é crítico para retenção

### Por Tenure
- **Anos 0-1**: ~45% de taxa de churn
- **Anos 5-10**: ~5% de taxa de churn
- **Insight**: Período crítico é nos primeiros meses

## 🤖 Modelos Utilizados

### Logistic Regression
- Interpretável e rápido
- Baseline de performance
- Bom para entender feature importance

### Random Forest
- Melhor performance geral
- Captura não-linearidades
- Mais robusto a outliers
- Modelo principal para predição

### Métricas de Avaliação
- **Accuracy**: Porcentagem de previsões corretas
- **Precision**: Taxa de acerto nas previsões positivas
- **Recall**: Capacidade de identificar todos os churn
- **F1-Score**: Balanço entre Precision e Recall
- **AUC-ROC**: Performance geral de classificação

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+**: Linguagem principal
- **Pandas**: Manipulação de dados
- **NumPy**: Operações numéricas
- **Scikit-learn**: Machine Learning
- **Plotly**: Visualizações interativas

### Frontend
- **Streamlit**: Framework web para data apps
- **CSS/HTML customizado**: Styling profissional

### Infraestrutura
- Executável localmente
- Pode ser deployado em Streamlit Cloud, Heroku, AWS, etc.

## 📦 Instalação

### Pré-requisitos
- Python 3.9+
- pip (gerenciador de pacotes)

### Passo a Passo

1. **Clonar repositório** (ou copiar arquivos)
```bash
git clone <seu-repositorio>
cd projeto-churn
```

2. **Criar ambiente virtual** (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Executar aplicação**
```bash
streamlit run app.py
```

5. **Acessar no navegador**
```
http://localhost:8501
```

## 📂 Estrutura de Arquivos

```
projeto-churn/
├── app.py                      # Aplicação Streamlit principal (800+ linhas)
├── Churn_Modelling.csv        # Dataset com 10.000 clientes
├── requirements.txt            # Dependências do projeto
└── README.md                   # Este arquivo
```

## 🚀 Como Usar

1. **Explorar Dados**: Use a seção "Exploração dos Dados" para entender o dataset
2. **Entender Padrões**: Acesse "Fatores Associados ao Churn" para descobrir comportamentos
3. **Identificar Risco**: Veja "Clientes em Alto Risco" para listar alvos de retenção
4. **Quantificar Impacto**: Use "Impacto no Negócio" para modelar cenários
5. **Implementar**: Siga as "Recomendações" para ações concretas

## 📊 Cenários de Uso

### Para Executivos
- Entender taxa de churn e impacto financeiro
- Ver KPIs principais em tempo real
- Validar ROI de estratégias de retenção

### Para Analistas
- Explorar dados e encontrar padrões
- Entender feature importance
- Validar hipóteses sobre churn

### Para Time de Retenção
- Identificar clientes prioritários
- Segmentar por perfil e risco
- Mensurar efetividade de campanhas

### Para Liderança
- Tomar decisões data-driven
- Alocar recursos de forma otimizada
- Monitorar KPIs e progressão

## 🎓 Aprendizados Técnicos

Este projeto demonstra:
- ✅ Análise exploratória de dados (EDA)
- ✅ Feature engineering e preprocessing
- ✅ Treinamento de múltiplos modelos
- ✅ Avaliação e seleção de modelos
- ✅ Interpretabilidade de modelos
- ✅ Desenvolvimento de aplicação web
- ✅ Design de UI/UX
- ✅ Storytelling com dados
- ✅ Transformação de insights em ações
- ✅ Boas práticas de código Python

## 🔄 Próximos Passos

### Curto Prazo
- [ ] Deploy em Streamlit Cloud
- [ ] Adicionar autenticação de usuários
- [ ] Criar dashboard de monitoramento
- [ ] Implementar exportação de relatórios

### Médio Prazo
- [ ] Integração com CRM (Salesforce, HubSpot)
- [ ] Implementar retraining automático do modelo
- [ ] Adicionar validação cruzada
- [ ] Criar API REST para predições

### Longo Prazo
- [ ] Implementar modelos mais complexos (XGBoost, LightGBM)
- [ ] Feature engineering avançado
- [ ] Análise causal (Causal Inference)
- [ ] Recomendações de oferta personalizada

## 📈 Métricas de Sucesso

### Para o Modelo
- AUC-ROC: > 0.85
- Recall: > 0.80 (não deixar ninguém escapar)
- Precision: > 0.70 (evitar falsos positivos)

### Para o Negócio
- Redução de churn: 5-10% no primeiro ano
- Aumento de lifetime value: 10-15%
- ROI de campanhas: 3:1 ou maior

## 💡 Recomendações de Negócio

### Imediato
1. Priorizar contato com clientes em alto risco
2. Oferecer incentivos personalizados
3. Melhorar atendimento ao cliente

### Curto Prazo (1-3 meses)
1. Implementar programa de onboarding melhorado
2. Criar estratégias segmentadas por perfil
3. Iniciar programa de ativação

### Médio Prazo (3-6 meses)
1. Monitorar e medir efetividade das ações
2. Refinar segmentação com base em resultados
3. Expandir para cross-sell

### Longo Prazo (6+ meses)
1. Integrar modelo com sistemas operacionais
2. Implementar retraining automático
3. Expandir para mais análises (CLV, LTV, etc)

## ⚖️ Considerações Éticas

Este projeto foi desenvolvido com:
- ✅ Privacidade de dados em mente
- ✅ Foco em benefício mútuo (cliente + empresa)
- ✅ Sem discriminação por características protegidas
- ✅ Transparência sobre decisões

## 📝 Licença

Projeto de portfólio - Livre para uso educacional e profissional.

## 👨‍💻 Autor

Desenvolvido como portfólio de Data Analytics e Machine Learning, demonstrando:
- Análise crítica de dados
- Modelagem preditiva
- Comunicação de insights
- Transformação de dados em ações de negócio

## 📞 Contato & Suporte

Para dúvidas ou sugestões sobre o projeto:
- Consulte a documentação em cada página da aplicação
- Verifique os insights e recomendações
- Experimente diferentes filtros e cenários

## 🙏 Agradecimentos

Dados de: Kaggle (Churn Modelling Dataset)
Framework: Streamlit
Inspiração: Boas práticas em Data Analytics e Storytelling

---

**Desenvolvido com ❤️ usando Python, Streamlit e Scikit-learn**

*"Os dados não mentem. Eles contam histórias."*
