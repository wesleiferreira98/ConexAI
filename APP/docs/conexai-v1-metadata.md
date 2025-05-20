# ConexAI V1 - Metadata Técnica e Funcional

## Identidade do Modelo

**Nome público:** ConexAI V1
**Descrição:** Assistente treinado para compreender métricas empresariais, extratos, cobranças e pagamentos com linguagem natural.
**Base técnica:** `deepseek-ai/deepseek-llm-7b-chat`
**Frameworks:** Transformers, PEFT (LoRA), Datasets, TRL
**Quantização:** 4-bit (BitsAndBytes - NF4)

---

## Treinamento

**Tipo:** Ajuste fino com LoRA (Low-Rank Adaptation)
**Técnica usada:** SFT (`Supervised Fine-Tuning`)
**Tokens de entrada:** `<|im_start|>` e `<|im_end|>` (formato tipo ChatML)
**Épocas:** 3
**Batch Size:** 2
**Gradient Accumulation Steps:** 2
**Dataset:** Dados empresariais reais (anonimizados), extraídos dos sistemas internos da Conexa (extrato, pagamento e cobrança).
**Total de exemplos:** *X* exemplos (*editar com o número real*)
**Tempo de treino estimado:** Aproximadamente *Y* horas (*editar se possível*)

---

## Exemplos de Uso

### Entrada:

```
<|im_start|>user
Qual o valor do extrato da conta Banco do Brasil?<|im_end|>
<|im_start|>assistant
O saldo atual da conta Banco do Brasil é R$4.959,27<|im_end|>
```

---

## Comportamento Esperado

- **Identidade:** Quando questionado, o modelo se apresenta como "ConexAI V1"
- **Respostas curtas e diretas**, com linguagem acessível e contextualizada
- Capacidade de **responder perguntas financeiras simples** sobre contas, extratos e cobranças
- Formato de resposta estruturado para facilitar compreensão humana e automação

---

## Armazenamento

```
/modelos_conexai/conexai-v1/
│
├── adapter_model.bin              # Pesos do LoRA ajustado
├── config.json                    # Metadados do modelo
├── special_tokens_map.json
├── tokenizer_config.json
└── tokenizer/                     # Arquivos de tokenização
```

---

## Benchmark Interno

| Métrica               | Valor Aproximado                                     |
| ---------------------- | ---------------------------------------------------- |
| Tempo de Resposta (T4) | ~45-60s/token completion                             |
| Tokens usados          | 4-bit quantized (NF4)                                |
| Tempo de ajuste        | ~X horas (*editar*)                                |
| Performance subjetiva  | Boa precisão nas queries sobre pagamentos e extrato |

---

## Observações

- O modelo ainda depende de otimizações no tempo de resposta.
- Planeja-se uma futura migração para `Mistral 7B` ou `LLaMA 3` com refinamentos maiores e mais responsivos.
- Versão gerenciada via `ConexAI Version Control`.

---

## Responsável Técnico

**Nome:** Weslei Ferreira
**Email:** *(inserir)*
**GitHub:** *(opcional)*
