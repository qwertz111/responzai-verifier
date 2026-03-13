# GitHub Setup für responzai — Kompletter Plan

Dieser Plan führt dich Schritt für Schritt durch die Erstellung der 3 GitHub-Repos und deren Konfiguration.

---

## Phase 1: Repos anlegen

### Schritt 1.1: GitHub CLI vorbereiten
```bash
# Installationsstatus prüfen
gh --version

# Falls nicht installiert, siehe https://cli.github.com/

# Falls noch nicht eingeloggt:
gh auth login
```

### Schritt 1.2: Erste Repo anlegen — responzai-verifier
```bash
cd /c/Projekte/Agentensystem_responzai-eu

# Repo auf GitHub erstellen und lokales Repo mit origin verknüpfen
gh repo create responzai-verifier \
  --public \
  --description "AI Agent Pipeline for Text Verification & Improvement (EU AI Act)" \
  --source=. \
  --remote=origin \
  --push
```

**Was macht dieser Befehl:**
- Erstellt ein öffentliches Repo auf GitHub
- Setzt `origin` auf dein neues GitHub-Repo
- Pushed den aktuellen Code (alle lokalen Commits) rauf
- Die `.gitignore` (Python) wird automatisch hinzugefügt

### Schritt 1.3: zweite + dritte Repos (leer, für später)

Diese Repos werden später befüllt, wenn die Code-Struktur aufgeteilt wird:

```bash
# responzai-knowledge (leer anlegen, wird später befüllt)
gh repo create responzai-knowledge \
  --public \
  --description "Knowledge Base: EU AI Act, Regulations, Case Law" \
  --gitignore=Python

# responzai-web (leer anlegen, wird später befüllt)
gh repo create responzai-web \
  --public \
  --description "Frontend Website & Dashboard for responzai" \
  --gitignore=Node
```

**Ergebnis:** Du hast jetzt 3 Repos auf GitHub. Der aktuelle Code ist in `responzai-verifier` gepusht.

---

## Phase 2: Branch-Schutzregeln

Diese Regeln verhindern, dass Code direkt auf `main` gepusht wird — alles läuft über Pull Requests.

### Schritt 2.1: `main`-Branch schützen

Für jedes Repo (`responzai-verifier`, `responzai-knowledge`, `responzai-web`):

1. Gehe zu **GitHub** → dein Repo → **Settings** → **Branches**
2. Klick auf **Add rule** (oder **Edit** falls `main` schon existiert)
3. Regel-Name: `main`
4. Aktiviere:
   - ☑ **Require a pull request before merging**
   - ☑ **Require approvals** (1 approval)
   - ☑ **Require status checks to pass before merging**
   - ☑ **Require branches to be up to date before merging**
5. Klick **Save changes**

### Schritt 2.2: Status-Checks verknüpfen (nach Phase 7 / CI/CD Setup)

Nach Phase 7, wenn GitHub Actions läuft:
- Gehe wieder zu **Branches** → **Edit** für `main`
- Under "Require status checks to pass before merging":
  - Suche und wähle: `test` (oder wie dein Check heisst)
  - Suche und wähle: `lint` (falls vorhanden)
- Speichern

---

## Phase 3: GitHub Secrets (für CI/CD & Deployment)

Diese Secrets sind Passwörter/API-Keys, die nur in GitHub Actions verfügbar sind (nicht sichtbar in Repos).

### Schritt 3.1: Secrets hinzufügen

Für `responzai-verifier`:

1. **GitHub** → Repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** — füge diese hinzu:

| Name | Wert | Beschreibung |
|------|------|-------------|
| `ANTHROPIC_API_KEY` | dein API-Key | Für Claude API-Calls in Tests |
| `VOYAGE_API_KEY` | dein API-Key | Für Voyage-3 Embeddings |
| `POSTGRES_PASSWORD` | sicheres Passwort | Für DB in CI/CD Tests |

**Wie du die Keys findest:**
- `ANTHROPIC_API_KEY`: https://console.anthropic.com/account/keys
- `VOYAGE_API_KEY`: https://dash.voyageai.com/api-keys
- `POSTGRES_PASSWORD`: Du kannst hier ein beliebiges Passwort setzen (z.B. `testing_only_123`)

