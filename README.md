# PEUP - Ponto de Entrada Universal ProtoAi

## Visão Geral
O PEUP (Ponto de Entrada Universal ProtoAi) é um serviço que atua como gateway unificado para processamento de intenções e gerenciamento de manifestos no ecossistema ProtoAi. Implementado em Go com componentes em Rust para processamento de linguagem natural.

## Arquitetura
- **Backend Principal (Go)**: Servidor HTTP/gRPC para processamento de requisições
- **Processador de Intenções (Rust)**: Análise e interpretação de queries em linguagem natural
- **Cache de Manifestos**: Sistema de cache em memória para otimização de performance
- **Protobuf**: Comunicação padronizada entre componentes usando Protocol Buffers

## Requisitos do Sistema
- Go 1.20 ou superior
- Rust (última versão estável)
- Protobuf compiler

## Instalação

### 1. Clone o Repositório
```bash
git clone [url-do-repositorio]
cd peup
```

### 2. Instale as Dependências
```bash
# Go dependencies
go mod download

# Rust dependencies (para o serviço de intenções)
cd services/intent_service
cargo build --release
cd ../..
```

### 3. Compile os Arquivos Protocol Buffer
```bash
protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    proto/*.proto
```

## Executando o Serviço
```bash
# Inicie o servidor
go run cmd/peup/main.go
```
O servidor estará disponível em:
- HTTP: `http://localhost:8080`
- gRPC: `localhost:50051`

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
- **Linguagem Natural**: `Buscar repositórios git do tipo jogo`

### 2. Formatos de Resposta
O PEUP suporta múltiplos formatos de resposta:
- Protocol Buffers (padrão)
- JSON
- Outros formatos específicos conforme necessidade

### 3. Cache de Manifestos
Implementa um sistema de cache em memória para:
- Redução de latência
- Otimização de recursos
- Cache invalidation baseado em tempo

## Endpoints

### POST /intent
Processa intenções em formato JSON ou texto natural.

### POST /peup
Endpoint principal para processamento de intenções com suporte a Protocol Buffers.

## Desenvolvimento

### Estrutura do Projeto
```
/
├── cmd/
│   └── peup/           # Ponto de entrada da aplicação
├── proto/              # Definições Protocol Buffer
├── server/             # Implementação do servidor gRPC
├── services/
│   ├── intent_service/ # Serviço de processamento de intenções (Rust)
│   └── manifest/       # Serviço de gerenciamento de manifestos
└── manifestos/         # Manifestos de exemplo e templates
```

## Contribuindo
Contribuições são bem-vindas! Por favor, leia nossas diretrizes de contribuição antes de submeter pull requests.

## Licença
Este projeto está licenciado sob os termos da licença MIT.