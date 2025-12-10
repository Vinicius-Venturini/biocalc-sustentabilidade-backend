# BioCalc Backend - FastAPI + PostgreSQL

Backend modular em FastAPI para replicar as fórmulas da planilha BioCalc (cálculo de emissões por ACV em biocombustíveis sólidos).

## Funcionalidades

- ✅ **Autenticação JWT** - Registro e login de usuários
- ✅ **Cálculo de Emissões** - Implementação completa das fórmulas BioCalc
- ✅ **Fases de Cálculo**:
  - Agrícola (produção de biomassa + MUT + transporte)
  - Industrial (eletricidade + combustíveis + água + insumos)
  - Transporte (doméstico + exportação)
  - Uso (combustão)
- ✅ **Resultados**:
  - Intensidade de Carbono (kg CO₂eq/MJ)
  - Nota de Eficiência vs Fóssil
  - Redução de Emissões (%)
  - CBIOs Gerados
  - Remuneração Estimada
- ✅ **Dados Auxiliares** - Tabelas de referência (biomassas, veículos, GWP, etc.)
- ✅ **API RESTful** - Documentação automática com Swagger/OpenAPI
- ✅ **Persistência** - PostgreSQL com SQLAlchemy

## Início Rápido com Docker (Recomendado)

A maneira mais rápida e fácil de executar o BioCalc Backend:

```bash
# 1. Clone o repositório
cd biocalc-sustentabilidade-backend

# 2. Inicie com Docker Compose
docker-compose up -d

# 3. Acesse a API
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

 **Pronto!** O banco de dados PostgreSQL e a API FastAPI estão rodando com dados auxiliares já populados automaticamente.

> **Documentação completa do Docker**: [DOCKER.md](DOCKER.md)

---

## 📋 Pré-requisitos

- Docker
- Docker Compose

> **Nota:** Não é necessário instalar Python, PostgreSQL ou configurar ambiente virtual. O Docker gerencia tudo automaticamente!

## Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI (interativa)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Principais

### Autenticação

- `POST /auth/register` - Registrar novo usuário
- `POST /auth/login` - Login (retorna JWT token)
- `GET /auth/me` - Obter usuário atual

### Projetos - Sistema de Steps Progressivos

O sistema de criação de projetos foi dividido em **10 steps** que espelham a estrutura da planilha BioCalc:

**Step 0: Identificação**
- `POST /projects` - Criar projeto inicial

**Steps 1-10: Rota Dinâmica Unificada**
- `PUT /projects/{id}/step/{step}` - Atualizar qualquer step (1-10)
  - Step 1: Produção de Biomassa
  - Step 2: Mudança de Uso da Terra (MUT)
  - Step 3: Transporte da Biomassa
  - Step 4: Dados do Sistema Industrial
  - Step 5: Consumo de Eletricidade
  - Step 6: Consumo de Combustíveis
  - Step 7: Outros Insumos
  - Step 8: Transporte Doméstico
  - Step 9: Transporte Exportação (Opcional)
  - Step 10: Volume de Produção

**Finalização**
- `POST /projects/{id}/calculate` - Calcular emissões e CBIOs

**Consultas**
- `GET /projects/{id}/progress` - Progresso do projeto (0-10)
- `GET /projects` - Listar todos os projetos
- `GET /projects/{id}` - Detalhes de um projeto
- `DELETE /projects/{id}` - Deletar projeto

> **Guia Completo:** Veja [docs/API_STEPS_GUIDE.md](docs/API_STEPS_GUIDE.md) para exemplos detalhados de cada step

### Dados Auxiliares

- `GET /auxiliary/biomass-properties` - Listar propriedades de biomassas
- `GET /auxiliary/vehicle-emission-factors` - Listar fatores de emissão de veículos
- `GET /auxiliary/gwp-factors` - Listar fatores GWP

## Estrutura do Projeto

```
biocalc-sustentabilidade-backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configurações centralizadas
│   │   └── database.py        # Configuração do banco de dados
│   ├── models/                # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── biomass_property.py
│   │   ├── vehicle_emission_factor.py
│   │   └── auxiliary.py
│   ├── schemas/               # Schemas Pydantic
│   │   ├── user.py
│   │   ├── project.py
│   │   └── auxiliary.py
│   ├── services/              # Lógica de negócio
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   └── calculation_service.py  # ⭐ Fórmulas BioCalc
│   ├── routers/               # Endpoints da API
│   │   ├── auth.py
│   │   ├── projects.py
│   │   └── auxiliary.py
│   └── main.py                # Aplicação FastAPI principal
├── scripts/
│   ├── extract_excel_info.py  # Extração de dados da planilha
│   └── seed_database.py       # Popular banco de dados
├── docs/
│   └── ESTRUTURA_PLANILHA.md  # Documentação da planilha
├── requirements.txt
├── .env.example
└── README.md
```

## Fórmulas Implementadas

O serviço de cálculo (`app/services/calculation_service.py`) implementa todas as fórmulas da planilha BioCalc:

### Intensidade de Carbono
```
C21 = SUM(C23:C26)
= Emissões Agrícolas + Industriais + Transporte + Uso
```

### Emissões Agrícolas
```
C23 = Produção de Biomassa + MUT + Transporte até Fábrica
```

### Emissões Industriais
```
C24 = Eletricidade + Combustíveis + Água + Outros Insumos
```

### Emissões de Transporte
```
C25 = Transporte Doméstico + Transporte Exportação
```

### Nota de Eficiência
```
C27 = Fóssil Substituto - Intensidade de Carbono
= 0.0867 - C21
```

### Redução de Emissões
```
C29 = (Fóssil Substituto - Intensidade de Carbono) / Fóssil Substituto
= (0.0867 - C21) / 0.0867
```

### CBIOs
```
H24 = PCI * Volume de Produção * Nota de Eficiência (se > 0)
```

## Testando a API

### 1. Registrar um usuário

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "password": "senha123",
    "company_name": "BioEnergia S.A.",
    "cnpj": "12.345.678/0001-90"
  }'
```

