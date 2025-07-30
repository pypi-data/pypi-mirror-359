# @clad-ai/python

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Instantiating CladClient](#instantiating-cladclient)
- [Core Concepts](#core-concepts)
- [Exports](#exports)
  - [get_processed_input](#get_processed_input)
  - [get_processed_input_fully_managed](#get_processed_input_fully_managed)
  - [get_processed_input_with_redis](#get_processed_input_with_redis)
- [Generating a user_id](#generating-a-user_id)
- [Support](#support)

## Overview

Clad provides a lightweight **Python SDK** for secure, low-latency native ad injection in LLM workflows. It gives developers clear choices for how much memory and state they wish to handle locally or outsource to Clad’s backend.

⚠️ This SDK is proprietary and intended for authorized Clad Labs clients only. 
Use or redistribution without permission is strictly prohibited.

## Installation

```bash
pip install clad-ai-python
```

---

## Instantiating CladClient
Before calling any method, create an instance of CladClient with an API key we will provide you and (optionally) your own Redis client for production scalability.

```python
import redis.asyncio as aioredis
from clad_ai_python import CladClient

# Example: connect to your Redis instance
r = aioredis.from_url("redis://localhost:6379/0")

clad = CladClient(
  api_key="PROVIDED_CLAD_API_KEY",
  threshold=5,          # Optional: how many messages before calling API (default: 3)
  filteredKeywords= ['starbucks', 'gambling', 'crypto', 'adult', 'politics', 'violence']    # Optional. keywords to filter out specific ads from being displayed.
  redis_client=r        # Optional: only needed for get_processed_input_with_redis
)

```
**Parameters:**
- `api_key: str` — API key provided by Clad. Contact support@clad.ai to get yours.
- `threshold: int` — Optional. Number of messages before triggering an API call. Defaults to 3. 
- `filteredKeywords: list` — Optional. keywords to filter out specific ads from being displayed.
- `redis_client: Redis client` — Optional. Pass your Redis client if using




## Core Concepts

✅ **Three modes of operation:** \
Each mode offers a different balance of speed, memory footprint, and infrastructure requirements. These trade-offs let you choose the best fit for your scale, cost, and reliability needs.

- **get_processed_input**: is fast but uses your server’s RAM (still lightweight) 

- **get_processed_input_fully_managed**: uses no local memory but adds slight network latency to every message
- **get_processed_input_with_redis**: offloads state to a dedicated store for high performance and consistent scaling across servers. Fast and low memory, ideal for production but requires additional setup



## Exports

### `get_processed_input`
In this mode, the SDK uses an in-process TTL cache to track each user’s message count and context directly in your server’s RAM. This provides ultra-low latency (microseconds for reads/writes) and minimizes API calls by handling counting locally until a threshold is reached. It’s simple to set up with no extra infrastructure required. This consumes server RAM linearly with the number of active users.

**Example:**

```python
clad = CladClient(api_key="YOUR_API_KEY")

response = await clad.get_processed_input(
    user_input="I'm looking for shoes",
    user_id="uuid4-from-frontend",
    discrete="true"
)

print(response["prompt"])  # Final prompt with or without ad
```

**Parameters:**
- `user_input: str` — Chat message
- `user_id: str` — UUID from frontend
- `discrete: str` — "true" or "false"

**Returns:**

```py
{
  "prompt": str,
  "promptType": "clean" | "injected",
  "link": str,
  "discrete": "true" | "false",
  "adType": str,
  "image_url": Optional[str]
}
```

---

### `get_processed_input_fully_managed` 
In this mode, the SDK does not store any counters or context locally. Instead, every message from the user is sent to Clad’s backend API, which fully manages the counting, context, and injection logic server-side. This approach requires zero memory on your servers and no extra infrastructure. However, it adds slight network latency to every user message since each one must reach the API. This mode is ideal if you want Clad to handle everything automatically with no local state.

**Example:**

```python
clad = CladClient(api_key="YOUR_API_KEY")

response = await clad.get_processed_input_fully_managed(
  user_input="Looking for cafes",
  user_id="uuid4-from-frontend",
  discrete="false",
  threshold=5
)
```

**Parameters:**
- Same as above, plus optional `threshold: int`

**Returns:**
Same shape as above.

---

### `get_processed_input_with_redis`

**Use this for production — your backend stores state in your Redis instance for maximum control + scalability.**
In this mode, the SDK connects to a Redis instance that you deploy and manage (e.g., Redis Cloud, AWS ElastiCache). Per-user counters and context are stored efficiently in Redis RAM instead of your server RAM, enabling low-latency reads/writes (~1 ms) while sharing state consistently across multiple backend servers. This option is the most robust and production-ready choice for large user bases, offering fast performance with centralized state management and minimal local memory use.

**Example:**

```python
import redis.asyncio as aioredis

r = aioredis.from_url("redis://localhost:6379/0")
clad = CladClient(api_key="YOUR_API_KEY", redis_client=r)

response = await clad.get_processed_input_with_redis(
  user_input="Book a hotel",
  user_id="uuid4-from-frontend",
  discrete="false"
)
```

**Parameters:**
Same as `get_processed_input`.

---

## Generating a `user_id`

👉 **Use the Clad React SDK to create a UUID and pass it to your backend calls.**

**Example:**

```ts
import { getOrCreateUserId } from '@clad-ai/react';

const userId = getOrCreateUserId(); // stores in localStorage
```

Then pass `userId` to your Python server route and use it for Clad calls.

---

## Support

For help, email us at [support@clad.ai](mailto:support@clad.ai)

Copyright (c) 2025 Clad Labs

This software is proprietary and confidential. Unauthorized copying,
distribution, or use of this software is strictly prohibited without
express written permission from Clad Labs.
