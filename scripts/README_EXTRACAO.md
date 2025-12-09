# Script de Extração de Dados da Planilha BioCalc

Este script extrai todas as informações da planilha `BioCalc_EngS.xlsx` para análise.

## Como usar

1. Instale a dependência necessária:
```bash
pip install openpyxl
```

2. Execute o script:
```bash
python scripts/extract_excel_info.py
```

3. O script criará uma pasta `extracted_data/` com todos os dados extraídos

## O que será extraído

- ✅ **Todas as abas** da planilha
- ✅ **Valores** de todas as células
- ✅ **Fórmulas** completas (preservando a sintaxe original)
- ✅ **Cores das células** (verde = input, azul = calculado)
- ✅ **Tabelas auxiliares** identificadas automaticamente
- ✅ **Estrutura** e dimensões de cada aba

## Arquivos gerados

Após a execução, você terá:

- `LEIA_ME.txt` - Relatório resumido
- `sheets_info.json` - Informações gerais
- `sheet_*_data.json` - Dados completos de cada aba
- `sheet_*_formulas.json` - Fórmulas em JSON
- `sheet_*_formulas.csv` - Fórmulas em CSV (fácil de abrir no Excel)
- `sheet_*_tables.json` - Tabelas identificadas
- `sheet_*_colored_cells.json` - Células coloridas

## Próximos passos

Depois de rodar o script, compartilhe a pasta `extracted_data/` comigo para que eu possa:

1. Entender todas as fórmulas de cálculo
2. Identificar as tabelas auxiliares
3. Mapear os inputs e outputs
4. Implementar o backend com precisão
