# genderapi-python

Official Python SDK for [GenderAPI.io](https://genderapi.io) — determine gender from **names**, **emails**, and **usernames** using AI.

---

## 🚀 Installation

Install the required package:

```bash
pip install genderapi
```


---

## 📝 Usage

### 🔹 Get Gender by Name

```python
from genderapi import GenderAPI

api = GenderAPI("YOUR_API_KEY")

# Basic usage
result = api.get_gender_by_name(name="Michael")
print(result)

# With askToAI set to True
result = api.get_gender_by_name(name="李雷", askToAI=True)
print(result)
```

---

### 🔹 Get Gender by Email

```python
result = api.get_gender_by_email(email="michael.smith@example.com")
print(result)

# With askToAI set to True
result = api.get_gender_by_email(email="michael.smith@example.com", askToAI=True)
print(result)
```

---

### 🔹 Get Gender by Username

```python
result = api.get_gender_by_username(username="michael_dev")
print(result)

# With askToAI set to True
result = api.get_gender_by_username(username="michael_dev", askToAI=True)
print(result)
```

---

## 📥 API Parameters

### Common Parameters

| Parameter | Required | Description             |
|-----------|----------|-------------------------|
| country   | No       | 2-letter country code (e.g. "US") |
| askToAI   | No       | `true` or `false`. Default is `false`. If `true`, the query goes directly to AI and costs 3 requests. If `false`, the system tries its internal database first and only uses AI if necessary without spending 3 requests. Recommended for non-latin characters. |

---

### Name Lookup

| Parameter | Required | Description             |
|-----------|----------|-------------------------|
| name      | Yes      | Name to query           |

---

### Email Lookup

| Parameter | Required | Description             |
|-----------|----------|-------------------------|
| email     | Yes      | Email address to query  |

---

### Username Lookup

| Parameter | Required | Description             |
|-----------|----------|-------------------------|
| username  | Yes      | Username to query       |

---

## ✅ API Response

Example JSON response for all endpoints:

```json
{
  "status": true,
  "used_credits": 1,
  "remaining_credits": 4999,
  "expires": 1743659200,
  "q": "michael.smith@example.com",
  "name": "Michael",
  "gender": "male",
  "country": "US",
  "total_names": 325,
  "probability": 98,
  "duration": "4ms"
}
```

---

### Response Fields

| Field             | Type               | Description                                         |
|-------------------|--------------------|-----------------------------------------------------|
| status            | Boolean            | `true` or `false`. Check errors if false.          |
| used_credits      | Integer            | Credits used for this request.                     |
| remaining_credits | Integer            | Remaining credits on your package.                 |
| expires           | Integer (timestamp)| Package expiration date (in seconds).             |
| q                 | String             | Your input query (name, email, or username).       |
| name              | String             | Found name.                                        |
| gender            | Enum[String]       | `"male"`, `"female"`, or `"null"`.                |
| country           | Enum[String]       | Most likely country (e.g. `"US"`, `"DE"`, etc.).  |
| total_names       | Integer            | Number of samples behind the prediction.          |
| probability       | Integer            | Likelihood percentage (50-100).                   |
| duration          | String             | Processing time (e.g. `"4ms"`).                   |

---

## ⚠️ Error Codes

When `status` is `false`, check the following error codes:

| errno | errmsg                      | Description                                                       |
|-------|-----------------------------|-------------------------------------------------------------------|
| 50    | access denied               | Unauthorized IP Address or Referrer. Check your access privileges. |
| 90    | invalid country code        | Check supported country codes. [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) |
| 91    | name not set \|\| email not set | Missing `name` or `email` parameter on your request.         |
| 92    | too many names \|\| too many emails | Limit is 100 for names, 50 for emails in one request.     |
| 93    | limit reached               | The API key credit has been finished.                            |
| 94    | invalid or missing key      | The API key cannot be found.                                      |
| 99    | API key has expired         | Please renew your API key.                                       |

Example error response:

```json
{
  "status": false,
  "errno": 94,
  "errmsg": "invalid or missing key"
}
```

---

## ⚖️ License

MIT License
