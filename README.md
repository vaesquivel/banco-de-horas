# Banco de Horas

Aplicativo web para controle pessoal de banco de horas. Cada colega tem seus próprios dados — tudo salvo localmente no navegador, sem servidor, sem conta.

---

## Como compartilhar com colegas via GitHub Pages

### Passo 1 — Crie um repositório no GitHub

1. Acesse [github.com](https://github.com) e entre na sua conta (ou crie uma gratuitamente)
2. Clique em **New repository** (botão verde no canto superior direito)
3. Dê o nome `banco-de-horas`
4. Deixe como **Public**
5. Clique em **Create repository**

### Passo 2 — Envie os arquivos

Na página do repositório recém-criado, clique em **uploading an existing file** e arraste (ou selecione) os seguintes arquivos da pasta `banco-de-horas`:

```
index.html
manifest.json
sw.js
icon.svg
```

Clique em **Commit changes**.

### Passo 3 — Ative o GitHub Pages

1. No repositório, clique em **Settings** (aba no topo)
2. No menu lateral, clique em **Pages**
3. Em **Source**, selecione **Deploy from a branch**
4. Em **Branch**, selecione `main` e pasta `/ (root)`
5. Clique em **Save**

Aguarde 1–2 minutos. O GitHub vai exibir a URL do app, no formato:

```
https://SEU-USUARIO.github.io/banco-de-horas/
```

### Passo 4 — Compartilhe

Envie esse link para os colegas. Cada um abre no navegador, clica em **✎ editar** e configura:

- **Nome** (aparece no cabeçalho)
- **Data de início** do controle
- **Horário de entrada e saída**
- **Dias de Home Office** (cada um marca os próprios dias)

Os dados ficam salvos apenas no navegador de cada pessoa. Ninguém vê os dados de ninguém.

---

## Uso do app

| Ação | Como fazer |
|------|-----------|
| Registrar um dia | Clicar na linha do dia |
| Editar configurações | Clicar em **✎ editar** no cabeçalho |
| Navegar por meses | Clicar nas abas Jan–Dez |
| Marcar Home Office | Marcar a caixa "🏠 Home Office" ao registrar o dia |
| Excluir registro | Abrir o dia e clicar em **Excluir** |

## Tipos de registro

- **Trabalhado** — dia normal; informe entrada e saída
- **Abono / HO** — dia de abono ou home office sem necessidade de registrar horas
- **Feriado** — não conta como falta nem saldo
- **Falta** — desconta a carga horária do dia

---

> Os dados são armazenados em `localStorage` no próprio navegador. Limpar os dados do site apaga o histórico.
