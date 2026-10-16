# docuhook

Official [DocuHook](https://docuhook.com) Python client (stdlib only — no third-party deps).

```bash
pip install docuhook
```

```python
from docuhook import Client

client = Client(api_key="dh_...")
result = client.render(
    {"invoice": {"number": "INV-1"}},
    "<h1>{{invoice.number}}</h1>",
)
print(result["html"])
```

## Async

```python
job = client.render(data, html, mode="async")
status = client.job_status(job["job_id"])
done = client.job_result(job["job_id"])
```
