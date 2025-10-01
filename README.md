# CapBot - Chatbot de Análise Financeira

Um chatbot inteligente com RAG (Retrieval-Augmented Generation) para consultas de folha de pagamento, desenvolvido para o processo seletivo da Capgemini.

## Sobre

O **CapBot** é uma aplicação de IA conversacional que combina:
- **Conversação geral** com LLMs (OpenAI/Groq)
- **Consultas específicas** de folha de pagamento via RAG
- **Busca na web** para informações externas
- **Interface moderna** estilo ChatGPT

## Tecnologias

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **IA:** OpenAI API, Groq API, RAG com embeddings
- **Dados:** Pandas, CSV
- **Deploy:** Railway, Docker

## Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd chatbot-rag-folha-pagamento
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração (Opcional)
O projeto funciona **imediatamente** em modo demo sem configuração!

**Para usar LLMs reais:**
```bash
cp env.example .env
# Edite o .env com suas chaves de API
```

## Como Usar

### Opção 1: Início Rápido (Recomendado)

**Terminal 1 - API:**
```bash
python main.py
```

**Terminal 2 - Frontend:**
```bash
python -m http.server 3000 --directory frontend
```

**Acesse:** http://localhost:3000

### Opção 2: Acesso Direto (Mais Simples)

```bash
python main.py
```

**Acesse:** http://localhost:8000

### Opção 3: Script Automático (Windows)

```bash
start_servers.bat
```

## Funcionalidades

### Consultas de Folha de Pagamento
- Salários líquidos por funcionário e período
- Descontos (INSS, IRRF)
- Bônus e benefícios
- Datas de pagamento
- Análises comparativas

### Recursos Extras
- Interface moderna com 4 temas
- Histórico de conversas
- Sidebar colapsível
- Busca na web
- Modo demo (sem API keys)

## Exemplos de Uso

```
"Quanto recebi de salário líquido em maio de 2025? (Ana Souza)"
"Qual foi o total líquido pago no primeiro trimestre de 2025?"
"Quem recebeu o maior bônus em 2025?"
"Qual a taxa Selic atual?"
```

## API Endpoints

- `POST /chat` - Enviar mensagem
- `GET /health` - Status da API
- `GET /docs` - Documentação Swagger

## Estrutura do Projeto

```
├── app/                    # Backend FastAPI
│   ├── api.py             # Endpoints principais
│   ├── config.py          # Configurações
│   ├── llm_service.py     # Integração com LLMs
│   ├── rag_system.py      # Sistema RAG
│   └── ...
├── frontend/              # Interface HTML/CSS/JS
│   ├── index.html         # Página principal
│   ├── style.css          # Estilos
│   └── script.js          # Lógica frontend
├── data/                  # Dados
│   └── payroll.csv        # Dataset de folha
└── requirements.txt       # Dependências
```

## Configuração de API Keys

Crie um arquivo `.env` com pelo menos uma chave:

```env
# OpenAI (pago)
OPENAI_API_KEY=sua_chave_openai

# Groq (gratuito)
GROQ_API_KEY=sua_chave_groq

# Configurações opcionais
WEB_SEARCH_ENABLED=True
DEBUG=True
```

**Nota:** Sem chaves, o sistema funciona em modo demo com respostas simuladas.

## Deploy

### Railway (Recomendado)
1. Conecte o repositório ao Railway
2. Configure as variáveis de ambiente
3. Deploy automático

### Docker
```bash
docker build -t capbot .
docker run -p 8000:8000 capbot
```

## Testes

```bash
# Testar API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como você está?"}'

# Testar saúde da API
curl http://localhost:8000/health
```

## Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto foi desenvolvido para o processo seletivo da Capgemini.

## Autor

Desenvolvido para o processo seletivo da Capgemini - 2025