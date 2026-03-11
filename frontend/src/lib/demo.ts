/**
 * DocQuery — Demo mode responses
 * Used when the FastAPI backend is unavailable (GitHub Pages static deployment).
 * Returns realistic canned answers with citations for each collection.
 */

interface DemoSource {
  title: string;
  url: string;
  section: string;
  score: number;
  doc_type: string;
}

interface DemoResponse {
  answer: string;
  sources: DemoSource[];
  confidence: string;
  confidence_score: number;
}

const DEMO_DATA: Record<string, Record<string, DemoResponse>> = {
  vaultpay: {
    default: {
      answer: "VaultPay supports multiple authentication methods including Bearer tokens (OAuth 2.0) for server-to-server calls and API keys for sandbox testing. All requests must include `Authorization: Bearer <token>` in the header. Tokens expire after 3,600 seconds and can be refreshed using the `/auth/token/refresh` endpoint.",
      sources: [
        { title: "Authentication Guide", url: "#/authentication", section: "OAuth 2.0 Flow", score: 0.94, doc_type: "reference" },
        { title: "API Quickstart", url: "#/quickstart", section: "Making Your First Request", score: 0.81, doc_type: "tutorial" }
      ],
      confidence: "HIGH", confidence_score: 0.91
    },
    auth: {
      answer: "VaultPay uses OAuth 2.0 Bearer tokens for authentication. Obtain a token via `POST /auth/token` with your `client_id` and `client_secret`. The token is valid for 3,600 seconds. Include it in every request as `Authorization: Bearer <token>`. For sandbox testing, API keys are also supported via the `X-API-Key` header.",
      sources: [
        { title: "Authentication Guide", url: "#/authentication", section: "OAuth 2.0 Bearer Tokens", score: 0.97, doc_type: "reference" },
        { title: "Sandbox Guide", url: "#/sandbox", section: "API Keys in Sandbox", score: 0.79, doc_type: "tutorial" }
      ],
      confidence: "HIGH", confidence_score: 0.95
    },
    webhook: {
      answer: "VaultPay webhooks send `POST` requests to your endpoint when payment events occur. Verify authenticity by computing `HMAC-SHA256` over the raw request body using your webhook secret, then compare it against the `X-VaultPay-Signature` header. Events include `payment.completed`, `payment.failed`, `refund.processed`, and `chargeback.opened`.",
      sources: [
        { title: "Webhook Reference", url: "#/webhooks", section: "Signature Verification", score: 0.96, doc_type: "reference" },
        { title: "Webhook Events", url: "#/webhooks/events", section: "Event Types", score: 0.88, doc_type: "reference" }
      ],
      confidence: "HIGH", confidence_score: 0.94
    },
    error: {
      answer: "VaultPay uses standard HTTP status codes with structured error responses. All errors return a JSON body with `error_code`, `message`, and `request_id`. Common codes: `4001` (invalid credentials), `4022` (insufficient funds), `4291` (rate limit exceeded), `5001` (upstream timeout). Use `request_id` when contacting support.",
      sources: [
        { title: "Error Reference", url: "#/errors", section: "Error Code Index", score: 0.95, doc_type: "reference" },
        { title: "Error Handling Guide", url: "#/errors/handling", section: "Retry Logic", score: 0.83, doc_type: "tutorial" }
      ],
      confidence: "HIGH", confidence_score: 0.93
    }
  },
  fraudshield: {
    default: {
      answer: "FraudShield AI Engine uses a multi-model ensemble scoring system that combines behavioral analytics, device fingerprinting, velocity checks, and network graph analysis to produce a risk score between 0 and 1000. Scores below 200 are auto-approved, 200–600 require review, and above 600 trigger automated decline or step-up authentication.",
      sources: [
        { title: "Risk Scoring Model", url: "#/risk-model", section: "Score Bands and Decisioning", score: 0.96, doc_type: "reference" },
        { title: "Model Configuration", url: "#/configuration", section: "Threshold Defaults", score: 0.84, doc_type: "reference" }
      ],
      confidence: "HIGH", confidence_score: 0.93
    },
    score: {
      answer: "FraudShield generates risk scores using a gradient-boosted ensemble model trained on 200+ features. The final score (0–1000) combines: transaction signals (40%), behavioral biometrics (25%), device/network reputation (20%), and historical velocity patterns (15%). Scores are computed in under 80ms p99.",
      sources: [
        { title: "Risk Scoring Model", url: "#/risk-model", section: "Model Architecture", score: 0.97, doc_type: "reference" },
        { title: "Model Input Features", url: "#/model-inputs", section: "Feature Weights", score: 0.91, doc_type: "reference" }
      ],
      confidence: "HIGH", confidence_score: 0.95
    },
    threshold: {
      answer: "Thresholds can be adjusted per product, channel, and customer segment in the FraudShield configuration panel. The default auto-decline threshold is 600 but can be tuned between 400 and 800. A/B testing mode allows parallel threshold evaluation before committing changes. Adjustments take effect within 5 minutes.",
      sources: [
        { title: "Threshold Tuning", url: "#/threshold-tuning", section: "Adjusting Thresholds", score: 0.95, doc_type: "task" },
        { title: "A/B Testing", url: "#/threshold-tuning/ab-testing", section: "Running Parallel Tests", score: 0.87, doc_type: "task" }
      ],
      confidence: "HIGH", confidence_score: 0.93
    }
  },
  "us-payments-hub": {
    default: {
      answer: "The US Payments Hub covers six major payment rails: ACH (batch, NACHA-governed), Fedwire (RTGS, same-day settlement), SWIFT (cross-border), RTP (The Clearing House, real-time), FedNow (Federal Reserve, real-time), and Card Networks (Visa, Mastercard). Each rail has different settlement timing, limits, reversibility, and compliance requirements.",
      sources: [
        { title: "Rail Overview", url: "#/overview", section: "Payment Rail Comparison", score: 0.96, doc_type: "concept" },
        { title: "ACH Guide", url: "#/ach", section: "ACH vs. Wire Comparison", score: 0.82, doc_type: "reference" }
      ],
      confidence: "HIGH", confidence_score: 0.93
    },
    ach: {
      answer: "ACH (Automated Clearing House) is a batch payment system governed by NACHA. Transactions settle in 1–2 business days for standard ACH, or same day for Same Day ACH (cutoff 4:45 PM ET). Return codes R01–R29 indicate failure reasons: R01 (insufficient funds), R02 (account closed), R10 (customer advises not authorized). NOC codes update routing/account details.",
      sources: [
        { title: "ACH Guide", url: "#/ach", section: "Processing Flow and Settlement", score: 0.97, doc_type: "reference" },
        { title: "Return Codes", url: "#/ach#returns", section: "R01–R29 Reference", score: 0.93, doc_type: "reference" }
      ],
      confidence: "HIGH", confidence_score: 0.95
    },
    fednow: {
      answer: "FedNow is the Federal Reserve's instant payment service, launched July 2023. Transactions settle in seconds, 24/7/365. Maximum transaction limit is $500,000 (institutions may set lower limits). Supports credit push only — no debit pull. Participating institutions must connect via FedLine and maintain sufficient Federal Reserve account balances.",
      sources: [
        { title: "FedNow Guide", url: "#/fednow", section: "How FedNow Works", score: 0.96, doc_type: "concept" },
        { title: "Liquidity Management", url: "#/fednow#liquidity", section: "Reserve Balance Requirements", score: 0.88, doc_type: "reference" }
      ],
      confidence: "HIGH", confidence_score: 0.94
    }
  }
};

