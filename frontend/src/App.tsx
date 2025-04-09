import { useState } from 'react';
import { Box, Container, Grid, Paper, TextField, Typography, Button, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: 'calc(100vh - 100px)',
  overflow: 'auto',
  display: 'flex',
  flexDirection: 'column'
}));

interface SearchResult {
  project: {
    name: string;
    description: string;
    type: string;
    level: number;
    repository_url: string;
    featured: boolean;
  };
  relevance_score: number;
  highlighted_snippet: string;
  matching_features: string[];
}

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [peupRequest, setPeupRequest] = useState<any>(null);
  const [peupResponse, setPeupResponse] = useState<any>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // Criar requisição de busca
      const searchRequest = {
        query: query,
        required_tags: [],
        filter_by_type: [],
        minimum_level: 0,
        only_featured: false
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
    } catch (error) {
      console.error('Erro na busca:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3} sx={{ height: 'calc(100vh - 32px)' }}>
        {/* Coluna da Busca */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>Busca</Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Digite sua busca..."
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={isLoading}
              >
                {isLoading ? <CircularProgress size={24} /> : 'Buscar'}
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
                  <Typography variant="subtitle1">{result.project.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {result.highlighted_snippet}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Relevância: {result.relevance_score.toFixed(2)}
                  </Typography>
                  {result.matching_features.length > 0 && (
                    <Typography variant="caption" display="block">
                      Features: {result.matching_features.join(', ')}
                    </Typography>
                  )}
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