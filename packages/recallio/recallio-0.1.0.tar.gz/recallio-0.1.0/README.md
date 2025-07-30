# Recallio Python Client

A lightweight Python wrapper for the [Recallio](https://app.recallio.ai) API.

## Installation

```bash
pip install recallio
```

## Usage

```python
from recallio import (
    RecallioClient,
    MemoryWriteRequest,
    MemoryRecallRequest,
)

client = RecallioClient(api_key="YOUR_RECALLIO_API_KEY")

req = MemoryWriteRequest(
    userId="user_123",
    projectId="project_abc",
    content="The user prefers dark mode and wants notifications disabled on weekends",
    consentFlag=True,
)

memory = client.write_memory(req)
print(memory.id)

# recall memories
recall_req = MemoryRecallRequest(
    projectId="project_abc",
    userId="user_123",
    query="dark mode",
    scope="user",
)
results = client.recall_memory(recall_req)
for m in results:
    print(m.content, m.similarityScore)

# summarized recall
summary = client.recall_summary(recall_req)
print(summary.content)
```

## API Key

The client authenticates using the `Authorization` header with a Bearer token. Pass
`RECALLIO_API_KEY` when creating `RecallioClient`.
