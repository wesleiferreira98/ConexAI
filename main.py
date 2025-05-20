from fastapi import FastAPI
from APP.API.routes import router
from APP.core.constantes import VERSAO_MODELO, ADAPTER_PATH, BASE_MODEL
import uvicorn
app = FastAPI()
app.include_router(router)

def exibir_informacoes_modelo():
    print("\n🔍 **INFORMAÇÕES DO MODELO**")
    print(f"🆔 Versão do Modelo: {VERSAO_MODELO}")
    print(f"📂 Caminho do Adaptador: {ADAPTER_PATH}")
    
    if BASE_MODEL:
        print(f"🧠 Modelo Base: {BASE_MODEL}")
    else:
        print(f"🧠 Modelo Base: (Utilizando ctransformers, sem modelo base)")

    print("\n🟢 Inicializando...\n")


if __name__ == "__main__":
    exibir_informacoes_modelo()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
