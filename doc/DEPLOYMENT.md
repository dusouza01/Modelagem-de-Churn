# 🚀 Guia de Deployment - Customer Churn Prediction

## Opções de Deploy

Esta seção descreve como fazer deploy da aplicação em diferentes plataformas.

---

## 1️⃣ Streamlit Cloud (Recomendado - Gratuito)

### Vantagens
- ✅ Deploy automático do GitHub
- ✅ Gratuito
- ✅ Fácil de usar
- ✅ Suporte oficial
- ✅ HTTPS automático

### Passos

1. **Fazer push para GitHub**
```bash
git init
git add .
git commit -m "Customer Churn Prediction App"
git push origin main
```

2. **Acessar Streamlit Cloud**
   - Ir em: https://share.streamlit.io/
   - Fazer login com GitHub
   - Clicar em "New app"

3. **Configurar**
   - Repository: seu-usuario/seu-repo
   - Branch: main
   - Main file path: app.py

4. **Deploy**
   - Clicar em "Deploy"
   - Aguardar 2-3 minutos
   - Acessar a URL gerada

5. **Compartilhar**
   - URL será: `https://seu-usuario-churn-prediction.streamlit.app`
   - Compartilhar com stakeholders

---

## 2️⃣ Heroku

### Vantagens
- ✅ Mais controle sobre ambiente
- ✅ Versão gratuita (com limitações)
- ✅ Fácil integração com CI/CD
- ✅ Suporte a variáveis de ambiente

### Passos

1. **Instalar Heroku CLI**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download em https://devcenter.heroku.com/articles/heroku-cli
```

2. **Criar arquivo Procfile**
```
web: streamlit run --server.port=$PORT app.py
```

3. **Criar arquivo .streamlit/config.toml**
```toml
[server]
headless = true
port = $PORT

[client]
showErrorDetails = false
```

4. **Fazer push para Heroku**
```bash
heroku login
heroku create seu-app-churn-prediction
git push heroku main
```

5. **Monitorar**
```bash
heroku logs --tail
```

---

## 3️⃣ Docker + AWS (EC2)

### Vantagens
- ✅ Máximo controle
- ✅ Escalabilidade
- ✅ Production-ready
- ✅ Suporte a monitoramento

### Criar Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Criar .dockerignore

```
.git
.gitignore
__pycache__
*.pyc
.DS_Store
.streamlit/secrets.toml
```

### Build e Run Local

```bash
# Build
docker build -t churn-prediction:latest .

# Run
docker run -p 8501:8501 churn-prediction:latest

# Acessar
# http://localhost:8501
```

### Deploy em AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 20.04)
# 2. SSH into instance
ssh -i seu-key.pem ec2-user@seu-instance-ip

# 3. Instalar Docker
sudo apt update
sudo apt install docker.io -y
sudo usermod -aG docker $USER

# 4. Clone repo
git clone seu-repo-url
cd projeto-churn

# 5. Build e run
docker build -t churn-prediction:latest .
docker run -d -p 80:8501 churn-prediction:latest

# 6. Acessar
# http://seu-instance-ip
```

---

## 4️⃣ Google Cloud Run (GCP)

### Vantagens
- ✅ Serverless
- ✅ Paga só pelo uso
- ✅ Escalamento automático
- ✅ HTTPS automático

### Passos

1. **Instalar Google Cloud SDK**
```bash
# https://cloud.google.com/sdk/docs/install
```

2. **Autenticar**
```bash
gcloud auth login
gcloud config set project seu-project-id
```

3. **Build e Deploy**
```bash
gcloud run deploy churn-prediction \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

4. **Acessar**
   - URL será fornecida no comando acima
   - Exemplo: `https://churn-prediction-abc123.run.app`

---

## 5️⃣ Azure App Service

### Vantagens
- ✅ Integração com Microsoft
- ✅ Fácil deployment
- ✅ Suporte a monitoramento
- ✅ Escalamento automático

### Passos

1. **Instalar Azure CLI**
```bash
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

2. **Criar Resource Group**
```bash
az group create --name myResourceGroup --location eastus
```

3. **Criar App Service Plan**
```bash
az appservice plan create \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --sku B1 \
  --is-linux
```

4. **Fazer Deploy**
```bash
az webapp up \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name seu-app-churn \
  --runtime "PYTHON:3.9"
```

---

## 6️⃣ Digital Ocean

### Vantagens
- ✅ Simples e confiável
- ✅ Pricing transparente
- ✅ Suporte bom
- ✅ Droplets gerenciáveis

### Passos

1. **Criar Droplet**
   - Size: $5-10/month (suficiente)
   - OS: Ubuntu 20.04
   - Region: Mais próximo

2. **SSH e Setup**
```bash
ssh root@seu-droplet-ip

# Atualizar sistema
apt update && apt upgrade -y

# Instalar Python
apt install python3-pip python3-venv -y

