from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from models.intent import ProtoAiIntent
from services.fetch_manifest import ManifestFetcher
from proto.protoai.v1.readme_pb2 import ReadmeProto
import httpx
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:5173",  # Frontend Vite
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def call_indexer_api(search_params: Dict[str, Any]) -> Dict[str, Any]:
    """Chama a API Indexadora com os parâmetros de busca fornecidos."""
    indexer_url = "http://localhost:8080/search"  # URL da API Indexadora
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(indexer_url, params=search_params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Erro ao chamar API Indexadora: {str(e)}")

@app.post("/intent", response_class=Response)
async def handle_intent(intent: ProtoAiIntent):
    # Obter o manifesto usando o fetcher (com cache e fallback)
    fetcher = ManifestFetcher()
    manifesto_data = fetcher.fetch_manifest(intent.scope)

    if not manifesto_data:
        raise HTTPException(status_code=500, detail="Falha ao obter manifesto")

    # Se a ação for BUSCAR, processa a busca através da API Indexadora
    search_result = None
    if intent.action.upper() == "BUSCAR":
        try:
            search_result = await call_indexer_api(intent.parameters)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar busca: {str(e)}")

    # Criar e preencher o objeto ReadmeProto
    proto_response = ReadmeProto()
    proto_response.intent = intent.scope
    
    # Preencher project_info
    proto_response.project_info.name = manifesto_data.get("name", "")
    proto_response.project_info.version = manifesto_data.get("version", "")
    proto_response.project_info.description = manifesto_data.get("description", "")
    proto_response.project_info.tags.extend(manifesto_data.get("tags", []))
    
    # Preencher communication_details
    if "communication_details" in manifesto_data:
        comm_details = manifesto_data["communication_details"]
        for interface in comm_details.get("access_interfaces", []):
            access_interface = proto_response.communication_details.access_interfaces.add()
            access_interface.type = getattr(AccessInterface.IfType, interface.get("type", "UNDEFINED"))
            access_interface.base_url_or_address = interface.get("base_url_or_address", "")
            access_interface.available_methods_or_operations.extend(interface.get("available_methods_or_operations", []))
        proto_response.communication_details.default_data_formats.extend(comm_details.get("default_data_formats", []))
    
    # Preencher security_info
    if "security_info" in manifesto_data:
        proto_response.security_info.encryption_required = manifesto_data["security_info"].get("encryption_required", False)
    
    # Preencher monetization_info se disponível
    if "monetization_info" in manifesto_data:
        mon_info = manifesto_data["monetization_info"]
        proto_response.monetization_info.model = getattr(MonetizationInfo.ModelType, mon_info.get("model", "MODEL_TYPE_UNSPECIFIED"))
        proto_response.monetization_info.price_details = mon_info.get("price_details", "")
        proto_response.monetization_info.currency = mon_info.get("currency", "")
        proto_response.monetization_info.pricing_page_url = mon_info.get("pricing_page_url", "")
        proto_response.monetization_info.commission_enabled = mon_info.get("commission_enabled", False)
        proto_response.monetization_info.commission_details_url = mon_info.get("commission_details_url", "")
    
    # Preencher licensing_info se disponível
    if "licensing_info" in manifesto_data:
        lic_info = manifesto_data["licensing_info"]
        proto_response.licensing_info.license_key = lic_info.get("license_key", "")
        proto_response.licensing_info.license_url = lic_info.get("license_url", "")
    
    # Serializar para protobuf
    serialized_response = proto_response.SerializeToString()
    
    # Retornar resposta serializada com o tipo de mídia correto
    return Response(
        content=serialized_response,
        media_type="application/x-protobuf",
        headers={
            "X-Response-Source": "cache" if manifesto_data.get("cache_hit") else ("network" if not manifesto_data.get("fallback") else "fallback"),
            "X-Scope-Requested": intent.scope
        }
    )

@app.get("/")
async def root():
    return {"message": "Bem-vindo ao PEUP - Ponto de Entrada Universal ProtoAi"}

@app.post("/peup/process")
async def process_request(request: Dict[str, Any]):
    logger.debug(f"Recebendo solicitação: {request}")
    
    # Passo 1: Interpretar a intenção (PIS)
    intent = {
        "action": "BUSCAR",
        "scope": request.get("scope", "repositories"),
        "parameters": request.get("parameters", {}),
        "response_format": "json"
    }
    logger.debug(f"Intenção interpretada: {intent}")

    # Passo 2: Buscar o manifesto diretamente usando o fetcher
    try:
        from services.fetch_manifest import ManifestFetcher
        fetcher = ManifestFetcher()
        manifest = fetcher.fetch_manifest(intent["scope"])
        logger.debug(f"Manifesto obtido: {manifest}")

        if not manifest:
            raise HTTPException(status_code=500, detail="Falha ao obter manifesto")

        # Passo 3: Processar a busca se necessário
        search_result = None
        if intent["action"].upper() == "BUSCAR":
            try:
                search_result = await call_indexer_api(intent["parameters"])
            except Exception as e:
                logger.error(f"Erro ao processar busca: {e}")
                raise HTTPException(status_code=500, detail=f"Erro ao processar busca: {str(e)}")

        # Passo 4: Montar resposta
        response = {
            "status": "ok",
            "mensagem": f"Ação '{intent['action']}' processada para escopo '{intent['scope']}'",
            "manifesto_info": {
                "source": "cache" if manifest.get("cache_hit") else "network",
                "scope_requested": intent["scope"],
                "retrieved_manifest_name": manifest.get("name", "N/A")
            },
            "filtros_aplicados": intent["parameters"],
            "formato_solicitado": intent["response_format"],
            "resultado_busca": search_result
        }
        return response
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}")
        raise HTTPException(status_code=500, detail=str(e))