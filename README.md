
# 🛡️ Exam Authentication System with WebAuthn

A Django-based exam authentication system that uses fingerprint biometrics via WebAuthn for secure student verification and eligibility checking.

---

## ✨ Key Features

- 🔒 Fingerprint registration & login using WebAuthn (FIDO2)
- 🎓 Course eligibility enforcement (requires ≥75% attendance)
- 📋 Secure and conditional access to exam questions

---

## ⚙️ Prerequisites

- Python 3.8+
- Django 3.2+
- PostgreSQL (recommended for production)
- HTTPS domain (required for WebAuthn to function)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/exam-auth-system.git
cd exam-auth-system
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in your project root:

```env
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgres://user:password@localhost/dbname
DEBUG=True  # Set to False in production
```

---

## 🔑 Configure Relying Party (RP) ID

In `views.py`, set your WebAuthn Relying Party ID:

```python
from fido2.webauthn import PublicKeyCredentialRpEntity

rp = PublicKeyCredentialRpEntity(id="your-domain.com", name="ExamAuth")
```

> ✅ **RP ID Examples:**
- `localhost` (for development)
- `example.com` (production)
- `abcd-123-456-789.ngrok-free.app` (for testing with ngrok)

> ❌ **Invalid RP IDs:**
- `https://example.com` (no protocol allowed)
- `localhost:8000` (no ports allowed)

---

## 🧪 Running the System

### Development

```bash
python manage.py migrate
python manage.py runserver
```

Access at: [http://localhost:8000](http://localhost:8000)

### Production

- Requires HTTPS (via Nginx, Gunicorn, etc.)
- Recommended stack:
  - Nginx + Gunicorn
  - Let’s Encrypt for SSL

---

## 📡 WebAuthn Configuration Notes

- **WebAuthn only works on:**
  - `localhost` (for dev)
  - `https` domains (production or tunnels)
- **Ngrok**: When using for testing:
  - Run: `ngrok http 8000`
  - Update `views.py` with the new subdomain:
    ```python
    rp = PublicKeyCredentialRpEntity(id="new-ngrok-subdomain.ngrok-free.app", name="ExamAuth")
    ```

---

## 📚 API Endpoints

| Endpoint                       | Method | Description                           |
|--------------------------------|--------|---------------------------------------|
| `/register-fingerprint/begin` | POST   | Starts fingerprint registration       |
| `/register-fingerprint`       | POST   | Completes fingerprint registration    |
| `/fingerprint-login/begin`    | POST   | Starts fingerprint login              |
| `/fingerprint-login`          | POST   | Completes fingerprint authentication  |
| `/dashboard`                  | GET    | Student dashboard (requires login)    |


---

## 🛠️ Troubleshooting

### WebAuthn Not Working?

- Ensure you’re using **HTTPS** (or `localhost`)
- Check that the **RP ID** matches your domain exactly
- Open your browser **DevTools console** and check for errors

### Ngrok Domain Changed?

Update `views.py`:

```python
rp = PublicKeyCredentialRpEntity(id="new-ngrok-subdomain.ngrok-free.app", name="ExamAuth")
```

### Browser Support

- ✅ Chrome
- ✅ Firefox
- ✅ Edge
- ⚠️ Safari: Requires user gesture and additional permissions

---

## 🔐 Security Notes

- WebAuthn credentials are stored securely and tied to users
- Never commit your `.env` file
- Use a secure `SECRET_KEY` and rotate it periodically
- Use `DEBUG = False` in production

---

## 🚀 Quick Ngrok Deployment Example

```bash
ngrok http 8000  # Start HTTPS tunnel
# Update RP ID in views.py with new ngrok domain
python manage.py runserver 0.0.0.0:8000
```

Access via the HTTPS ngrok link from your mobile or another device.

---

## 👨‍💻 Author

Built by Kaycee

