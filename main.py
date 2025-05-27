import logging
from fastapi import FastAPI
from APP.API.routes import router
from APP.core.config import CONFIG
from APP.core.constantes import VERSAO_MODELO, ADAPTER_PATH, BASE_MODEL
from APP.services.chat_factory import close_db_connection, get_shared_resources
import uvicorn # Configura o logging básico para a aplicação
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Instância do FastAPI com metadados
app = FastAPI(
    title="ConexAI Chat API",
    description="API para o chatbot ConexAI de gestão, com recursos de validação e explicabilidade.",
    version=CONFIG.VERSAO_MODELO, # Pega a versão do modelo diretamente da CONFIG
    docs_url="/docs", # URL para a documentação interativa (Swagger UI)
    redoc_url="/redoc" # URL para a documentação alternativa (ReDoc)
)

# Inclui o roteador da API
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """
    Este evento é executado uma única vez na inicialização da aplicação.
    É o lugar ideal para carregar recursos pesados que serão compartilhados.
    """
    logging.info("🚀 Iniciando a aplicação FastAPI...")
    
    # Exibe informações do modelo no console/log na inicialização
    logging.info("\n🔍 **INFORMAÇÕES DO MODELO**")
    logging.info(f"🆔 Versão do Modelo Ativa: {CONFIG.VERSAO_MODELO}")
    
    model_info = CONFIG.get_model_info()
    if model_info["llama_cpp"]:
        logging.info(f"🧠 Modelo Base: (Utilizando Llama.cpp - {model_info['llama_cpp_model_info']['filename']})")
    else:
        logging.info(f"🧠 Modelo Base Hugging Face: {model_info['base_model']}")
        if model_info["adapter_repo"]:
            logging.info(f"📦 Adaptador LoRA: {model_info['adapter_repo']}")
        else:
            logging.info("📦 Sem Adaptador LoRA")
    
    logging.info("🟢 Carregando recursos compartilhados (LLM, explicadores, etc.). Isso pode levar alguns segundos...")
    # Força o carregamento dos recursos compartilhados no startup
    # (A função get_shared_resources() deve ser chamada para preencher _shared_resources)
    get_shared_resources() 
    logging.info("✅ Recursos compartilhados carregados. API pronta para uso.")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Este evento é executado quando a aplicação está sendo desligada.
    Útil para fechar conexões de banco de dados, limpar recursos, etc.
    """
    # CORREÇÃO: Chamando a função de fechamento do DB que foi definida em chat_factory.py
    await close_db_connection() 
    logging.info("🔴 Desligando a aplicação FastAPI...")
   

if __name__ == "__main__":
    logging.info("Iniciando o servidor Uvicorn a partir de main.py...")
    # Atenção: reload=True é ótimo para desenvolvimento, mas NÃO deve ser usado em produção.
    # Em produção, use uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=X)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)