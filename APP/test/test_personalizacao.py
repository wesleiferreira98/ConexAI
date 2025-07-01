# test_personalizacao.py (VERSÃO 2, com teste de filtro)
import asyncio
import logging
from typing import Dict, Any

from APP.services.chat_factory import get_shared_resources, close_db_connection, CONFIG
from APP.services.chat_gestao import ChatGestao
from APP.schemas.perfil_schema import PerfilUsuarioSchema, ConfiguracoesSchema

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- DEFINIÇÃO DAS PERSONAS DE TESTE ---

perfil_gestor_financeiro = PerfilUsuarioSchema(
    id_usuario="gestor_fin_01",
    preferencias=["Análise de KPIs", "Redução de Custos", "Fluxo de Caixa"],
    configuracoes=ConfiguracoesSchema(nivel_experiencia="avançado", formato_resposta="conciso")
)

# Persona fora do escopo para testar o filtro de segurança
perfil_gamer = PerfilUsuarioSchema(
    id_usuario="gamer_user_02",
    preferencias=["Jogos de RPG", "Hardware de PC", "E-sports"],
    configuracoes=ConfiguracoesSchema(nivel_experiencia="expert", formato_resposta="gírias")
)

# --- DEFINIÇÃO DOS CENÁRIOS DE TESTE ---

cenarios_de_teste = [
    {
        "id_teste": "Teste 1: Pergunta DENTRO do escopo para perfil financeiro",
        "perfil": perfil_gestor_financeiro,
        "pergunta": "O que é KPI eficaz?",
        "comportamento_esperado": "A resposta deve ser focada em negócios, com linguagem profissional, e o campo 'valido' deve ser True."
    },
    {
        "id_teste": "Teste 2: Pergunta FORA do escopo para perfil gamer",
        "perfil": perfil_gamer,
        "pergunta": "Qual a melhor build de personagem para o novo jogo de fantasia?",
        "comportamento_esperado": "A pergunta deve ser bloqueada. O campo 'valido' deve ser False e a resposta deve ser a mensagem de recusa."
    }
]


async def executar_teste_de_personalizacao():
    print("="*60)
    print("🚀 INICIANDO TESTE ISOLADO (V2) 🚀")
    print("="*60)

    shared_resources = None
    try:
        print("\n[SETUP] Carregando recursos...")
        shared_resources = await get_shared_resources()
        
        chat_manager = ChatGestao(
            validador=shared_resources["validador_pergunta"],
            gerador=shared_resources["gerador_llm"],
            context_db=shared_resources["context_db"], 
            versao=CONFIG.VERSAO_MODELO,
            mock_llm_for_explanation=shared_resources["mock_llm_for_explanation"],
            lime_explicator=shared_resources["lime_explicator"],
            shap_explicator=shared_resources["shap_explicator"],
            gerador_grafico=shared_resources["gerador_grafico"],
            document_retriever=shared_resources["document_retriever"]
        )
        print("[SETUP] Recursos carregados.")

        print("\n[SETUP] Cadastrando perfis de teste...")
        await chat_manager.context_db.atualizar_perfil(perfil_gestor_financeiro)
        await chat_manager.context_db.atualizar_perfil(perfil_gamer)
        print("[SETUP] Perfis prontos.")

        for cenario in cenarios_de_teste:
            print("\n" + "-"*50)
            print(f"▶️  {cenario['id_teste']}")
            print(f"👤 Usuário: {cenario['perfil'].id_usuario}")
            print(f"❓ Pergunta: '{cenario['pergunta']}'")
            print(f"🎯 Comportamento Esperado: {cenario['comportamento_esperado']}")
            print("-"*50)

            resultado = await chat_manager.processar_pergunta_api(
                usuario=cenario['perfil'].id_usuario,
                pergunta=cenario['pergunta'],
                chat_id=None
            )

            print("\n📋 RESULTADO OBTIDO:")
            print(f"   - Pergunta Válida? {'Sim' if resultado.get('valido') else 'Não'}")
            print(f"   - Resposta: {resultado.get('resposta_llm_bruta')}")
            print("-" * 50 + "\n")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante o teste: {e}")
        logging.error("Erro no script de teste", exc_info=True)
    finally:
        if shared_resources:
            print("\n[TEARDOWN] Fechando conexão...")
            await close_db_connection()
            print("[TEARDOWN] Conexão fechada.")
    
    print("="*60)
    print("✅ TESTE CONCLUÍDO ✅")
    print("="*60)
