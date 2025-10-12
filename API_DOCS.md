# 📖 API Documentation - NeoBank External Integration API

This document describes the External Transaction API for integrating with NeoBank from your ESP32 projects, vendor terminals, or other in-game systems.

## Authentication

All API requests must include an API key. API keys can be generated and managed through the Admin Panel.

### Header Authentication (Recommended)
```http
X-API-Key: your_api_key_here
```

### Body Authentication (Alternative)
```json
{
  "api_key": "your_api_key_here",
  "from_account": "NC-XXXX-XXXX",
  ...
}
```

## Endpoints

### 1. Create Transaction

Transfer funds between accounts.

**Endpoint:** `POST /api/v1/external/transactions`

**Request Headers:**
```http
Content-Type: application/json
X-API-Key: your_api_key_here
```

**Request Body:**
```json
{
  "from_account": "NC-8A6F-4E2B",
  "to_account": "NC-1B2C-3D4E",
  "amount": 100.50,
  "memo": "Payment for services rendered"
}
```

**Response (Success - 201):**
```json
{
  "message": "Transaction successful",
  "transaction": {
    "id": 123,
    "from_account": "NC-8A6F-4E2B",
    "from_name": "Alice Runner",
    "to_account": "NC-1B2C-3D4E",
    "to_name": "Bob Vendor",
    "amount": 100.50,
    "memo": "Payment for services rendered",
    "timestamp": "2025-10-11T14:30:00",
    "type": "transfer"
  }
}
```

**Response (Error - 400):**
```json
{
  "error": "Insufficient funds"
}
```

**Error Codes:**
- `400` - Invalid request (missing fields, insufficient funds, invalid amount)
- `401` - Invalid or missing API key
- `404` - Account not found

---

### 2. Check Account Balance

Query the balance of a specific account.

**Endpoint:** `GET /api/v1/external/account/{account_number}/balance`

**Request Headers:**
```http
X-API-Key: your_api_key_here
```

**Response (Success - 200):**
```json
{
  "account_number": "NC-8A6F-4E2B",
  "balance": 1234.56
}
```

**Response (Error - 404):**
```json
{
  "error": "Account not found"
}
```

---

## Rate Limiting

- Default: **100 requests per minute** per API key
- Exceeded requests will return `429 Too Many Requests`

---

## Example Integrations

### Python (ESP32/MicroPython)

```python
import urequests
import ujson

API_BASE = "http://neobank.neotropolis.larp"
API_KEY = "your_api_key_here"

def check_balance(account_number):
    url = f"{API_BASE}/api/v1/external/account/{account_number}/balance"
    headers = {"X-API-Key": API_KEY}
    
    response = urequests.get(url, headers=headers)
    data = ujson.loads(response.text)
    
    return data.get("balance")

def create_transaction(from_account, to_account, amount, memo=""):
    url = f"{API_BASE}/api/v1/external/transactions"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount,
        "memo": memo
    }
    
    response = urequests.post(url, headers=headers, data=ujson.dumps(body))
    return ujson.loads(response.text)

# Usage
balance = check_balance("NC-8A6F-4E2B")
print(f"Balance: {balance}")

result = create_transaction(
    "NC-8A6F-4E2B",
    "NC-VEND-0001",
    50.00,
    "Vendor purchase"
)
print(result)
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_BASE = 'http://neobank.neotropolis.larp';
const API_KEY = 'your_api_key_here';

async function checkBalance(accountNumber) {
    const response = await axios.get(
        `${API_BASE}/api/v1/external/account/${accountNumber}/balance`,
        { headers: { 'X-API-Key': API_KEY } }
    );
    return response.data.balance;
}

async function createTransaction(fromAccount, toAccount, amount, memo = '') {
    const response = await axios.post(
        `${API_BASE}/api/v1/external/transactions`,
        {
            from_account: fromAccount,
            to_account: toAccount,
            amount: amount,
            memo: memo
        },
        { headers: { 'X-API-Key': API_KEY } }
    );
    return response.data;
}

// Usage
(async () => {
    const balance = await checkBalance('NC-8A6F-4E2B');
    console.log(`Balance: ${balance}`);
    
    const result = await createTransaction(
        'NC-8A6F-4E2B',
        'NC-VEND-0001',
        50.00,
        'Vendor purchase'
    );
    console.log(result);
})();
```

### PowerShell

```powershell
$API_BASE = "http://neobank.neotropolis.larp"
$API_KEY = "your_api_key_here"

# Check Balance
function Get-AccountBalance {
    param([string]$AccountNumber)
    
    $headers = @{
        "X-API-Key" = $API_KEY
    }
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/v1/external/account/$AccountNumber/balance" -Headers $headers
    return $response.balance
}

# Create Transaction
function New-Transaction {
    param(
        [string]$FromAccount,
        [string]$ToAccount,
        [decimal]$Amount,
        [string]$Memo = ""
    )
    
    $headers = @{
        "X-API-Key" = $API_KEY
        "Content-Type" = "application/json"
    }
    
    $body = @{
        from_account = $FromAccount
        to_account = $ToAccount
        amount = $Amount
        memo = $Memo
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/v1/external/transactions" -Method Post -Headers $headers -Body $body
    return $response
}

# Usage
$balance = Get-AccountBalance -AccountNumber "NC-8A6F-4E2B"
Write-Host "Balance: $balance"

$result = New-Transaction -FromAccount "NC-8A6F-4E2B" -ToAccount "NC-VEND-0001" -Amount 50.00 -Memo "Vendor purchase"
Write-Host $result
```

---

## Best Practices

1. **Store API keys securely** - Never hardcode keys in source code
2. **Handle errors gracefully** - Always check response status codes
3. **Implement retry logic** - For transient network errors
4. **Cache balance checks** - Don't query balance on every request
5. **Use memos** - Provide clear transaction descriptions
6. **Validate amounts** - Always use positive numbers with max 2 decimal places
7. **Log transactions** - Keep audit trail of API usage

---

## Testing

### Health Check

```bash
curl http://localhost:8080/health
```

### Test Transaction (with curl)

```bash
curl -X POST http://localhost:8080/api/v1/external/transactions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "from_account": "NC-8A6F-4E2B",
    "to_account": "NC-1B2C-3D4E",
    "amount": 10.00,
    "memo": "Test transaction"
  }'
```

---

## Support

For issues or questions during the Neotropolis event:
- Contact Tech Team via in-game radio
- Discord: [Your Discord Link]
- Emergency: [Emergency Contact]

---

**Happy Hacking! 🌃💾**
