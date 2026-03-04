# Termux + Vertex + GitHub (branch twitter)

## 1) Preparar no Android (Termux)

No Termux, dentro do projeto:

```bash
chmod +x scripts/termux-setup.sh scripts/start-vertex.sh
./scripts/termux-setup.sh
```

## 2) Configurar Vertex no Termux

```bash
export LLM_PROVIDER=vertex
export VERTEX_AUTH_MODE=env
export VERTEX_PROJECT_ID=seu-projeto-gcp
export VERTEX_LOCATION=us-central1
export VERTEX_MODEL=gemini-1.5-flash
export VERTEX_ACCESS_TOKEN=seu-token
```

Iniciar:

```bash
./scripts/start-vertex.sh
```

## 3) Subir para GitHub no branch twitter

Se a pasta ainda não for git:

```bash
git init
git add .
git commit -m "feat: vertex advanced + termux support"
```

Configurar remote:

```bash
git remote add origin git@github.com:<SEU_USUARIO>/cerebro-central.git
```

Criar e subir branch:

```bash
git checkout -b twitter
git push -u origin twitter
```

Se já existir git e branch local:

```bash
git checkout -B twitter
git add .
git commit -m "feat: vertex advanced + termux support"
git push -u origin twitter
```
