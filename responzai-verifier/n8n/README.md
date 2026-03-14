# n8n Workflows fuer responzai

## Workflows

| Datei | Name | Trigger |
|-------|------|---------|
| 01_weekly_verification.json | Woechentlicher Prueflauf | Cron: Mo 06:00 |
| 02_eurlex_monitoring.json | EUR-Lex Monitoring (Pia) | Cron: Taeglich 07:00 |
| 03_newsletter_check.json | Newsletter-Pruefung | Webhook: POST /newsletter-published |
| 04_pre_publication_check.json | Pre-Publication Check | Webhook: POST /pre-publish |

## Import in n8n

1. n8n oeffnen: `http://37.27.11.4:5678`
2. Menu > Workflows > Import from File
3. Jede JSON-Datei einzeln importieren
4. In jedem Workflow: E-Mail-Adressen und URLs anpassen

## SMTP-Konfiguration

Die E-Mail-Nodes benoetigen SMTP-Zugangsdaten. Diese werden in n8n als **Credentials** konfiguriert:

1. In n8n: Menu > Credentials > Add Credential > SMTP
2. Folgende Werte eintragen:

```
Host:     smtp.example.com     (z.B. smtp.ionos.de, smtp.gmail.com)
Port:     587
Security: STARTTLS
User:     verifier@responzai.eu
Password: [SMTP-Passwort]
```

3. Credential speichern
4. In jedem Workflow die E-Mail-Nodes oeffnen und das SMTP-Credential auswaehlen

### Umgebungsvariablen

Die Workflows nutzen `$env.ALERT_EMAIL` fuer die Empfaenger-Adresse. In der n8n docker-compose config:

```yaml
environment:
  - ALERT_EMAIL=deine-email@example.com
```

Alternativ: In jedem E-Mail-Node die Adresse direkt eintragen.

## Anpassungen nach Import

### Workflow 1 (Woechentlicher Prueflauf)
- E-Mail-Adresse anpassen (oder ALERT_EMAIL env setzen)
- SMTP-Credential zuweisen

### Workflow 2 (EUR-Lex Monitoring)
- EUR-Lex RSS Feed URL: Die `AI_ACT_FEED_ID` durch eine echte Feed-ID ersetzen
  (EUR-Lex > Suche nach "AI Act" > RSS-Feed abonnieren > URL kopieren)
- SMTP-Credential zuweisen

### Workflow 3 (Newsletter-Pruefung)
- Webhook-URL notieren: `http://37.27.11.4:5678/webhook/newsletter-published`
- In CMS/Newsletter-Tool als Webhook konfigurieren
- SMTP-Credential zuweisen

### Workflow 4 (Pre-Publication Check)
- Webhook-URL notieren: `http://37.27.11.4:5678/webhook/pre-publish`
- In CMS als Pre-Publish-Hook konfigurieren
- SMTP-Credential zuweisen