const KEYWORD_MAP: Record<string, string> = {
  auth: 'auth', authentication: 'auth', token: 'auth', oauth: 'auth', 'api key': 'auth',
  webhook: 'webhook', event: 'webhook', signature: 'webhook', hmac: 'webhook',
  error: 'error', '4xx': 'error', '5xx': 'error', 'error code': 'error', retry: 'error',
  score: 'score', scoring: 'score', risk: 'score', model: 'score', ensemble: 'score',
  threshold: 'threshold', 'tune threshold': 'threshold', decline: 'threshold',
  ach: 'ach', 'return code': 'ach', nacha: 'ach', 'same day': 'ach',
  fednow: 'fednow', 'fed now': 'fednow', 'real-time': 'fednow', instant: 'fednow',
};

function detectIntent(question: string): string {
  const q = question.toLowerCase();
  for (const [kw, intent] of Object.entries(KEYWORD_MAP)) {
    if (q.includes(kw)) return intent;
  }
  return 'default';
}

export function getDemoResponse(question: string, collection: string): DemoResponse {
  const intent = detectIntent(question);
  const collectionData = DEMO_DATA[collection] || DEMO_DATA['vaultpay'];
  return collectionData[intent] || collectionData['default'];
}

export const DEMO_BANNER = "⚠️ Demo mode — backend not connected. Showing pre-loaded example responses. Run the FastAPI backend locally for live RAG queries.";
