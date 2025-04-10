import { useState } from 'react';
import { Box, Container, Grid, Paper, TextField, Typography, Button, CircularProgress, List, ListItem, ListItemText } from '@mui/material';
import { styled } from '@mui/material/styles';
import { IntentRequest, IntentResponse } from './types/proto';
import { Project, ProjectSearchResult } from './types/project';

interface Message {
  text: string;
  type: 'user' | 'bot';
  response?: IntentResponse | null;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: 'calc(100vh - 100px)',
  overflow: 'auto',
  display: 'flex',
  flexDirection: 'column'
}));

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [searchResults, setSearchResults] = useState<ProjectSearchResult[]>([]);
  const [peupRequest, setPeupRequest] = useState<IntentRequest | null>(null);
  const [peupResponse, setPeupResponse] = useState<IntentResponse | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // Adicionar mensagem do usuário
      const userMessage: Message = {
        text: query,
        type: 'user'
      };
      setMessages(prev => [...prev, userMessage]);

      // Criar requisição de busca usando o formato do protobuf
      const searchRequest: IntentRequest = {
        version: "1.0",
        action: "BUSCAR",
        scope: "projeto",
        parameters: { query: query },
        response_format: "json",
        auth_info: { token: "test_token" }
      };

      // Enviar para o endpoint de busca
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchRequest)
      });

      const data = await response.json();
      setSearchResults(data.results);
      setPeupRequest(searchRequest);
      setPeupResponse(data);

      // Adicionar resposta do bot
      const botMessage: Message = {
        text: 'Aqui está o resultado da sua busca:',
        type: 'bot',
        response: data
      };
      setMessages(prev => [...prev, botMessage]);
      setQuery('');
    } catch (error) {
      console.error('Erro na busca:', error);
      // Adicionar mensagem de erro
      const errorMessage: Message = {
        text: 'Desculpe, ocorreu um erro ao processar sua solicitação.',
        type: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3} sx={{ height: 'calc(100vh - 32px)' }}>
        {/* Coluna do Chat */}
        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>Chat ProtoAI</Typography>
            <List sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
              {messages.map((message, index) => (
                <ListItem key={index} sx={{
                  justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1
                }}>
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor: message.type === 'user' ? 'primary.light' : 'grey.100',
                      color: message.type === 'user' ? 'white' : 'text.primary'
                    }}
                  >
                    <ListItemText primary={message.text} />
                    {message.response && (
                      <Box sx={{ mt: 1, fontSize: '0.8em' }}>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                          {JSON.stringify(message.response, null, 2)}
                        </pre>
                      </Box>
                    )}
                  </Paper>
                </ListItem>
              ))}
            </List>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Digite sua mensagem..."
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={isLoading}
              >
                {isLoading ? <CircularProgress size={24} /> : 'Enviar'}
              </Button>
            </Box>
          </StyledPaper>
        </Grid>

        {/* Coluna da Requisição PEUP */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>Requisição PEUP</Typography>
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
              {peupRequest && (
                <pre style={{ margin: 0 }}>
                  {JSON.stringify(peupRequest, null, 2)}
                </pre>
              )}
            </Box>
          </StyledPaper>
        </Grid>

        {/* Coluna da Resposta */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>Resposta ProtoAI MCP</Typography>
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
              {searchResults.map((result, index) => (
                <Box key={index} sx={{ mb: 2, p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
                  <Typography variant="subtitle1">{result.project.nome}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {result.project.descricao}
                  </Typography>
                  {result.project.imagens.length > 0 && (
                    <Box sx={{ mt: 1, display: 'flex', gap: 1, overflow: 'auto' }}>
                      {result.project.imagens.map((img, imgIndex) => (
                        <img 
                          key={imgIndex} 
                          src={img} 
                          alt={`${result.project.nome} - Imagem ${imgIndex + 1}`}
                          style={{ width: 100, height: 100, objectFit: 'cover', borderRadius: 4 }}
                        />
                      ))}
                    </Box>
                  )}
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" display="block">
                      Tipo: {result.project.tipo}
                    </Typography>
                    <Typography variant="caption" display="block">
                      Nível: {result.project.nivel}
                    </Typography>
                    <Typography variant="caption" display="block">
                      Relevância: {result.relevance_score.toFixed(2)}
                    </Typography>
                    {result.project.destaque && (
                      <Typography variant="caption" display="block" sx={{ color: 'primary.main' }}>
                        Projeto em Destaque
                      </Typography>
                    )}
                  </Box>
                </Box>
              ))}

            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;