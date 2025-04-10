export interface Project {
  id: number;
  nome: string;
  descricao: string;
  tipo: string;
  imagens: string[];
  nivel: number;
  repositorio: string;
  destaque: boolean;
}

export interface ProjectSearchResult {
  project: Project;
  relevance_score: number;
  highlighted_snippet?: string;
}