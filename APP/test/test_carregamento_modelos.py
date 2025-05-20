
from APP.core.carregador_modelo import (
    carregar_modelo,
    carregar_tokenizer,
    gerar_configuracao_geracao
)
import pytest # type: ignore
@pytest.mark.parametrize("versao", ["ConexAI V1", "ConexAI V2"])
def test_carregamento_modelo_transformers(versao):
    try:
        model = carregar_modelo(versao)
        assert model is not None
        assert hasattr(model, "generate")
        print(f"✅ Modelo {versao} carregado com sucesso.")
    except Exception as e:
        pytest.fail(f"❌ Falha ao carregar {versao}: {e}")


@pytest.mark.parametrize("versao", ["ConexAI V1", "ConexAI V2"])
def test_carregamento_tokenizer(versao):
    try:
        tokenizer = carregar_tokenizer(versao)
        assert tokenizer is not None
        encoded = tokenizer("Teste", return_tensors="pt")
        assert "input_ids" in encoded
        print(f"✅ Tokenizer de {versao} carregado e funcional.")
    except Exception as e:
        pytest.fail(f"❌ Falha ao carregar tokenizer de {versao}: {e}")


def test_configuracao_geracao():
    tokenizer = carregar_tokenizer("ConexAI V1")
    config = gerar_configuracao_geracao(tokenizer)
    assert config is not None
    assert config.max_new_tokens == 512
    print("✅ Configuração de geração carregada corretamente.")


def test_carregamento_modelo_llama():
    try:
        llm = carregar_modelo("ConexAI Vteste")
        assert llm is not None
        resposta = llm("Instruct: Diga olá.\nOutput:", max_tokens=10)
        assert "content" in resposta or isinstance(resposta, dict) or isinstance(resposta, str)
        print("✅ Modelo Llama (ConexAI Vteste) carregado e respondeu com sucesso.")
    except Exception as e:
        pytest.fail(f"❌ Falha ao carregar modelo Llama: {e}")
