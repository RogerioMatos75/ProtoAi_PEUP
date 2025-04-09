# PEUP - Ponto de Entrada Universal ProtoAi

O PEUP (Ponto de Entrada Universal ProtoAi) é um componente central do ecossistema ProtoAi que atua como um gateway universal para processamento de intenções e comunicação com diferentes serviços.

## Visão Geral

O ProtoAi MCP é uma solução projetada para facilitar a descoberta, documentação e interação com serviços, especialmente focada em cenários envolvendo agentes de IA. O sistema é construído sobre três pilares principais:

- **Manifestos Semânticos** (`README.protobuf`): Documentação estruturada que descreve capacidades, interfaces e políticas de serviços
- **Mecanismos de Descoberta de Serviços**: Sistema para localizar e interagir com serviços compatíveis
- **Especificação de Intenções Padronizada**: Formato padronizado para expressar requisições

## Estrutura do Projeto

```
peup/
├── api/            # Endpoints da API FastAPI
├── models/         # Modelos de dados e schemas
├── manifestos/     # Definições de manifestos e Protocol Buffers
├── services/       # Serviços de negócio
└── tests/          # Testes unitários e de integração
```

## Funcionalidades Principais

### 1. Processamento de Intenções (PIS)
O PEUP aceita intenções em diferentes formatos:

- **JSON Estruturado**:
```json
{
  "protoai_intent": "1.0",
  "action": "BUSCAR",
  "scope": "repositorio_git",
  "parameters": {
    "tipo": "jogo",
    "linguagem": "python"
  },
  "response_format": "protobuf"
}
```

- **URI-like**: `protoai:buscar?escopo=repositorio_git&tipo=jogo`
- **Linguagem Natural Estruturada**: `BUSCAR repositorios_git TIPO=jogo.protobuf`

### 2. Fluxo de Processamento

1. **Recebimento da Intenção**:
   - Endpoint `/intent` para requisições HTTPS
   - Parsing e validação da intenção PIS
   - Identificação de ação e escopo

2. **Descoberta de Serviço**:
   - Consulta ao Registry Service
   - Download e processamento do manifesto

3. **Execução**:
   - Mapeamento de parâmetros
   - Chamada ao serviço alvo
   - Formatação da resposta

### 3. Benefícios

- **Acessibilidade Universal**: Compatível com qualquer cliente HTTPS
- **Ponto Único de Interação**: Simplificação da integração
- **Segurança**: Comunicação criptografada e controle de acesso
- **Flexibilidade**: Suporte a múltiplos formatos e protocolos

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

O PEUP é desenvolvido usando FastAPI e Protocol Buffers para garantir:
- Alta performance na comunicação
- Tipagem forte entre serviços
- Documentação automática via OpenAPI/Swagger
- Cache de manifestos para otimização

## Segurança e Escalabilidade

### Segurança
- Autenticação e autorização em nível de serviço
- Validação de intenções
- Proteção contra uso indevido

### Escalabilidade
- Cache de manifestos
- Balanceamento de carga
- Descoberta distribuída

## Contribuindo

1. Faça um fork do projeto
2. Crie sua feature branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Crie um novo Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.