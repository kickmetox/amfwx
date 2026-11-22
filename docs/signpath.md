# SignPath Foundation

Ziel: öffentlich vertrauenswürdige Authenticode-Signatur für
`AMFWX-Own-Setup-*.exe` über die SignPath Foundation.

## Wichtig

Die SignPath Foundation stellt das Zertifikat aus. Der Herausgeber ist
damit **SignPath Foundation**, nicht AMFWX. Das ist der Preis der
kostenlosen Variante.

## 1. Antrag

1. [SignPath Foundation](https://signpath.org/) öffnen.
2. Open-Source-Projekt beantragen.
3. Öffentliches Repository und OSS-Lizenz angeben.
4. GitHub App „SignPath“ für das Repository installieren.
5. Projekt anlegen:
   - Project Slug: `amfwx`
   - Signing Policy: `release-signing`
   - Artifact Configuration: `amfwx-installer`

## 2. Artefakt-Konfiguration

Die Datei [signpath/artifact-configuration.xml](signpath/artifact-configuration.xml)
in SignPath als Artefakt-Konfiguration `amfwx-installer` hochladen.

## 3. GitHub Secrets/Variablen

Im Repository setzen:

- Secret `SIGNPATH_API_TOKEN`
- Variable `SIGNPATH_ORGANIZATION_ID`

Der Token wird in SignPath unter „API Tokens“ erzeugt.

## 4. Workflow

[.github/workflows/signpath.yml](.github/workflows/signpath.yml) baut:

1. `dist/AMFWX/AMFWX.exe`
2. `dist/AMFWX-Own-Setup-<version>.exe`
3. lädt den unsignierten Installer als GitHub-Artefakt hoch
4. sendet ihn an SignPath
5. lädt den signierten Installer als `signed-installer` hoch

## 5. Prüfung

Nach dem Lauf:

```powershell
Get-AuthenticodeSignature signed\AMFWX-Own-Setup-*.exe
```

Erwartet:

```text
Status : Valid
SignerCertificate.Subject : CN=SignPath Foundation, ...
```

## 6. Grenzen

- Herausgeber ist die Foundation.
- SignPath muss den Build als vertrauenswürdig einstufen.
- SmartScreen-Reputation beginnt bei null und wächst mit Downloads.
- Der private Schlüssel liegt bei SignPath; lokal wird nichts signiert.
- Kein Ersatz für ein eigenes EV-Zertifikat.

## 7. Lokale Testsignatur

Die lokale Test-CA bleibt nur für Entwicklung:

```text
dist/AMFWX-Own-Setup-<version>.exe
Status: Valid (nur auf diesem Rechner)
```

Sie wird nicht in den SignPath-Workflow hochgeladen.
