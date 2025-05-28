

# ConexAI API – Documentação Técnica

> API em FastAPI que expõe os recursos do modelo  **ConexAI VX** , permitindo integração com aplicações externas (como backend em Node.js), gerenciamento de contexto e acesso ao histórico de conversas.

---

## Execução com Docker

### 1. **Build e execução simples**

```bash
docker build -t conexai .
docker run -p 8000:8000 conexai
```

### 2. **Execução via Docker Compose (recomendado)**

```bash
docker-compose up --build
```

> A API estará acessível em: `http://localhost:8000`

### Configurações via `.env`

* `VERSAO_MODELO` → Define a versão do modelo (ex: `V1`, `V2`)
* `DB_PATH` → Caminho do banco de dados (SQLite ou outro)
* `API_PORT` → Porta da aplicação (default: 8000)

---

## Endpoints Disponíveis

| Método | Rota                          | Descrição                               |
| ------- | ----------------------------- | ----------------------------------------- |
| GET     | `/status`                   | Retorna status da API e versão do modelo |
| POST    | `/chat/pergunta`            | Envia pergunta ao ConexAI e registra      |
| GET     | `/chat/historico?usuario=x` | Lista o histórico de chats do usuário   |

---

## Arquitetura da API

### `ChatGestao`

Gerencia o fluxo completo de uma interação:

* Valida com `ValidadorPergunta`
* Gera resposta via `GeradorRespostaLLM`
* Registra com `HistoricoInteracao`

### `ValidadorPergunta`

Valida perguntas com filtros lexicais e semânticos. Bloqueia termos técnicos não suportados.

### `GeradorRespostaLLM`

Gera respostas com `transformers.pipeline`, de acordo com a versão do modelo selecionada.

### `HistoricoInteracao`

Registra e consulta interações, armazenando em memória e SQLite. Suporte a múltiplos `chat_id`.

### `InterfaceTerminal`

Camada local de testes. Pode ser substituída por interface web/CLI.

### `carregador_modelo.py`

Carrega modelo, tokenizer e config conforme versão (`V1`, `V2`, etc).

### `formatador_prompt.py`

Funções utilitárias para montagem padronizada dos prompts.

---

## Suporte a Múltiplas Versões

A seleção do modelo ocorre dinamicamente em `criar_chat(versao: str)`.

| Versão    | Modelo Base                            |
| ---------- | -------------------------------------- |
| ConexAI V1 | `deepseek-ai/deepseek-llm-7b-chat`   |
| ConexAI V2 | `mistralai/Mistral-7B-Instruct-v0.2` |

---

## Execução Local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Detalhes dos Endpoints

### `GET /status`

Retorna o status da API.

**Exemplo:**

```bash
curl http://localhost:8000/status
```

**Resposta:**

```json
{
  "status": "API online",
  "modelo": "ConexAI V1"
}
```

---

### `POST /chat/pergunta`

Envia pergunta e registra no histórico.

**Requisição:**

```http
POST /chat/pergunta
Content-Type: application/json
```

**Corpo:**

```json
{
  "usuario": "weslei",
  "pergunta": "Qual é o faturamento da empresa?"
}
```

**Resposta:**

```json
{
  "mensagem": "Pergunta processada."
}
```

> Um novo chat é criado automaticamente caso não exista um `chat_id` ativo.

---

### `GET /chat/historico`

Consulta histórico por usuário.

**Exemplo:**

```bash
curl http://localhost:8000/chat/historico?usuario=weslei
```

**Resposta:**

```json
[
  {
    "id": 1,
    "nome": "Qual é o faturamento da empresa?",
    "data_criacao": "2024-04-16 13:05:02"
  },
  {
    "id": 2,
    "nome": "Como reduzir inadimplência?",
    "data_criacao": "2024-04-16 13:15:40"
  }
]
```

---

## Informações Técnicas

* **Frameworks:** FastAPI, Transformers, PEFT (LoRA), SQLite
* **Quantização:** 4-bit (NF4 via BitsAndBytes)
* **Tokenização:** `AutoTokenizer` (`pad_token = eos_token`)
* **Banco de dados:** SQLite (`contexto_chat.db`, com possibilidade de upgrade)

---

## Fluxo Interno

1. Validação semântica via `ValidadorPergunta`
2. Geração de resposta com o modelo configurado
3. Registro automático no SQLite
4. Histórico organizado por `usuario` e título da pergunta
5. Uso de LoRA em modelo quantizado

---

## Requisitos

* **Python 3.10+**
* Instalar dependências:
  ```bash
  pip install -r requirements.txt
  ```
* Executar API localmente:
  ```bash
  uvicorn main:app --reload
  ```

---

# ConexAI V1 – Especificações

**Nome Público:** ConexAI V1

**Descrição:** Assistente treinado com foco em métricas, extratos, cobranças e pagamentos empresariais.

**Base:** `deepseek-ai/deepseek-llm-7b-chat`

**Quantização:** NF4 (4-bit via BitsAndBytes)

**Frameworks:** Transformers, PEFT, Datasets, TRL

### Treinamento

* **Técnica:** SFT com LoRA
* **Prompt format:** estilo ChatML (`<|im_start|>` e `<|im_end|>`)
* **Épocas:** 3
* **Batch size:** 2
* **Dataset:** Anonimizado, baseado em dados reais da Conexa
* **Total de exemplos:** *Preencher com valor real*
* **Tempo estimado:** *Preencher*

### Armazenamento

```
/modelos_conexai/conexai-v1/
├── adapter_model.bin
├── config.json
├── tokenizer/
└── tokenizer_config.json
```

---

## Exemplos

**Entrada:**

```
<|im_start|>user
Qual o valor do extrato da conta Banco do Brasil?<|im_end|>
```

**Saída:**

```
<|im_start|>assistant
O saldo atual da conta Banco do Brasil é R$4.959,27<|im_end|>
```

---

## Comportamento Esperado

* Se identifica como “ConexAI V1”
* Respostas curtas, precisas e acessíveis
* Foco em perguntas empresariais e financeiras
* Saída estruturada, com foco em clareza e automação

---

## Benchmark Interno (estimado)

| Métrica               | Valor Aproximado              |
| ---------------------- | ----------------------------- |
| Tempo de resposta (T4) | ~45–60s por token completion |
| Tokens usados          | Quantizados (4-bit NF4)       |
| Precisão subjetiva    | Boa em queries financeiras    |

---

# ConexAI V2 – Especificações

* **Modelo base:** `mistralai/Mistral-7B-Instruct-v0.2`
* **Frameworks:** Transformers + PEFT (LoRA) + TRL
* **Tarefa:** Ajustado para linguagem natural em contexto financeiro

### Objetivo

Atuar como assistente inteligente para:

* KPIs financeiros
* Requisições baseadas em extrato, pagamento e cobrança
* Recomendação operacional e análise gerencial

### Dados

* Utiliza dados reais extraídos da plataforma Conexa:
  * `Admin Extrato.xls`
  * `Admin Pagamento.xls`
  * `Admin Cobranca.xls`

### Prompt

```text
<|im_start|>user
[PERGUNTA]
<|im_end|>
<|im_start|>assistant
[RESPOSTA]
<|im_end|>
```

### Treinamento com LoRA

* **Modelo base:** Mistral 7B
* **Parâmetros LoRA:**
  * `r = 8`
  * `alpha = 32`
  * `dropout = 0.05`
  * `target_modules = ["q_proj", "v_proj"]`
* **Épocas:** 3
* **Batch efetivo:** 4 (2 x 2)
