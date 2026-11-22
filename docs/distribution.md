# Distribution and code signing

AMFWX is a framework, not a distributor.

## Responsibility

Code signing, store submission, SmartScreen reputation and public
certificates are the responsibility of the **publisher, marketer or
distributor** of the final application.

The framework itself ships:

- unsigned development wheels
- test-signed local installers for development
- no public certificate
- no store account

## What a distributor must do

1. Build the final application with AMFWX.
2. Obtain a public code-signing certificate (OV/EV) or use a signing service.
3. Sign the final `.exe`/installer with a timestamp.
4. Publish and maintain the certificate.
5. Handle SmartScreen/reputation and store requirements.

## Local test signature

The development installer can be signed with a local test CA. That signature
is only valid on machines that trust that CA. It is not a release signature.

## What AMFWX provides

- installer/uninstaller tooling
- reproducible build scripts
- SHA-256 manifest for native DLLs
- `tools/verify_native.py`
- no hidden signing service, no external certificate dependency

## Legal situation

Code signing is not a general legal requirement for distributing a normal
Windows desktop application. It becomes relevant for:

- kernel drivers
- some enterprise/managed environments
- some stores or procurement rules
- regulated industries

For a normal downloaded EXE, Windows shows SmartScreen warnings for unsigned
or unknown binaries. That is a reputation/UX issue, not a general legal ban.

## Warum lokale Programme oft keine Warnung zeigen

Windows SmartScreen warnt vor allem bei Dateien, die aus dem Internet
stammen und ein Mark-of-the-Web (MOTW) tragen. Lokal gebaute, per USB
kopierte oder aus einem ZIP ohne MOTW entpackte EXEs starten meist ohne
Warnung, auch wenn sie unsigniert sind.

Das bedeutet nicht, dass die Datei signiert ist. Es bedeutet nur, dass
SmartScreen in diesem Kontext nicht ausgeloest wurde.

## Automation

A coding agent or CI system can run `signtool` or a cloud signing API, but it
cannot create a publicly trusted certificate by itself. The certificate and
private key (or a signing service account) must be provided by the publisher.

## Why this separation

A framework cannot know:

- who publishes the final app
- which legal entity is responsible
- which certificate/store account is used
- how long the certificate is valid

Those are distribution decisions.
