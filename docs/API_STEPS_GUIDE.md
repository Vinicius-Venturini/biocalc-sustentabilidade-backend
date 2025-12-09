# API de Criação de Projetos por Steps - Guia de Uso

## 📋 Visão Geral

O sistema de criação de projetos foi dividido em **10 steps progressivos** que espelham a estrutura da planilha BioCalc. O usuário pode salvar o progresso a qualquer momento e retornar depois.

## 🎯 Fluxo Completo

```
Step 0: Identificação
    ↓
Steps 1-3: Fase Agrícola
    ↓
Steps 4-7: Fase Industrial
    ↓
Steps 8-9: Fase de Distribuição
    ↓
Step 10: Volume de Produção
    ↓
POST /calculate → Resultados
```

## 📝 Endpoints por Step

### Step 0: Criar Projeto Inicial

```http
POST /projects
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "Projeto Pinus 2024",
  "company_name": "BioEnergia S.A.",
  "cnpj": "12.345.678/0001-90",
  "state": "SP",
  "city": "São Carlos",
  "tech_responsible": "João Silva",
  "phone": "(16) 99999-9999",
  "email": "joao@bioenergia.com.br"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Projeto Pinus 2024",
  "status": "Em Rascunho",
  "current_step": 0,
  "message": "Projeto criado com sucesso! Prossiga para o Step 1."
}
```

---

### Steps 1-10: Rota Dinâmica Única

**Todos os steps (1-10) usam a mesma rota:**

```http
PUT /projects/{project_id}/step/{step}
Content-Type: application/json
Authorization: Bearer {token}
```

**Exemplos:**

#### Step 1: Produção de Biomassa

```http
PUT /projects/1/step/1
Content-Type: application/json
Authorization: Bearer {token}

{
  "biomass_type": "Resíduo de Pinus",
  "biomass_consumption_known": "Não",
  "biomass_consumption_value": null,
  "starch_input": 0.0
}
```

#### Step 2: Mudança de Uso da Terra (MUT)

```http
PUT /projects/1/step/2
Content-Type: application/json
Authorization: Bearer {token}

{
  "production_state": "SP",
  "wood_residue_stage": "Processamento"
}
```

#### Step 3: Transporte da Biomassa

```http
PUT /projects/1/step/3
Content-Type: application/json
Authorization: Bearer {token}

{
  "agr_transport_distance": 50,
  "agr_transport_vehicle": "Caminhão Toco/Semipesado (16-32t)"
}
```

#### Step 4: Dados do Sistema Industrial

```http
PUT /projects/1/step/4
Content-Type: application/json
Authorization: Bearer {token}

{
  "has_cogeneration": "Não",
  "biomass_processed": 12000000,
  "biomass_cogeneration": 0
}
```

#### Step 5: Consumo de Eletricidade

```http
PUT /projects/1/step/5
Content-Type: application/json
Authorization: Bearer {token}

{
  "elec_grid": 50000,
  "elec_solar": 10000,
  "elec_wind": 0,
  "elec_hydro": 0,
  "elec_biomass": 5000,
  "elec_other": 0
}
```

#### Step 6: Consumo de Combustíveis

```http
PUT /projects/1/step/6
Content-Type: application/json
Authorization: Bearer {token}

{
  "fuel_diesel": 5000,
  "fuel_gasoline": 0,
  "fuel_ethanol": 0,
  "fuel_biodiesel": 0,
  "fuel_gnv": 0,
  "fuel_lpg": 0,
  "fuel_biomass": 0,
  "fuel_other": 0
}
```

#### Step 7: Outros Insumos

```http
PUT /projects/1/step/7
Content-Type: application/json
Authorization: Bearer {token}

{
  "water_consumption": 1000,
  "input_lubricant": 100,
  "input_chemical": 200,
  "input_other": 50
}
```

#### Step 8: Transporte Doméstico

```http
PUT /projects/1/step/8
Content-Type: application/json
Authorization: Bearer {token}

{
  "dom_mass": 12000000,
  "dom_distance": 50,
  "dom_modal_road_pct": 100,
  "dom_modal_rail_pct": 0,
  "dom_vehicle_type": "Caminhão Toco/Semipesado (16-32t)"
}
```

#### Step 9: Transporte Exportação (Opcional)

```http
PUT /projects/1/step/9
Content-Type: application/json
Authorization: Bearer {token}

{
  "exp_mass": 0,
  "exp_factory_port_dist": 0,
  "exp_modal_road_pct": 100,
  "exp_modal_rail_pct": 0,
  "exp_modal_water_pct": 0,
  "exp_vehicle_port": null,
  "exp_port_consumer_dist": 0
}
```

#### Step 10: Volume de Produção