### Schritt 3.2: Deploy-Secrets (nur für responzai-web, später)

Nach Phase 9 (Deployment):
- `CLOUDFLARE_API_TOKEN`: Für Cloudflare Pages Deployment
- `CLOUDFLARE_ACCOUNT_ID`: Deine Cloudflare Account-ID

---

## Phase 4: Lokale Git-Konfiguration

### Schritt 4.1: Globale Git-Konfiguration (einmalig)
```bash
git config --global user.name "Dein Name"
git config --global user.email "deine@email.com"
```

### Schritt 4.2: SSH-Key (optional, aber empfohlen)

Falls du noch keinen SSH-Key hast:

```bash
ssh-keygen -t ed25519 -C "deine@email.com"
# → Akzeptiere alle Defaults (Enter, Enter, Enter)
# → Key wird unter ~/.ssh/id_ed25519 gespeichert

# Key zu GitHub hinzufügen:
gh ssh-key add ~/.ssh/id_ed25519.pub --title "My Machine"

# Test:
ssh -T git@github.com
# → Sollte sagen: "Hi [username]! You've successfully authenticated..."
```

---

## Phase 5: Erstes Push & Verifikation

### Schritt 5.1: Status checken
```bash
cd /c/Projekte/Agentensystem_responzai-eu
git status
git log --oneline -5
```

### Schritt 5.2: Remote checken
```bash
git remote -v
# Sollte zeigen:
# origin  https://github.com/[username]/responzai-verifier.git (fetch)
# origin  https://github.com/[username]/responzai-verifier.git (push)
```

### Schritt 5.3: Verifikation auf GitHub

Gehe zu:
- https://github.com/[dein-username]/responzai-verifier
- Solltest du alle Dateien + Commits sehen

---

## Phase 6: Workflow für zukünftige Entwicklung

Sobald alles Setup ist, funktioniert die tägliche Arbeit so:

```bash
# Feature-Branch erstellen
git checkout -b feature/deine-feature

# Änderungen machen, committen
git add .
git commit -m "feature: beschreibung"

# Push zu GitHub
git push origin feature/deine-feature

# → Auf GitHub: "Create Pull Request"-Button wird angezeigt
# → PR öffnen, Code Review, Merge nach Approval
```

---

## Checkliste: Was du nacheinander machen musst

- [ ] **1.1** `gh --version` prüfen, ggf. installieren
- [ ] **1.1** `gh auth login` (einmalig)
- [ ] **1.2** `responzai-verifier` Push mit `gh repo create`
- [ ] **1.3** `responzai-knowledge` Repo anlegen (leer)
- [ ] **1.3** `responzai-web` Repo anlegen (leer)
- [ ] **2.1** `main`-Branch schützen (alle 3 Repos)
- [ ] **3.1** GitHub Secrets hinzufügen für `responzai-verifier`
- [ ] **4.1** Git global konfigurieren
- [ ] **4.2** SSH-Key erstellen + zu GitHub hinzufügen (optional)
- [ ] **5.3** Auf GitHub verifizieren, dass Code da ist

---

## Troubleshooting

### Problem: "Authentication failed"
**Lösung:**
```bash
# SSH verwenden (empfohlen):
git remote set-url origin git@github.com:[username]/responzai-verifier.git

# Oder GitHub CLI neu authentifizieren:
gh auth logout
gh auth login
```

### Problem: "Repository already exists"
**Lösung:** Repo existiert schon auf GitHub. Entweder:
- Manuell löschen: GitHub → Settings → **Delete this repository**
- Oder: Lokal einen anderen Namen wählen: `gh repo create responzai-verifier-v2`

### Problem: "No commits yet on main"
**Lösung:** Du brauchst mindestens einen Commit lokal:
```bash
echo "# responzai" > README.md
git add README.md
git commit -m "Initial commit"
git push -u origin main
```

---

**Nächster Schritt nach diesem Setup:** Phase 7 → CI/CD Pipelines (GitHub Actions)
