# Cisco AI Defense + LiteLLM Podman Workshop

A reproducible multi-container workshop for deploying **LiteLLM Proxy** integrated with **Cisco AI Defense Runtime Protection** and **Ollama (Llama 3.2)**.

## Quickstart

1. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Add your AI_DEFENSE_API_KEY in .env

2. Export Corporate SSL Certificates (macOS / Cisco VPN):

security find-certificate -a -p /Library/Keychains/System.keychain /System/Library/Keychains/SystemRootCertificates.keychain > ca-bundle.crt

3. Start the Stack:

podman compose up -d


4. Pull Local Model:

podman exec -it lab_ollama ollama pull llama3.2:1b

5.Run Security Test Suite:

Benign Inference:
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-cisco-lab-key" \
  -d '{"model":"cisco-llama3","messages":[{"role":"user","content":"Explain BGP AS in 2 sentences."}]}'
Jailbreak (Pre-Call Block - HTTP 400): Prompt injection attack.
DLP Leak (Post-Call Block - HTTP 400): Sensitive data exfiltration with cisco-leaking-mock.

