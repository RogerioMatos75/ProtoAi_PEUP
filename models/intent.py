from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProtoAiIntent(BaseModel):
    """Modelo que representa uma intenção do ProtoAi.
    
    Attributes:
        action (str): A ação a ser executada (ex: BUSCAR, CRIAR, ATUALIZAR)
        scope (str): O escopo da ação (ex: repositories, users)
        parameters (Dict[str, Any]): Parâmetros adicionais para a ação
        response_format (str): Formato desejado para a resposta (ex: json, protobuf)
        query (Optional[str]): Query em linguagem natural (opcional)
    """
    action: str = Field(..., description="Ação a ser executada")
    scope: str = Field(..., description="Escopo da ação")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros adicionais")
    response_format: str = Field(default="json", description="Formato da resposta")
    query: Optional[str] = Field(None, description="Query em linguagem natural")