# Instalar git
apt install git -y
```

3. **Clonar e Setup**
```bash
cd /home
git clone seu-repo-url
cd projeto-churn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Instalar Nginx**
```bash
apt install nginx -y
```

5. **Configurar Nginx**
```bash
# Editar /etc/nginx/sites-available/default
# Adicionar proxy para streamlit
```

6. **Usar systemd para keep-alive**
```bash
# Criar arquivo /etc/systemd/system/streamlit.service
[Unit]
Description=Streamlit
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/projeto-churn
Environment="PATH=/home/projeto-churn/venv/bin"
ExecStart=/home/projeto-churn/venv/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Iniciar serviço**
```bash
systemctl enable streamlit
systemctl start streamlit
```

---

## Comparação de Plataformas

| Plataforma | Custo | Facilidade | Controle | Escalabilidade | Recomendação |
|-----------|-------|-----------|----------|---|---|
| Streamlit Cloud | Gratuito | ⭐⭐⭐⭐⭐ | ⭐⭐ | Automático | ✅ Para começar |
| Heroku | $7+/mês | ⭐⭐⭐⭐ | ⭐⭐⭐ | Bom | ✅ Médio volume |
| Docker + AWS | $5+/mês | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Excelente | ✅ Production |
| Google Cloud Run | Pay-per-use | ⭐⭐⭐ | ⭐⭐⭐ | Automático | ✅ Variable load |
| Azure | $10+/mês | ⭐⭐⭐ | ⭐⭐⭐ | Bom | Para Microsoft |
| Digital Ocean | $5+/mês | ⭐⭐⭐ | ⭐⭐⭐⭐ | Manual | ✅ Controle total |

---

## Dicas de Production

### 1. Variáveis de Ambiente
```python
import os

# Em vez de hardcoding
DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('API_KEY')
```

### 2. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Aplicação iniciada")
logger.error("Erro ao carregar dados")
```

### 3. Monitoring
- Usar ferramentas como Datadog, New Relic, ou CloudWatch
- Monitorar performance
- Alertas para erros

### 4. Segurança
```python
# Adicionar autenticação
import streamlit_authenticator as stauth

# Usar secrets.toml para credenciais
import streamlit as st
db_password = st.secrets["db_password"]
```

### 5. Performance
- Usar `@st.cache_data` agressivamente
- Limitar dados quando possível
- Usar índices no dataset

### 6. Scaling
- Separar treino de modelo (batch) de inferência (online)
- Usar cache de modelos
- Considerar API + Dashboard separados

---

## CI/CD (GitHub Actions)

### Arquivo .github/workflows/deploy.yml

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/
    - name: Deploy
      if: success()
      run: |
        # Script de deployment automático
```

---

## Troubleshooting Deploy

### "Module not found"
Certifique-se que requirements.txt está completo:
```bash
pip freeze > requirements.txt
```

### "Port already in use"
```bash
streamlit run app.py --server.port 8502
```

### "Out of memory"
Limitar dados ou usar processamento em chunks:
```python
# Em vez de carregar tudo
chunk_size = 1000
for chunk in pd.read_csv('file.csv', chunksize=chunk_size):
    process(chunk)
```

### "Slow loading"
Usar `@st.cache_data` mais agressivamente:
```python
@st.cache_data
def expensive_function():
    # Longo processamento
    return result
```

---

## Monitoramento em Production

### Métricas Importantes
- Response time
- Error rate
- CPU/Memory usage
- Número de usuários concurrent
- Taxa de erro

### Alertas Recomendados
- Response time > 5s
- Error rate > 1%
- Memory > 80%
- Downtime > 1 min

### Dashboard Recomendado
```python
# Adicionar página de monitoring
if admin_logged_in:
    st.write("📊 Monitoring Dashboard")
    st.metric("Uptime", "99.9%")
    st.metric("Avg Response", "0.5s")
    st.metric("Errors (24h)", 0)
```

---

## Backup & Recovery

### Backup de Dados
```bash
# Backup diário
0 2 * * * tar -czf /backups/churn-app-$(date +\%Y\%m\%d).tar.gz /app/
```

### Disaster Recovery Plan
1. Manter cópia de código em GitHub
2. Backup automático de dados
3. Teste de recovery mensal
4. Documentação atualizada

---

## Checklist de Deploy

- [ ] Código testado localmente
- [ ] requirements.txt atualizado
- [ ] Secrets configurados (senhas, APIs)
- [ ] Variáveis de ambiente definidas
- [ ] Logging implementado
- [ ] Performance testada
- [ ] UI/UX validada
- [ ] Documentação atualizada
- [ ] Backup strategy definida
- [ ] Monitoring configurado
- [ ] Alertas definidos
- [ ] Suporte técnico disponível

---

## Próximos Passos

1. Escolher plataforma (Recomendação: Streamlit Cloud ou Docker + AWS)
2. Seguir passos específicos acima
3. Validar com stakeholders
4. Monitorar performance
5. Iteração baseada em feedback

---

**Bom deployment! 🚀**
