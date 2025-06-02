# APP/API/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from matplotlib.dates import relativedelta
from pydantic import BaseModel, Field # Importe Field para default values
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# Importa a função que fornece a instância de ChatGestao por requisição
from APP.services.cac_exporter import CacExporter
from APP.services.chat_factory import get_chat_gestion_for_request, get_shared_resources 
from APP.services.chat_gestao import ChatGestao # Para type hinting
from APP.helpers.explicabilidade.utils import formatar_explicacao # Para formatar explicações
import logging 
import locale # Para formatação de moeda local
from APP.db.cac_storage import CacStorage
import re
import aiofiles # type: ignore

logging.basicConfig(level=logging.INFO)

# Configura o locale para português do Brasil (ISO 8601 ou nome do sistema)
# Esta configuração idealmente deveria estar no `main.py` no `startup_event` para ser global.
# Aqui, está sendo configurada uma vez na importação do módulo.
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR') # Tenta sem UTF-8 para Windows
    except locale.Error:
        logging.warning("Não foi possível configurar a localização 'pt_BR' para formatação monetária.")


router = APIRouter()

# --- Modelos Pydantic para Input e Output ---
class PerguntaInput(BaseModel):
    usuario: str
    pergunta: str
    chat_id: Optional[int] = None # <<< CORREÇÃO: chat_id agora é int ou None

class RespostaFormatada(BaseModel):
    analise_detalhada: List[str]
    acoes_recomendadas: List[str]
    metricas_acompanhamento: List[str]

# Define um modelo Pydantic para os itens de dados dentro de dados_grafico
class DadosGraficoItem(BaseModel):
    data: Optional[str] = None      # Para gráficos de linha
    categoria: Optional[str] = None # Para gráficos de barra/pizza
    valor: float                    # Valor numérico bruto
    valor_formatado: Optional[str] = None # Campo para o valor já formatado

# Define o modelo Pydantic completo para dados_grafico
class DadosGraficoOutput(BaseModel):
    grafico: str
    titulo: str
    dados: List[DadosGraficoItem]
    unidade: str # Renomeado de 'moeda' para 'unidade' para ser mais genérico


class ChatInteracaoOutput(BaseModel):
    chat_id: int # ID do chat agora é int
    usuario: str
    pergunta: str
    resposta_formatada: RespostaFormatada # Tipo aninhado
    resposta_bruta_llm: str # Mantém a resposta bruta do LLM
    modelo: str
    data: str # Mantemos como string no formato desejado para a saída
    valido: bool
    detalhes_validacao: Optional[Dict[str, Any]] = None
    explicacao_lime: Optional[str] = None
    explicacao_shap: Optional[str] = None
    dados_grafico: Optional[DadosGraficoOutput] = None # <<< NOVO TIPO Pydantic


# --- Funções Auxiliares de Formatação ---

def _formatar_valor_monetario_ou_percentual(valor: float, unidade: str) -> str:
    """
    Formata um valor float para string monetária ou percentual, baseando-se na unidade.
    """
    if unidade.upper() == "BRL":
        # Retorna o valor monetário formatado conforme o locale 'pt_BR'
        # Ex: R$ 1.234.567,89
        return locale.currency(valor, grouping=True, symbol=True)
    elif unidade == "%":
        # Retorna o valor como percentual com duas casas decimais
        return f"{valor:.2f}%"
    else:
        # Formato genérico com a unidade especificada
        return f"{valor:.2f} {unidade}"

def _formatar_dados_grafico_para_cliente(
    dados_grafico_bruto: Optional[Dict[str, Any]]
) -> Optional[DadosGraficoOutput]:
    """
    Processa e formata os dados brutos do gráfico extraídos do LLM para o cliente.
    Adiciona um campo `valor_formatado` a cada item.
    """
    if not dados_grafico_bruto:
        return None

    # Certifique-se de que a estrutura base do gráfico está presente
    if not all(k in dados_grafico_bruto for k in ["grafico", "titulo", "dados", "unidade"]):
        logging.warning(f"Dados do gráfico brutos incompletos: {dados_grafico_bruto}")
        return None

    unidade = dados_grafico_bruto.get("unidade", "BRL")
    formatted_items: List[DadosGraficoItem] = []

    for item_bruto in dados_grafico_bruto.get("dados", []):
        valor = item_bruto.get("valor")
        if isinstance(valor, (int, float)):
            valor_formatado = _formatar_valor_monetario_ou_percentual(valor, unidade)
            formatted_items.append(DadosGraficoItem(
                data=item_bruto.get("data"),
                categoria=item_bruto.get("categoria"),
                valor=valor,
                valor_formatado=valor_formatado # Adiciona o campo formatado
            ))
        else:
            logging.warning(f"Valor não numérico encontrado no item do gráfico: {item_bruto}")
            # Se o valor não for numérico, adiciona sem formatação de valor
            formatted_items.append(DadosGraficoItem(
                data=item_bruto.get("data"),
                categoria=item_bruto.get("categoria"),
                valor=0.0, # Ou algum valor padrão para não quebrar o Pydantic
                valor_formatado="N/A"
            ))

    return DadosGraficoOutput(
        grafico=dados_grafico_bruto["grafico"],
        titulo=dados_grafico_bruto["titulo"],
        dados=formatted_items,
        unidade=unidade
    )