### 2. Fazer login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@example.com&password=senha123"
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Criar projeto (Step 0)

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Projeto Pinus 2024",
    "state": "SP",
    "city": "São Carlos"
  }'
```

Resposta:
```json
{
  "id": 1,
  "name": "Projeto Pinus 2024",
  "status": "Em Rascunho",
  "current_step": 0,
  "message": "Projeto criado com sucesso! Prossiga para o Step 1."
}
```

### 4. Preencher Step 1 (Produção de Biomassa)

```bash
curl -X PUT "http://localhost:8000/projects/1/step/1" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "biomass_type": "Resíduo de Pinus",
    "biomass_consumption_known": "Não"
  }'
```

### 5. Preencher Step 5 (Eletricidade) - exemplo de navegação

```bash
curl -X PUT "http://localhost:8000/projects/1/step/5" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "elec_grid": 50000,
    "elec_solar": 10000,
    "elec_wind": 0,
    "elec_hydro": 0,
    "elec_biomass": 5000,
    "elec_other": 0
  }'
```

### 6. Consultar progresso

```bash
curl -X GET "http://localhost:8000/projects/1/progress" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

Resposta:
```json
{
  "id": 1,
  "name": "Projeto Pinus 2024",
  "status": "Em Rascunho",
  "current_step": 5,
  "total_steps": 10,
  "progress_percentage": 50.0,
  "can_calculate": false
}
```

### 7. Após completar todos os steps (1-10), calcular resultados

```bash
curl -X POST "http://localhost:8000/projects/1/calculate" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

A resposta incluirá todos os resultados calculados automaticamente!

## Integração com Frontend

O backend está configurado para aceitar requisições do frontend React (CORS habilitado).

Endpoints para o frontend:
- Base URL: `http://localhost:8000`
- Autenticação: JWT Bearer Token no header `Authorization`

Exemplo de chamada do frontend:

```typescript
const response = await fetch('http://localhost:8000/projects', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(projectData)
});

const result = await response.json();
console.log('Intensidade de Carbono:', result.carbon_intensity);
console.log('CBIOs:', result.cbios);
```

## Dados Auxiliares Disponíveis

### Biomassas
1. Resíduo de Pinus (18.8 MJ/kg)
2. Resíduo de Eucaliptus (15.8 MJ/kg)
3. Carvão vegetal de eucalipto (15.8 MJ/kg)
4. Casca de Amendoin (17.1 MJ/kg)
5. Eucaliptus Virgem (15.8 MJ/kg)
6. Pinus Virgem (18.8 MJ/kg)

### Fatores GWP (AR6 IPCC 2021)
- CO₂ Fóssil: 1.0
- CH₄ Fóssil: 29.8
- CH₄ Biogênico: 27.2
- N₂O: 273.0

### Veículos
- Caminhão Toco/Semipesado: 0.062 kg CO₂eq/t.km
- Carreta/Pesado: 0.062 kg CO₂eq/t.km
- VUC: 0.089 kg CO₂eq/t.km
- Trem: 0.022 kg CO₂eq/t.km

## 🛠️ Desenvolvimento

### Adicionar novas biomassas

Edite `scripts/seed_database.py` e adicione na lista `biomasses`:

```python
{
    "biomass_name": "Nova Biomassa",
    "pci_mj_kg": 16.5,
    "combustion_emission": 0.0,
    "source": "Sua Referência",
    "biofuel_pci": 16.5
}
```

Execute novamente: `python scripts/seed_database.py`

### Ajustar fórmulas de cálculo

Edite `app/services/calculation_service.py` e modifique os métodos de cálculo.

##  Licença

Este projeto foi desenvolvido para a Chamada CNPq nº 26/2021 - 401237/2022-2.

## Autores

Desenvolvido para o projeto BioCalc - UFSCar

##  Suporte

Para dúvidas ou problemas:
1. Verifique a documentação da API em `/docs`
2. Consulte os logs do servidor
3. Revise as configurações do `.env`
4. Verifique a conexão com o PostgreSQL

---

**Status**:  Backend funcional e pronto para integração com o frontend!
