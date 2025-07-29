# Analytics Ingest Client

A lightweight Python library to batch and push signals, DTCs, GPS data, and network stats to a GraphQL backend, with optional JWT or certificate-based auth.

---

## 🔧 Features

- Supports Python 3.11+
- Clean, single-class interface: `AnalyticsIngestClient`
- In-memory caching for resolved IDs (signals, messages, ECUs, etc.)
- Batching support (by interval, count, or signal limit)
- Async-safe request queuing (only 1 request at a time)
- JWT (`SEC_AUTH_TOKEN`) or cert-based authentication
- Minimal dependency footprint
- Easy to test and integrate

---

## 🚀 Installation

```bash
pip install analytics-ingest

---

## 🚀 Deploying to PyPI

Follow these steps to publish this library to [PyPI](https://pypi.org/):

### ✅ 1. Install Build & Upload Tools

```bash
pip install --upgrade build twine

```bash
python -m build

```bash
python -m twine upload dist/*