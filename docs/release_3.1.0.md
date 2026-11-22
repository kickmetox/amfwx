# AMFWX 3.1.0

AMFWX 3.1 closes the AI/SDK hardening gaps and adds CI, SBOM and an
installer test.

## New

- streaming for Ollama and OpenAI-compatible providers
- retry/backoff for HTTP providers
- conversation persistence (`Conversation`)
- DPAPI-backed `KeyStore`
- Ollama `pull`/`delete`
- `ProgressBar` UI tool
- optional live Ollama test
- GitHub Actions CI without any signing integration
- SBOM generation (`tools/sbom.py`)
- installer silent install/uninstall test

## Assets

- `amfwx-3.1.0-py3-none-any.whl`
- `AMFWX-Portable-3.1.0.zip`
- `AMFWX-Own-Setup-3.1.0.exe` (unsigned)
- `SHA256SUMS.txt`

## Tests

167 tests, 1 optional live Ollama test skipped unless enabled.

## Notes

- Windows 10/11 x64
- code signing is intentionally not part of this release
- local models stay local; online providers are opt-in
- no telemetry
