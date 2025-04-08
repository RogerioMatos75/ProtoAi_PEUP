from pydantic import BaseModel
from typing import Dict, Any

class ProtoAiIntent(BaseModel):
    """Modelo que representa uma intenção do ProtoAi.
    
    Attributes:
        action (str): A ação a ser executada (ex: BUSCAR, CRIAR, ATUALIZAR)
        scope (str): O escopo da ação (ex: repositories, users)
        parameters (Dict[str, Any]): Parâmetros adicionais para a ação
        response_format (str): Formato desejado para a resposta (ex: json, protobuf)
    """
    action: str
    scope: str
    parameters: Dict[str, Any] = {}
    response_format: str = "json"