```http
PUT /projects/1/step/10
Content-Type: application/json
Authorization: Bearer {token}

{
  "production_volume": 12000
}
```

**Response (todos os steps):**
```json
{
  "id": 1,
  "name": "Projeto Pinus 2024",
  "status": "Em Rascunho",
  "current_step": 10,
  "message": "Step 10 salvo! Volume de produção definido. Pronto para calcular!"
}
```

---

## 🧮 Finalizar e Calcular

```http
POST /projects/1/calculate
Authorization: Bearer {token}
```

**Response:** ProjectResponse completo com todos os resultados calculados

```json
{
  "id": 1,
  "name": "Projeto Pinus 2024",
  "status": "Concluído",
  "current_step": 10,
  "biomass_type": "Resíduo de Pinus",
  "production_volume": 12000,
  "carbon_intensity": 0.0026,
  "agricultural_emissions": -0.0064,
  "industrial_emissions": 0.0009,
  "transport_emissions": 0.0077,
  "use_emissions": 0.0,
  "efficiency_note": 0.0841,
  "emission_reduction": 97.0,
  "cbios": 18982,
  "cbios_revenue": 1481547.74,
  ...
}
```

---

## 📊 Consultar Progresso

```http
GET /projects/1/progress
Authorization: Bearer {token}
```

**Response:**
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

---

## 🔄 Navegação Flexível

### Voltar e Editar Step Anterior

O usuário pode **voltar** e editar qualquer step anterior:

```http
PUT /projects/1/step3
Content-Type: application/json
Authorization: Bearer {token}

{
  "agr_transport_distance": 75,  // Alterado de 50 para 75
  "agr_transport_vehicle": "Carreta/Pesado (>32t)"  // Mudou veículo
}
```

O `current_step` **não regride**, apenas avança. Se o usuário está no step 7 e edita o step 3, o `current_step` permanece 7.

---

## 💾 Salvamento Automático

- Cada step é salvo **imediatamente** no banco de dados
- Projeto fica em modo **"Em Rascunho"** até calcular
- `current_step` rastreia até onde o usuário chegou
- Usuário pode **fechar** e **retornar depois** do step que parou

---

## ✅ Validações

### Por Step
Cada step valida apenas seus próprios campos:
- Step 1: `biomass_type` é obrigatório
- Step 10: `production_volume` é obrigatório (> 0)

### Para Calcular
Para chamar `/calculate`, é necessário:
- ✅ `current_step >= 10`
- ✅ `biomass_type` preenchido
- ✅ `production_volume` preenchido

---

## 🎨 Exemplo de Uso no Frontend

```typescript
// 1. Criar projeto (Step 0)
const createResponse = await fetch('/projects', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Projeto Pinus 2024',
    company_name: 'BioEnergia S.A.',
    state: 'SP',
    city: 'São Carlos'
  })
});

const project = await createResponse.json();
const projectId = project.id; // 1

// 2. Salvar qualquer step usando rota dinâmica
const saveStep = async (step: number, data: any) => {
  return await fetch(`/projects/${projectId}/step/${step}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
};

// Exemplo: Step 1
await saveStep(1, {
  biomass_type: 'Resíduo de Pinus',
  biomass_consumption_known: 'Não'
});

// Exemplo: Step 5
await saveStep(5, {
  elec_grid: 50000,
  elec_solar: 10000,
  elec_wind: 0,
  elec_hydro: 0,
  elec_biomass: 5000,
  elec_other: 0
});

// Exemplo: Step 10
await saveStep(10, {
  production_volume: 12000
});

// 3. Consultar progresso
const progressResponse = await fetch(`/projects/${projectId}/progress`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

const progress = await progressResponse.json();
console.log(`Progresso: ${progress.progress_percentage}%`);
console.log(`Step atual: ${progress.current_step}/10`);

// 4. Após completar todos steps...
if (progress.can_calculate) {
  const resultsResponse = await fetch(`/projects/${projectId}/calculate`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const results = await resultsResponse.json();
  console.log('CBIOs:', results.cbios);
  console.log('Intensidade:', results.carbon_intensity);
}
```

---

## 📋 Resumo dos Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/projects` | POST | Step 0: Criar projeto |
| `/projects/{id}/step/{step}` | PUT | Steps 1-10: Atualizar step dinâmico |
| `/projects/{id}/calculate` | POST | Finalizar e calcular |
| `/projects/{id}/progress` | GET | Consultar progresso |
| `/projects/{id}` | GET | Detalhes completos |
| `/projects` | GET | Listar projetos |
| `/projects/{id}` | DELETE | Deletar projeto |

**Total:** 7 endpoints (rota dinâmica unificou 10 endpoints em 1)
