# fxpyD365api

A Python wrapper for interacting with Microsoft Dynamics 365 Web API (both Customer Engagement and Finance & Operations).  
Includes built-in support for token authentication, paging, CRUD operations, retries, and both synchronous and asynchronous usage.

---

## 📦 Installation

```bash
pip install fxpyD365api
```

---

## 🔧 Environment Configuration

Set these environment variables or pass them as keyword arguments when initializing the wrapper:

```env
D365_ORG_URL=https://yourorg.crm4.dynamics.com
D365_TENANT=yourtenantid
D365_CLIENT_ID=yourclientid
D365_CLIENT_SECRET=yourclientsecret
```

---

## ✅ Usage

### 🔁 Synchronous (default)

```python
from d365_wrapper import GenericWrapper

accounts = GenericWrapper(entity_type='accounts')
response = accounts.get_top(qty=5)
print(response)
```

### ⚡ Asynchronous

```python
import asyncio
from d365_wrapper import get_wrapper

async def main():
    contacts = get_wrapper(entity_type='contacts', async_mode=True)
    data = await contacts.get_top(qty=10)
    print(data)
    await contacts.close()

asyncio.run(main())
```

---

## 🎛 Available Methods

Both sync and async wrappers implement:

- `get_page(page=1, ...)`
- `get_next_page()`
- `get_previous_page()`
- `get_top(qty, ...)`
- `create(data)`
- `retrieve(entity_id)`
- `update(entity_id, data)`
- `delete(entity_id)`

---

## 🔒 Authentication Flow

Uses `msal.ConfidentialClientApplication` with `client_credentials` flow.
Token is cached and refreshed when expiring.

---

## 🛠 Advanced Options

You can also configure:
- `timeout`: request timeout (default: 20 seconds)
- `retries`: number of retries (default: 3 for sync)
- `backoff_factor`: retry delay multiplier

```python
from d365_wrapper import get_wrapper

api = get_wrapper('contacts', timeout=10, retries=5)
```

---

## 📚 Legacy Support

You may continue using the original `GenericWrapper`:

```python
from d365_wrapper import GenericWrapper

wrapper = GenericWrapper('contacts', async_mode=False)
```

---

## 📜 License

BSD-3-Clause

---

## 🌐 Repository

[https://github.com/flexitdev/fxpyD365api](https://github.com/flexitdev/fxpyD365api)
