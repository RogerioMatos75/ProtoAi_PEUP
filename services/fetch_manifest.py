import json
import os
from typing import Dict, Any, Optional
import logging

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
        return os.path.join(self.cache_dir, f"{scope}_manifest.json")
    
    def _load_from_cache(self, scope: str) -> Optional[Dict[str, Any]]:
        """Carrega um manifesto do cache local."""
        cache_path = self._get_cache_path(scope)
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['cache_hit'] = True
                    return data
        except Exception as e:
            logger.error(f"Erro ao carregar cache para {scope}: {e}")
        return None
    
    def _save_to_cache(self, scope: str, data: Dict[str, Any]) -> None:
        """Salva um manifesto no cache local."""
        try:
            cache_path = self._get_cache_path(scope)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar cache para {scope}: {e}")
    
    def _load_fallback(self, scope: str) -> Optional[Dict[str, Any]]:
        """Carrega um manifesto de fallback para casos de falha total."""
        try:
            fallback_path = os.path.join(self.cache_dir, 'exemplo_readme.protobuf')
            if os.path.exists(fallback_path):
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['fallback'] = True
                    return data
        except Exception as e:
            logger.error(f"Erro ao carregar fallback para {scope}: {e}")
        return None
    
    def fetch_manifest(self, scope: str) -> Optional[Dict[str, Any]]:
        """Busca um manifesto para o escopo especificado.
        
        Args:
            scope (str): O escopo do manifesto a ser buscado
            
        Returns:
            Optional[Dict[str, Any]]: O manifesto encontrado ou None em caso de falha
        """
        # Tentar carregar do cache primeiro
        manifest = self._load_from_cache(scope)
        if manifest:
            logger.info(f"Manifesto para {scope} carregado do cache")
            return manifest
        
        # Se não houver cache, carregar do fallback
        manifest = self._load_fallback(scope)
        if manifest:
            logger.info(f"Manifesto para {scope} carregado do fallback")
            return manifest
        
        logger.error(f"Não foi possível carregar manifesto para {scope}")
        return None