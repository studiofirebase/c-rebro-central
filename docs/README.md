# italosantos.com - Documentação Completa

## 📚 Índice

1. [Visão Geral](#visão-geral)
2. [🆕 Sistema Multi-Admin com ProfileSettings Isolado](#-sistema-multi-admin-com-profilesettings-isolado)
3. [Sistema de Registro de Administradores](#sistema-de-registro-de-administradores)
4. [Facebook OpenAPI - WhatsApp Business](#facebook-openapi---whatsapp-business)
5. [Solução de Problemas da Câmera](#solução-de-problemas-da-câmera)
6. [Guia Rápido de Início](#guia-rápido-de-início)
7. [Configuração e Deploy](#configuração-e-deploy)

---

## Visão Geral

Plataforma completa com:
- Sistema de autenticação facial (Face ID)
- Painel administrativo
- Integrações sociais (Twitter, Instagram, Facebook)
- Sistema de assinaturas
- Pagamentos (PayPal, Stripe, Mercado Pago)
- WhatsApp Business API (via OpenAPI)

---

## 🆕 Sistema Multi-Admin com ProfileSettings Isolado

### 📋 Descrição

Cada administrador do sistema possui seu próprio **ProfileSettings completamente isolado**, permitindo que múltiplos criadores/vendedores (ex: pedro, lucas, italo) tenham suas próprias configurações sem compartilhar dados.

### 🌟 SuperAdmin - Italo Santos (Perfil Global Principal)

**O SuperAdmin controla a página inicial (`/`) sem precisar de UID**:

```
italosantos.com/                 ← ⭐ Perfil Global (SuperAdmin)
├── admin/profileSettings         ← Dados globais (SEM UID)
├── Usuário: Italo Santos
├── Username: severepics
├── Email: pix@italosantos.com
└── isMainAdmin: true

italosantos.com/pedro            ← Admin individual
├── admins/{uid_pedro}/profile/settings ← Dados isolados de Pedro
│
italosantos.com/lucas            ← Admin individual
├── admins/{uid_lucas}/profile/settings ← Dados isolados de Lucas
│
italosantos.com/maria            ← Admin individual
└── admins/{uid_maria}/profile/settings ← Dados isolados de Maria
```

**Privilégios do SuperAdmin**:
- ✅ Controla a homepage (`/`)
- ✅ Acessa painel via `/admin` (sem slug)
- ✅ Dados em `admin/profileSettings` (global)
- ✅ Pode gerenciar outros admins
- ✅ Não precisa de UID para ser acessado

**Diferenças vs Regular Admin**:
| | SuperAdmin | Regular Admin |
|---|------------|---------------|
| URL | `/` e `/admin` | `/{username}` |
| Dados | `admin/profileSettings` | `admins/{uid}/profile/settings` |
| Gerenciar outros | ✅ Sim | ❌ Não |

### 📚 Documentação

Para entender completamente a arquitetura de isolamento:

1. **[SUPERADMIN_GLOBAL_PROFILE_SETUP.md](./docs/SUPERADMIN_GLOBAL_PROFILE_SETUP.md)** ⭐ **PERFIL GLOBAL**
   - Configuração do SuperAdmin (Italo Santos)
   - Como funciona o perfil global
   - Scripts de setup e verificação
   - Diferenças entre SuperAdmin e Regular Admin

2. **[PROFILE_SETTINGS_EXECUTIVE_SUMMARY.md](./docs/PROFILE_SETTINGS_EXECUTIVE_SUMMARY.md)** 📌 **COMECE AQUI**
   - Resumo executivo (5 min)
   - O que foi implementado
   - Fluxos principais
   - Exemplos de uso

3. **[PROFILE_SETTINGS_ISOLATION_ARCHITECTURE.md](./docs/PROFILE_SETTINGS_ISOLATION_ARCHITECTURE.md)** 🏗️ **ARQUITETURA DETALHADA**
   - Análise completa de isolamento
   - Matriz de funcionalidades
   - Exemplo de código para cada cenário
   - Validações de segurança
   - Retrocompatibilidade

4. **[PROFILE_SETTINGS_SECURITY_TESTS.md](./docs/PROFILE_SETTINGS_SECURITY_TESTS.md)** 🔒 **TESTES DE SEGURANÇA**
   - 8 testes de isolamento
   - Cenários de erro
   - Checklist de validação
   - Comandos úteis

### ✨ Funcionalidades

- ✅ Cada admin tem perfil isolado (`admins/{uid}/profile/settings`)
- ✅ Admin global preservado para compatibilidade (`admin/profileSettings`)
- ✅ URLs públicas individuais (`italosantos.com/username`)
- ✅ API protegida com autenticação JWT
- ✅ Firestore rules validam acesso por UID
- ✅ Cache isolado por admin (5 min TTL)
- ✅ Main admin pode gerenciar outros admins
- ✅ Dados sensíveis removidos para público

### 🚀 Uso Rápido

#### Admin Editar Seu Perfil
```typescript
const { user } = useAuth();
const settings = { name: 'Novo Nome', ... };

const response = await fetch('/api/admin/profile-settings', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${await user.getIdToken()}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    settings,
    adminUid: user.uid  // ← Sempre seu próprio uid
  })
});
```

#### Carregar Perfil Público
```typescript
// Hook detecta username na URL e carrega automaticamente
const { settings } = useProfileSettings();
// Exemplo: em /pedro, carrega de admins/{pedro_uid}/profile/settings
```

#### Main Admin Editar Outro Admin
```typescript
const targetAdminUid = 'abc123';
// POST com targetAdminUid
// API valida isMainAdmin == true
// Salva em: admins/{abc123}/profile/settings
```

### 🔐 Segurança

| Camada | Proteção |
|---|---|
| **Firestore Rules** | Apenas admin autenticado acessa seu `admins/{uid}/*` |
| **API Authentication** | Requer Bearer token JWT |
| **Ownership Validation** | Admin A não consegue salvar Admin B |
| **Main Admin Powers** | Apenas main admin pode gerenciar outros |
| **Secrets Removal** | Dados públicos não contêm PayPal/Mercado Pago secrets |

---

## Sistema de Registro de Administradores

### Arquitetura

#### Componentes Principais

1. **Frontend**
   - `src/components/admin/admin-registration-wizard.tsx` - Wizard de 4 etapas
   - `src/components/auth/face-id-register.tsx` - Captura facial
   
2. **Backend APIs**
   - `src/app/api/admin/auth/start-registration/route.ts` - Inicia processo
   - `src/app/api/admin/auth/complete-registration/route.ts` - Finaliza cadastro
   - `src/app/api/production/admin/auth/send-email-code/route.ts` - Envia código email
   - `src/app/api/production/admin/auth/send-sms-code/route.ts` - Envia código SMS

#### Fluxo de Registro

```
1. Usuário informa código de convite
   ↓
2. Sistema valida código e inicia registro pendente
   ↓
3. Captura facial + dados pessoais
```
   ↓
4. Verificação 2FA (Email + SMS)
   ↓
5. Admin criado no Firestore + Auditoria
```

#### Firestore Collections

**`pending_admin_registrations`**
```json
{
  "email": "admin@example.com",
  "name": "João Silva",
  "phone": "+5511999999999",
  "faceDescriptor": [0.123, 0.456, ...],
  "createdAt": "2025-01-01T10:00:00Z",
  "expiresAt": "2025-01-01T10:30:00Z"
}
```

**`verification_codes`**
```json
{
  "email": "admin@example.com",
  "code": "123456",
  "type": "email" | "sms",
  "expiresAt": "2025-01-01T10:10:00Z",
  "attempts": 0
}
```

**`admins`**
```json
{
  "email": "admin@example.com",
  "name": "João Silva",
  "phone": "+5511999999999",
  "faceDescriptor": [0.123, 0.456, ...],
  "createdAt": "2025-01-01T10:00:00Z",
  "isActive": true
}
```

**`admin_audit_log`**
```json
{
  "action": "admin_registered",
  "adminEmail": "admin@example.com",
  "timestamp": "2025-01-01T10:00:00Z",
  "metadata": {}
}
```

### Configuração

#### Variáveis de Ambiente (`.env.local`)

```bash
# Firebase Admin
FIREBASE_PROJECT_ID=seu-projeto
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@seu-projeto.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# Admin Registration
ADMIN_INVITATION_CODE=seu_codigo_secreto

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@seudominio.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+15555555555

# Face API
FACE_API_MODEL_URL=/models
```

#### Setup

```bash
# 1. Copiar variáveis de ambiente
cp .env.admin-auth.example .env.local

# 2. Preencher credenciais no .env.local

# 3. Executar script de setup
node scripts/setup-admin-registration.js

# 4. Iniciar desenvolvimento
npm run dev
```

### Segurança

1. **Código de Convite**
   - Obrigatório para iniciar registro
   - Configurável via `ADMIN_INVITATION_CODE`
   - Nunca exposto no frontend

2. **Autenticação Facial**
   - Face descriptor armazenado no Firestore
   - Usado para login posterior
   - Validação via face-api.js

3. **Verificação 2FA**
   - Email: código de 6 dígitos (válido por 10 min)
   - SMS: código de 6 dígitos (válido por 10 min)
   - Máximo 3 tentativas por código

4. **Expiração**
   - Registros pendentes: 30 minutos
   - Códigos de verificação: 10 minutos
   - Limpeza automática de expirados

5. **Auditoria**
   - Todos os registros são logados
   - Timestamp e metadata completos
   - Rastreamento de ações administrativas

### Deploy em Produção

#### 1. Configurar Serviços de Email/SMS

**SendGrid (Email)**
```bash
# 1. Criar conta em sendgrid.com
# 2. Criar API Key
# 3. Verificar domínio de email
# 4. Adicionar ao .env.local:
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@seudominio.com
```

**Twilio (SMS)**
```bash
# 1. Criar conta em twilio.com
# 2. Obter Account SID e Auth Token
# 3. Comprar número de telefone
# 4. Adicionar ao .env.local:
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1555555555
```

#### 2. Configurar Firebase

```bash
# 1. Baixar Service Account Key do Firebase Console
# 2. Extrair credenciais para .env.local
# 3. Criar índices no Firestore:
```

**Índices necessários:**
- `pending_admin_registrations`: email (ASC), expiresAt (ASC)
- `verification_codes`: email (ASC), type (ASC), expiresAt (ASC)
- `admin_audit_log`: timestamp (DESC)

#### 3. Deploy

```bash
# Build
npm run build

# Deploy Firebase
firebase deploy

# Ou Docker
docker build -t italosantos-com .
docker run -p 3000:3000 italosantos-com
```

#### 4. Pós-Deploy

- [ ] Testar registro de admin end-to-end
- [ ] Verificar envio de emails
- [ ] Verificar envio de SMS
- [ ] Testar autenticação facial
- [ ] Monitorar logs de auditoria

### Troubleshooting

#### Erro: "Código de convite inválido"
- Verificar `ADMIN_INVITATION_CODE` no `.env.local`
- Garantir que não há espaços extras
- Reiniciar servidor após alterar

#### Erro: "Falha ao enviar email"
- Verificar `SENDGRID_API_KEY` válida
- Confirmar domínio verificado no SendGrid
- Checar logs do SendGrid para detalhes

#### Erro: "Falha ao enviar SMS"
- Verificar credenciais Twilio
- Confirmar número de telefone válido
- Checar saldo da conta Twilio

#### Erro: "Código expirado"
- Códigos válidos por 10 minutos
- Solicitar novo código
- Verificar timezone do servidor

#### Erro: "Face não detectada"
- Melhorar iluminação
- Posicionar rosto centralizado
- Aguardar modelos carregarem
- Verificar permissões da câmera

---

## Facebook OpenAPI - WhatsApp Business

### Visão Geral

Este projeto integra as especificações OpenAPI oficiais da Meta para a **WhatsApp Business API**. As especificações estão disponíveis no diretório `/openapi/` e permitem:

- 📱 Enviar mensagens de texto, mídia e templates via WhatsApp
- 💬 Receber mensagens de clientes
- 🔔 Configurar webhooks para notificações em tempo real
- 📊 Obter métricas e analytics
- 📝 Gerenciar templates de mensagens

### Arquivos Disponíveis

```
openapi/
├── business-messaging-api_v23.0.yaml  # Especificação OpenAPI completa
├── LICENSE                             # Licença MIT
├── README.md                           # README original do repositório
└── INTEGRACAO_FACEBOOK_API.md         # Documentação completa em português
```

### Início Rápido

#### 1. Configurar Credenciais

Adicione no `.env.local`:

```bash
# WhatsApp Business API
WHATSAPP_BUSINESS_ACCOUNT_ID=seu_account_id
WHATSAPP_PHONE_NUMBER_ID=seu_phone_number_id
WHATSAPP_ACCESS_TOKEN=seu_access_token
WHATSAPP_API_VERSION=v23.0
WHATSAPP_QR_PREFILLED_MESSAGE="Olá! Gostaria de mais informações."
WHATSAPP_VERIFY_TOKEN=seu_verify_token_personalizado
```

#### 2. Exemplo: Enviar Mensagem

```typescript
// src/services/whatsapp-service.ts
import axios from 'axios';

export async function sendWhatsAppMessage(to: string, message: string) {
  const WHATSAPP_API_URL = 'https://graph.facebook.com/v23.0';
  const PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
  const ACCESS_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN;

  const response = await axios.post(
    `${WHATSAPP_API_URL}/${PHONE_NUMBER_ID}/messages`,
    {
      messaging_product: 'whatsapp',
      to: to,
      type: 'text',
      text: { body: message }
    },
    {
      headers: {
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return response.data;
}
```

#### 3. Configurar Webhook (Opcional)

Crie o endpoint para receber mensagens:

```typescript
// src/app/api/webhooks/whatsapp/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const mode = searchParams.get('hub.mode');
  const token = searchParams.get('hub.verify_token');
  const challenge = searchParams.get('hub.challenge');

  if (mode === 'subscribe' && token === process.env.WHATSAPP_VERIFY_TOKEN) {
    return new NextResponse(challenge, { status: 200 });
  }
  return new NextResponse('Forbidden', { status: 403 });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Processar mensagens recebidas
  if (body.object === 'whatsapp_business_account') {
    body.entry?.forEach((entry: any) => {
      entry.changes?.forEach((change: any) => {
        if (change.field === 'messages') {
          const messages = change.value.messages;
          // Processar cada mensagem
        }
      });
    });
  }
  
  return NextResponse.json({ status: 'ok' });
}
```

### Ferramentas Úteis

#### Gerar QR Code para WhatsApp Business

1. Acesse o painel: `/admin/whatsapp`
2. Defina a mensagem pré-preenchida
3. Clique em **Gerar QR code**

Também é possível chamar a API diretamente:

`POST /api/whatsapp/generate-qr`

Body:

```
{
  "prefilledMessage": "Olá! Gostaria de mais informações.",
  "generateQrImage": "PNG"
}
```

#### Gerar SDK TypeScript

```bash
npm install @openapitools/openapi-generator-cli -g

openapi-generator-cli generate \
  -i openapi/business-messaging-api_v23.0.yaml \
  -g typescript-axios \
  -o src/generated/whatsapp-sdk
```

#### Visualizar Documentação

```bash
npm install -g redoc-cli

redoc-cli bundle openapi/business-messaging-api_v23.0.yaml \
  -o docs/whatsapp-api.html
```

#### Gerar Tipos TypeScript

```bash
npm install openapi-typescript

npx openapi-typescript openapi/business-messaging-api_v23.0.yaml \
  --output src/types/whatsapp-api.d.ts
```

### Documentação Completa

Para informações detalhadas sobre:
- Geração de SDKs em múltiplas linguagens
- Configuração de documentação interativa
- Validação de requisições/respostas
- Exemplos de uso avançados
- Rate limits e melhores práticas

Consulte: **[openapi/INTEGRACAO_FACEBOOK_API.md](openapi/INTEGRACAO_FACEBOOK_API.md)**

### Recursos Externos

- **[WhatsApp Business API - Documentação Oficial](https://developers.facebook.com/docs/whatsapp)**
- **[Repositório Facebook OpenAPI](https://github.com/facebook/openapi)**
- **[Business Messaging Overview](https://developers.facebook.com/documentation/business-messaging/whatsapp/overview)**

### Notas Importantes

⚠️ **Termos e Condições**: O uso da WhatsApp Business API está sujeito aos termos da Meta.

🔒 **Segurança**: Nunca commite tokens de acesso. Use sempre variáveis de ambiente.

📊 **Rate Limits**: Consulte a documentação oficial para limites de taxa e quotas.

---

## Solução de Problemas da Câmera

### Erro: "Não foi possível acessar a câmera"

#### Causas Comuns

1. **Permissões do Navegador**
   - Navegador bloqueou acesso
   - Usuário negou permissão

2. **Contexto Inseguro**
   - Aplicação não está em HTTPS
   - Exceção: localhost é permitido

3. **Câmera em Uso**
   - Outro programa está usando
   - Outra aba do navegador está usando

4. **Hardware**
   - Câmera não conectada
   - Driver desatualizado

#### Soluções

##### 1. Verificar Permissões (Chrome)

```
1. Clicar no ícone 🔒 ou ⓘ na barra de endereços
2. Localizar "Câmera"
3. Selecionar "Permitir"
4. Recarregar a página
```

##### 2. Verificar Permissões (Safari)

```
1. Safari → Preferências → Sites
2. Câmera
3. Localizar seu site
4. Selecionar "Permitir"
```

##### 3. Verificar Permissões (Firefox)

```
1. Clicar no ícone 🔒 na barra de endereços
2. Clicar na seta ao lado de "Conexão segura"
3. Mais informações → Permissões
4. Desmarcar "Usar padrão" na Câmera
5. Marcar "Permitir"
```

##### 4. Verificar HTTPS

```bash
# Desenvolvimento local
npm run dev # localhost é permitido

# Produção
# Garantir que o site usa HTTPS
```

##### 5. Fechar Outros Programas

```
1. Fechar Zoom, Skype, Teams
2. Fechar outras abas do navegador
3. Reiniciar navegador se necessário
```

##### 6. Verificar Hardware (macOS)

```bash
# Terminal
sudo killall VDCAssistant
sudo killall AppleCameraAssistant
```

##### 7. Verificar Hardware (Windows)

```
1. Gerenciador de Dispositivos
2. Câmeras
3. Botão direito → Atualizar driver
```

#### Teste Manual

```javascript
// Console do navegador
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    console.log('✅ Câmera funcionando');
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(err => {
    console.error('❌ Erro:', err.name, err.message);
  });
```

#### Erros Específicos

**NotAllowedError**
- Usuário negou permissão
- Solução: Conceder permissão

**NotFoundError**
- Nenhuma câmera encontrada
- Solução: Conectar câmera

**NotReadableError**
- Câmera em uso
- Solução: Fechar outros programas

**OverconstrainedError**
- Resolução não suportada
- Solução: Reduzir constraints

**SecurityError**
- Contexto inseguro (não HTTPS)
- Solução: Usar HTTPS ou localhost

---

## Guia Rápido de Início

### Pré-requisitos

- Node.js 18+ ou 20+
- npm ou yarn
- Conta Firebase
- Conta SendGrid (email)
- Conta Twilio (SMS)

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/italosantos-com.git
cd italosantos-com

# 2. Instalar dependências
npm install

# 3. Configurar variáveis de ambiente
cp .env.admin-auth.example .env.local
# Editar .env.local com suas credenciais

# 4. Baixar modelos face-api.js
node download-face-api-models.js

# 5. Executar setup do Firestore
node scripts/setup-admin-registration.js

# 6. Iniciar desenvolvimento
npm run dev
```

### Primeiro Admin

```bash
# 1. Acessar http://localhost:3000/admin/login
# 2. Clicar em "Cadastre-se como Admin"
# 3. Informar código de convite (definido em .env.local)
# 4. Seguir wizard de 4 etapas
# 5. Verificar email e SMS
# 6. Login concluído!
```

### Comandos Úteis

```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# Produção
npm start

# Lint
npm run lint

# Testes
npm test

# Deploy Firebase
firebase deploy
```

---

## Configuração e Deploy

### Estrutura do Projeto

```
italosantos-com/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── admin/             # Painel admin
│   │   └── api/               # API routes
│   ├── components/            # Componentes React
│   │   ├── admin/            # Componentes admin
│   │   └── auth/             # Autenticação
│   ├── contexts/             # React Context
│   ├── hooks/                # Custom hooks
│   ├── lib/                  # Utilitários
│   └── services/             # Serviços externos
├── public/
│   └── models/               # Modelos face-api.js
├── scripts/                  # Scripts utilitários
├── docs/                     # Documentação
├── .env.local               # Variáveis de ambiente
├── firebase.json            # Config Firebase
├── apphosting.yaml          # Config App Hosting
├── Dockerfile               # Container Docker
└── package.json
```

### Tecnologias

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Backend:** Next.js API Routes, Firebase Admin SDK
- **Database:** Firestore
- **Storage:** Firebase Storage
- **Auth:** Firebase Auth + Face ID
- **Face Recognition:** face-api.js (TensorFlow.js)
- **Email:** SendGrid
- **SMS:** Twilio
- **Payments:** PayPal, Stripe, Mercado Pago
- **Social:** Twitter API, Instagram API, Facebook SDK

### Deploy Options

#### Opção 1: Firebase App Hosting (Recomendado)

```bash
# 1. Instalar Firebase CLI
npm install -g firebase-tools

# 2. Login
firebase login

# 3. Selecionar projeto
firebase use creatorsphere-srajp

# 4. Deploy
firebase deploy --only apphosting:italosantos
```

#### Opção 2: Firebase Hosting + Cloud Run

```bash
# 1. Build
npm run build

# 2. Deploy Cloud Run
gcloud run deploy italosantos \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# 3. Deploy Hosting
firebase deploy --only hosting
```

#### Opção 3: Docker

```bash
# 1. Build
docker build -t italosantos-com .

# 2. Run
docker run -p 3000:3000 \
  --env-file .env.local \
  italosantos-com

# 3. Deploy (Cloud Run, AWS, etc)
docker push gcr.io/creatorsphere-srajp/italosantos-com
```

### Variáveis de Ambiente Completas

```bash
# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
NEXT_PUBLIC_FIREBASE_DATABASE_URL=

# Firebase Admin
FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=

# Admin Registration
ADMIN_INVITATION_CODE=
FACE_API_MODEL_URL=/models

# SendGrid (Email)
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=

# Twilio (SMS)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Social Media
NEXT_PUBLIC_TWITTER_API_KEY=
NEXT_PUBLIC_TWITTER_API_SECRET=
NEXT_PUBLIC_INSTAGRAM_CLIENT_ID=
NEXT_PUBLIC_INSTAGRAM_CLIENT_SECRET=
NEXT_PUBLIC_FACEBOOK_APP_ID=
NEXT_PUBLIC_FACEBOOK_APP_SECRET=

# Payments
NEXT_PUBLIC_PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
MERCADOPAGO_ACCESS_TOKEN=

# Admin Panel
ADMIN_PANEL_KEY=
```

### Monitoramento e Logs

```bash
# Firebase Logs
firebase functions:log

# Cloud Run Logs
gcloud logging read "resource.type=cloud_run_revision"

# Next.js Logs
# Disponíveis no console do servidor
```

### Backup e Recuperação

```bash
# Exportar Firestore
gcloud firestore export gs://creatorsphere-srajp-backup

# Importar Firestore
gcloud firestore import gs://creatorsphere-srajp-backup/[TIMESTAMP]

# Backup Storage
gsutil -m cp -r gs://creatorsphere-srajp.appspot.com gs://backup-bucket
```

### Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Modelos face-api.js baixados
- [ ] Firebase inicializado
- [ ] SendGrid configurado
- [ ] Twilio configurado
- [ ] Domínio configurado
- [ ] SSL/HTTPS ativo
- [ ] Índices Firestore criados
- [ ] Testes end-to-end passando
- [ ] Monitoramento configurado
- [ ] Backup configurado

---

## Suporte

- **Email:** suporte@italosantos.com
- **GitHub:** https://github.com/seu-usuario/italosantos-com
- **Documentação:** https://italosantos.com/docs

---

**Última atualização:** Outubro 2025
Documentação do Projeto Italo Santos
Bem-vindo à documentação do projeto Italo Santos. Este documento visa fornecer um guia completo para entender, configurar e contribuir para este projeto. O projeto Italo Santos é uma aplicação web multifacetada com foco em conteúdo adulto, que inclui um site de apresentação, uma loja virtual, um sistema de assinaturas e um painel de administração robusto.

Tecnologias Utilizadas
O projeto é construído com um conjunto de tecnologias modernas e escaláveis:

Framework: Next.js (com App Router)
Linguagem: TypeScript
Backend e Banco de Dados: Firebase (Firestore, Realtime Database, Storage, Authentication)
Estilização: Tailwind CSS com componentes ShadCN/UI
Inteligência Artificial: Google Genkit para funcionalidades de IA (tradução, verificação facial, etc.)
Pagamentos: Integração com Mercado Pago (PIX) e PayPal.
APIs de Terceiros: Facebook Graph API, Instagram Graph API, Twitter API.
ORIENTAÇÕES COMPLETAS DO SISTEMA ITALO SANTOS
INSTRUÇÃO IMPORTANTE: Este documento deve conter exemplos e instruções para absolutamente tudo que for encontrado ou gerado no sistema: cada área, funcionalidade, integração, componente, serviço, página, regra, script, API, SDK, biblioteca, menu, botão, fluxo, categoria, fetiche, fantasia, configuração, backup, deploy, erro, teste, notificação, etc. Sempre que algo novo for identificado ou criado, adicione exemplos práticos e instruções detalhadas para facilitar o uso, manutenção e expansão do sistema.

ATENÇÃO: Este sistema NÃO utiliza roxo ou azul como cor de fundo, texto ou destaque. As únicas cores permitidas no layout são PRETO, BRANCO e CINZA. O azul só aparece como efeito neon especial em botões de ação e destaques, nunca como cor base. Não utilize roxo ou azul em nenhum componente, página ou elemento visual do sistema.

Este sistema é um webapp de e-commerce no modelo OnlyFans, onde cada assinante pode criar e gerenciar seu próprio website exclusivo, vender conteúdo, receber pagamentos diretamente (PIX, PayPal, Google Pay) e não precisa pagar comissão para terceiros. O painel permite total autonomia ao assinante, incluindo uploads, integração com redes sociais, IA, relatórios e personalização.

Este documento reúne todas as instruções, regras, credenciais, integrações, scripts, APIs, SDKs, bibliotecas e detalhes técnicos para configurar, executar, manter e expandir o sistema.

Detalhamento de Todas as Áreas, Funcionalidades e Componentes
Esta seção detalha cada área, funcionalidade, componente, integração, serviço, página, regra, script, API, SDK, biblioteca, menu, botão, fluxo, categoria, fetiche, fantasia, configuração, backup, deploy, erro, teste, notificação e outros itens do sistema. Para cada item, são fornecidas explicações, exemplos práticos, instruções de uso, localização no projeto, dependências, fluxos de dados, permissões, dicas de manutenção e expansão.

Explicações Detalhadas de Cada Área, Funcionalidade e Componente
Estrutura de Diretóriosdo Projeto
src/app/: Contém todas as rotas e páginas do site, seguindo o padrão do Next.js App Router.
(public)/: Páginas públicas como a home, loja, fotos, etc.
admin/: Contém todo o painel de administração.
api/: Rotas de API do Next.js para tarefas de backend.
src/components/: Componentes React reutilizáveis.
layout/: Componentes principais do layout (header, footer, sidebar).
ui/: Componentes de UI da biblioteca ShadCN.
admin/: Componentes específicos para o painel de administração.
src/ai/flows/: Contém os fluxos do Genkit que orquestram as funcionalidades de IA.
src/services/: Módulos que interagem com serviços externos, como o banco de dados.
src/lib/: Utilitários e configuração de bibliotecas (Firebase, etc.).
public/: Arquivos estáticos.
*.rules: Arquivos de configuração das regras de segurança do Firebase.
O projeto é organizado em pastas para separar responsabilidades: páginas, componentes, serviços, utilitários, funções customizadas, assets e documentação. Isso facilita a manutenção, escalabilidade e colaboração entre desenvolvedores.

FuncionalidadesComponentes Principais
1. Autenticação
Face ID para Clientes: Usuários podem se cadastrar e autenticar usando reconhecimento facial. O sistema compara a imagem de login com uma base de dados de usuários cadastrados.
Acesso de Administrador: O administrador (pix@italosantos.com) tem acesso a um painel de controle exclusivo (/admin) através de login com email e senha.
Acesso de Visitante do Assinante: O administrador pode visualizar a área do assinante usando suas credenciais de admin na página de autenticação facial.
2. Painel de Administração (/admin)
Um painel completo para gerenciar todo o conteúdo e operações do site.

Dashboard: Visão geral com estatísticas de assinantes, conversas, produtos, avaliações pendentes e as páginas mais acessadas do site.
Conversas: Uma caixa de entrada centralizada para visualizar e responder a todas as conversas do "Chat Secreto" com os visitantes.
Assinantes: Lista de todos os usuários cadastrados com Face ID, com opção de remoção.
Gerenciamento de Conteúdo:
Produtos: Adicionar, editar e remover produtos da loja (conteúdo não relacionado a vídeos).
Fotos: Gerenciar a galeria de fotos que aparece na página pública.
Vídeos: Gerenciar os vídeos vendidos avulsamente na loja.
Uploads: Uma central para enviar mídias (imagens, vídeos) para o Firebase Storage e obter os links para usar nas outras seções.
Integrações: Ligar e desligar a exibição dos feeds do Facebook, Instagram e Twitter no site, além de controlar a ativação dos métodos de pagamento.
Avaliações: Moderar (aprovar ou rejeitar) os comentários deixados pelos usuários.
Configurações: Um local central para atualizar informações de perfil (nome, contato), foto de perfil, imagem de capa e as 7 galerias de fotos que aparecem no rodapé da página inicial.
Cada componente tem uma função específica e pode ser reutilizado em várias páginas. Por exemplo, o Header.tsx centraliza a navegação e o menu hamburguer, enquanto o PaymentButton.tsx encapsula toda a lógica de pagamento, tornando fácil adicionar novos métodos ou customizar o visual.

Serviços e Integrações
Os serviços (firebase.ts, payments.ts, ai.ts, social.ts) concentram a lógica de comunicação com APIs externas, banco de dados, autenticação, pagamentos e IA. Isso garante que as páginas e componentes fiquem limpos e focados na interface.

Páginas e Rotas
Cada página representa uma área do sistema (home, admin, VIP, login, galeria, fetiche, fantasia, configurações). As rotas protegidas garantem que apenas usuários autorizados acessem áreas sensíveis, como o painel admin.

Fluxos de Dados e Permissões
O sistema utiliza regras de segurança do Firebase para controlar leitura/escrita no banco de dados e storage. Permissões são definidas por tipo de usuário (admin, cliente, visitante) e reforçadas tanto no backend quanto nas rotas do Next.js.

Scripts e Configurações
Scripts automatizam tarefas como deploy, backup, download de modelos de IA. As configurações (variáveis de ambiente, Tailwind, Next.js, Firebase) garantem que o sistema funcione corretamente em diferentes ambientes (desenvolvimento, produção, testes).

Visual e Experiência do Usuário
O layout é responsivo, adaptando-se a mobile e desktop. O uso de cores restritas e efeitos neon cria uma identidade visual única e moderna. O menu hamburguer facilita a navegação entre todas as áreas e categorias do sistema.

Categorias, Fetiches e Fantasias
O sistema suporta centenas de categorias, cada uma com sua própria página, galeria, opções de assinatura VIP e botões de pagamento. Novas categorias podem ser criadas facilmente pelo painel admin, permitindo expansão contínua.

Testes, Backup, Migração e Monitoramento
Testes garantem que integrações de pagamento e IA funcionem corretamente. Backup e migração protegem os dados dos usuários e facilitam a restauração em novos ambientes. Monitoramento por logs e analytics permite identificar e corrigir erros rapidamente.

Exemplos Práticos e Instruções
Para cada área, há exemplos de importação, uso, configuração, permissões e manutenção. Isso facilita o onboarding de novos desenvolvedores e a expansão do sistema por qualquer pessoa.

Explicações Específicas e Detalhadas de Todas as Páginas, Fluxos, Serviços e Integrações
Páginas
/page.tsx (Home): Página inicial pública, exibe textos institucionais, cards de destaque, galeria pública, botões de login e assinatura. Integra com componentes de navegação, galeria e pagamentos. Permite acesso a visitantes, assinantes e admin.
/admin/page.tsx (Painel Admin): Área restrita ao admin, exibe dashboard com gráficos, tabelas de produtos, fotos, vídeos, avaliações, switches de integrações, botões de backup, logs e configuração de IA. Protegida por autenticação e regras de email. Permite gerenciamento total do sistema.
/vip/page.tsx (Área VIP): Página exclusiva para assinantes VIP, mostra galeria privada, botões de pagamento, conteúdo restrito, integração com Firestore e Storage. Permite acesso apenas a usuários autenticados e pagantes.
/login/page.tsx: Página de autenticação, oferece login por Face ID ou email, formulário de cadastro, integração com Firebase Auth e IA facial. Exibe mensagens de erro/sucesso e redireciona conforme permissões.
/gallery/page.tsx: Galeria pública/VIP, exibe fotos e vídeos filtrados por categoria, fetiche ou fantasia. Integra com Storage e Firestore para busca e exibição dinâmica.
/fetiche/[categoria]/page.tsx: Página temática para cada fetiche, exibe galeria exclusiva, botões de assinatura VIP, chat privado, integração com pagamentos e Storage. Permite expansão dinâmica de categorias.
/fantasia/[categoria]/page.tsx: Página temática para cada fantasia, galeria, assinatura VIP, pedidos personalizados, integração com pagamentos e Storage.
/admin/settings.tsx: Página de configurações do admin, permite editar perfil, preferências, ativar/desativar integrações, configurar fluxos de IA.
Fluxos
Autenticação: Usuário acessa login > escolhe Face ID ou email > autentica via Firebase Auth > recebe permissões conforme tipo (admin, assinante, visitante).
Assinatura VIP: Usuário acessa área VIP ou página de fetiche/fantasia > clica em botão de pagamento (PIX, PayPal, Google Pay) > realiza pagamento > recebe acesso à galeria exclusiva e conteúdo restrito.
Upload de Conteúdo: Admin acessa painel > seleciona galeria > faz upload de fotos/vídeos > arquivos são salvos no Storage > metadados registrados no Firestore > conteúdo aparece na galeria pública/VIP.
Integração com Redes Sociais: Admin ativa integração > sistema conecta com APIs do Facebook, Instagram, Twitter > busca feeds, postagens, loja > exibe conteúdo nas páginas e dashboard.
Configuração de IA: Admin acessa painel > configura fluxos de IA (tradução, verificação facial, automação) > integra com Genkit e face-api.js > resultados usados em autenticação, tradução de conteúdo, moderação.
Backup/Migração: Admin clica em botão de backup > sistema exporta dados do Firestore/Storage > arquivos podem ser restaurados em novo ambiente via painel ou CLI.
Monitoramento de Erros/Logs: Sistema registra logs de ações, erros, pagamentos, uploads > integra com Vercel Analytics, Sentry, LogRocket > admin visualiza logs no painel.
Serviços
firebase.ts: Centraliza autenticação, Firestore, Storage, Functions, regras de segurança, integração com Admin SDK. Funções para login, cadastro, upload, leitura/escrita de dados, proteção de rotas.
payments.ts: Gerencia pagamentos via PIX (Mercado Pago), PayPal, Google Pay. Funções para geração de QR Code, integração com APIs externas, verificação de status, registro de transações.
ai.ts: Gerencia fluxos de IA (tradução, verificação facial, automação). Funções para chamada de Genkit, face-api.js, processamento de resultados, integração com autenticação e moderação.
social.ts: Gerencia integração com Facebook, Instagram, Twitter. Funções para autenticação social, busca de feeds, postagens, loja, registro de interações.
Integrações
Firebase: Banco de dados (Firestore), autenticação (Auth), storage de arquivos, funções customizadas (Functions), regras de segurança. Integração via SDK e Admin SDK.
Google Genkit: Fluxos de IA para tradução, verificação facial, automação. Integração via SDK, configuração de modelos e fluxos customizados.
Mercado Pago: Pagamentos via PIX, integração via SDK, geração de QR Code, registro de transações, verificação de status.
PayPal: Pagamentos internacionais, integração via SDK, registro de transações, sandbox para testes.
Google Pay: Botões oficiais, integração via API, ambiente sandbox/teste, registro de pagamentos.
Facebook Graph API: Integração para feed, login, perfil, busca de conteúdo, registro de interações.
Instagram Graph API: Integração para feed, loja, busca de conteúdo, registro de interações.
Twitter API: Integração para feed, postagens, busca de conteúdo, registro de interações.
Vercel: Deploy automático via GitHub, configuração de variáveis, monitoramento de requisições.
Sentry/LogRocket/Vercel Analytics: Monitoramento de erros, logs, análise de uso, integração com painel admin.
3Permissões Regras dee Segurança
A aplicação segue o princípio de "negar por padrão", garantindo segurança máxima:

Admin: Acesso total ao painel, escrita em Firestore, upload no Storage, ativação de integrações, configuração de IA, backup/migração, visualização de logs.
Assinante VIP: Acesso à área VIP, galeria exclusiva, conteúdo restrito, pagamentos, perfil personalizado.
Visitante: Acesso à home, galeria pública, textos institucionais, opção de login/assinatura.
Controle: Regras de segurança no Firebase, lógica nas rotas Next.js, validação de email/admin, proteção de uploads e dados sensíveis.
Expansão e Manutenção
Novas páginas, componentes, serviços e integrações podem ser criados facilmente seguindo o padrão modular do projeto. Basta adicionar arquivos nas pastas corretas, registrar rotas e permissões, e documentar exemplos de uso.
Estrutura do Projeto
src/app/: Páginas principais, rotas protegidas, APIs, autenticação, painel admin, área VIP, login, galeria, configurações.
src/components/: Componentes reutilizáveis (Header, Footer, tabelas, galerias, botões, formulários, switches, dashboards, moderadores, backup, logs, IA, notificações).
src/services/: Serviços de integração (Firebase, pagamentos, IA, redes sociais).
src/lib/: Utilitários, helpers, validações, formatação de dados.
public/: Assets estáticos (imagens, ícones, scripts de teste, sw.js).
functions/: Funções customizadas do Firebase (webhooks, autenticação, pagamentos, IA).
docs/: Documentação técnica, orientações, tutoriais, exemplos.
Raiz do projeto: Configurações, scripts de deploy, regras, variáveis de ambiente, Dockerfile, configs do Next.js, Tailwind, Vercel, Firebase, etc.
Componentes Principais
Header.tsx: Cabeçalho, menu hamburguer, navegação, botões de login/logout, links institucionais, fetiches, VIP, admin.
Footer.tsx: Rodapé, textos institucionais, links de redes sociais, copyright.
ProductTable.tsx: Tabela de produtos, botões de editar/excluir/adicionar, filtros, ordenação, integração com Firestore.
PhotoGallery.tsx: Galeria de fotos/vídeos, upload (admin), visualização pública/VIP, integração com Storage.
PaymentButton.tsx: Botões de pagamento (PIX, PayPal, Google Pay), integração com Mercado Pago, PayPal SDK, Google Pay API, efeito neon.
FaceAuthButton.tsx: Autenticação facial, integração com Firebase Auth e IA.
IntegrationSwitch.tsx: Switches para ativar/desativar integrações (Facebook, Instagram, Twitter, IA), controle admin.
StatsDashboard.tsx: Gráficos, estatísticas de assinantes, vendas, visualizações, integração com Firestore.
ReviewModerator.tsx: Moderação de avaliações, botões de aprovar/reprovar, integração com Firestore.
BackupButton.tsx: Backup/migração de dados, exportação/importação Firestore/Storage.
LogViewer.tsx: Visualização de logs de ações, erros, integração com Sentry/LogRocket/Vercel Analytics.
IAConfigForm.tsx: Configuração de fluxos de IA, integração com Genkit, face-api.js.
NotificationPanel.tsx: Painel de notificações, exibição de mensagens para o usuário.
Serviços e Integrações
firebase.ts: Funções de autenticação, Firestore, Storage, Functions, regras de segurança, integração com Admin SDK.
payments.ts: Funções de pagamento (PIX, PayPal, Google Pay), geração de QR Code, integração com APIs externas.
ai.ts: Funções de IA (tradução, verificação facial, automação), integração com Genkit, face-api.js.
social.ts: Funções de integração com Facebook, Instagram, Twitter, busca de feeds, postagens, login social.
Páginas e Rotas
/page.tsx: Home pública, textos institucionais, destaques, cards, galeria pública, botões de login/assinatura.
/admin/page.tsx: Painel admin, dashboard, tabelas, gerenciamento, gráficos, logs, backup, integrações, IA.
/vip/page.tsx: Área VIP, galeria exclusiva, botões de pagamento, conteúdo restrito, assinatura.
/login/page.tsx: Autenticação por Face ID/email, formulário de cadastro/login, integração com Firebase Auth.
/gallery/page.tsx: Galeria pública/VIP, visualização de fotos/vídeos, filtros por categoria/fetiche/fantasia.
/fetiche/[categoria]/page.tsx: Páginas temáticas de fetiche, galeria, assinatura VIP, botões de pagamento, chat privado.
/fantasia/[categoria]/page.tsx: Páginas temáticas de fantasia, galeria, assinatura VIP, pedidos personalizados.
/admin/settings.tsx: Configurações de perfil, preferências, IA, integrações.
Fluxos de Dados e Permissões
Autenticação: Firebase Auth, Face ID, regras de segurança, controle de acesso por email/admin.
Banco de Dados: Firestore (coleções: subscribers, payments, products, reviews, chats), Realtime Database (autenticação facial, chat), Storage (imagens, vídeos, uploads).
Permissões: Admin (acesso total, escrita), Cliente (leitura pública, área VIP), controle por regras e lógica nas rotas.
Scripts e Configurações
deploy.sh: Deploy automatizado para Vercel/Firebase, comandos de build, push, deploy.
deploy-firebase.js: Deploy de regras e funções Firebase, exportação/importação de dados.
download-face-api-models.js: Download de modelos de IA facial, integração com face-api.js.
download-models.js: Download de modelos de IA, integração com Genkit.
Configurações: Variáveis de ambiente (.env.local), Tailwind (cores, neon), Next.js, Firebase, Vercel, Dockerfile.
Visual e Experiência do Usuário
Paleta de cores: Preto, branco, cinza, neon (azul/verde) em botões de ação/destaque.
Efeito neon: Botões de pagamento, títulos principais, cards de destaque, hover em botões de ação.
Layout responsivo: Mobile, desktop, menu hamburguer, navegação intuitiva.
Menu hamburguer: Home, Assinar VIP, Login, Admin, Galeria, Pagamentos, Integrações, Configurações, Logout, Fetiches, Fantasias.
Categorias, Fetiches e Fantasias
Categorias dinâmicas: Centenas de fetiches/fantasias, organizadas no menu, cada uma com página temática, galeria, assinatura VIP, botões de pagamento, chat privado, pedidos personalizados.
Exemplo de fluxo: Usuário acessa menu > escolhe fetiche/fantasia > visualiza galeria > assina VIP > realiza pagamento > acessa conteúdo exclusivo.
Testes, Backup, Migração e Monitoramento
Testes: Google Pay (test-google-pay.html), pagamentos sandbox, debug de callbacks, logs detalhados.
Backup/migração: Exportação/importação Firestore/Storage, scripts customizados, botões no painel admin.
Monitoramento: Vercel Analytics, Firebase Crashlytics, Sentry, LogRocket, logs customizados.
Exemplos Práticos e Instruções
Para cada área, componente, serviço, página, integração, categoria, fetiche, fantasia, fluxo, botão, script, regra, API, SDK, biblioteca, menu, configuração, backup, deploy, erro, teste, notificação, etc., há exemplos práticos e instruções detalhadas ao longo do documento.
Sempre consulte as seções específicas para exemplos de importação, uso, configuração, localização, permissões, manutenção e expansão.
Dados Pessoais e Credenciais de Exemplo
Autor: Italo Santos
Email principal (admin): pix@italosantos.com
Instagram: @italosantos
Twitter: @italosantos
Site pessoal: https://italosantos.com
Pix para recebimento: pix@italosantos.com
PayPal para recebimento: italosantos@gmail.com
Google Pay: italosantos@gmail.com
Descrição:
Italo Santos é empreendedor digital, desenvolvedor fullstack e especialista em e-commerce, automação e inteligência artificial. Criou este sistema para permitir que criadores tenham total autonomia, recebam pagamentos diretamente e possam expandir seus negócios sem pagar comissão para terceiros.

1. Passo a Passo Inicial
Clone o repositório:

git clone <url-do-repo>
cd <pasta>
Instale dependências:

npm install
Configure as variáveis de ambiente (.env.local):

Adicione na raiz do projeto:

NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAhh1pfOoXCXcXv28WQK5XmOzcYZqqXXOo
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=authkit-y9vjx.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=authkit-y9vjx
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=authkit-y9vjx.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=308487499277
NEXT_PUBLIC_FIREBASE_APP_ID=1:308487499277:web:4ee1111ab0be47f29f2f44
NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://authkit-y9vjx-default-rtdb.firebaseio.com
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-R612CBBL12

MERCADOPAGO_PUBLIC_KEY=APP_USR-e9289eca-b8bd-4677-9481-bc9f6388eb67
MERCADOPAGO_ACCESS_TOKEN=APP_USR-1595377099020994-122510-cd38e362938f5ca604774d3efa719cbe-696581588
NEXT_PUBLIC_PAYPAL_CLIENT_ID=AXykIWKfbbsR_Qe4eLrDgxudUWcoFn-cihQdgWJTqEOVQiP5fxXln-C5fr1QABQ4jowP7Oz2nkNtPFie
PAYPAL_CLIENT_SECRET=EGcfrzzmrL_jpRt-9kp2GaaF3f7jVNvOg4EHVwsnMl4V28_0iyN0UXu5OGvAT1c9e_OeikFuWe8QqSlX
PAYPAL_ENVIRONMENT=production
NEXT_PUBLIC_PAYPAL_BUSINESS_EMAIL=pix@italosantos.com

NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=BCR2DN4T6OKKN3DX
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_NAME=Italo Santos
NEXT_PUBLIC_GOOGLE_PAY_ENVIRONMENT=PRODUCTION
GOOGLE_PAY_GATEWAY_MERCHANT_ID=BCR2DN7TZCU7FEQW

NEXT_PUBLIC_ENVIRONMENT=production

TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAEebugEAAAAA54Zk%2BYxiPsyxHQdrsWm5enS8C9M%3DkOVn6m1pvz8wb1jqM9QQTLpeFs7QyZvOeJycHfjXdrDw7M378z
INSTAGRAM_FEED_ACCESS_TOKEN=IGAAKe7p2HuutBZAFBpWHNBcWFmOXlOWVFiMS1yODN6elprU1oxRlZAtb0UxMnRZATFdSN0JLbUZASMXJpMElmLXhZARVRuWHNJYTNRcGt5blNWYlczb3FWYzcxemQ3Y2pkaHg1NkVSMzBDc21JRENpMTl2dGxNMzFPZATBWdHBCUW1TZAwZDZD
INSTAGRAM_SHOP_ACCESS_TOKEN=IGAAKe7p2HuutBZAE14YkM0TVZACbldrWW4zZAktYclFPb1c3ZADQ5emFhNjFJOEI2MFlHMGxlWXRxR2ExSmpSZADg4MTBNcVMtTkxoNzhMODFaMnpnMnZAnNG1RUGNXcHpQTGVoaF9uNTBsbENFaGV0Mm84bkpGTWJFR1FFMnhOSm5VOAZDZD
FACEBOOK_PAGE_ACCESS_TOKEN=YOUR_FACEBOOK_PAGE_ACCESS_TOKEN
GEMINI_API_KEY=AIzaSyDsUxT8enFtbfWFQKUCkvL6dj9W0e7KXoA

FIREBASE_PROJECT_ID=authkit-y9vjx
FIREBASE_PRIVATE_KEY_ID=38eb440ea2c3075585f8077cd635f033052679e5
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDlGmV/+SEqlViX\neM7IhpHZI8+sSXrgm6FeIJQ28I+erkxFQ3tyWBuNB023g9tNfGw5T0awd8pQDFJF\nopo6/r+g7T3G9/IK6iOxEhOcQjIgNhQUo9H+fOIvTqORVLsXwQRTprDx15jcaK+R\nT7u2EdsPPaZq47SAARYob6ZdjRJgkbNyoUWfvWnCj+q00Gk8mg4J1AzJIA8ItUKB\n9H5kCzdSyQuK3jpU83TAmXNPDYTK57FFEu0wxvzRcP1ZcFe5x1rl4nIrF7qtXxml\n4oBAncCCzqYK/rsq57UUoxnUMZy2qINw5xDR3Oly5XZujXpL/IzubKcVXGmXn/p7\nKj5cMuETAgMBAAECggEANYt+z3MVelNfWj+E7L7u1XYWMmkWC+qzw0EQAuskVezc\nrI+CCY5oGgTr+AkcNzbuQFKz7ciBg0Xt8JJ5Q3KIrP7lolwOuNhSMS9NYAbkmjyp\nYs2K5dSgNHhHqE7KT1nwPfDGiC9gbZsV9XtSHtJ7hUteWrsPU59tY1P86P5wnhre\nQoPCBkPRnQM5N4o3G4kOPU5+49ppPTz3U7kUFTmDIQdRzZcug5rlXCK0EBWdU9SK\nmzRyvt+txTt1SaNqLYn4IOdW2mNBHw1OG1w3OnUIVHRdHU7pk+IFKliJMTfGO1Lu\n+1RFE572m1/1ARD1PjlUcXD0BbXahRTWicmiiO9EsQKBgQD2YShwQQuoFTHTEFUL\nQXmGtolwicH9Q51T38HqABxXymJ5KR9SvE88tGwm8qUgexD+mR9x4aOOzYL/mLTk\nusYjij+oChLoYp8k/+gYH8RX6dq97Xg+I9EqVx8Vc9/s+MhoOKOejiamMJ/Jss3z\ngL2tMszNzf7jgB/5ai8XGdV6iwKBgQDuDIqOtHy1x7Gn4jKNb0QhzUEDdsjEPfY2\nMGfU+5kG5pLQrKOTkIdSa75RT8tlPYoknI6d5o4iZ7jM4Y/7BxdzYMrjo2YRjBvp\nEk8zc/X9/axUhjfNqCVITFZQQmtViZwT0/qAhdz3n/VX8hWP7uLFi/e8sAs0yCwG\ngSRlkv5smQKBgF0fvgwn2cMPN8TiIHLfrZJofixmNUeH/fhM09uhbRUVrwDCtU8t\nU/nK7DIQdq9/NJ42vDbsJUj9jq0TSBRIMEoQoBzgqeLiG+r9OvmbUDg2cPJmxpMe\nMJoDUgFmydWk9wLFnbp5WkxohozTI5sNJyRG1jhXyyasL+my49ekcRcfAoGBAJAK\ntqyzOeMk+rMDhGNguHFbqcNW1RUqCRmxIKMXuvkZ/CyYykI4ainNWFQLXJ/eJQES\nWpnhMJBRAtm2g1D6cY43O42TCegER784fQQ9XtRZ8zUSIiInZKfiyTe3eQtBQVge\nJK4wUgzklaipq7J0cnPmxfk+7Qj7NuiYrFVqJNnBAoGAYnLmaYCSRd45jzWJlyUQ\nhrhhNzQZO0AAPjXvBUV+M/ruumQHBSNrSG+qtMQcxdr4mVoeU0DaHRVs+nRr7sST\nnSK96eQvZ0FWHrXnvXUYZjkaBaejIQj43oF0jr5Dv4GicA3ImedESM7eLMrdGu8Z\nAykj0eP/QSJTdyMx3NlRdUg=\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@authkit-y9vjx.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=111384061705768262166

GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account","project_id":"authkit-y9vjx","private_key_id":"38eb440ea2c3075585f8077cd635f033052679e5","private_key":"-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDlGmV/+SEqlViX\\neM7IhpHZI8+sSXrgm6FeIJQ28I+erkxFQ3tyWBuNB023g9tNfGw5T0awd8pQDFJF\\nopo6/r+g7T3G9/IK6iOxEhOcQjIgNhQUo9H+fOIvTqORVLsXwQRTprDx15jcaK+R\\nT7u2EdsPPaZq47SAARYob6ZdjRJgkbNyoUWfvWnCj+q00Gk8mg4J1AzJIA8ItUKB\\n9H5kCzdSyQuK3jpU83TAmXNPDYTK57FFEu0wxvzRcP1ZcFe5x1rl4nIrF7qtXxml\\n4oBAncCCzqYK/rsq57UUoxnUMZy2qINw5xDR3Oly5XZujXpL/IzubKcVXGmXn/p7\\nKj5cMuETAgMBAAECggEANYt+z3MVelNfWj+E7L7u1XYWMmkWC+qzw0EQAuskVezc\\nrI+CCY5oGgTr+AkcNzbuQFKz7ciBg0Xt8JJ5Q3KIrP7lolwOuNhSMS9NYAbkmjyp\\nYs2K5dSgNHhHqE7KT1nwPfDGiC9gbZsV9XtSHtJ7hUteWrsPU59tY1P86P5wnhre\\nQoPCBkPRnQM5N4o3G4kOPU5+49ppPTz3U7kUFTmDIQdRzZcug5rlXCK0EBWdU9SK\\nmzRyvt+txTt1SaNqLYn4IOdW2mNBHw1OG1w3OnUIVHRdHU7pk+IFKliJMTfGO1Lu\\n+1RFE572m1/1ARD1PjlUcXD0BbXahRTWicmiiO9EsQKBgQD2YShwQQuoFTHTEFUL\\nQXmGtolwicH9Q51T38HqABxXymJ5KR9SvE88tGwm8qUgexD+mR9x4aOOzYL/mLTk\\nusYjij+oChLoYp8k/+gYH8RX6dq97Xg+I9EqVx8Vc9/s+MhoOKOejiamMJ/Jss3z\\ngL2tMszNzf7jgB/5ai8XGdV6iwKBgQDuDIqOtHy1x7Gn4jKNb0QhzUEDdsjEPfY2\\nMGfU+5kG5pLQrKOTkIdSa75RT8tlPYoknI6d5o4iZ7jM4Y/7BxdzYMrjo2YRjBvp\nEk8zc/X9/axUhjfNqCVITFZQQmtViZwT0/qAhdz3n/VX8hWP7uLFi/e8sAs0yCwG\ngSRlkv5smQKBgF0fvgwn2cMPN8TiIHLfrZJofixmNUeH/fhM09uhbRUVrwDCtU8t\nU/nK7DIQdq9/NJ42vDbsJUj9jq0TSBRIMEoQoBzgqeLiG+r9OvmbUDg2cPJmxpMe\nMJoDUgFmydWk9wLFnbp5WkxohozTI5sNJyRG1jhXyyasL+my49ekcRcfAoGBAJAK\ntqyzOeMk+rMDhGNguHFbqcNW1RUqCRmxIKMXuvkZ/CyYykI4ainNWFQLXJ/eJQES\nWpnhMJBRAtm2g1D6cY43O42TCegER784fQQ9XtRZ8zUSIiInZKfiyTe3eQtBQVge\nJK4wUgzklaipq7J0cnPmxfk+7Qj7NuiYrFVqJNnBAoGAYnLmaYCSRd45jzWJlyUQ\nhrhhNzQZO0AAPjXvBUV+M/ruumQHBSNrSG+qtMQcxdr4mVoeU0DaHRVs+nRr7sST\nnSK96eQvZ0FWHrXnvXUYZjkaBaejIQj43oF0jr5Dv4GicA3ImedESM7eLMrdGu8Z\nAykj0eP/QSJTdyMx3NlRdUg=\\n-----END PRIVATE KEY-----\\n","client_email":"firebase-adminsdk-fbsvc@authkit-y9vjx.iam.gserviceaccount.com","client_id":"111384061705768262166","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40authkit-y9vjx.iam.gserviceaccount.com","universe_domain":"googleapis.com"}'

FIREBASE_DATABASE_SECRET="uDTldQT51eWmN4KsNOa1AD1aTUoAMAogCCtMdCub"
FIREBASE_FACEID_SECRET="lk8GvW8uZGm7NVr9rm7k6CLoP8l349GHMLbKibZU"
Inicie o servidor:

npm run dev
2. Estrutura do Projeto
Integrações do Sistema
O sistema possui as seguintes integrações principais:

Firebase:

Firestore (banco de dados principal)
Realtime Database (autenticação facial, chat)
Storage (uploads de imagens e vídeos)
Authentication (login por email, Face ID)
Functions (funções customizadas, webhooks)
Google Genkit:

Fluxos de IA para tradução, verificação facial, automação
Pagamentos:

Mercado Pago (PIX, pagamentos nacionais)
PayPal (pagamentos internacionais)
Google Pay (botões oficiais, ambiente sandbox/teste)
Redes Sociais:

Facebook Graph API (feed, login, perfil)
Instagram Graph API (feed, loja)
Twitter API (feed, postagens)
Outros:

Integração com Vercel para deploy automático
Sentry/LogRocket/Vercel Analytics para monitoramento e logs
Cada integração está documentada nas seções específicas deste arquivo, com exemplos de uso, configuração e localização dos arquivos relacionados.

Localização dos Arquivos de Cada Integração
Integração	Arquivo(s) Principal(is)	Pasta/Localização
Firebase	firebase.ts, regras (firestore.rules, storage.rules)	src/services/, raiz do projeto
Firestore	firebase.ts, regras (firestore.rules)	src/services/, raiz
Realtime Database	firebase.ts, regras (database.rules.json)	src/services/, raiz
Storage	firebase.ts, regras (storage.rules)	src/services/, raiz
Authentication	firebase.ts, componentes de login	src/services/, src/components/FaceAuthButton.tsx, src/app/login/page.tsx
Functions	Funções (src/app/api/, functions/)	src/app/api/, functions/
Google Genkit	Fluxos IA (src/ai/flows/, genkit.ts)	src/ai/flows/, src/ai/genkit.ts
Mercado Pago	payments.ts, botões (PaymentButton.tsx)	src/services/, src/components/PaymentButton.tsx
PayPal	payments.ts, botões (PaymentButton.tsx)	src/services/, src/components/PaymentButton.tsx
Google Pay	payments.ts, botões (PaymentButton.tsx)	src/services/, src/components/PaymentButton.tsx
Facebook API	social.ts	src/services/social.ts
Instagram API	social.ts	src/services/social.ts
Twitter API	social.ts	src/services/social.ts
Vercel Deploy	deploy.sh, vercel.json	raiz do projeto
Monitoramento/Logs	Sentry/LogRocket config, funções customizadas	src/services/, raiz
Para detalhes e exemplos de uso, consulte as seções específicas deste documento e os arquivos indicados acima.

3. Regras de Segurança
Firestore: Leitura pública de produtos, fotos, vídeos e reviews aprovadas. Escrita apenas via painel admin (Admin SDK).
Realtime Database: Bloqueado por padrão. Permissões específicas para autenticação facial e chat.
Storage: Leitura pública, upload apenas autenticado (admin).
4. Variáveis de Ambiente (.env.local)
Adicione na raiz do projeto:

NEXT_PUBLIC_FIREBASE_API_KEY="..."
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="..."
NEXT_PUBLIC_FIREBASE_PROJECT_ID="..."
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="..."
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="..."
NEXT_PUBLIC_FIREBASE_APP_ID="..."
NEXT_PUBLIC_FIREBASE_DATABASE_URL="..."
MERCADOPAGO_PUBLIC_KEY="..."
MERCADOPAGO_ACCESS_TOKEN="..."
NEXT_PUBLIC_PAYPAL_CLIENT_ID="..."
PAYPAL_CLIENT_SECRET="..."
NEXT_PUBLIC_ENVIRONMENT="production"
NEXT_PUBLIC_PAYPAL_BUSINESS_EMAIL="..."
TWITTER_BEARER_TOKEN="..."
INSTAGRAM_FEED_ACCESS_TOKEN="..."
INSTAGRAM_SHOP_ACCESS_TOKEN="..."
FACEBOOK_PAGE_ACCESS_TOKEN="..."
GEMINI_API_KEY="..."
5. Instalação de Pacotes
Execute:

npm install
Principais dependências:

next
react
firebase
tailwindcss
shadcn/ui
genkit
mercado-pago
paypal-rest-sdk
axios
dotenv
6. Emulador e Servidor Local
Para testar Firebase localmente:

npm run dev
# Para emulador Firebase
firebase emulators:start --only firestore,functions,auth
7. Scripts Úteis
deploy.sh: Deploy automatizado para Vercel/Firebase
deploy-firebase.js: Deploy de regras e funções Firebase
download-face-api-models.js: Baixar modelos de IA facial
download-models.js: Baixar modelos de IA
8. Firebase Functions
Local: src/app/api/ e functions/
Funções customizadas para autenticação, pagamentos, integração IA, webhooks
Deploy:
firebase deploy --only functions
9. Banco de Dados
Firestore: Coleções: subscribers, payments, products, reviews, chats
Realtime Database: Autenticação facial, chat
Storage: Imagens, vídeos, uploads
10. Inteligência Artificial
Genkit: Fluxos em src/ai/flows/
Tradução, verificação facial, automação
Instalar dependências IA:
npm install @genkit-ai/core
11. Integrações API/SDK
Facebook Graph API: Feed, login, perfil
Instagram Graph API: Feed, loja
Twitter API: Feed, postagens
Mercado Pago: PIX, pagamentos
PayPal: Pagamentos internacionais
Google Pay: Botões oficiais, ambiente sandbox/teste
12. Sistemas e Bibliotecas
UI: ShadCN/UI, Tailwind
Autenticação: Firebase Auth, Face ID
Admin: Painel Next.js, rotas protegidas
Pagamentos: Mercado Pago, PayPal, Google Pay
IA: Genkit, face-api.js
API: Next.js API routes, Firebase Functions
Banco: Firestore, Realtime Database
Storage: Firebase Storage
13. Deploy
Vercel: Deploy automático via GitHub
Firebase: Deploy de regras, funções e storage
Configuração de variáveis: Manual no painel Vercel
14. Testes e Debug
Teste Google Pay: test-google-pay.html, test-google-pay (React)
Debug: public/debug-google-pay-callbacks.html
Logs detalhados no console
15. Referências e Ajuda
Next.js Docs
Firebase Docs
Genkit Docs
ShadCN/UI
Mercado Pago Docs
PayPal Docs
Google Pay Docs
16. Passo a Passo Inicial
Clone o repositório:
git clone <url-do-repo>
cd <pasta>
Instale dependências:
npm install
Crie .env.local conforme seção 3.
Inicie o servidor:
npm run dev
17. Configuração do Firebase Admin SDK
Crie um projeto no Firebase Console
Gere uma chave de serviço (serviceAccountKey.json)
Adicione o caminho da chave nas variáveis de ambiente:
GOOGLE_APPLICATION_CREDENTIALS="/caminho/serviceAccountKey.json"
18. Exemplos de Regras de Segurança
Firestore:

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /products/{productId} {
      allow read: if true;
      allow write: if request.auth.token.email == "pix@italosantos.com";
    }
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
Storage:

service firebase.storage {
  match /b/{bucket}/o {
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
19. Exemplos de Integração API
Facebook Feed:

import axios from 'axios';
const url = `https://graph.facebook.com/v17.0/<page_id>/feed?access_token=${process.env.FACEBOOK_PAGE_ACCESS_TOKEN}`;
const res = await axios.get(url);
Mercado Pago PIX:

import MercadoPago from 'mercadopago';
const mp = new MercadoPago(process.env.MERCADOPAGO_ACCESS_TOKEN);
const payment_data = { transaction_amount: 99, payment_method_id: 'pix', payer: { email: 'user@email.com' } };
const payment = await mp.payment.create(payment_data);
20. Exemplo de Função Firebase
// src/app/api/hello/route.ts
export async function GET() {
  return Response.json({ message: 'Hello from Firebase Function!' });
}
21. Uso do Painel Admin
Acesse /admin com credenciais de admin
Gerencie produtos, fotos, vídeos, assinantes, avaliações
Ative/desative integrações e métodos de pagamento
22. Teste de Pagamentos
PIX: Gere QR Code e pague via Mercado Pago PayPal: Use sandbox para testes internacionais Google Pay: Teste em Android ou localhost conforme instruções

23. Exemplo de Fluxo IA Genkit
// src/ai/flows/translate.ts
import { translate } from '@genkit-ai/core';
export async function traduzir(texto, idioma) {
  return await translate(texto, { to: idioma });
}
24. Backup e Migração de Dados
Use Firebase Console para exportar/importar dados
Para Firestore: gcloud firestore export gs://<bucket>
Para Storage: Baixe arquivos pelo painel
25. Atualização de Dependências e Scripts
Atualize pacotes:
npm update
Teste scripts customizados após atualização
26. Dicas Finais
Sempre teste em ambiente de desenvolvimento antes de subir para produção
Mantenha backup das regras e credenciais
Use logs detalhados para debug
Documente novas integrações e scripts
27. Exemplos de Rotas Protegidas Next.js
// src/app/admin/page.tsx
import { getServerSession } from 'next-auth';
export default async function AdminPage() {
  const session = await getServerSession();
  if (!session || session.user.email !== 'pix@italosantos.com') {
    return <div>Acesso restrito</div>;
  }
  return <PainelAdmin />;
}
28. Permissões de Usuário (Admin vs Cliente)
Admin: email pix@italosantos.com, acesso total ao painel, escrita em Firestore
Cliente: acesso apenas à área de assinante, leitura pública
Controle via regras do Firebase e lógica nas rotas Next.js
29. Restaurar Backup em Ambiente Novo
Importe dados do Firestore pelo Console ou CLI
Importe arquivos do Storage pelo painel
Configure variáveis de ambiente e credenciais
Teste todas as integrações e permissões
30. Monitoramento de Erros e Logs em Produção
Use Vercel Analytics para monitorar requisições
Configure Firebase Crashlytics para erros críticos
Use logs customizados nas funções e APIs
Recomenda-se integração com Sentry ou LogRocket
31. Adicionar Novos Métodos de Pagamento ou IA
Para pagamentos: siga o padrão de integração de Mercado Pago/PayPal
Para IA: crie novo fluxo em src/ai/flows/ e registre no painel admin
Documente e teste cada novo recurso antes de liberar para produção
32. Exemplos Visuais do Painel Admin
Dashboard: estatísticas, gráficos de assinantes, vendas
Gerenciamento: tabelas de produtos, fotos, vídeos, avaliações
Upload: formulário para envio de mídia
Integrações: switches para ativar/desativar APIs
Logs: área para visualizar logs de ações e erros
33. Fluxo do Sistema (Diagrama Simplificado)
Unable to render rich display

Parse error on line 2:
... --> B[Autenticação (Face ID ou Email)]
-----------------------^
Expecting 'SQE', 'DOUBLECIRCLEEND', 'PE', '-)', 'STADIUMEND', 'SUBROUTINEEND', 'PIPE', 'CYLINDEREND', 'DIAMOND_STOP', 'TAGEND', 'TRAPEND', 'INVTRAPEND', 'UNICODE_TEXT', 'TEXT', 'TAGSTART', got 'PS'

For more information, see https://docs.github.com/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams#creating-mermaid-diagrams

flowchart TD
    A[Usuário acessa site] --> B[Autenticação (Face ID ou Email)]
    B --> C{Tipo de usuário}
    C -->|Admin| D[Painel Admin]
    C -->|Assinante| E[Área VIP]
    C -->|Visitante| F[Área Pública]
    D --> G[Gerenciar Produtos/Fotos/Vídeos]
    D --> H[Moderador de Avaliações]
    D --> I[Configurar Integrações]
    D --> J[Ver Estatísticas]
    E --> K[Galeria Exclusiva]
    E --> L[Pagamentos]
    L --> M[PIX/MercadoPago]
    L --> N[PayPal]
    L --> O[Google Pay]
    G --> P[Upload para Storage]
    F --> Q[Visualizar Conteúdo Público]
    D --> R[Logs/Admin]
    D --> S[Backup/Migração]
    D --> T[Configurar IA]
34. Itens Essenciais do Sistema
Next.js, TypeScript, Tailwind, ShadCN/UI
Firebase (Firestore, Storage, Auth, Functions)
Variáveis de ambiente
Scripts de deploy e backup
Painel admin protegido
Integração de pagamentos (PIX, PayPal, Google Pay)
IA (Genkit, face-api.js)
Regras de segurança
Testes e logs
Backup/migração de dados
35. Itens Não Essenciais (Opcional/Expansão)
Integração com redes sociais (Facebook, Instagram, Twitter)
Analytics avançado (Sentry, LogRocket, Vercel Analytics)
Novos métodos de pagamento (Stripe, Apple Pay)
Novos fluxos de IA (tradução, moderação, automação)
Customização visual avançada
Painel de relatórios customizados
Notificações push
Integração com apps mobile
Automação de marketing
Plugins de terceiros
36. Localização de Itens, Textos, Botões e Funções nos Componentes e Páginas
Estrutura de Componentes e Páginas
src/app/

/page.tsx: Página pública principal (home, textos institucionais, botões de login/assinatura)
/admin/page.tsx: Painel admin (dashboard, tabelas, botões de gerenciamento, gráficos, logs)
/vip/page.tsx: Área VIP do assinante (galeria exclusiva, botões de pagamento, conteúdo restrito)
/login/page.tsx: Autenticação (Face ID, email, botões de login)
/api/: Rotas de API (funções Next.js, integração com Firebase Functions, pagamentos, IA)
src/components/

Header.tsx: Cabeçalho, navegação, botões de login/logout, links principais
Footer.tsx: Rodapé, textos institucionais, links de redes sociais
ProductTable.tsx: Tabela de produtos (admin), botões de editar/excluir/adicionar
PhotoGallery.tsx: Galeria de fotos/vídeos (VIP e público), botões de upload (admin)
PaymentButton.tsx: Botões de pagamento (PIX, PayPal, Google Pay)
FaceAuthButton.tsx: Botão de autenticação facial
IntegrationSwitch.tsx: Switches para ativar/desativar integrações (admin)
StatsDashboard.tsx: Gráficos e estatísticas (admin)
ReviewModerator.tsx: Moderação de avaliações (admin), botões de aprovar/reprovar
BackupButton.tsx: Botão para backup/migração (admin)
LogViewer.tsx: Visualização de logs (admin)
IAConfigForm.tsx: Formulário para configurar fluxos de IA (admin)
NotificationPanel.tsx: Painel de notificações (opcional)
src/services/

firebase.ts: Funções de integração com Firebase (auth, firestore, storage, functions)
payments.ts: Funções de integração com Mercado Pago, PayPal, Google Pay
ai.ts: Funções de integração com Genkit e face-api.js
social.ts: Funções de integração com Facebook, Instagram, Twitter
src/lib/

Utilitários, helpers, validações, formatação de dados
Exemplos de Localização de Funções e Botões
Botão "Login": Header.tsx e /login/page.tsx
Botão "Assinar": /vip/page.tsx, PaymentButton.tsx
Botão "Upload": PhotoGallery.tsx (admin), /admin/page.tsx
Botão "Backup": BackupButton.tsx, /admin/page.tsx
Botão "Ativar Integração": IntegrationSwitch.tsx, /admin/page.tsx
Botão "Configurar IA": IAConfigForm.tsx, /admin/page.tsx
Botão "Ver Logs": LogViewer.tsx, /admin/page.tsx
Botão "Aprovar Avaliação": ReviewModerator.tsx, /admin/page.tsx
Botão "Pagar com PIX/PayPal/Google Pay": PaymentButton.tsx, /vip/page.tsx
Botão "Logout": Header.tsx
Textos e Informações
Textos institucionais: /page.tsx, Footer.tsx
Textos de instrução: Login, Assinatura, Admin (em cada respectivo componente/página)
Textos de erro/sucesso: Em cada componente de ação (ex: pagamentos, uploads, autenticação)
Textos de status: Dashboard, tabelas, logs, notificações
Funções Principais
Autenticação: firebase.ts, FaceAuthButton.tsx, /login/page.tsx
Gerenciamento de produtos/fotos/vídeos: ProductTable.tsx, PhotoGallery.tsx, /admin/page.tsx
Pagamentos: payments.ts, PaymentButton.tsx, /vip/page.tsx
Integrações: social.ts, IntegrationSwitch.tsx, /admin/page.tsx
IA: ai.ts, IAConfigForm.tsx, /admin/page.tsx
Backup/Migração: BackupButton.tsx, /admin/page.tsx
Logs: LogViewer.tsx, /admin/page.tsx
Notificações: NotificationPanel.tsx (opcional)
37. Exemplos de Importação dos Principais Componentes e Serviços
Exemplos de Importação de Componentes
// src/app/page.tsx
import Header from '../components/Header';
import Footer from '../components/Footer';
import PaymentButton from '../components/PaymentButton';
import PhotoGallery from '../components/PhotoGallery';
// src/app/admin/page.tsx
import ProductTable from '../../components/ProductTable';
import StatsDashboard from '../../components/StatsDashboard';
import IntegrationSwitch from '../../components/IntegrationSwitch';
import BackupButton from '../../components/BackupButton';
import LogViewer from '../../components/LogViewer';
import IAConfigForm from '../../components/IAConfigForm';
import ReviewModerator from '../../components/ReviewModerator';
// src/app/vip/page.tsx
import PhotoGallery from '../../components/PhotoGallery';
import PaymentButton from '../../components/PaymentButton';
Exemplos de Importação de Serviços
// src/app/api/payments.ts
import { processPixPayment, processPaypalPayment } from '../../services/payments';

// src/app/api/auth.ts
import { signInWithFaceId, signInWithEmail } from '../../services/firebase';

// src/app/api/ai.ts
import { runGenkitFlow } from '../../services/ai';

// src/app/api/social.ts
import { fetchInstagramFeed, fetchFacebookFeed } from '../../services/social';
Exemplos de Importação de Utilitários
// src/app/api/utils.ts
import { formatDate, validateEmail } from '../../lib/utils';
Esses exemplos mostram como importar os componentes, serviços e utilitários em suas páginas e APIs.

Paleta de Cores e Efeitos Visuais
O sistema utiliza as seguintes cores principais:

Preto: Fundo principal das páginas, painéis e áreas VIP (bg-black, text-white)
Branco: Textos, botões, áreas de destaque (bg-white, text-black)
Cinza: Bordas, backgrounds secundários, cards, tabelas (bg-gray-900, bg-gray-800, bg-gray-700, text-gray-300, border-gray-600)
Neon: Efeito visual em botões de ação, títulos principais e elementos de destaque.
Exemplo de Neon:
Cor: #00ffe7 (azul neon) ou #39ff14 (verde neon)
Utilizado em:
Botão "Assinar" na área VIP (PaymentButton.tsx)
Títulos principais (Header.tsx)
Borda animada em cards de destaque
Hover em botões de pagamento
Como aplicar o efeito neon no Tailwind CSS:

// Exemplo de botão neon
<button className="bg-black text-neon-green border-2 border-neon-green shadow-neon-green hover:shadow-lg hover:border-white transition-all">
  Assinar VIP
</button>

// Adicione ao tailwind.config.js:
module.exports = {
  theme: {
    extend: {
      colors: {
        'neon-green': '#39ff14',
        'neon-blue': '#00ffe7',
      },
      boxShadow: {
        'neon-green': '0 0 10px #39ff14, 0 0 20px #39ff14',
        'neon-blue': '0 0 10px #00ffe7, 0 0 20px #00ffe7',
      },
    },
  },
}
Onde o efeito neon aparece:

Botão "Assinar" (VIP)
Botões de pagamento (PIX, PayPal, Google Pay)
Títulos principais do painel admin
Cards de destaque na home
Hover em botões de ação
Itens do Menu Hamburguer
O menu hamburguer (geralmente em Header.tsx ou MobileMenu.tsx) contém os seguintes itens:

Home:
Vai para /page.tsx (página principal)
Mostra textos institucionais, destaques, cards, galeria pública
Assinar VIP:
Vai para /vip/page.tsx
Mostra galeria exclusiva, botões de pagamento, informações de assinatura
Login:
Vai para /login/page.tsx
Permite autenticação por Face ID ou email
Admin:
Vai para /admin/page.tsx (apenas para admin)
Dashboard, gerenciamento de produtos, fotos, vídeos, avaliações, integrações, backup, logs
Galeria:
Vai para /gallery/page.tsx ou componente PhotoGallery.tsx
Mostra fotos e vídeos públicas ou VIP
Pagamentos:
Vai para /vip/page.tsx ou componente PaymentButton.tsx
Botões de PIX, PayPal, Google Pay
Integrações:
Vai para /admin/page.tsx (admin)
Switches para ativar/desativar Facebook, Instagram, Twitter
Configurações:
Vai para /admin/settings.tsx ou modal de configurações
Permite editar perfil, dados, preferências, IA
Logout:
Executa função de logout (em Header.tsx ou firebase.ts)
Redireciona para home
Cada item do menu hamburguer está ligado a uma página ou componente específico, facilitando a navegação e o acesso às principais funcionalidades do sistema.

Itens de Fetiche no Menu Hamburguer
Além dos itens principais, o menu hamburguer pode conter seções dedicadas a fetiches, permitindo que assinantes e visitantes naveguem por categorias específicas de conteúdo. Exemplos de itens de fetiche e suas respectivas páginas/funções:

Fetiche - Pés:

Página: /fetiche/pes/page.tsx
Mostra galeria exclusiva de fotos e vídeos de pés, opção de assinatura VIP, botões de pagamento
Fetiche - BDSM:

Página: /fetiche/bdsm/page.tsx
Conteúdo temático, galeria, informações, assinatura VIP
Fetiche - Uniforme:

Página: /fetiche/uniforme/page.tsx
Galeria de fotos e vídeos com uniformes, opção de assinatura
Fetiche - Cosplay:

Página: /fetiche/cosplay/page.tsx
Conteúdo de cosplay, galeria, assinatura VIP
Fetiche - Dominação:

Página: /fetiche/dominacao/page.tsx
Conteúdo exclusivo, informações, assinatura
Fetiche - Outros:

Página: /fetiche/outros/page.tsx
Galeria de outros fetiches, opção de sugestão de novos temas
Cada item de fetiche pode ser exibido como submenu ou categoria especial no menu hamburguer, levando o usuário diretamente para a página temática, onde é possível visualizar conteúdo, assinar VIP, interagir e realizar pagamentos.

Lista Ampliada de Fetiches e Fantasias
O sistema suporta centenas de categorias de fetiche e fantasia, todas organizadas dinamicamente no menu hamburguer. Exemplos de categorias disponíveis:

Pés
BDSM
Uniforme
Cosplay
Dominação
Outros
Latex
Couro
Fantasia de Enfermeira
Fantasia de Policial
Fantasia de Estudante
Fantasia de Super-Herói
Roleplay
Voyeur
Exibição
Bondage
Spanking
Sadomasoquismo
Submissão
Dominatrix
Crossdressing
Furry
Infantilização
Adult Baby
Age Play
Pet Play
Pony Play
Ballbusting
Chuva Dourada
Cuckold
Humilhação
Facesitting
Pegging
Strap-on
Sensory Play
Wax Play
Electro Play
Medical Play
Tickle
Food Play
Oil Play
Massagem Erótica
Striptease
Exibição Pública
Masturbação
Sexo Virtual
Sexting
Fantasia de Anjo
Fantasia de Diabo
Fantasia de Coelho
Fantasia de Gato
Fantasia de Pirata
Fantasia de Princesa
Fantasia de Bruxa
Fantasia de Zumbi
Fantasia de Palhaço
Fantasia de Militar
Fantasia de Marinheiro
Fantasia de Bombeiro
Fantasia de Motociclista
Fantasia de Dançarina
Fantasia de Professora
Fantasia de Secretária
Fantasia de Chef
Fantasia de Jogadora
Fantasia de Gamer
Fantasia de Animadora
Fantasia de Atleta
Fantasia de Lutadora
Fantasia de Samurai
Fantasia de Ninja
Fantasia de Geisha
Fantasia de Egípcia
Fantasia de Grega
Fantasia de Romana
Fantasia de Viking
Fantasia de Medieval
Fantasia de Steampunk
Fantasia de Cyberpunk
Fantasia de Alien
Fantasia de Robô
Fantasia de Monstro
Fantasia de Fada
Fantasia de Sereia
Fantasia de Pirata
Fantasia de Cavaleira
Fantasia de Rainha
Fantasia de Rei
Fantasia de Príncipe
Fantasia de Prisioneira
Fantasia de Detetive
Fantasia de Cientista
Fantasia de Astronauta
Fantasia de Surfista
Fantasia de Skatista
Fantasia de Bailarina
Fantasia de Cantora
Fantasia de DJ
Fantasia de Celebridade
Fantasia de Influencer
Fantasia de Youtuber
Fantasia de Streamer
Fantasia de TikToker
Fantasia de Modelo
Fantasia de Fotógrafa
Fantasia de Pintora
Fantasia de Escritora
Fantasia de Jornalista
Fantasia de Advogada
Fantasia de Médica
Fantasia de Dentista
Fantasia de Veterinária
Fantasia de Psicóloga
Fantasia de Engenheira
Fantasia de Arquiteta
Fantasia de Empresária
Fantasia de Executiva
Fantasia de Policial
Fantasia de Bombeira
Fantasia de Militar
Fantasia de Marinheira
Fantasia de Motociclista
Fantasia de Dançarina
Fantasia de Professora
Fantasia de Secretária
Fantasia de Chef
Fantasia de Jogadora
Fantasia de Gamer
Fantasia de Animadora
Fantasia de Atleta
Fantasia de Lutadora
Fantasia de Samurai
Fantasia de Ninja
Fantasia de Geisha
Fantasia de Egípcia
Fantasia de Grega
Fantasia de Romana
Fantasia de Viking
Fantasia de Medieval
Fantasia de Steampunk
Fantasia de Cyberpunk
Fantasia de Alien
Fantasia de Robô
Fantasia de Monstro
Fantasia de Fada
Fantasia de Sereia
...e muitos outros! Novas categorias podem ser adicionadas facilmente pelo painel admin, e cada uma possui sua própria página temática, galeria, opções de assinatura VIP e botões de pagamento.

Exemplos Específicos de Fetiches e Fantasias
Fetiche - Pés
Página: /fetiche/pes/page.tsx
Função: Galeria exclusiva de fotos e vídeos de pés, botão "Assinar VIP", botões de pagamento (PIX, PayPal, Google Pay)
Exemplo de botão:
<button className="bg-black text-neon-green border-2 border-neon-green shadow-neon-green">Assinar VIP Fetiche Pés</button>
Fantasia - Enfermeira
Página: /fantasia/enfermeira/page.tsx
Função: Galeria temática, opção de assinatura VIP, formulário para pedidos personalizados
Exemplo de botão:
<button className="bg-black text-neon-blue border-2 border-neon-blue shadow-neon-blue">Assinar VIP Fantasia Enfermeira</button>
Fetiche - BDSM
Página: /fetiche/bdsm/page.tsx
Função: Conteúdo temático, vídeos, chat privado, assinatura VIP
Exemplo de botão:
<button className="bg-black text-neon-green border-2 border-neon-green">Entrar no Chat BDSM VIP</button>
Fantasia - Cosplay
Página: /fantasia/cosplay/page.tsx
Função: Galeria de fotos e vídeos de cosplay, opção de assinatura VIP, pedidos de fantasias personalizadas
Exemplo de botão:
<button className="bg-black text-neon-blue border-2 border-neon-blue">Assinar VIP Cosplay</button>
Fetiche - Dominação
Página: /fetiche/dominacao/page.tsx
Função: Conteúdo exclusivo, vídeos, chat, assinatura VIP
Exemplo de botão:
<button className="bg-black text-neon-green border-2 border-neon-green">Assinar VIP Dominação</button>
Fantasia - Super-Herói
Página: /fantasia/superheroi/page.tsx
Função: Galeria temática, vídeos, pedidos personalizados, assinatura VIP
Exemplo de botão:
<button className="bg-black text-neon-blue border-2 border-neon-blue">Assinar VIP Super-Herói</button>
Esses exemplos mostram como cada categoria pode ter sua própria página, galeria, botões de assinatura VIP e funções específicas, facilitando a navegação e monetização de conteúdos temáticos.

Exemplos Específicos de Todas as Áreas do Sistema
Cadastro de Usuário
Página: /login/page.tsx Função: Cadastro por email ou Face ID Exemplo:

import { signInWithEmail, signInWithFaceId } from '../../services/firebase';
// Formulário de cadastro
Login
Página: /login/page.tsx Função: Login por email ou Face ID Exemplo:

<button onClick={signInWithEmail}>Entrar com Email</button>
<button onClick={signInWithFaceId}>Entrar com Face ID</button>
Upload de Conteúdo
Página: /admin/page.tsx, componente: PhotoGallery.tsx Função: Upload de fotos e vídeos Exemplo:

import PhotoGallery from '../components/PhotoGallery';
<PhotoGallery onUpload={handleUpload} />
Pagamento (PIX, PayPal, Google Pay)
Página: /vip/page.tsx, componente: PaymentButton.tsx Função: Assinatura VIP, compra de conteúdo Exemplo:

import PaymentButton from '../components/PaymentButton';
<PaymentButton method="pix" />
<PaymentButton method="paypal" />
<PaymentButton method="googlepay" />
Integração com Redes Sociais
Serviço: social.ts Função: Buscar feed do Instagram, Facebook, Twitter Exemplo:

import { fetchInstagramFeed, fetchFacebookFeed, fetchTwitterFeed } from '../../services/social';
const instagram = await fetchInstagramFeed();
Painel Admin
Página: /admin/page.tsx Função: Gerenciar produtos, fotos, vídeos, assinantes, avaliações Exemplo:

import ProductTable from '../../components/ProductTable';
import StatsDashboard from '../../components/StatsDashboard';
<ProductTable />
<StatsDashboard />
Fluxo de IA (Genkit)
Arquivo: src/ai/flows/translate.ts Função: Tradução automática Exemplo:

import { translate } from '@genkit-ai/core';
const resultado = await translate('Olá', { to: 'en' });
Backup e Migração
Script: deploy-firebase.js, botão: BackupButton.tsx Função: Exportar/importar dados do Firestore e Storage Exemplo:

import BackupButton from '../../components/BackupButton';
<BackupButton />
Menu Hamburguer
Componente: Header.tsx, MobileMenu.tsx Função: Navegação entre páginas principais e fetiches Exemplo:

import Header from '../components/Header';
<Header />
Fetiche/Fantasia
Página: /fetiche/pes/page.tsx, /fantasia/enfermeira/page.tsx Função: Galeria temática, assinatura VIP Exemplo:

<button className="bg-black text-neon-green">Assinar VIP Fetiche Pés</button>
<button className="bg-black text-neon-blue">Assinar VIP Fantasia Enfermeira</button>
Logout
Componente: Header.tsx, serviço: firebase.ts Função: Encerrar sessão e redirecionar para home Exemplo:

import { signOut } from '../../services/firebase';
<button onClick={signOut}>Logout</button>
Notificações
Componente: NotificationPanel.tsx Função: Exibir notificações para o usuário Exemplo:

import NotificationPanel from '../../components/NotificationPanel';
<NotificationPanel />
Esses exemplos cobrem as principais áreas do sistema, mostrando como implementar cada funcionalidade com componentes, serviços e páginas específicas.

Especificações Detalhadas dos Caminhos de Cada Página, Componente, Serviço e Item
Estrutura de Diretórios e Caminhos
Páginas (src/app/)
src/app/page.tsx: Página inicial pública (home)
src/app/admin/page.tsx: Painel admin
src/app/vip/page.tsx: Área VIP do assinante
src/app/login/page.tsx: Autenticação (Face ID, email)
src/app/gallery/page.tsx: Galeria pública/VIP
src/app/api/: Rotas de API (ex: src/app/api/payments.ts, src/app/api/hello/route.ts)
src/app/fetiche/[categoria]/page.tsx: Página de fetiche específica (ex: src/app/fetiche/pes/page.tsx)
src/app/fantasia/[categoria]/page.tsx: Página de fantasia específica (ex: src/app/fantasia/enfermeira/page.tsx)
src/app/admin/settings.tsx: Configurações do admin
Componentes (src/components/)
src/components/Header.tsx: Cabeçalho, menu hamburguer
src/components/Footer.tsx: Rodapé
src/components/ProductTable.tsx: Tabela de produtos
src/components/PhotoGallery.tsx: Galeria de fotos/vídeos
src/components/PaymentButton.tsx: Botões de pagamento
src/components/FaceAuthButton.tsx: Autenticação facial
src/components/IntegrationSwitch.tsx: Switches de integrações
src/components/StatsDashboard.tsx: Gráficos e estatísticas
src/components/ReviewModerator.tsx: Moderação de avaliações
src/components/BackupButton.tsx: Backup/migração
src/components/LogViewer.tsx: Visualização de logs
src/components/IAConfigForm.tsx: Configuração de IA
src/components/NotificationPanel.tsx: Notificações
Serviços (src/services/)
src/services/firebase.ts: Integração com Firebase (auth, firestore, storage, functions)
src/services/payments.ts: Integração com Mercado Pago, PayPal, Google Pay
src/services/ai.ts: Integração com Genkit, face-api.js
src/services/social.ts: Integração com Facebook, Instagram, Twitter
Utilitários (src/lib/)
src/lib/utils.ts: Funções utilitárias (formatação, validação)
Funções Customizadas (functions/)
functions/index.js: Funções Firebase Functions customizadas
Assets Públicos (public/)
public/: Imagens, ícones, scripts de teste, sw.js
public/firebase-messaging-sw.js: Service Worker do Firebase Messaging
public/test-upload-script.js: Script de teste de upload
Documentação (docs/)
docs/ORIENTACAO_GERAL.md: Orientação geral do sistema
docs/DEPLOY_VERCEL.md: Instruções de deploy Vercel
docs/GOOGLE_PAY_BOTOES_OFICIAIS.md: Detalhes sobre Google Pay
Configurações e Scripts (raiz do projeto)
.env.local: Variáveis de ambiente
firebase.json: Configuração do Firebase
firestore.rules: Regras de segurança Firestore
storage.rules: Regras de segurança Storage
database.rules.json: Regras de segurança Realtime Database
deploy.sh: Script de deploy automatizado
deploy-firebase.js: Script de deploy Firebase
next.config.js / next.config.mjs: Configuração do Next.js
tailwind.config.ts / tailwind.config.js: Configuração do Tailwind CSS
vercel.json: Configuração do Vercel
Exemplos de Caminhos Específicos
Firestore (firestore.rules):
Leitura: A leitura de dados públicos (produtos, fotos, vídeos, reviews aprovadas) é permitida para todos.
Escrita: Nenhuma escrita é permitida diretamente pelo cliente. Todas as modificações de dados são feitas de forma segura através do painel de administração, que utiliza credenciais de administrador no servidor (Admin SDK).
Realtime Database (database.rules.json):
Padrão: Todo o banco de dados é bloqueado para leitura e escrita por padrão.
Exceções: Apenas os dados de facialAuth/users (para verificação de login) e as conversas do chat (acessíveis apenas pelos participantes da conversa) têm permissões específicas.
Storage (storage.rules):
Leitura: A leitura de arquivos é pública para que as imagens e vídeos do site possam ser exibidos.
Escrita: O upload de novos arquivos é permitido apenas para usuários autenticados, o que na prática restringe essa ação ao painel de administração.
Página de fetiche "Pés": src/app/fetiche/pes/page.tsx
Página de fantasia "Enfermeira": src/app/fantasia/enfermeira/page.tsx
Botão de pagamento: src/components/PaymentButton.tsx
Serviço de IA: src/services/ai.ts
Função de backup: src/components/BackupButton.tsx
API de pagamentos: src/app/api/payments.ts
Script de deploy: deploy.sh
Regras do Firestore: firestore.rules
Documentação de deploy: docs/DEPLOY_VERCEL.md
4. Pagamentos
PIX (via Mercado Pago): Um modal customizado permite que clientes no Brasil gerem um QR Code PIX para pagamento.
PayPal: Um botão de pagamento direciona para o checkout do PayPal para pagamentos internacionais.
Variáveis de Ambiente (.env.local)
Para que o projeto funcione localmente, crie um arquivo .env.local na raiz e adicione as seguintes variáveis:

# Firebase (Cliente)
NEXT_PUBLIC_FIREBASE_API_KEY="AIza..."
NEXT_PUBLIC_MERCADOPAGO_PUBLIC_KEY="TEST-..."

# Firebase (Servidor - Admin SDK)
# Geralmente gerenciado pelo ambiente de hospedagem (ex: App Hosting)
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json"

# APIs de Terceiros
FACEBOOK_PAGE_ACCESS_TOKEN="EAA..."
INSTAGRAM_FEED_ACCESS_TOKEN="IGQVJ..."
INSTAGRAM_SHOP_ACCESS_TOKEN="IGQVJ..."
TWITTER_BEARER_TOKEN="AAAAA..."
MERCADOPAGO_ACCESS_TOKEN="APP_USR-..."
PAYPAL_CLIENT_ID="AZ..."
PAYPAL_CLIENT_SECRET="E..."

# Segurança dos Webhooks
GOOGLE_SHEETS_WEBHOOK_SECRET="seu_token_secreto_aqui"

# Cloudflare (Chat Externo - Se aplicável)
CLOUDFLARE_ORG_ID="..."
.# italosantos-com

italosantos
italosantos
Estrutura Resumida
src/app/
  page.tsx
  admin/page.tsx
  vip/page.tsx
  login/page.tsx
  gallery/page.tsx
  api/
  fetiche/[categoria]/page.tsx
  fantasia/[categoria]/page.tsx
  admin/settings.tsx
src/components/
  Header.tsx
  Footer.tsx
  ProductTable.tsx
  PhotoGallery.tsx
  PaymentButton.tsx
  FaceAuthButton.tsx
  IntegrationSwitch.tsx
  StatsDashboard.tsx
  ReviewModerator.tsx
  BackupButton.tsx
  LogViewer.tsx
  IAConfigForm.tsx
  NotificationPanel.tsx
src/services/
  firebase.ts
  payments.ts
  ai.ts
  social.ts
src/lib/
  utils.ts
functions/
  index.js
public/
  ...
docs/
  ...
.env.local
firebase.json
firestore.rules
storage.rules
database.rules.json
deploy.sh
deploy-firebase.js
next.config.js
tailwind.config.ts
vercel.json
