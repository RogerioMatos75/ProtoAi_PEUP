# ProtoAi MCP: Conceitos Fundamentais

Este documento descreve os conceitos fundamentais e a arquitetura do ProtoAi MCP (Manifesto e Catálogo de Protocolos), incluindo seus mecanismos de descoberta de serviços e interação padronizada.

## 1. Visão Geral

O ProtoAi MCP é uma solução projetada para facilitar a descoberta, documentação e interação com serviços, especialmente focada em cenários envolvendo agentes de IA. O sistema é construído sobre três pilares principais:

- Manifestos Semânticos (`README.protobuf`)
- Mecanismos de Descoberta de Serviços
- Especificação de Intenções Padronizada

## 2. Manifesto Semântico

O `README.protobuf` é um manifesto estruturado que descreve as capacidades, interfaces e políticas de um serviço. Este formato permite que tanto humanos quanto máquinas compreendam facilmente as características e requisitos do serviço.

## 3. Descoberta e Interação Padronizada

Para facilitar a interação, especialmente por agentes de IA, o ProtoAi MCP propõe mecanismos para descoberta de serviços e uma forma padronizada de expressar intenções.

### 3.1. Descoberta de Serviços

* **Manifesto (`README.protobuf`):** Cada serviço compatível com ProtoAi deve fornecer um manifesto descrevendo suas capacidades, interfaces e políticas.
* **Mecanismos de Descoberta:**
    * **Descentralizado:** Exposição do manifesto via endpoint conhecido (e.g., `/.well-known/protoai-readme.protobuf`).
    * **Centralizado (Recomendado para Ecossistemas):** Um Registry Service cataloga os manifestos e permite buscas.

### 3.2. ProtoAi Intent Specification (PIS)

Para abstrair a complexidade de encontrar e chamar o endpoint correto, propomos o PIS, uma forma padronizada de expressar o que o usuário/IA deseja fazer.

**Objetivo:** Permitir que um cliente formule uma intenção clara que pode ser interpretada por um agente ou ponto de entrada universal.

**Formatos Possíveis:**

1. **Linguagem Natural Estruturada:** `[Ação] [Escopo] [Filtros].[Protocolo]`
   Exemplo: `BUSCAR repositorios_git TIPO=jogo.protobuf`

2. **URI-like:** `protoai:[Ação]?escopo=[Escopo]&[param1]=[valor1]`
   Exemplo: `protoai:buscar?escopo=repositorio_git&tipo=jogo`

3. **JSON Estruturado:**
   ```json
   {
     "protoai_intent": "1.0",    // Versão do PIS
     "action": "BUSCAR",        // Ação desejada (BUSCAR, OBTER, EXECUTAR, etc.)
     "scope": "repositorio_git", // O tipo de recurso alvo
     "parameters": {             // Parâmetros específicos da ação/escopo
       "tipo": "jogo",
       "linguagem": "python"
       // ... outros filtros ou dados ...
     },
     "response_format": "protobuf" // Formato preferido da resposta (opcional)
   }
   ```

### 3.3. Ponto de Entrada Universal ProtoAi (PEUP)

Um componente opcional (mas poderoso) que pode ser implementado como um serviço web (HTTPS).

#### 3.3.1. Fluxo de Processamento de Intenções

**1. O PEUP Recebe a Intenção:**
- Recebe requisição HTTPS no endpoint `/intent`
- Parseia e valida a intenção PIS recebida
- Identifica a ação (ex: BUSCAR) e o escopo (ex: repositorio_git)

**2. Descoberta do Serviço:**
- Consulta o Registry Service para encontrar serviços compatíveis
- O Registry retorna a URL do manifesto (README.protobuf) do serviço relevante
- PEUP baixa e processa o README.protobuf do serviço encontrado

**3. Tradução e Execução:**
- Identifica o endpoint específico para a ação (ex: /search)
- Mapeia parâmetros PIS para parâmetros da API real (ex: tipo=jogo → tags=game)
- Executa a chamada HTTP para o endpoint do serviço alvo

**4. Processamento da Resposta:**
- Recebe a resposta do serviço alvo
- Formata conforme solicitado (ex: JSON ou Protobuf)
- Retorna ao cliente original

**Exemplo de Interação:** 
```
POST https://peup.protoai.org/intent
Content-Type: application/json

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

#### 3.3.2. Vantagens do PEUP via HTTPS

**1. Acessibilidade Universal**
- Compatível com qualquer cliente que suporte HTTPS
- Integração simplificada para navegadores, scripts e aplicações

**2. Ponto Único de Interação**
- Cliente precisa conhecer apenas a URL do PEUP
- Abstração da complexidade do ecossistema

**3. Encapsulamento da Lógica**
- Descoberta de serviços transparente
- Tradução automática de parâmetros
- Gerenciamento de formatos de resposta

**4. Segurança e Controle**
- Comunicação criptografada via HTTPS
- Camada centralizada de autenticação/autorização
- Monitoramento e controle de acesso

**5. Flexibilidade e Evolução**
- Suporte a novos formatos PIS sem mudança no cliente
- Atualizações transparentes do mecanismo de descoberta
- Extensibilidade via plugins

#### 3.3.3. Desafios de Implementação

**1. Centralização**
- PEUP como ponto único de falha
- Necessidade de alta disponibilidade
- Potencial gargalo de performance

**2. Complexidade Técnica**
- Interpretação precisa de intenções
- Mapeamento correto de parâmetros
- Gerenciamento de diferentes formatos

**3. Segurança e Confiança**
- Proteção contra uso malicioso
- Garantia de roteamento correto
- Preservação da privacidade dos dados

## 4. Benefícios e Casos de Uso

### 4.1. Para Desenvolvedores
- Documentação padronizada e legível por máquina
- Integração simplificada com outros serviços
- Flexibilidade na escolha do mecanismo de descoberta

### 4.2. Para Agentes de IA
- Descoberta automática de serviços
- Interpretação semântica das capacidades do serviço
- Interação padronizada através do PIS

### 4.3. Para Organizações
- Catálogo centralizado de serviços
- Governança e controle de acesso simplificados
- Padronização da documentação e interação

## 5. Considerações de Implementação

### 5.1. Segurança
- Autenticação e autorização em nível de serviço
- Validação de intenções no PEUP
- Proteção contra uso indevido

### 5.2. Escalabilidade
- Cache de manifestos
- Balanceamento de carga no PEUP
- Descoberta distribuída

### 5.3. Extensibilidade
- Suporte a novos formatos de intenção
- Plugins para o PEUP
- Extensões do manifesto

## 6. Próximos Passos

1. Implementação de referência do PEUP
2. Ferramentas de validação de manifestos
3. SDK para diferentes linguagens
4. Extensões para frameworks populares