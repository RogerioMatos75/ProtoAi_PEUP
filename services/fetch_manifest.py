import os
from typing import Optional
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from google.protobuf import json_format
from models.readme_pb2 import ReadmeProto
from models.indexer_pb2 import ProjectInfoFromCsv, ReadmeInfo

logger = logging.getLogger(__name__)

class ManifestFetcher:
    """Serviço responsável por buscar e gerenciar manifestos.
    
    Implementa estratégias de cache e fallback para garantir disponibilidade
    dos manifestos mesmo em caso de falhas na rede.
    """
    
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'manifestos')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_path(self, scope: str) -> str:
        """Retorna o caminho do arquivo de cache para um determinado escopo."""
        return os.path.join(self.cache_dir, f"{scope}_manifest.pb")
    
    def _load_from_cache(self, scope: str) -> Optional[ReadmeProto]:
        """Carrega um manifesto do cache local."""
        cache_path = self._get_cache_path(scope)
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    manifest = ReadmeProto()
                    manifest.ParseFromString(f.read())
                    # Adicionar metadados de cache
                    manifest.metadata.source = "cache"
                    return manifest
        except Exception as e:
            logger.error(f"Erro ao carregar cache para {scope}: {e}")
        return None
    
    def _save_to_cache(self, scope: str, manifest: ReadmeProto) -> None:
        """Salva um manifesto no cache local."""
        try:
            cache_path = self._get_cache_path(scope)
            with open(cache_path, 'wb') as f:
                f.write(manifest.SerializeToString())
        except Exception as e:
            logger.error(f"Erro ao salvar cache para {scope}: {e}")
    
    def _load_fallback(self, scope: str) -> Optional[ReadmeProto]:
        """Carrega um manifesto de fallback para casos de falha total."""
        try:
            fallback_path = os.path.join(self.cache_dir, 'exemplo_readme.protobuf')
            if os.path.exists(fallback_path):
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    # Converter JSON para protobuf
                    manifest = ReadmeProto()
                    json_format.Parse(f.read(), manifest)
                    # Adicionar metadados de fallback
                    manifest.metadata.source = "fallback"
                    return manifest
        except Exception as e:
            logger.error(f"Erro ao carregar fallback para {scope}: {e}")
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.NetworkError)),
        before_sleep=lambda retry_state: logger.info(
            f"Tentativa {retry_state.attempt_number} falhou, tentando novamente em 2 segundos..."
        )
    )
    async def _fetch_from_api(self, scope: str) -> ReadmeProto:
        """Busca o manifesto da API com mecanismo de retentativa."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/protoai/readme.protobuf",
                params={"scope": scope},
                headers={"Accept": "application/x-protobuf"}
            )
            response.raise_for_status()
            
            manifest = ReadmeProto()
            manifest.ParseFromString(response.content)
            manifest.metadata.source = "api"
            return manifest
    
    async def fetch_manifest(self, scope: str) -> Optional[ReadmeProto]:
        """Busca um manifesto para o escopo especificado.
        
        Args:
            scope (str): O escopo do manifesto a ser buscado
            
        Returns:
            Optional[ReadmeProto]: O manifesto encontrado ou None em caso de falha
        """
        # Tentar carregar do cache primeiro
        manifest = self._load_from_cache(scope)
        if manifest:
            logger.info(f"Manifesto para {scope} carregado do cache")
            return manifest
        
        try:
            # Tentar buscar da API com retentativa
            manifest = await self._fetch_from_api(scope)
            
            # Salvar no cache
            self._save_to_cache(scope, manifest)
            return manifest
                
        except Exception as e:
            logger.error(f"Erro ao buscar manifesto da API para {scope}: {e}")
            
            # Se falhar, tentar carregar do fallback
            manifest = self._load_fallback(scope)
            if manifest:
                logger.info(f"Manifesto para {scope} carregado do fallback")
                return manifest
        
        logger.error(f"Não foi possível carregar manifesto para {scope}")
        return None