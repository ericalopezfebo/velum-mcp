# VELUM by Abogado Virtual

**Legal Document Anonymization & Privacy MCP for lawyers**

VELUM is a **local-first MCP server for legal documents**. Its purpose is to help lawyers protect confidential client information before using an external AI system such as ChatGPT, Claude, or another model.

VELUM is **not** the Puerto Rico jurisprudence search MCP. That is a separate project: [mcp-puerto-rico-sentencias](https://github.com/ericalopezfebo/mcp-puerto-rico-sentencias).

## The core privacy model

```text
Original client document
        |
        v
   VELUM running locally
        |
        +-- local extraction
        +-- deterministic redaction
        +-- custom substitutions
        +-- local sanitized copy
        |
        v
 Human review by the lawyer
        |
        v
Only the material the lawyer chooses to share
        |
        v
 ChatGPT / Claude / another AI service
```

VELUM is designed so that **the original document is processed on the lawyer's own computer**. The privacy tools do not require a VELUM cloud account, a VELUM database, or a VELUM server to process a document.

### What VELUM does not promise

VELUM cannot control what a lawyer subsequently sends to an outside AI provider. If a tool returns sanitized text and the lawyer sends that text to ChatGPT or Claude, that text leaves the lawyer's computer and is handled by that provider.

VELUM also does **not** guarantee that every possible identifier, fact pattern, or combination of facts will be detected automatically. Legal documents require human review.

The intended workflow is therefore:

1. Keep the original client material locally.
2. Process it with VELUM locally.
3. Review the sanitization result.
4. Add custom redactions where necessary.
5. Share only the minimum information the lawyer has decided is appropriate for the intended AI task.

## Why this is designed for legal practice

VELUM is a technical privacy tool. It does not make the legal or ethical decision for the lawyer.

For Puerto Rico lawyers, the design is intended to support careful handling of confidential client information in light of the **Puerto Rico Rules of Professional Conduct**, including the duties concerning confidentiality, competence, communication, and supervision. Lawyers should also evaluate the applicable Puerto Rico Rules of Evidence, court orders, protective orders, discovery obligations, and any matter-specific confidentiality restrictions before using AI.

For lawyers following the **ABA Model Rules of Professional Conduct**, the relevant considerations include, among others, **Model Rule 1.1 (competence), Comment [8] concerning technology and continuing learning, Rule 1.6 (confidentiality), Rule 1.4 (communication), Rule 5.1 (supervision of lawyers), and Rule 5.3 (supervision of nonlawyer assistance)**. The precise obligations depend on the circumstances and the lawyer's jurisdiction.

VELUM does not establish that a particular use of AI is ethically permissible. It is intended to reduce one technical risk: unnecessarily exposing the original client document before the lawyer has reviewed and controlled what will be shared.

## Local security boundary

The privacy tools are designed around a local document root configured with `VELUM_RAICES`.

The implementation is intended to enforce these boundaries:

- Documents are read from authorized local roots.
- Relative paths and path traversal are rejected.
- Symbolic-link escapes are rejected.
- The original document is not modified by anonymization.
- Sanitized copies are written locally.
- The original document is not returned as the result of document-anonymization tools.
- No LLM is used to decide what to redact.
- No OpenAI, Anthropic, or other AI API is required for the local anonymization engine.
- Privacy processing does not require an HTTP listener.

These are **technical properties of the implementation, not legal guarantees**.

## What gets replaced and what should normally be preserved

VELUM is intended to redact information that identifies a client, witness, opposing party, or other person or entity when the lawyer decides that information is unnecessary for the AI task.

Typical targets include:

- names and aliases;
- government identifiers;
- Social Security numbers;
- driver's-license and passport identifiers;
- addresses;
- telephone numbers and email addresses;
- bank-account and payment-card information;
- identifying corporate information;
- other personally identifying information selected by the lawyer.

VELUM should generally preserve the legal substance needed for the task, such as:

- amounts and damages;
- dates material to the facts;
- statutes and rules;
- legal citations;
- court names;
- procedural posture;
- case numbers when the lawyer determines they are not themselves confidential;
- the factual and legal structure of the document.

**Preservation is not automatic permission to disclose.** A lawyer must decide whether any particular fact, citation, case number, or combination of facts could identify a client or confidential matter.

## Puerto Rico example

Original:

```text
La demandante María Rivera López, residente en San Juan, Puerto Rico,
identifica en su contestación a la demanda la cuenta bancaria utilizada para
recibir el pago y describe la relación contractual con ABC Caribe, Inc.
```

Sanitized example:

```text
La demandante [ACTORA_1], residente en [MUNICIPIO_1], Puerto Rico,
identifica en su contestación a la demanda la cuenta bancaria utilizada para
recibir el pago y describe la relación contractual con [EMPRESA_1].
```

The objective is **not** to erase the legal theory or factual issue. The objective is to remove unnecessary identifying information while preserving enough context for the intended legal/AI task.

For a real Puerto Rico filing, the lawyer should review the entire result for indirect identifiers, unique facts, names embedded in exhibits, captions, footnotes, signatures, metadata, and other context that could re-identify a person.

## Anonymization vs. pseudonymization

A replacement such as `[CLIENTE_1]` is useful for an AI workflow, but terminology matters.

If a lawyer keeps a separate mapping that can reconnect `[CLIENTE_1]` to the real person, the resulting process may be better characterized as **pseudonymization** rather than irreversible anonymization. The lawyer should therefore control and protect any mapping table separately.

VELUM should not be described as making a document legally anonymous merely because it replaced a few names or identifiers.

## Tools

The MCP exposes privacy-oriented tools such as:

| Tool | Purpose | Returns original document content? |
| --- | --- | --- |
| `estado` | Reports local runtime/security configuration | No |
| `revisar_texto` | Inspects supplied text for detectable identifiers | No original file |
| `revisar_documento` | Reviews a local document | No |
| `revisar_carpeta` | Reviews authorized local documents | No |
| `anonimizar_texto` | Applies local redactions to supplied text | Sanitized text |
| `anonimizar_documento` | Creates a sanitized local document | No original document content |
| `anonimizar_carpeta` | Creates sanitized local copies | No original document content |

The exact tool schemas and supported categories are defined by the code and tests in this repository.

## Installation

```bash
git clone https://github.com/ericalopezfebo/velum-mcp.git
cd velum-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Python 3.10+ is required.

Create a local document root:

```bash
mkdir -p ~/Documents/VELUM
export VELUM_RAICES="$HOME/Documents/VELUM"
```

The local MCP server uses `stdio`; it does not need a public HTTP server to perform local anonymization.

## Claude Desktop / other local MCP clients

A local MCP client can launch the VELUM executable directly. Configure the client to use the executable from your virtual environment and set `VELUM_RAICES` to the directory containing the documents the lawyer has intentionally authorized.

Example:

```json
{
  "mcpServers": {
    "velum": {
      "command": "/ABSOLUTE/PATH/TO/velum-mcp/.venv/bin/velum-mcp",
      "env": {
        "VELUM_RAICES": "/Users/USER/Documents/VELUM"
      }
    }
  }
}
```

A local MCP connection is different from a remote MCP connection. The fact that VELUM runs locally does not mean that content subsequently returned to an external AI provider stays local.

## ChatGPT and external AI systems

VELUM's local privacy boundary is independent of the connection mechanism used by an AI client.

If an AI client can launch a local MCP by `stdio`, VELUM can run as a local process. If a product requires a separate connection mechanism to reach a local MCP, that connection mechanism must be evaluated separately.

**Do not describe VELUM as preventing all information from reaching an AI provider.** The correct statement is that VELUM is designed to process the original document locally and to give the lawyer an opportunity to sanitize and review the material before deciding what to send to an external AI service.

## Limitations

- No automated detector catches every personal or confidential fact.
- Names and identifiers expressed indirectly may require custom rules.
- Unique factual combinations can identify a person even after obvious identifiers are removed.
- Exhibits, attachments, headers, footers, signatures, comments, document metadata, and images may require separate review depending on the file format and implementation.
- Legal privilege and confidentiality are legal questions; VELUM cannot determine whether a particular disclosure waives a privilege or violates a professional rule.
- A sanitized document can still contain confidential or identifying information.

## Tests

Run:

```bash
python3 -m pytest -q
```

The test suite is intended to verify the technical privacy boundary, path restrictions, deterministic redaction behavior, and output-safety properties. Passing tests do not constitute a legal or ethical certification.

## Security reporting

See [`SECURITY.md`](SECURITY.md) for responsible disclosure information.

## Separate Puerto Rico jurisprudence project

VELUM and the Puerto Rico jurisprudence search MCP are intentionally separate projects.

**VELUM:** protects and prepares confidential legal documents locally.

**mcp-puerto-rico-sentencias:** searches and retrieves public Puerto Rico judicial decisions.

They should not be presented as the same product, repository, or security boundary.

## Disclaimer

VELUM is software for privacy-oriented document preparation. It is not legal advice, does not determine whether an AI workflow complies with a particular jurisdiction's professional-responsibility rules, and does not guarantee attorney-client privilege, work-product protection, confidentiality, or waiver prevention.

The lawyer remains responsible for evaluating the specific client matter, applicable professional rules, court requirements, contracts, AI-provider terms, security controls, and the content actually shared with an AI system.
