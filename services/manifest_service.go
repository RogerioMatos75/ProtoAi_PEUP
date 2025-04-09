package services

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	pb "peup/proto"
	"google.golang.org/protobuf/proto"
)

// ManifestService gerencia o cache e recuperação de manifestos
type ManifestService struct {
	mu    sync.RWMutex
	cache map[string]*CacheEntry
}

type CacheEntry struct {
	manifest   *pb.Manifest
	expiration time.Time
}

// NewManifestService cria uma nova instância do serviço de manifestos
func NewManifestService() *ManifestService {
	return &ManifestService{
		cache: make(map[string]*CacheEntry),
	}
}

// GetManifest recupera um manifesto do cache ou busca do registro
func (s *ManifestService) GetManifest(ctx context.Context, serviceID string) (*pb.Manifest, error) {
	// Tenta recuperar do cache primeiro
	s.mu.RLock()
	if entry, exists := s.cache[serviceID]; exists && time.Now().Before(entry.expiration) {
		s.mu.RUnlock()
		return entry.manifest, nil
	}
	s.mu.RUnlock()

	// Se não está no cache ou expirou, busca do registro
	manifest, err := s.fetchManifestFromRegistry(ctx, serviceID)
	if err != nil {
		// Tenta usar fallback se disponível
		return s.handleFallback(ctx, serviceID)
	}

	// Armazena no cache
	s.cacheManifest(serviceID, manifest)
	return manifest, nil
}

// fetchManifestFromRegistry busca o manifesto do serviço de registro
func (s *ManifestService) fetchManifestFromRegistry(ctx context.Context, serviceID string) (*pb.Manifest, error) {
	// TODO: Implementar a lógica real de busca no registro
	// Por enquanto, retorna um manifesto de exemplo
	manifest := &pb.Manifest{
		ServiceId: serviceID,
		Version:   "1.0",
		Endpoint: &pb.ServiceEndpoint{
			Url:      "http://localhost:8081",
			Protocol: "http",
			TimeoutMs: 5000,
		},
		Metadata: &pb.ServiceMetadata{
			Name:           "ExemploServico",
			CacheTtlSeconds: 3600,
		},
	}

	return manifest, nil
}

// handleFallback tenta usar um serviço de fallback
func (s *ManifestService) handleFallback(ctx context.Context, serviceID string) (*pb.Manifest, error) {
	// TODO: Implementar lógica de fallback
	log.Printf("Tentando fallback para serviço: %s", serviceID)
	return nil, fmt.Errorf("serviço não disponível e nenhum fallback configurado")
}

// cacheManifest armazena um manifesto no cache
func (s *ManifestService) cacheManifest(serviceID string, manifest *pb.Manifest) {
	ttl := time.Duration(manifest.Metadata.CacheTtlSeconds) * time.Second
	if ttl == 0 {
		ttl = time.Hour // TTL padrão
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	s.cache[serviceID] = &CacheEntry{
		manifest:   manifest,
		expiration: time.Now().Add(ttl),
	}
}