# Guia de Instalação com Docker

Este guia descreve como executar o BioCalc Backend usando Docker e Docker Compose.

## Por que usar Docker?

- Não precisa instalar Python, PostgreSQL ou dependências manualmente
- Ambiente padronizado e isolado
- Configuração automática do banco de dados
- População automática de dados auxiliares
- Pronto para produção

## Início Rápido

## Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/Vinicius-Venturini/biocalc-sustentabilidade-backend.git
cd biocalc-sustentabilidade-backend

# 2. Inicie os containers
docker-compose up -d

# 3. Acesse a API
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

**Pronto!** A API está rodando com banco de dados PostgreSQL e dados auxiliares populados.

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 1.29+

---

## Estrutura Docker

### Serviços

O `docker-compose.yml` define 2 serviços:

#### 1. Database (PostgreSQL)
- **Image**: `postgres:15-alpine`
- **Container**: `biocalc_db`
- **Porta**: `5432:5432`
- **Volume**: `postgres_data` (persistência dos dados)
- **Healthcheck**: Verifica se o banco está pronto

#### 2. API (FastAPI)
- **Build**: Dockerfile local
- **Container**: `biocalc_api`
- **Porta**: `8000:8000`
- **Depende de**: Database (aguarda healthcheck)
- **Auto-reload**: Código sincronizado com volume

### Variáveis de Ambiente

O docker-compose usa as seguintes variáveis:

```yaml
DATABASE_URL: postgresql://biocalc_user:biocalc_password@db:5432/biocalc_db
SECRET_KEY: ${SECRET_KEY:-change-this-secret-key-in-production}
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30
CORS_ORIGINS: '["http://localhost:5173","http://localhost:3000"]'
DEBUG: ${DEBUG:-True}
```

---

## Comandos Úteis

### Iniciar containers

```bash
docker-compose up -d
```

### Ver logs

```bash
# Todos os serviços
docker-compose logs -f

# Apenas API
docker-compose logs -f api

# Apenas Database
docker-compose logs -f db
```

### Parar containers

```bash
docker-compose stop
```

### Parar e remover containers

```bash
docker-compose down
```

### Parar e remover containers + volumes (apaga banco de dados)

```bash
docker-compose down -v
```

### Reconstruir imagens

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Acessar shell do container da API

```bash
docker exec -it biocalc_api sh
```

### Acessar PostgreSQL

```bash
docker exec -it biocalc_db psql -U biocalc_user -d biocalc_db
```

---

## Desenvolvimento com Docker

### Hot Reload

O código fonte está montado como volume, então mudanças no código local são refletidas automaticamente no container (uvicorn com `--reload`).

```yaml
volumes:
  - ./app:/app/app
  - ./scripts:/app/scripts
```

### Popular banco de dados novamente

```bash
docker exec -it biocalc_api python scripts/seed_database.py
```

### Executar testes dentro do container

```bash
docker exec -it biocalc_api pytest
```

---

## Variáveis de Ambiente Customizadas

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=False
```

O docker-compose usará automaticamente essas variáveis.

---

## Troubleshooting

### Porta 5432 já está em uso

Se você tem PostgreSQL rodando localmente:

```bash
# Opção 1: Parar PostgreSQL local
sudo systemctl stop postgresql

# Opção 2: Mudar a porta no docker-compose.yml
ports:
  - "5433:5432"  # Usar 5433 no host
```

### Porta 8000 já está em uso

```bash
# Mudar a porta no docker-compose.yml
ports:
  - "8001:8000"  # Usar 8001 no host
```

### Container da API não inicia

```bash
# Ver logs detalhados
docker-compose logs api

# Reconstruir imagem
docker-compose build --no-cache api
docker-compose up -d
```

### Banco de dados não popula

```bash
# Popular manualmente
docker exec -it biocalc_api python scripts/seed_database.py

# Verificar dados
docker exec -it biocalc_api python scripts/verify_seed.py
```

### Limpar tudo e recomeçar

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## Produção

### Usar SECRET_KEY segura

```bash
# Gerar chave
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Adicionar ao .env
echo "SECRET_KEY=sua_chave_gerada" > .env
```

### Desabilitar DEBUG

```env
DEBUG=False
```

### Remover volume de código fonte

Edite `docker-compose.yml` e remova:

```yaml
volumes:
  - ./app:/app/app  # Remover esta linha
  - ./scripts:/app/scripts  # Remover esta linha
```

### Usar proxy reverso (Nginx)

```nginx
server {
    listen 80;
    server_name api.exemplo.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Mais Informações

- **API Documentation**: Consulte o [README.md](README.md) principal
- **Endpoints e Uso**: Veja [docs/API_STEPS_GUIDE.md](docs/API_STEPS_GUIDE.md)
- **Estrutura da Planilha**: Confira [docs/ESTRUTURA_PLANILHA.md](docs/ESTRUTURA_PLANILHA.md)
