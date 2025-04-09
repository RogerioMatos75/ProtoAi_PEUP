use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use log::{info, error};

#[derive(Debug, Serialize, Deserialize)]
pub struct Intent {
    pub action: String,
    pub scope: String,
    pub parameters: HashMap<String, serde_json::Value>,
    pub response_format: String,
    pub query: Option<String>,
}

#[derive(Debug)]
pub struct IntentParser {
    model: Option<transformers::Pipeline>,
}

impl IntentParser {
    pub fn new() -> Self {
        Self { model: None }
    }

    fn ensure_model_loaded(&mut self) {
        if self.model.is_none() {
            info!("Carregando modelo de NLP...");
            self.model = Some(transformers::Pipeline::new(
                transformers::ModelType::TextClassification,
                "bert-base-multilingual-uncased",
                None,
            ));
        }
    }

    pub async fn parse_intent(&mut self, query: &str) -> Result<(String, HashMap<String, serde_json::Value>), Box<dyn std::error::Error>> {
        self.ensure_model_loaded();

        let action_mapping: HashMap<&str, &str> = [
            ("search", "BUSCAR"),
            ("create", "CRIAR"),
            ("update", "ATUALIZAR"),
            ("delete", "DELETAR"),
        ].iter().cloned().collect();

        // Processar a query usando o modelo
        let model = self.model.as_ref().unwrap();
        let results = model.predict(&[query]);
        
        // Extrair a ação mais provável
        let top_result = &results[0];
        let action = action_mapping
            .get(top_result.label.as_str())
            .unwrap_or(&"BUSCAR")
            .to_string();

        // Extrair parâmetros
        let params = self.extract_parameters(query);

        info!("Intent parseada: {} com parâmetros {:?}", action, params);
        Ok((action, params))
    }

    fn extract_parameters(&self, query: &str) -> HashMap<String, serde_json::Value> {
        let mut params = HashMap::new();
        let query_lower = query.to_lowercase();

        // Detectar tipo de projeto
        let type_keywords: HashMap<&str, Vec<&str>> = [
            ("web", vec!["web", "website", "site"]),
            ("mobile", vec!["mobile", "app", "android", "ios"]),
            ("jogo", vec!["jogo", "game", "gaming"]),
        ].iter().cloned().collect();

        for (type_name, keywords) in type_keywords.iter() {
            if keywords.iter().any(|&k| query_lower.contains(k)) {
                params.insert("tipo".to_string(), serde_json::Value::String(type_name.to_string()));
                break;
            }
        }

        // Detectar nível
        if query_lower.contains("nível") || query_lower.contains("level") {
            if let Some(level) = query_lower
                .split_whitespace()
                .skip_while(|&w| w != "nível" && w != "level")
                .nth(1)
                .and_then(|n| n.parse::<i64>().ok())
            {
                params.insert("level".to_string(), serde_json::Value::Number(level.into()));
            }
        }

        // Detectar destaques
        if query_lower.contains("destaque") || query_lower.contains("featured") {
            params.insert("only_featured".to_string(), serde_json::Value::Bool(true));
        }

        params
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_parse_intent() {
        let mut parser = IntentParser::new();
        let result = parser.parse_intent("buscar projetos web em destaque").await;
        assert!(result.is_ok());
        
        let (action, params) = result.unwrap();
        assert_eq!(action, "BUSCAR");
        assert!(params.contains_key("tipo"));
        assert!(params.contains_key("only_featured"));
    }
}