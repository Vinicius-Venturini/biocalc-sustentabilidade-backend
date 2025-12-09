# BioCalc Backend - Docker Setup

## 🐳 Executando com Docker

### Pré-requisitos

- Docker Desktop instalado
- Docker Compose (incluído no Docker Desktop)

### Início Rápido

1. **Clone o repositório**
```bash
cd biocalc-sustentabilidade-backend
```

2. **Configure as variáveis de ambiente (opcional)**
```bash
cp .env.docker .env
# Edite .env se necessário
```

3. **Inicie os containers**
```bash
docker-compose up -d
```

Isso irá:
- ✅ Criar container PostgreSQL
- ✅ Criar container FastAPI
- ✅ Criar tabelas no banco
- ✅ Popular dados auxiliares automaticamente
- ✅ Iniciar API em http://localhost:8000

4. **Verificar status**
```bash
docker-compose ps
```

5. **Ver logs**
```bash
# Todos os serviços
docker-compose logs -f

# Apenas API
docker-compose logs -f api

# Apenas Database
docker-compose logs -f db
```

### Acessar a API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Comandos Úteis

#### Parar containers
```bash
docker-compose down
```

#### Parar e remover volumes (apaga dados do banco)
```bash
docker-compose down -v
```

#### Reconstruir imagens
```bash
docker-compose build
docker-compose up -d
```

#### Acessar shell do container da API
```bash
docker-compose exec api bash
```

#### Acessar PostgreSQL
```bash
docker-compose exec db psql -U biocalc_user -d biocalc_db
```

#### Ver logs em tempo real
```bash
docker-compose logs -f api
```

#### Executar seed manualmente
```bash
docker-compose exec api python scripts/seed_database.py
```

### Desenvolvimento com Hot Reload

O docker-compose está configurado com volumes para hot reload:
- Alterações em `app/` são detectadas automaticamente
- A API reinicia automaticamente

### Variáveis de Ambiente

Principais variáveis no `.env`:

```env
DATABASE_URL=postgresql://biocalc_user:biocalc_password@db:5432/biocalc_db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=True
```

### Portas Expostas

- **API**: 8000
- **PostgreSQL**: 5432

### Volumes

- `postgres_data`: Dados persistentes do PostgreSQL

### Troubleshooting

#### Erro de conexão com banco
```bash
# Verificar se o banco está rodando
docker-compose ps

# Ver logs do banco
docker-compose logs db

# Reiniciar serviços
docker-compose restart
```

#### Limpar tudo e começar do zero
```bash
docker-compose down -v
docker-compose up -d --build
```

#### Erro "port already in use"
```bash
# Parar containers que estão usando a porta
docker-compose down

# Ou mudar a porta no docker-compose.yml
# ports:
#   - "8001:8000"  # Usar porta 8001 no host
```

### Produção

Para produção, ajuste:

1. **Gere uma SECRET_KEY segura**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Desabilite DEBUG**
```env
DEBUG=False
```

3. **Use senhas fortes**
```env
POSTGRES_PASSWORD=senha-muito-forte-aqui
```

4. **Configure CORS apropriadamente**
```env
CORS_ORIGINS=https://seu-dominio.com
```

5. **Use volumes externos ou serviços gerenciados**
```yaml
# docker-compose.prod.yml
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - /data/postgres:/var/lib/postgresql/data
```

### Estrutura dos Containers

```
┌─────────────────────┐
│   biocalc_api       │
│   (FastAPI)         │
│   Port: 8000        │
└──────────┬──────────┘
           │
           │ connects to
           │
┌──────────▼──────────┐
│   biocalc_db        │
│   (PostgreSQL 15)   │
│   Port: 5432        │
└─────────────────────┘
```

### Health Checks

O PostgreSQL tem health check configurado:
- Verifica a cada 10 segundos
- API só inicia após DB estar saudável

---

## 📦 Executando Localmente (sem Docker)

Se preferir rodar sem Docker, siga as instruções no [README.md](README.md) principal.
