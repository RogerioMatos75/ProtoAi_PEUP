package server

import (
	"context"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"
	pb "peup/proto"
)

type PEUPServer struct {
	pb.UnimplementedPEUPServiceServer
}

// ProcessIntent implementa a interface do serviço PEUP
func (s *PEUPServer) ProcessIntent(ctx context.Context, req *pb.IntentRequest) (*pb.IntentResponse, error) {
	log.Printf("[PEUP] Intenção recebida: %s -> %s (%v)", req.Action, req.Scope, req.Parameters)

	// TODO: Implementar lógica de descoberta de serviço e processamento do manifesto
	// Por enquanto, retornamos uma resposta simulada
	response := &pb.IntentResponse{
		Status:  "success",
		Message: fmt.Sprintf("Intenção '%s' aplicada no escopo '%s' com sucesso.", req.Action, req.Scope),
	}

	return response, nil
}

// StartServer inicia o servidor gRPC do PEUP
func StartServer(port string) error {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		return fmt.Errorf("falha ao iniciar listener: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterPEUPServiceServer(s, &PEUPServer{})

	log.Printf("Servidor PEUP iniciado na porta %s", port)
	return s.Serve(lis)
}