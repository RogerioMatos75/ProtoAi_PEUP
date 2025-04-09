from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional
from models.readme_pb2 import ReadmeProto
from models.indexer_pb2 import ProjectInfoFromCsv, ReadmeInfo
from services.fetch_manifest import ManifestFetcher
from services.intent_parser import IntentParser
from models.intent import ProtoAiIntent
from google.protobuf import json_format

# Configurar logging
logging.basicConfig(level=logging.INFO)
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

# Instanciar serviços
intent_parser = IntentParser()
manifest_fetcher = ManifestFetcher()

@app.post("/peup/parse")
async def parse_natural_language(query: str) -> dict:
    """
    Endpoint para processar queries em linguagem natural.
    
    Args:
        query (str): Query em linguagem natural
        
    Returns:
        dict: Intenção parseada com ação e parâmetros
    """
    try:
        action, params = await intent_parser.parse_intent(query)
        return {
            "action": action,
            "parameters": params
        }
    except Exception as e:
        logger.error(f"Erro ao processar query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/peup")
async def process_request(intent: ProtoAiIntent):
    """
    Processa uma requisição do PEUP.
    
    Args:
        intent (ProtoAiIntent): A intenção do usuário
        
    Returns:
        Response: Resposta no formato solicitado (protobuf ou json)
    """
    try:
        logger.info(f"Processando requisição para escopo: {intent.scope}")
        
        # Se receber uma query em linguagem natural, usar o parser
        if hasattr(intent, 'query') and intent.query:
            action, params = await intent_parser.parse_intent(intent.query)
            intent.action = action
            intent.parameters.update(params)
        
        # Buscar manifesto com mecanismo de retentativa
        manifest = await manifest_fetcher.fetch_manifest(intent.scope)
        
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifesto não encontrado")

        # Retornar no formato solicitado
        if intent.response_format == "protobuf":
            return Response(
                content=manifest.SerializeToString(),
                media_type="application/x-protobuf",
                headers={
                    "X-Source": manifest.metadata.source,
                    "X-Scope": intent.scope
                }
            )
        else:
            # Converter para JSON
            json_data = json_format.MessageToJson(
                manifest,
                including_default_value_fields=True,
                preserving_proto_field_name=True
            )
            return Response(
                content=json_data,
                media_type="application/json",
                headers={
                    "X-Source": manifest.metadata.source,
                    "X-Scope": intent.scope
                }
            )
            
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/protoai/readme.protobuf")
async def get_manifest(scope: str = None):
    """
    Retorna o manifesto no formato Protocol Buffer.
    
    Args:
        scope (str): O escopo do manifesto solicitado
        
    Returns:
        Response: Manifesto serializado em formato protobuf
    """
    try:
        manifest = await manifest_fetcher.fetch_manifest(scope or "default")
        
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifesto não encontrado")
        
        return Response(
            content=manifest.SerializeToString(),
            media_type="application/x-protobuf",
            headers={
                "X-Source": manifest.metadata.source,
                "X-Scope": scope or "default"
            }
        )
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Retorna informações básicas sobre a API."""
    return {
        "name": "ProtoAi PEUP",
        "version": "1.0.0",
        "description": "Ponto de Entrada Universal ProtoAi"
    }