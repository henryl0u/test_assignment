# Message Service API

A simple messaging service using REST API for submitting, fetching, and deleting plain-text messages

---

## 🚀 Features

- Submit a message to a recipient
- Retrieve unread messages
- Delete a single message
- Delete multiple messages
- Retrieve messages ordered by time (pagination supported)

---

## 🛠️ Requirements

- Python 3.10+
- pip3
- Virtual environment

---

## ⚙️ Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone git@github.com:henryl0u/test_assignment.git
   cd test_assignment
   ```

2. **Set up a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip3 install -r requirements.txt
   ```

4. **Run the app**:

   ```bash
   python src/app.py
   ```

   The server will start at: `http://127.0.0.1:5000`

---

## 📬 API Endpoints

### ➕ POST `/messages`

Submit a new message.

```bash
curl -X POST http://127.0.0.1:5000/messages \
-H "Content-Type: application/json" \
-d '{"recipient": "test@example.com", "content": "Hello"}'
```

---

### 📥 GET `/messages?recipient=<recipient>&start=<start>&stop=<stop>`

Fetch messages for a recipient, ordered by time. Supports optional pagination.

```bash
curl -X GET "http://127.0.0.1:5000/messages recipient=test@example.com"
```

- `start` (optional): index to start from
- `stop` (optional): index to stop at

---

### 📩 GET `/messages/unread?recipient=<recipient>`

Fetch all unread messages for a recipient and mark them as read.

```bash
curl -X GET "http://127.0.0.1:5000/messages/unread recipient=test@example.com"
```

---

### ❌ DELETE `/messages/<message_id>`

Delete a single message by ID.

```bash
curl -X DELETE http://127.0.0.1:5000/messages/<message_id>
```

---

### ❌ DELETE `/messages`

Delete multiple messages by ID.

```bash
curl -X DELETE http://127.0.0.1:5000/messages \
-H "Content-Type: application/json" \
-d '{"ids": ["id1", "id2"]}'
```