def _formatar_resposta_llm_para_cliente(resposta_bruta: str) -> RespostaFormatada:
    """
    Formata a resposta bruta do LLM para a estrutura esperada pelo cliente.
    """
    partes = resposta_bruta.strip().split('\n\n')
    analise = []
    acoes = []
    metricas = []
    secao = None

    for linha in partes:
        if "1. Análise detalhada do problema" in linha:
            secao = "analise"
        elif "2. 3 ações recomendadas" in linha:
            secao = "acoes"
        elif "3. Métricas de acompanhamento" in linha:
            secao = "metricas"
        elif linha.strip(): # Garante que a linha não é vazia após strip
            if secao == "analise":
                analise.append(linha.strip('- '))
            elif secao == "acoes":
                acoes.append(linha.strip('- '))
            elif secao == "metricas":
                metricas.append(linha.strip('- '))
    
    return RespostaFormatada(
        analise_detalhada=analise,
        acoes_recomendadas=acoes,
        metricas_acompanhamento=metricas
    )

# --- Endpoints da API ---
@router.post("/chat/pergunta", response_model=ChatInteracaoOutput, status_code=status.HTTP_200_OK)
async def responder_pergunta_endpoint(
    payload: PerguntaInput, 
    chat_manager: ChatGestao = Depends(get_chat_gestion_for_request) # Injeção de dependência
):
    """
    Processa uma pergunta do usuário e retorna a resposta do LLM,
    juntamente com validação e explicações.
    """
    logging.info(f"Requisição recebida de '{payload.usuario}' para o chat '{payload.chat_id or 'novo'}'")
    
    try:
        # Processa a pergunta usando o ChatGestao refatorado
        # Ele agora gerencia a criação do chat_id se necessário.
        resultado_processamento = await chat_manager.processar_pergunta_api(
            usuario=payload.usuario,
            pergunta=payload.pergunta,
            chat_id=payload.chat_id
        )
    except ValueError as e: # Captura a exceção de segurança de chat_id inválido/não autorizado
        logging.error(f"Erro de validação de chat_id para '{payload.usuario}': {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Ou 404 Not Found para ocultar a existência
            detail=str(e) # Retorna a mensagem de erro da exceção
        )
    except Exception as e:
        logging.error(f"Erro inesperado ao processar pergunta para '{payload.usuario}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno ao processar sua pergunta."
        )

    # Formata a resposta bruta do LLM para o cliente (partes estruturadas)
    resposta_formatada_para_cliente = _formatar_resposta_llm_para_cliente(resultado_processamento["resposta_llm_bruta"])

    # Formata os dados do gráfico para o cliente, adicionando o campo 'valor_formatado'
    dados_grafico_para_cliente = _formatar_dados_grafico_para_cliente(resultado_processamento["dados_grafico"])
    
    # Prepara a data para o formato de saída string
    data_interacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepara o dicionário de interação para o banco de dados
    # O DB deve armazenar os dados BRUTOS, não os formatados para exibição
    interacao_para_db = {
        "chat_id": resultado_processamento["chat_id"],
        "usuario": resultado_processamento["usuario"],
        "pergunta": resultado_processamento["pergunta"],
        "resposta_raw": resultado_processamento["resposta_llm_bruta"],
        "valido": resultado_processamento["valido"],
        "detalhes_validacao": resultado_processamento["detalhes_validacao"],
        "explicacao_lime": resultado_processamento["explicacao_lime"],
        "explicacao_shap": resultado_processamento["explicacao_shap"],
        "dados_grafico": resultado_processamento["dados_grafico"], # Salva o dado bruto no DB
        "modelo": resultado_processamento["modelo_versao"],
        "data": data_interacao # Usa a string formatada para salvar no DB
    }
    await chat_manager.context_db.registrar_interacao(resultado_processamento["chat_id"], interacao_para_db) # <<< Adicionado await


    # Monta e retorna o objeto de resposta para o cliente
    return ChatInteracaoOutput(
        chat_id=resultado_processamento["chat_id"], # Já é int
        usuario=resultado_processamento["usuario"],
        pergunta=resultado_processamento["pergunta"],
        resposta_formatada=resposta_formatada_para_cliente,
        resposta_bruta_llm=resultado_processamento["resposta_llm_bruta"],
        modelo=resultado_processamento["modelo_versao"],
        data=data_interacao, # Retorna a data formatada como string
        valido=resultado_processamento["valido"],
        detalhes_validacao=resultado_processamento["detalhes_validacao"],
        explicacao_lime=resultado_processamento["explicacao_lime"],
        explicacao_shap=resultado_processamento["explicacao_shap"],
        dados_grafico=dados_grafico_para_cliente # <<< Retorna os dados FORMATADOS para o cliente
    )


