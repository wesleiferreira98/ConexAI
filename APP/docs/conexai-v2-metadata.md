
# Documentação Técnica – ConexAI V2

## Versão

**ConexAI V2**

 **Modelo Base** : `mistralai/Mistral-7B-Instruct-v0.2`

 **Framework** : Hugging Face Transformers + PEFT (LoRA) + TRL (SFTTrainer)

 **Tipo de Modelo** : Language Model ajustado para domínio financeiro-empresarial

 **Tarefa** : Geração de linguagem natural (Causal Language Modeling)

---

## Objetivo do Modelo

Adaptar um modelo de linguagem open-source para atuar como um **assistente financeiro virtual** com foco em:

* KPIs financeiros e operacionais
* Contexto empresarial
* Recomendações de gestão
* Atendimento baseado em dados de extrato, pagamento e cobrança

---

## Pipeline de Treinamento

### 1. **Dados Utilizados**

* Arquivos reais da plataforma Conexa:
  * `Conexa - Admin Extrato.xls`
  * `Conexa - Admin Pagamento.xls`
  * `Conexa - Admin Cobranca.xls`

### 2. **Pré-processamento**

* Extração e normalização de colunas
* Conversão em prompts estruturados com marcações no estilo:

```text
<|im_start|>user
[PERGUNTA]
<|im_end|>
<|im_start|>assistant
[RESPOSTA]
<|im_end|>
```

### 3. **Modelagem com LoRA**

* Modelo base: `mistralai/Mistral-7B-Instruct-v0.1`
* Estratégia: LoRA (Low-Rank Adaptation) via PEFT
* Hiperparâmetros LoRA:
  * `r = 8`
  * `lora_alpha = 32`
  * `lora_dropout = 0.05`
  * `target_modules = ["q_proj", "v_proj"]`

### 4. **Configurações de Treinamento**

* Batch size efetivo: 4 (2 por device × 2 acumulações)
* `num_train_epochs = 3`
* `learning_rate = 2e-5`
* `optimizer = paged_adamw_8bit`
* `fp16 = True`
* Salvo em: `modelos_conexAI/ConexAI V2`

---

## Artefatos Gerados

```bash
modelos_conexAI/
└── ConexAI V2/
    ├── adapter_model.safetensors
    ├── adapter_config.json
    ├── tokenizer_config.json
    ├── tokenizer.json
```

---

## Carregamento do Modelo

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.1",
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)

model = PeftModel.from_pretrained(base_model, "modelos_conexAI/ConexAI V2")
model = model.merge_and_unload()

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
```

---

## Teste de Inferência

```python
prompt = "<|im_start|>user\nO que são KPIs?<|im_end|>\n<|im_start|>assistant\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    pad_token_id=tokenizer.eos_token_id
)

resposta = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

---

## Prompt de Identidade Incorporado

* Instrução no pipeline/chat:

  `"Você é o ConexAI V2, um assistente financeiro virtual treinado para fornecer respostas com precisão e foco em KPIs empresariais."`

---

## Resultados Observados

* Tempo médio de resposta: ~45s a 1min com T4 15GB RAM
* Coerência temática: Alta
* Fluência: Alta
* Tempo de resposta: *ainda em processo de otimização*

---

## Próximos Passos

* Integração total com pipeline do `chat.py` e `validador.py`
* Benchmarking com ConexAI V1 (DeepSeek-7B)
* Lançamento da versão `ConexAI V3` com LLaMA 3 8B ou Mistral Mix
