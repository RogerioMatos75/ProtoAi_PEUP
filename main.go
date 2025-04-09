package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	pb "peup/proto"
	"peup/server"
)

// Cache de manifestos
type ManifestCache struct {
	mu    sync.RWMutex
	items map[string]CacheItem
}

type CacheItem struct {
	manifest   []byte
	expiration time.Time
}

var (
	manifestCache = &ManifestCache{
		items: make(map[string]CacheItem),
	}
)

// Estrutura da Intenção (PIS)
type IntentRequest struct {
	ProtoAiIntent string            `json:"protoai_intent"`
	Action        string            `json:"action"`
	Scope         string            `json:"scope"`
	Parameters    map[string]string `json:"parameters"`
	ResponseFormat string           `json:"response_format"`
}

// Estrutura da Resposta
type IntentResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
	Result  any    `json:"result,omitempty"`
}

// Converte IntentRequest HTTP para Protocol Buffer
func convertToProtoIntent(req *IntentRequest) *pb.IntentRequest {
	return &pb.IntentRequest{
		ProtoaiIntent:  req.ProtoAiIntent,
		Action:         req.Action,
		Scope:          req.Scope,
		Parameters:     req.Parameters,
		ResponseFormat: req.ResponseFormat,
	}
}

// Manipulador HTTP para intenções
func handleIntent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Método não permitido", http.StatusMethodNotAllowed)
		return
	}

	var intent IntentRequest
	err := json.NewDecoder(r.Body).Decode(&intent)
	if err != nil {
		http.Error(w, "JSON inválido", http.StatusBadRequest)
		return
	}

	log.Printf("[PEUP] Intenção recebida: %s -> %s (%v)", intent.Action, intent.Scope, intent.Parameters)

	// Converte para Protocol Buffer e processa
	protoIntent := convertToProtoIntent(&intent)
	ctx := context.Background()

	// TODO: Implementar chamada ao servidor gRPC
	// Por enquanto, retornamos uma resposta simulada
	resposta := IntentResponse{
		Status:  "success",
		Message: fmt.Sprintf("Intenção '%s' aplicada no escopo '%s' com sucesso.", intent.Action, intent.Scope),
		Result: map[string]string{
			"endpoint": "/api/search",
			"access":   "granted",
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resposta)
}

func main() {
	// Inicia o servidor gRPC em uma goroutine separada
	go func() {
		if err := server.StartServer("50051"); err != nil {
			log.Fatalf("Falha ao iniciar servidor gRPC: %v", err)
		}
	}()

	// Configura rotas HTTP
	http.HandleFunc("/intent", handleIntent)

	// Inicia servidor HTTP
	fmt.Println("PEUP Server iniciado em http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}