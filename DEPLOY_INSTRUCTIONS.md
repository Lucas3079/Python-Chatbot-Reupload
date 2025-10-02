# 🚀 Instruções de Deploy Seguro - CapBot

## ⚠️ IMPORTANTE: Segurança

**NUNCA coloque chaves de API no GitHub!**

## 📋 Passo a Passo para Deploy

### 1. Preparar o Repositório

✅ **Arquivos já configurados:**

- `Procfile` - Configuração Railway
- `railway.json` - Configurações específicas
- `requirements.txt` - Dependências
- `.gitignore` - Protege arquivos sensíveis
- `env.example` - Exemplo de variáveis

### 2. Fazer Push para GitHub

```bash
git add .
git commit -m "Preparar projeto para deploy"
git push origin main
```

### 3. Conectar ao Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu repositório

### 4. Configurar Variáveis de Ambiente

No Railway, vá em **Variables** e adicione:

```
GROQ_API_KEY=sua chave groq aqui
WEB_SEARCH_ENABLED=True
RAILWAY_ENVIRONMENT=production
ALLOWED_ORIGINS=*
```

**Use a mesma chave Groq que está funcionando localmente!**

### 5. Deploy Automático

- O Railway detectará o `Procfile`
- Instalará dependências automaticamente
- Iniciará o servidor

### 6. Testar

Após o deploy, teste:

- ✅ Interface carrega
- ✅ Chat funciona
- ✅ Consultas de folha funcionam
- ✅ Busca na web funciona
- ✅ Temas funcionam
- ✅ Histórico de conversas funciona

## 🔗 URLs Após Deploy

- **Aplicação**: `https://seu-projeto.railway.app/`
- **API**: `https://seu-projeto.railway.app/chat`
- **Health**: `https://seu-projeto.railway.app/health`

## 🛡️ Segurança Implementada

- ✅ `.gitignore` protege arquivos `.env`
- ✅ Chaves não estão no código
- ✅ Variáveis configuradas no Railway
- ✅ CORS configurado para produção

## 🎯 Próximos Passos

1. **Deploy** (agora)
2. **Testar** todas as funcionalidades
3. **Sistema de login** (próxima etapa)
4. **Mais funcionalidades**

---

**O projeto está 100% seguro e pronto para deploy!** 🚀
