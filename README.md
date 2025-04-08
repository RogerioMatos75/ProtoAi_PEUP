# PEUP - Ponto de Entrada Universal ProtoAi

O PEUP (Ponto de Entrada Universal ProtoAi) é um componente central do ecossistema ProtoAi que atua como um gateway universal para processamento de intenções e comunicação com diferentes serviços.

## Estrutura do Projeto

```
peup/
├── api/            # Endpoints da API FastAPI
├── models/         # Modelos de dados e schemas
├── proto/          # Definições Protocol Buffers
├── services/       # Serviços de negócio
└── tests/          # Testes unitários e de integração
```

## Funcionalidades Principais

- Processamento de intenções via API REST
- Integração com serviço de manifestos
- Comunicação via Protocol Buffers
- Sistema de cache para manifestos

## Configuração e Execução

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
uvicorn api.main:app --reload
```

## Desenvolvimento

O PEUP é desenvolvido usando FastAPI e Protocol Buffers para garantir alta performance e tipagem forte na comunicação entre serviços.