package intent_agent

import (
    "context"
    "encoding/json"
    "fmt"
    "github.com/google/generative-ai-go/genai"
    "google.golang.org/api/option"
)

type Intent struct {
    ProtoAIIntent  string     `json:"protoai_intent"`
    Action        string     `json:"action"`
    Scope         string     `json:"scope"`
    Parameters    Parameters `json:"parameters"`
    ResponseFormat string     `json:"response_format"`
}

type Parameters struct {
    Tipo      string `json:"tipo"`
    Linguagem string `json:"linguagem"`
    Interface string `json:"interface"`
}

func InterpretIntent(input string) (*Intent, error) {
    cfg, err := LoadConfig()
    if err != nil {
        return nil, fmt.Errorf("erro ao carregar configuração: %v", err)
    }

    ctx := context.Background()
    client, err := genai.NewClient(ctx, option.WithAPIKey(cfg.GeminiAPIKey))
    if err != nil {
        return nil, fmt.Errorf("erro ao criar cliente Gemini: %v", err)
    }
    defer client.Close()

    model := client.GenerativeModel("gemini-pro")
    prompt := fmt.Sprintf(`Analise a seguinte entrada do usuário e extraia a intenção estruturada:
"%s"

Retorne apenas um objeto JSON com a seguinte estrutura, sem explicações adicionais:
{
  "protoai_intent": "1.0",
  "action": "BUSCAR",
  "scope": "repositorio_git",
  "parameters": {
    "tipo": "[tipo do projeto]",
    "linguagem": "[linguagem de programação]",
    "interface": "[tipo de interface]"
  },
  "response_format": "json"
}`, input)

    resp, err := model.GenerateContent(ctx, genai.Text(prompt))
    if err != nil {
        return nil, fmt.Errorf("erro ao gerar conteúdo: %v", err)
    }

    if len(resp.Candidates) == 0 || len(resp.Candidates[0].Content.Parts) == 0 {
        return nil, fmt.Errorf("nenhuma resposta gerada")
    }

    jsonStr := resp.Candidates[0].Content.Parts[0].Text()
    var intent Intent
    if err := json.Unmarshal([]byte(jsonStr), &intent); err != nil {
        return nil, fmt.Errorf("erro ao decodificar resposta: %v", err)
    }

    return &intent, nil
}