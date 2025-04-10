package intent_agent

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
)

const GeminiURL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

type GeminiResponse struct {
    Candidates []struct {
        Content struct {
            Parts []struct {
                Text string `json:"text"`
            } `json:"parts"`
        } `json:"content"`
    } `json:"candidates"`
}

// Recebe um texto do usuário e retorna uma intenção ProtoAi estruturada
func InterpretIntent(userInput string) (map[string]interface{}, error) {
    cfg, err := LoadConfig()
    if err != nil {
        return nil, err
    }

    prompt := fmt.Sprintf(`Converta esta solicitação em uma intenção ProtoAi (PIS) no formato JSON:
"%s"
Apenas retorne o JSON.`, userInput)

    body := map[string]interface{}{
        "contents": []map[string]interface{}{
            {
                "parts": []map[string]string{
                    {"text": prompt},
                },
            },
        },
    }

    bodyBytes, _ := json.Marshal(body)

    req, _ := http.NewRequest("POST", GeminiURL+"?key="+cfg.GeminiAPIKey, bytes.NewBuffer(bodyBytes))
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    res, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer res.Body.Close()

    resBody, _ := ioutil.ReadAll(res.Body)

    var gemResp GeminiResponse
    json.Unmarshal(resBody, &gemResp)

    if len(gemResp.Candidates) == 0 {
        return nil, fmt.Errorf("nenhuma resposta gerada")
    }

    // Parse do JSON da resposta gerada (o modelo retorna texto do JSON)
    var intent map[string]interface{}
    err = json.Unmarshal([]byte(gemResp.Candidates[0].Content.Parts[0].Text), &intent)
    if err != nil {
        return nil, err
    }

    return intent, nil
}
