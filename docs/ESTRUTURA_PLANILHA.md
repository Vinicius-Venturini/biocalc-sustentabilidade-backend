# Estrutura de Dados Extraída da Planilha BioCalc

## Resumo das Abas

1. **Instruções** - Instruções gerais
2. **EngS_BioCalc** - Aba principal de cálculo (39 fórmulas)
3. **Dados auxiliares** - Tabelas de referência (342 fórmulas)
4. **CFF** - Fatores de conversão
5. **Resultados** - Consolidação de resultados (54 fórmulas)
6. **Referências** - Referências bibliográficas
7. **_E2G** - Cálculos auxiliares (243 fórmulas)
8. **_EMISSOES_AGRICOLAS_RENOVACALC** - Emissões agrícolas (12 fórmulas)

## Fórmulas Principais Identificadas

### Intensidade de Carbono (C21)
```
=SUM(C23:C26)
```
Soma das emissões de todas as fases:
- C23: Agrícola
- C24: Industrial
- C25: Transporte
- C26: Uso

### Emissões por Fase

#### Agrícola (C23)
```
=IFERROR(SUM(E40,E47,E53),0)
```
- E40: Impacto da produção de biomassa
- E47: Impacto MUT (Mudança de Uso da Terra)
- E53: Transporte da biomassa até fábrica

#### Industrial (C24)
```
=IFERROR((SUM(E69,E81,E85,E91)),0)
```
- E69: Eletricidade
- E81: Combustíveis
- E85: Água
- E91: Outros insumos

#### Transporte (C25)
```
=IFERROR(SUM(E104,E117)," ")
```
- E104: Transporte doméstico
- E117: Transporte exportação

### Nota de Eficiência (C27)
```
=J20-C21
```
Onde J20 = 0.0867 (fóssil substituto: média ponderada Diesel A, Gasolina A, GNV)

### Redução de Emissões (C29)
```
=(J20-C21)/J20
```
Percentual de redução vs fóssil

### CBIOs (H24)
```
=IFERROR(ROUNDDOWN(VLOOKUP(E33,'Dados auxiliares'!B7:D12,3,0)*(H21*(SUMIF(C27,">0",C27))),0),"")
```
- E33: Tipo de biomassa
- H21: Volume de produção (toneladas)
- Lookup na tabela de PCI

## Tabelas Auxiliares Identificadas

### 1. Propriedades de Biomassa (Dados auxiliares B7:H12)
Colunas:
- B: Fonte de Biomassa
- C: PCI (g/MJ) - calculado
- D: PCI (MJ/kg)
- E: Combustão estacionária (kg CO2 eq/MJ)
- F: Referência
- G: Biocombustível sólido
- H: PCI Biocombustível (MJ/kg)

Biomassas:
1. Resíduo de Pinus (18.8 MJ/kg)
2. Resíduo de Eucaliptus (15.8 MJ/kg)
3. Carvão vegetal de eucalipto (15.8 MJ/kg)
4. Casca de Amendoin (17.1 MJ/kg)
5. Eucaliptus Virgem (15.8 MJ/kg)
6. Pinus Virgem (18.8 MJ/kg)

### 2. Fatores GWP (Dados auxiliares B17:D20)
- CO2 Fóssil: 1.0
- CH4 Fóssil: 29.8
- CH4 Biogênico: 27.2
- N2O: 273.0

### 3. Emissões de Insumos (Dados auxiliares B26:K39)
Biomassas com fatores de emissão, alocação e referências ecoinvent

### 4. Fatores de Transporte (Dados auxiliares B70:G76)
Tipos de veículos e fatores de emissão por modal

### 5. Mudança de Uso da Terra - MUT (Dados auxiliares B95:N124)
Fatores por estado e tipo de cultivo

## Inputs do Usuário (Células Verdes)

### Dados da Empresa
- Nome da Empresa (C4)
- CNPJ (C6)
- Estado (C8)
- Cidade (C10)
- Responsável (C12)
- Telefone (C14)
- E-mail (C16)

### Biomassa e Produção
- Tipo de Biomassa (E33) - dropdown
- Volume de Produção (H21) - toneladas/ano
- Consumo de Biomassa (E35) - opcional
- Estado da produção (E42) - dropdown
- Etapa do ciclo (E44) - dropdown para resíduos

### Fase Agrícola
- Distância transporte biomassa (E49) - km
- Tipo de veículo (E50) - dropdown
- Entrada de amido de milho (E38) - kg/MJ

### Fase Industrial
- Quantidade biomassa processada (E59) - kg/ano
- Consumo de eletricidade (E62:E67) - kWh/ano por fonte
- Consumo de combustíveis (E71:E78) - litros/kg por tipo
- Consumo de água (E60) - m³/ano
- Outros insumos (E87:E89)

### Transporte Doméstico
- Massa transportada (E96) - kg/ano
- Distância média (E97) - km
- % Modal rodoviário (E98)
- % Modal ferroviário (E99)
- Tipo de veículo (E101) - dropdown

### Transporte Exportação
- Massa exportada (E107) - t/ano
- Distância fábrica-porto (E108) - km
- % Modal rodoviário (E109)
- % Modal ferroviário (E110)
- Tipo de veículo (E112) - dropdown
- Distância marítima (E113) - km

## Outputs Calculados (Células Azuis)

### Resultados Principais
- Intensidade de Carbono (C21) - kg CO₂eq/MJ
- Nota de Eficiência (C27) - kg CO₂eq/MJ
- Redução de Emissões (C29) - %
- CBIOs (H24) - créditos
- Remuneração (H29) - R$

### Detalhamento por Fase
- Emissão Agrícola (C23)
- Emissão Industrial (C24)
- Emissão Transporte (C25)
- Emissão Uso (C26)

### Aba Resultados
Comparação com diferentes fósseis substitutos:
- Diesel A
- Gasolina A
- GNV