@router.get("/chat/historico", response_model=List[Tuple[int, str, str]]) # <<< CORREÇÃO: response_model para List[Tuple]
async def obter_historico(usuario: str, chat_manager: ChatGestao = Depends(get_chat_gestion_for_request)):
    """
    Lista todos os chats de um usuário.
    """
    return await chat_manager.context_db.listar_chats(usuario) # <<< Adicionado await


@router.get("/chat/historico/detalhado", response_model=Dict[str, Any]) 
async def obter_historico_detalhado(usuario: str, chat_manager: ChatGestao = Depends(get_chat_gestion_for_request)):
    """
    Retorna o histórico detalhado de interações para um usuário.
    """
    historico = await chat_manager.context_db.listar_interacoes(usuario) # <<< Adicionado await
    
    # Processa o histórico para formatar dados_grafico e a data para cada interação
    formatted_interacoes = []
    for interacao in historico:
        formatted_interacao = interacao.copy()
        # Formata dados_grafico se existirem
        formatted_interacao["dados_grafico"] = _formatar_dados_grafico_para_cliente(interacao.get("dados_grafico"))
        # Formata resposta_formatada para consistência
        formatted_interacao["resposta_formatada"] = _formatar_resposta_llm_para_cliente(interacao.get("resposta_llm_bruta", ""))
        # Certifica-se de que a data está no formato de string desejado para a saída
        # interacao.get("data") já deve vir como string do DB se o DB salvou como string
        formatted_interacoes.append(formatted_interacao)

    return {"usuario": usuario, "interacoes": formatted_interacoes}


@router.get("/status", response_model=Dict[str, str])
async def status(chat_manager: ChatGestao = Depends(get_chat_gestion_for_request)):
    """
    Retorna o status da API e a versão do modelo LLM em uso.
    """
    return {"status": "API online", "modelo": chat_manager.versao}


@router.get("/relatorio/cac_mensal", response_model=Dict[str, Any])
async def obter_cac_mensal(ano_mes: str, cac_storage: CacStorage = Depends(get_shared_resources)["cac_storage"]): # Injeta direto o cac_storage
    """
    Retorna o CAC para um mês específico (formato YYYY-MM).
    """
    if not re.match(r"^\d{4}-\d{2}$", ano_mes):
        raise HTTPException(status_code=400, detail="Formato de ano_mes inválido. Use YYYY-MM.")

    try:
        total_despesas = await cac_storage.calcular_total_despesas_cac_mensal(ano_mes)
        num_novos_clientes = await cac_storage.contar_novos_clientes_mensal(ano_mes)
        cac = await cac_storage.calcular_cac_mensal(ano_mes)

        return {
            "ano_mes": ano_mes,
            "total_despesas_cac": total_despesas,
            "num_novos_clientes": num_novos_clientes,
            "cac": cac,
            "observacao": "CAC é 0.0 se não houver novos clientes no mês." if num_novos_clientes == 0 else None
        }
    except Exception as e:
        logging.error(f"Erro ao calcular CAC para {ano_mes}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao calcular CAC.")



@router.get("/relatorio/cac/exportar", response_class=FileResponse)
async def exportar_cac_excel(
    start_month: str = (datetime.now() - relativedelta(months=5)).strftime('%Y-%m'), # Default 6 meses atrás
    end_month: str = datetime.now().strftime('%Y-%m'), # Default mês atual
    cac_exporter: CacExporter = Depends(lambda s=Depends(get_shared_resources): s["cac_exporter"]) # Injeção customizada
):
    """
    Exporta o relatório de CAC para um arquivo Excel.
    """
    if not re.match(r"^\d{4}-\d{2}$", start_month) or not re.match(r"^\d{4}-\d{2}$", end_month):
        raise HTTPException(status_code=400, detail="Formato de mês inválido. Use YYYY-MM.")

    temp_file_path = f"/tmp/relatorio_cac_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx" # Caminho temporário

    success = await cac_exporter.export_cac_report_to_excel(
        output_filepath=temp_file_path,
        start_month=start_month,
        end_month=end_month
    )

    if not success:
        raise HTTPException(status_code=500, detail="Falha ao gerar o relatório Excel.")

    # Retorna o arquivo para download
    return FileResponse(
        path=temp_file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="relatorio_cac.xlsx"
    )