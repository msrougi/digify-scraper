# Digify Scraper — Deploy no Railway

## 1. Suba para o GitHub

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/SEU_USUARIO/digify-scraper.git
git push -u origin main
```

## 2. Deploy no Railway

1. Acesse https://railway.app e entre com GitHub
2. **New Project → Deploy from GitHub repo** → selecione o repositório
3. Railway detecta Python automaticamente e faz o deploy
4. Vá em **Settings → Networking → Generate Domain**
5. Você recebe uma URL ex: `https://digify-scraper.up.railway.app`

## 3. Domínio personalizado

Ainda em **Settings → Networking → Custom Domain**:
- Adicione `imagescrapper.digify.live`
- No painel do seu DNS, crie um CNAME apontando para a URL do Railway

Pronto — seu site estará em `https://imagescrapper.digify.live`

## Endpoints

- `GET /` — frontend (HTML)
- `GET /health` — status do servidor
- `GET /scrape?url=...&depth=2&delay=0.3&same_domain=true` — scraping via SSE
- `GET /download?url=...` — download de imagem individual
