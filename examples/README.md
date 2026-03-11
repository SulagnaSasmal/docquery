# DocQuery — Demo Collections

Pre-defined documentation collections for local testing and demo purposes.
Each folder contains the raw source documents and a `collection.json` manifest.

## Collections

| Folder | Source | Description |
|--------|--------|-------------|
| `vaultpay/` | VaultPay API Docs | Payment processing API reference |
| `fraudshield/` | FraudShield Docs | AI fraud detection platform |
| `us-payments-hub/` | US Payments Hub | ACH, Fedwire, SWIFT, RTP, FedNow reference |

## How to index a collection

```bash
# Requires OPENAI_API_KEY in .env
python ingest.py --collection vaultpay --source https://sulagnasasmal.github.io/vaultpay-api-docs/
python ingest.py --collection fraudshield --source https://sulagnasasmal.github.io/fraudshield-docs/
python ingest.py --collection us-payments-hub --source https://sulagnasasmal.github.io/us-payments-hub/
```

Or index from a local HTML file:

```bash
python ingest.py --collection vaultpay --source ./examples/vaultpay/index.html
```

## Without an OpenAI API key

The frontend runs in **demo mode** automatically when the backend is unreachable.
Pre-loaded canned responses are served from `frontend/src/lib/demo.ts` for each collection.
No API key or backend is required to explore the UI.
