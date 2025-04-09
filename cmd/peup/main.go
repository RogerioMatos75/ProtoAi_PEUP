package main

import (
	"context"
	"log"
	"net/http"
	"encoding/json"
	"github.com/gin-gonic/gin"
	"github.com/gin-contrib/cors"
	pb "peup/proto"
	"peup/services"
)

type ProtoAiIntent struct {
	ProtoAiIntent  string                 `json:"protoai_intent"`
	Action         string                 `json:"action"`
	Scope          string                 `json:"scope"`
	Parameters     map[string]interface{} `json:"parameters"`
	ResponseFormat string                 `json:"response_format"`
	Query          *string                `json:"query,omitempty"`
}

func main() {
	// Inicializar serviços
	manifestService := services.NewManifestService()

	// Configurar Gin
	r := gin.Default()

	// Configurar CORS
	r.Use(cors.New(cors.Config{
		AllowOrigins: []string{"http://localhost:5173", "http://127.0.0.1:5173"},
		AllowMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders: []string{"Origin", "Content-Type"},
		AllowCredentials: true,
	}))

	// Endpoints
	r.POST("/intent", func(c *gin.Context) {
		var query string
		if err := c.BindJSON(&query); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// TODO: Integrar com o serviço de intenções em Rust
		// Por enquanto, retornar uma resposta padrão
		c.JSON(http.StatusOK, gin.H{
			"action": "BUSCAR",
			"parameters": map[string]interface{}{},
		})
	})

	r.POST("/peup", func(c *gin.Context) {
		var intent ProtoAiIntent
		if err := c.BindJSON(&intent); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Processar query em linguagem natural se presente
		if intent.Query != nil {
			// TODO: Integrar com o serviço de intenções em Rust
			// Por enquanto, manter a ação original
		}

		// Buscar manifesto
		manifest, err := manifestService.GetManifest(context.Background(), intent.Scope)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Manifesto não encontrado"})
			return
		}

		// Retornar no formato solicitado
		if intent.ResponseFormat == "protobuf" {
			data, err := manifest.Marshal()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			c.Data(http.StatusOK, "application/x-protobuf", data)
			return
		}

		// Converter para JSON por padrão
		c.JSON(http.StatusOK, manifest)
	})

	// Iniciar servidor
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Falha ao iniciar servidor: %v", err)
	}
}