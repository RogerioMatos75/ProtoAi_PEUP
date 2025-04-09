import logging
from transformers import pipeline
from typing import Dict, Any, Tuple
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

class IntentParser:
    def __init__(self):
        self._nlp = None  # Lazy loading do modelo
        
    @lru_cache(maxsize=1)
    def _get_pipeline(self):
        """Carrega o modelo de NLP de forma lazy."""
        if self._nlp is None:
            logger.info("Carregando modelo de NLP...")
            self._nlp = pipeline(
                "text-classification",
                model="bert-base-multilingual-uncased",
                top_k=3
            )
        return self._nlp

    async def parse_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Analisa a query do usuário para extrair a intenção e parâmetros.
        
        Args:
            query (str): Query em linguagem natural
            
        Returns:
            Tuple[str, Dict[str, Any]]: Tupla contendo (intenção, parâmetros)
        """
        # Executar classificação em um thread separado para não bloquear
        loop = asyncio.get_event_loop()
        nlp = self._get_pipeline()
        results = await loop.run_in_executor(None, nlp, query)
        
        # Mapear labels para ações do sistema
        action_mapping = {
            "search": "BUSCAR",
            "create": "CRIAR",
            "update": "ATUALIZAR",
            "delete": "DELETAR"
        }
        
        # Extrair a ação mais provável
        top_result = results[0][0]
        action = action_mapping.get(top_result["label"], "BUSCAR")
        
        # Extrair parâmetros da query usando heurísticas simples
        params = self._extract_parameters(query)
        
        logger.info(f"Intent parseada: {action} com parâmetros {params}")
        return action, params
    
    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extrai parâmetros da query usando heurísticas.
        
        Args:
            query (str): Query em linguagem natural
            
        Returns:
            Dict[str, Any]: Dicionário de parâmetros extraídos
        """
        params = {}
        
        # Lista de palavras-chave para tipos de projeto
        type_keywords = {
            "web": ["web", "website", "site"],
            "mobile": ["mobile", "app", "android", "ios"],
            "jogo": ["jogo", "game", "gaming"]
        }
        
        query_lower = query.lower()
        
        # Detectar tipo de projeto
        for type_name, keywords in type_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                params["tipo"] = type_name
                break
        
        # Detectar nível (se mencionado)
        if "nível" in query_lower or "level" in query_lower:
            # Procurar por números após "nível" ou "level"
            import re
            level_match = re.search(r"(?:nível|level)\s*(\d+)", query_lower)
            if level_match:
                params["level"] = int(level_match.group(1))
        
        # Detectar se deve mostrar apenas destaques
        if "destaque" in query_lower or "featured" in query_lower:
            params["only_featured"] = True
            
        return params