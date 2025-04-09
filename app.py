import streamlit as st
import httpx
import asyncio
import json
from models.intent import ProtoAiIntent

st.set_page_config(
    page_title="ProtoAi PEUP - Manifest Viewer",
    page_icon="🔍",
    layout="wide"
)

st.title('🔍 ProtoAi PEUP - Manifest Viewer')

with st.sidebar:
    st.header("Configurações")
    action = st.selectbox(
        "Ação",
        ["BUSCAR", "CRIAR", "ATUALIZAR", "DELETAR"],
        index=0
    )
    scope = st.text_input('Escopo', 'repositories')
    response_format = st.selectbox(
        "Formato de Resposta",
        ["json", "protobuf"],
        index=0
    )
    
    # Parâmetros dinâmicos
    st.subheader("Parâmetros")
    num_params = st.number_input("Número de parâmetros", min_value=0, max_value=10, value=0)
    params = {}
    for i in range(num_params):
        col1, col2 = st.columns(2)
        with col1:
            key = st.text_input(f"Chave {i+1}")
        with col2:
            value = st.text_input(f"Valor {i+1}")
        if key and value:
            params[key] = value

if st.sidebar.button('Enviar Requisição'):
    try:
        # Criar objeto de intenção
        intent = ProtoAiIntent(
            action=action,
            scope=scope,
            parameters=params,
            response_format=response_format
        )

        # Fazer a requisição para a API
        async def fetch_manifest():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'http://localhost:8000/peup',
                    json=intent.model_dump(),
                    timeout=30
                )
                response.raise_for_status()
                return response.json()

        with st.spinner('Processando requisição...'):
            manifest_data = asyncio.run(fetch_manifest())

        # Exibir o manifesto
        st.subheader('📄 Manifesto')
        
        # Criar três colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Status",
                value="✅ Sucesso" if "error" not in manifest_data else "❌ Erro"
            )
        
        with col2:
            if "cache_hit" in manifest_data:
                st.metric(label="Fonte", value="Cache")
            elif "fallback" in manifest_data:
                st.metric(label="Fonte", value="Fallback")
            else:
                st.metric(label="Fonte", value="API")
        
        with col3:
            st.metric(label="Formato", value=response_format.upper())

        # Exibir o JSON formatado
        st.json(manifest_data)

    except httpx.HTTPStatusError as e:
        st.error(f'Erro na requisição: {e}')
    except Exception as e:
        st.error(f'Erro: {e}')

# Adicionar informações de ajuda
with st.expander("ℹ️ Ajuda"):
    st.markdown("""
    ### Como usar
    1. Selecione a ação desejada no menu lateral
    2. Digite o escopo da busca
    3. Adicione parâmetros adicionais se necessário
    4. Escolha o formato de resposta desejado
    5. Clique em 'Enviar Requisição'
    
    ### Ações disponíveis
    - **BUSCAR**: Busca informações sobre um recurso
    - **CRIAR**: Cria um novo recurso
    - **ATUALIZAR**: Atualiza um recurso existente
    - **DELETAR**: Remove um recurso existente
    
    ### Formatos de resposta
    - **JSON**: Retorna os dados em formato JSON
    - **PROTOBUF**: Retorna os dados em formato Protocol Buffers
    """)

# Adicionar rodapé
st.markdown("---")
st.markdown(
    "Desenvolvido com ❤️ pela equipe ProtoAi | "
    "[Documentação](https://github.com/seu-usuario/protoai-peup) | "
    "[Reportar Problema](https://github.com/seu-usuario/protoai-peup/issues)"
)