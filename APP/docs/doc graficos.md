# Documentação Técnica - Módulo de Exportação de Dados Visuais

## Objetivo

Este módulo é responsável por analisar a resposta textual da IA (ConexAI) e, quando possível, extrair dados estruturados adequados para visualizações gráficas (linha, barra ou pizza). Os dados são exportados no formato JSON para que o front-end possa renderizar os gráficos dinamicamente.Funcionamento Interno

- A resposta da IA é processada por expressões regulares.
- O sistema tenta identificar padrões de:
  - Categoria + Valor → ex.: 'Marketing: R$ 5000'
  - Data + Valor → ex.: 'Jan/2024 - R$ 12.000'
- Se os dados forem reconhecidos, são convertidos em uma estrutura JSON e salvos localmente.

## Formato do Arquivo Exportado

O JSON gerado segue um dos formatos abaixo:

### Exemplo 1: Gráfico de Linha (dados temporais)

{
  "grafico": "linha",
  "titulo": "Evolução temporal extraída",
  "dados": [
    { "data": "2024-01", "valor": 10000.0 },
    { "data": "2024-02", "valor": 15000.0 },
    { "data": "2024-03", "valor": 12500.0 }
  ],
  "moeda": "BRL"
}

### Exemplo 2: Gráfico de Pizza ou Barra (categorias)

{
  "grafico": "pizza",
  "titulo": "Distribuição extraída",
  "dados": [
    { "categoria": "Marketing", "valor": 5000.0 },
    { "categoria": "Operações", "valor": 7000.0 },
    { "categoria": "TI", "valor": 3000.0 }
  ],
  "moeda": "BRL"
}

## Localização do Arquivo

O JSON gerado é salvo localmente no projeto backend com o nome:

resposta_estruturada.json

Este arquivo pode ser:

- Lido diretamente pelo front-end (se compartilhado via rota/endpoint).
- Encaminhado para visualização em tempo real (via WebSocket/API REST futura).

## Observações Importantes

- A IA não gera os gráficos — ela responde normalmente e o módulo tenta extrair dados dela.
- Se nenhum dado estruturado for detectado, nenhum JSON é gerado.
- A moeda padrão é "BRL".
- Ideal para visualizações com dados financeiros, KPIs por mês, departamento ou categoria.
