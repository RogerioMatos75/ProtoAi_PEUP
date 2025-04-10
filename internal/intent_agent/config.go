package intent_agent

import (
    "encoding/json"
    "os"
)

type Config struct {
    GeminiAPIKey string `json:"GEMINI_API_KEY"`
}

func LoadConfig() (Config, error) {
    var cfg Config
    file, err := os.Open("config.json")
    if err != nil {
        return cfg, err
    }
    defer file.Close()

    decoder := json.NewDecoder(file)
    err = decoder.Decode(&cfg)
    return cfg, err
}
