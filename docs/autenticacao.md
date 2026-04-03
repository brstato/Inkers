# 🔐 Documentação do Módulo de Autenticação (Login)

**Projeto:** CaixaCerto PWA  
**Caminho do módulo:** `controller/logincontroller.py`, `view/loginview.py`, `model/loginmodel.py`  
**Framework:** [Flet](https://flet.dev/) — UI Python multiplataforma (web, desktop, mobile)  
**Padrão arquitetural:** MVC (Model-View-Controller)  
**Data da documentação:** 31/03/2026  

---

## 📑 Índice

1. [Visão Geral](#1-visão-geral)
2. [Diagrama de Arquitetura](#2-diagrama-de-arquitetura)
3. [Fluxo de Autenticação](#3-fluxo-de-autenticação)
   - 3.1 [Login com Google (OAuth2)](#31-login-com-google-oauth2)
   - 3.2 [Login Tradicional (E-mail e Senha)](#32-login-tradicional-e-mail-e-senha)
   - 3.3 [Auto Login via Refresh Token](#33-auto-login-via-refresh-token)
   - 3.4 [Recuperação de Senha](#34-recuperação-de-senha)
4. [Model — `loginmodel.py`](#4-model--loginmodelpy)
5. [View — `loginview.py`](#5-view--loginviewpy)
6. [Controller — `logincontroller.py`](#6-controller--logincontrollerpy)
7. [Gerenciamento de Estado e Tokens](#7-gerenciamento-de-estado-e-tokens)
8. [Tratamento de Erros](#8-tratamento-de-erros)
9. [Variáveis de Ambiente](#9-variáveis-de-ambiente)
10. [Dependências](#10-dependências)
11. [Estado Atual da UI (Features Comentadas)](#11-estado-atual-da-ui-features-comentadas)
12. [Observações e Melhorias Sugeridas](#12-observações-e-melhorias-sugeridas)

---

## 1. Visão Geral

O módulo de autenticação é o ponto de entrada da aplicação CaixaCerto PWA. Ele é responsável por:

- Autenticar usuários via **Google OAuth2** (método principal ativo).
- Suportar autenticação tradicional via **e-mail e senha** (implementado, atualmente oculto na UI).
- Aplicar o fluxo de **Auto Login** com *refresh token* persistido no dispositivo.
- Iniciar o fluxo de **recuperação de senha** por e-mail.
- Armazenar tokens de acesso de forma **volátil** (sessão atual) e **persistente** (entre sessões).

### Rota associada

| Componente | Rota   | Observação                                |
|------------|--------|-------------------------------------------|
| `LoginView` | `/`   | Tela inicial para usuários não autenticados |
| Redirecionamento pós-login | `/main` | Rota de destino após autenticação bem-sucedida |

---

## 2. Diagrama de Arquitetura

```
┌───────────────────────────────────────────────────────────────────┐
│                         CAMADA DE VIEW                            │
│  LoginView (ft.View, rota="/")                                    │
│  ─ Componentes: logo, campos de texto, botões, progress_ring      │
│  ─ Delega todos os eventos ao LoginController                     │
└──────────────────────────┬────────────────────────────────────────┘
                           │ chama métodos do
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│                       CAMADA DE CONTROLLER                        │
│  LoginController                                                  │
│  ─ Lógica de negócio, OAuth2, gestão de tokens                    │
│  ─ Comunica-se com a View (feedback visual) e com o Model (dados) │
└──────────────────────────┬────────────────────────────────────────┘
                           │ chama métodos do
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│                        CAMADA DE MODEL                            │
│  LoginModel                                                       │
│  ─ Requisições HTTP assíncronas (httpx)                           │
│  ─ Comunica-se com a API backend                                  │
└──────────────────────────┬────────────────────────────────────────┘
                           │ retorna httpx.Response
                           ▼
                   [ API Backend REST ]
```

---

## 3. Fluxo de Autenticação

### 3.1 Login com Google (OAuth2)

Este é o **método principal ativo** na interface. O fluxo completo é:

```
Usuário clica em "Entrar"
        │
        ▼
LoginView._on_click_login_google()
        │
        ▼
LoginController.handle_login_google()
  └─ page.login(provider=GoogleOAuthProvider) → abre popup do Google
        │
        ▼ (callback de retorno)
LoginController.on_login(e)
  ├─ 1. Verifica se houve erro (e.error)
  ├─ 2. Obtém token_obj via page.auth.get_token()
  ├─ 3. Salva access_token e refresh_token na session.store
  ├─ 4. Extrai dados do usuário (email, sub/id, name)
  └─ 5. Chama LoginModel.login_google(g_mail, g_id, g_token, g_name)
              │
              ▼
        API Backend (/login_google)
              │
              ▼ resposta HTTP
  ├─ Status 200 → Extrai r_token, token, user_id
  │    ├─ Salva na session.store (volátil)
  │    ├─ Salva no SharedPreferences (persistente)
  │    └─ Navega para /main
  └─ Outro status → Exibe CustonDialog com mensagem de erro
```

**Escopos OAuth2 solicitados:**

| Escopo | Finalidade |
|--------|-----------|
| `userinfo.email` | Acesso ao e-mail da conta Google |
| `userinfo.profile` | Acesso ao nome e foto de perfil |
| `calendar` | Acesso ao Google Calendar (feature futura) |

> **Nota:** O parâmetro `?access_type=offline&prompt=consent` é adicionado ao endpoint de autorização para forçar a entrega de um `refresh_token` do Google, mesmo em logins repetidos.

---

### 3.2 Login Tradicional (E-mail e Senha)

> ⚠️ **Status:** A UI desta feature está comentada em `LoginView`. Toda a lógica de backend está implementada e funcional.

```
Usuário clica em "Entrar" (botão tradicional)
        │
        ▼
LoginView._on_click_login(e)
        │
        ▼
LoginController.handle_login(e, view_instance)
  ├─ 1. Valida campos (e-mail e senha não podem ser vazios)
  ├─ 2. Exibe progress_ring
  └─ 3. Chama LoginModel.login(email, senha)
              │
              ▼
        API Backend (/login)
              │
              ▼ resposta HTTP
  ├─ 200 → Salva tokens na session.store → Navega para /main
  ├─ 401 → "E-mail ou senha incorretos"
  ├─ 404 → "Usuário não encontrado"
  ├─ 422 → "Dados inválidos"
  └─ Outro → "Serviço indisponível"
```

**Payload enviado ao backend:**

```json
{
  "email": "usuario@exemplo.com",
  "senha": "senha_do_usuario"
}
```

---

### 3.3 Auto Login via Refresh Token

Executado automaticamente ao abrir a tela de login, sem interação do usuário:

```
LoginView.did_mount()
        │
        ▼ (em background, sem bloquear a UI)
LoginView._refresh_token_task()
        │
        ▼
LoginController.refresh_token(view_instance)
  ├─ 1. Lê r_token e id do SharedPreferences (persistente)
  ├─ 2. Se r_token existe:
  │    ├─ Exibe progress_ring
  │    └─ Chama LoginModel.refresh_token(r_token, id)
  │              │
  │              ▼ resposta HTTP
  │    ├─ 200 → Obtém new_token e new_r_token
  │    │    ├─ Atualiza SharedPreferences (new_r_token, id)
  │    │    ├─ Atualiza session.store (token, r_token, id)
  │    │    ├─ Restaura google_refresh_token na session.store
  │    │    └─ Navega para /main
  │    └─ Outro status → Limpa tokens (clear_persistent_tokens)
  └─ 3. Se r_token não existe: nenhuma ação (usuário vê tela de login)
```

**Payload enviado ao backend:**

```json
{
  "uuid": "id_do_usuario",
  "r_token": "refresh_token_armazenado"
}
```

---

### 3.4 Recuperação de Senha

```
Usuário clica em "Esqueci minha senha"
        │
        ▼
LoginView._on_click_forgot(e)
        │
        ▼
LoginController.handler_forgot_password(e, view_instance)
  ├─ 1. Valida se e-mail foi preenchido
  ├─ 2. Exibe progress_ring
  └─ 3. Chama LoginModel.recovery_password(email)
              │
              ▼ resposta HTTP
  ├─ 200 → Exibe mensagem de sucesso (message["message"])
  └─ 404 → Exibe mensagem de erro (message["message"])
```

**Payload enviado ao backend:**

```json
{
  "email": "usuario@exemplo.com"
}
```

---

## 4. Model — `loginmodel.py`

**Arquivo:** `model/loginmodel.py`  
**Classe:** `LoginModel`  
**Biblioteca HTTP:** `httpx` (cliente assíncrono)

### Atributos de Classe (Endpoints)

Os endpoints são configurados centralizadamente em `model.config.Config`:

| Atributo | Constante de Config | Finalidade |
|----------|---------------------|-----------|
| `loginURL` | `Config.LOGIN_URL` | Autenticação e-mail/senha |
| `logingoogleURL` | `Config.LOGIN_GOOGLE_URL` | Autenticação via Google |
| `refreshTokenURL` | `Config.REFRESH_TOKEN_URL` | Renovação de token |
| `recovery_passwordURL` | `Config.RECOVERY_PASSWORD_URL` | Recuperação de senha |

### Métodos

---

#### `login_google(g_email, g_id, g_token, g_name) → httpx.Response`

Autentica um usuário identificado pelo provedor Google junto ao backend da aplicação.

**Parâmetros:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `g_email` | `str` | E-mail da conta Google do usuário |
| `g_id` | `str` | Identificador único (`sub`) da conta Google |
| `g_token` | `str` | Access token emitido pelo Google OAuth2 |
| `g_name` | `str` | Nome completo do usuário na conta Google |

**Payload HTTP (POST):**
```json
{
  "g_email": "usuario@gmail.com",
  "g_id": "109876543210987654321",
  "g_token": "ya29.a0...",
  "g_name": "Nome Sobrenome"
}
```

**Retorno:** `httpx.Response` com o resultado da requisição ao backend.

---

#### `login(username, password) → httpx.Response`

Autentica um usuário com credenciais tradicionais (e-mail e senha).

**Parâmetros:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `username` | `str` | Endereço de e-mail do usuário |
| `password` | `str` | Senha em texto simples (a criptografia é responsabilidade do backend) |

**Payload HTTP (POST):**
```json
{
  "email": "usuario@exemplo.com",
  "senha": "minhasenha"
}
```

**Retorno:** `httpx.Response` com o resultado da requisição ao backend.

---

#### `refresh_token(r_token, id) → httpx.Response`

Renova a sessão do usuário usando um *refresh token* previamente armazenado.

**Parâmetros:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `r_token` | `str` | Refresh token armazenado via `SharedPreferences` |
| `id` | `str` | ID do usuário armazenado localmente |

**Payload HTTP (POST):**
```json
{
  "uuid": "id_do_usuario",
  "r_token": "eyJhbGciO..."
}
```

**Retorno:** `httpx.Response` com novo `token` e `r_token` em caso de sucesso.

---

#### `recovery_password(username) → httpx.Response`

Dispara o fluxo de recuperação de senha por e-mail no backend.

**Parâmetros:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `username` | `str` | E-mail do usuário que solicitou a recuperação |

**Payload HTTP (POST):**
```json
{
  "email": "usuario@exemplo.com"
}
```

> **Nota:** Este método define `timeout=30` segundos (explícito), enquanto os demais usam o timeout padrão do `httpx`.

**Retorno:** `httpx.Response`. O campo `message` no JSON de resposta contém o texto a ser exibido ao usuário.

---

## 5. View — `loginview.py`

**Arquivo:** `view/loginview.py`  
**Classe:** `LoginView(ft.View)`  
**Rota:** `/`  
**Cor de fundo:** `AppColors.BACKGROUND_DARK`

### Inicialização (`__init__`)

No construtor, a View:
1. Instancia o `LoginController(page)`.
2. Cria todos os componentes visuais.
3. Define o layout (`self.controls`).

### Componentes Visuais

| Atributo | Tipo Flet | Visível na UI | Descrição |
|----------|-----------|:-------------:|-----------|
| `logo` | `ft.Image` | ✅ | Logotipo da aplicação (`inkers_logo.png`, 300px de largura) |
| `progress_ring` | `CustonProgressRing` | Condicional | Spinner de carregamento, exibido durante operações assíncronas |
| `txt_username` | `CustomTextField` | ❌ (comentado) | Campo de entrada para e-mail |
| `txt_password` | `CustomTextField` | ❌ (comentado) | Campo de entrada para senha (com toggle de visibilidade) |
| `btn_login_google` | `ft.Row` + `ft.Button` | ✅ | Botão principal "Entrar" com OAuth Google — cor `ORANGE_DARK` |
| `btn_login` | `ft.Row` + `ft.Button` | ❌ (comentado) | Botão "Entrar" tradicional — cor `ORANGE_BURNT` |
| `btn_create_account` | `ft.Row` + `ft.OutlinedButton` | ❌ (comentado) | Botão "Criar Conta" |
| `btn_forgot_password` | `ft.Row` + `ft.OutlinedButton` | ❌ (comentado) | Botão "Esqueci minha senha" |
| `btn_support` | `ft.Row` + `ft.OutlinedButton` | ✅ | Link para suporte via WhatsApp (`wa.me/...`) |
| `infor` | `ft.Row` + `ft.TextButton` | ✅ | Link para o site `inkers.com.br` |

### Layout

```
ft.Stack (expand=True)
├── ft.Container (alignment=CENTER, expand=True)
│   └── ft.Container (padding=40)
│       └── ft.Column
│           ├── logo
│           ├── btn_login_google   ← visível
│           ├── btn_support        ← visível
│           └── infor              ← visível
└── progress_ring                  ← sobreposto ao conteúdo (z-index)
```

### Métodos

---

#### `did_mount(self)`

Ciclo de vida do Flet, chamado automaticamente quando a view é montada na página.  
Agenda a tarefa de *auto login* em background via `page.run_task()`.

```python
def did_mount(self):
    self.page.run_task(self._refresh_token_task)
```

> **Importante:** Este método usa `run_task` (e não `await`) para não bloquear a thread principal da UI enquanto a requisição de refresh token ocorre.

---

#### `_refresh_token_task(self)` *(async)*

Wrapper assíncrono que delega ao controller o processo de tentativa de *auto login*.

---

#### `_go_to_account(self, e)` *(async)*

Navega para a rota `/account` (cadastro de nova conta). Atualmente, o botão que chama este método está **comentado** no layout.

---

#### `_on_click_login_google(self, e)` *(async)*

Delegação do clique no botão Google para `LoginController.handle_login_google()`.

---

#### `_on_click_login(self, e)` *(async)*

Delegação do clique no botão de login tradicional para `LoginController.handle_login(e, self)`.

---

#### `_on_click_forgot(self, e)` *(async)*

Delegação do clique em "Esqueci minha senha" para `LoginController.handler_forgot_password(e, self)`.

---

## 6. Controller — `logincontroller.py`

**Arquivo:** `controller/logincontroller.py`  
**Classe:** `LoginController`  
**Dependências internas:** `LoginModel`, `CustonDialog`, `ProtectedApiCall`

### Inicialização (`__init__`)

O construtor recebe o objeto `page: ft.Page` e configura todo o ambiente OAuth2:

1. **Lê credenciais** via variáveis de ambiente (`CLIENT_ID`, `SECRET_ID`).
2. **Determina o redirect URI** dinamicamente a partir da URL atual da página:
   ```python
   self.parsed_url = urlparse(self.page.url)
   self.base_domain = f"https://{self.parsed_url.netloc}/oauth_callback"
   ```
3. **Instancia o `GoogleOAuthProvider`** com `client_id`, `secret_id` e o `redirect_uri` dinâmico.
4. **Estende os escopos** OAuth2 (email, profile, calendar).
5. **Adiciona parâmetros extras** ao endpoint de autorização: `access_type=offline&prompt=consent`.
6. **Registra o callback** `on_login` na página: `self.page.on_login = self.on_login`.

### Métodos

---

#### `handle_login_google(self)` *(async)*

Inicia o fluxo de login do Google pelo Flet, abrindo o popup/redirecionamento de autorização.

```python
async def handle_login_google(self):
    await self.page.login(provider=self.provider)
```

---

#### `on_login(self, e)` *(async)* — Callback OAuth2

Ponto de retorno após o usuário autorizar (ou negar) no provedor Google. É o método mais crítico do fluxo OAuth2.

**Sequência de execução:**

| Passo | Ação | Detalhe |
|-------|------|---------|
| 1 | Verificação de erro | Se `e.error` existe, exibe `SnackBar` e encerra |
| 2 | Obtenção do token | `await self.page.auth.get_token()` → `token_obj` |
| 3 | Persistência dos tokens Google | Salva `access_token` e `refresh_token` na `session.store` |
| 4 | Extração dos dados do usuário | `g_mail`, `g_id` (`sub`), `g_name` de `page.auth.user` |
| 5 | Chamada ao backend | `LoginModel.login_google(...)` |
| 6 | Processamento da resposta | Salva tokens da API e navega para `/main` se status 200 |
| 7 | Tratamento de erro | Exibe `CustonDialog` com o status HTTP recebido |

**Dados salvos após login Google bem-sucedido:**

| Armazenamento | Chave | Valor |
|--------------|-------|-------|
| `session.store` | `google_access_token` | Token de acesso Google |
| `session.store` | `google_refresh_token` | Refresh token Google |
| `session.store` | `r_token` | Refresh token da API backend |
| `session.store` | `token` | Token de acesso da API backend |
| `session.store` | `id` | ID do usuário na API backend |
| `SharedPreferences` | `r_token` | Refresh token (persistente) |
| `SharedPreferences` | `id` | ID do usuário (persistente) |
| `SharedPreferences` | `google_refresh_token` | Refresh token Google (persistente) |
| `SharedPreferences` | `login_method` | `"google"` (persistente) |

---

#### `refresh_token(self, view_instance)` *(async)*

Tenta renovar a sessão do usuário automaticamente usando o *refresh token* persistido.

**Lógica:**
1. Lê `r_token` e `id` do `SharedPreferences`.
2. Se existir, exibe `progress_ring` e chama o model.
3. **Sucesso (200):** Atualiza todos os storages e navega para `/main`.
4. **Falha:** Chama `clear_persistent_tokens()` para limpar os dados inválidos e deixar o usuário na tela de login.
5. Oculta o `progress_ring` ao final, independente do resultado.

---

#### `clear_persistent_tokens(self)` *(async)*

Remove todas as chaves de autenticação do `SharedPreferences`, forçando o usuário a realizar um novo login completo.

**Chaves removidas:**
- `r_token`
- `id`
- `google_refresh_token`
- `login_method`

---

#### `handle_login(self, e, view_instance)` *(async)*

Gerencia o fluxo de login tradicional com e-mail e senha.

**Validações e respostas:**

| Status HTTP | Título do Dialog | Mensagem exibida |
|-------------|-----------------|-----------------|
| Campos vazios | "Atenção" | "Por favor, preencha o e-mail e a senha." |
| 200 | — | Navega para `/main` |
| 401 | "Acesso Negado" | "E-mail ou senha incorretos." |
| 404 | "Usuário não encontrado" | "Não encontramos uma conta com esse e-mail." |
| 422 | "Dados inválidos" | "Verifique os dados informados e tente novamente." |
| Outros | "Serviço indisponível" | "Não foi possível realizar o login no momento." |
| Exceção | "Erro de conexão" | "Não foi possível conectar ao servidor." |

> **Nota:** Em todos os casos de erro, o `progress_ring` é ocultado antes de exibir o dialog.

---

#### `handler_forgot_password(self, e, view_instance)` *(async)*

Gerencia o fluxo de recuperação de senha.

**Validações e respostas:**

| Condição | Ação |
|----------|------|
| E-mail vazio | Exibe dialog "Por favor informe o email." |
| 200 | Exibe dialog com `message["message"]` (retorno do backend) |
| 404 | Exibe dialog com `message["message"]` (retorno do backend) |

---

#### `fetch_google_calendar_events(self)` *(async)* — Feature futura

> ⚠️ **Status:** Método implementado, mas **não está sendo chamado** (linha de chamada comentada em `on_login`).

Realiza uma chamada direta à Google Calendar API para buscar os próximos 10 eventos do usuário, usando a biblioteca `requests` de forma síncrona.

**Parâmetros da requisição:**

| Parâmetro | Valor |
|-----------|-------|
| URL | `https://www.googleapis.com/calendar/v3/calendars/primary/events` |
| Header | `Authorization: Bearer {access_token}` |
| `timeMin` | Data/hora atual UTC (ISO 8601) |
| `maxResults` | 10 |
| `singleEvents` | `true` |
| `orderBy` | `startTime` |

> ⚠️ **Atenção:** Este método usa `requests` (síncrono) em vez de `httpx` (assíncrono), o que pode bloquear o event loop do Flet. Recomenda-se migrar para `httpx.AsyncClient` para consistência.

---

## 7. Gerenciamento de Estado e Tokens

A aplicação utiliza dois mecanismos distintos de armazenamento para tokens:

### Comparativo dos Mecanismos de Storage

| Característica | `page.session.store` | `ft.SharedPreferences` |
|----------------|---------------------|----------------------|
| **Persistência** | Volátil (memória) | Permanente (device storage) |
| **Escopo** | Sessão atual | Entre sessões |
| **Leitura** | Síncrona | Assíncrona (`await`) |
| **Uso** | Acesso rápido durante uso | Auto login na próxima abertura |
| **Limpeza** | Automática ao fechar app | Manual (`remove()`) |

### Tokens Armazenados

| Token | Origem | Via volátil | Via persistente | Finalidade |
|-------|--------|:-----------:|:---------------:|-----------|
| `token` | Backend API | ✅ | ❌ | Autorização nas chamadas à API |
| `r_token` | Backend API | ✅ | ✅ | Renovar o `token` sem novo login |
| `id` | Backend API | ✅ | ✅ | Identificar o usuário nas requisições |
| `google_access_token` | Google OAuth2 | ✅ | ❌ | Acesso atual a APIs do Google |
| `google_refresh_token` | Google OAuth2 | ✅ | ✅ | Renovar o access token do Google |
| `login_method` | Lógica interna | ❌ | ✅ | Saber como refazer o login (ex: "google") |

---

## 8. Tratamento de Erros

### Erros de Autenticação Google

| Situação | Comportamento |
|----------|---------------|
| `e.error` presente | Exibe `SnackBar` com mensagem de erro e encerra |
| Falha na comunicação com backend | Exibe `CustonDialog` com status HTTP |
| Exceção genérica | `print` no console (log técnico) |

### Erros de Login Tradicional

Todos os erros são capturados em bloco `try/except`. Erros HTTP específicos recebem mensagens amigáveis. Exceções genéricas geram uma mensagem de "Erro de conexão" ao usuário.

### Princípio de Mensagens de Erro

Os erros técnicos (status HTTP inesperado, exceções de rede) são registrados apenas via `print()` no console do servidor. Para o usuário, são sempre exibidas mensagens genéricas e amigáveis via `CustonDialog`, sem expor detalhes técnicos.

---

## 9. Variáveis de Ambiente

A aplicação requer as seguintes variáveis de ambiente configuradas:

| Variável | Uso em código | Descrição |
|----------|--------------|-----------|
| `CLIENT_ID` | `os.getenv('CLIENT_ID')` | Client ID do projeto no Google Cloud Console |
| `SECRET_ID` | `os.getenv('SECRET_ID')` | Client Secret do projeto no Google Cloud Console |

> **Segurança:** As credenciais OAuth2 (anteriormente hardcoded e visíveis nos comentários do código) foram corretamente migradas para variáveis de ambiente, evitando sua exposição em repositórios de código.

---

## 10. Dependências

### Dependências Python (do módulo)

| Biblioteca | Uso |
|-----------|-----|
| `flet` | Framework de UI e OAuth2 |
| `flet.auth.providers.GoogleOAuthProvider` | Provedor de autenticação Google |
| `httpx` | Cliente HTTP assíncrono (Model) |
| `requests` | Cliente HTTP síncrono (usado apenas em `fetch_google_calendar_events`) |
| `urllib.parse.urlparse` | Parsing da URL base para construir o redirect URI |
| `json` | Parse das respostas da API |
| `os` | Leitura das variáveis de ambiente |
| `datetime` | Obtenção de data/hora atual para Google Calendar |

### Dependências Internas do Projeto

| Módulo | Importado em | Finalidade |
|--------|-------------|-----------|
| `model.loginmodel.LoginModel` | Controller | Acesso à API backend |
| `model.config.Config` | Model | Centralização de URLs |
| `controller.call_api.ProtectedApiCall` | Controller | (Importado, mas não usado diretamente no arquivo) |
| `view.controls.custondialog.CustonDialog` | Controller | Exibição de modais de feedback |
| `view.controls.colors.AppColors` | View | Paleta de cores da aplicação |
| `view.controls.custontextfield.CustomTextField` | View | Campo de texto customizado |
| `view.controls.custonprogressring.CustonProgressRing` | View | Indicador de carregamento |

---

## 11. Estado Atual da UI (Features Comentadas)

O código demonstra uma evolução em andamento. A tabela abaixo documenta o estado atual de cada feature visível na UI:

| Feature | Código | UI Visível | Motivo presumido |
|---------|--------|:----------:|-----------------|
| Login com Google | Completo | ✅ | Método principal ativo |
| Logo da aplicação | Completo | ✅ | — |
| Link de suporte (WhatsApp) | Completo | ✅ | — |
| Link do site (inkers.com.br) | Completo | ✅ | — |
| Campo de e-mail | Completo | ❌ | Oculto enquanto apenas Google OAuth está ativo |
| Campo de senha | Completo | ❌ | Idem |
| Botão "Entrar" (tradicional) | Completo | ❌ | Idem |
| Botão "Criar Conta" | Completo | ❌ | Feature pausada ou não liberada |
| Botão "Esqueci minha senha" | Completo | ❌ | Feature pausada ou não liberada |
| Google Calendar | Implementado | ❌ | Chamada comentada; feature futura |

---

## 12. Observações e Melhorias Sugeridas

| # | Categoria | Observação |
|---|-----------|------------|
| 1 | ⚠️ Inconsistência assíncrona | `fetch_google_calendar_events` usa `requests` (bloqueante) num contexto assíncrono. Substituir por `httpx.AsyncClient` para evitar bloqueio do event loop. |
| 2 | 🔐 Credenciais hardcoded | As linhas com `client_id` e `id_secreto` hardcoded ainda aparecem como comentários (`#`) no código. Recomenda-se removê-las definitivamente do arquivo. |
| 3 | 📦 Importação não utilizada | `ProtectedApiCall` é importado no controller mas não é usado no arquivo. Verificar se é necessário ou remover. |
| 4 | 🔄 Navegação inconsistente | `on_login` usa `self.page.go("/main")` enquanto `refresh_token` usa `await self.page.push_route("/main")`. Padronizar o método de navegação. |
| 5 | 📝 Logging | Os erros são tratados apenas com `print()`. Considerar a adoção de um sistema de logging (`logging` module) com níveis (DEBUG, INFO, ERROR) para melhor rastreabilidade em produção. |
| 6 | ⏱️ Timeout ausente | `login()` e `login_google()` não definem timeout explícito no `httpx.AsyncClient`, podendo ficar travados indefinidamente. Adicionar timeout como em `recovery_password`. |
