# 🚀 FABERLIC SATIRE RAG - DEMO & LAUNCH GUIDE

## 🎯 Что это за проект?

Это **производственное приложение** для генерации сатирического контента о Faberlic с использованием:
- **Perplexity Pro API** для генерации текста
- **RAG (Retrieval-Augmented Generation)** для контекстного поиска
- **FastAPI** для REST API
- **PostgreSQL + SQLAlchemy ORM** для хранения данных
- **JWT Authentication** для безопасности
- **Docker** для простого развертывания

---

## 📋 БЫСТРЫЙ СТАРТ (5 минут)

### Вариант 1️⃣: Локальный запуск (рекомендуется)

```bash
# 1️⃣ Клонируй репозиторий
git clone https://github.com/Spirix198/faberlic-satire-rag
cd faberlic-satire-rag

# 2️⃣ Создай .env файл
cp .env.example .env

# 3️⃣ Отредактируй .env (добавь свои ключи)
# Открой .env и заполни:
# PERPLEXITY_API_KEY=твой_ключ_от_perplexity_pro
# JWT_SECRET_KEY=какой-нибудь_случайный_ключ
# DATABASE_URL=postgresql://user:password@localhost:5432/faberlic_satire

# 4️⃣ Установи зависимости
pip install -r requirements.txt

# 5️⃣ Запусти API сервер
python api.py

# ✅ Готово! API доступен на:
# http://localhost:8000
# http://localhost:8000/docs (интерактивная документация Swagger)
```

---

### Вариант 2️⃣: Docker запуск

```bash
# 1️⃣ Собери Docker образ
docker build -t faberlic-satire-rag .

# 2️⃣ Запусти контейнер
docker run -p 8000:8000 \
  -e PERPLEXITY_API_KEY=твой_ключ \
  -e JWT_SECRET_KEY=твой_ключ \
  faberlic-satire-rag

# ✅ API доступен на http://localhost:8000
```

---

## 🧪 ТЕСТИРОВАНИЕ API

### Методо 1: Swagger UI (самый простой) 🎨

1. Открой в браузере: **http://localhost:8000/docs**
2. Видишь интерактивный Swagger interface
3. Нажимай "Try it out" для каждого endpoint
4. Заполняй параметры и видишь ответы

### Метод 2: cURL (из терминала)

```bash
# 🏥 Health check (для проверки, что сервер работает)
curl http://localhost:8000/health

# Ответ:
# {"status": "ok", "timestamp": "2025-12-10T..."}
```

### Метод 3: Python requests (из скрипта)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1️⃣ Проверь здоровье сервера
response = requests.get(f"{BASE_URL}/health")
print(response.json())  # {"status": "ok"}

# 2️⃣ Получи список контента
response = requests.get(
    f"{BASE_URL}/api/content",
    params={"skip": 0, "limit": 10}
)
print(response.json())

# 3️⃣ Создай новый контент
payload = {
    "title": "Faberlic: Липидный крем, который изменит жизнь",
    "body": "Представьте себе кремом, который обещает чудеса...",
    "style": "satirical",
    "language": "ru"
}
headers = {"Authorization": "Bearer твой_jwt_token"}
response = requests.post(
    f"{BASE_URL}/api/content",
    json=payload,
    headers=headers
)
print(response.json())
```

---

## 📊 СТРУКТУРА ПРОЕКТА

```
faberlic-satire-rag/
├── api.py                      # Основной FastAPI приложение
├── api/routes/content.py        # REST endpoints для контента
├── auth/jwt_utils.py            # JWT & password utilities
├── database/
│   ├── db_config.py            # Database configuration
│   └── models.py               # SQLAlchemy models
├── security/cors_config.py      # CORS & security headers
├── rag/                         # RAG система с FAISS
├── caching/                     # LRU cache с TTL
├── monitoring/                  # Prometheus metrics
├── rate_limiting/               # API rate limiter
├── errors/                      # Exception handling
├── tests/                       # Integration tests
├── requirements.txt             # Python зависимости
├── Dockerfile                   # Docker конфигурация
├── .env.example                 # Шаблон переменных окружения
├── DEVELOPMENT.md               # Development guide
├── PERPLEXITY_SETUP.md          # Perplexity API setup
└── README.md                    # Основная документация
```

---

## 🔑 НЕОБХОДИМЫЕ КЛЮЧИ

### 1️⃣ Perplexity Pro API Key

1. Перейди на https://www.perplexity.ai
2. Зарегистрируйся/войди в аккаунт
3. Перейди в **Settings → API Keys**
4. Создай новый key
5. Скопируй и вставь в .env как `PERPLEXITY_API_KEY`

### 2️⃣ JWT Secret Key

Можешь использовать любую случайную строку:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3️⃣ Database URL (если используешь PostgreSQL)

```
postgresql://username:password@localhost:5432/faberlic_satire
```

---

## 📖 ПРИМЕРЫ API ЗАПРОСОВ

### Пример 1: Получить здоровье сервера
```bash
curl -X GET http://localhost:8000/health
```

### Пример 2: Создать новый контент
```bash
curl -X POST http://localhost:8000/api/content \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Faberlic: Революция в косметике",
    "body": "Это сатирический пост о Faberlic...",
    "style": "satirical",
    "language": "ru"
  }'
```

### Пример 3: Получить контент по ID
```bash
curl -X GET http://localhost:8000/api/content/content_uuid
```

### Пример 4: Список контента
```bash
curl -X GET "http://localhost:8000/api/content?skip=0&limit=10"
```

---

## 🔒 БЕЗОПАСНОСТЬ

✅ **JWT Authentication** - все endpoints защищены  
✅ **Password Hashing** - bcrypt для хранения паролей  
✅ **CORS** - белый список origin'ов  
✅ **Rate Limiting** - защита от DDoS  
✅ **Security Headers** - HSTS, CSP, X-Frame-Options  
✅ **Input Sanitization** - защита от SQL injection  

---

## 📚 ДОКУМЕНТАЦИЯ

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Development Guide**: [DEVELOPMENT.md](DEVELOPMENT.md)
- **Perplexity Setup**: [PERPLEXITY_SETUP.md](PERPLEXITY_SETUP.md)
- **Full README**: [README.md](README.md)

---

## 🐛 TROUBLESHOOTING

### Ошибка: "Module not found: 'fastapi'"
```bash
# Решение: установи зависимости
pip install -r requirements.txt
```

### Ошибка: "Connection refused" (database)
```bash
# Убедись, что PostgreSQL запущен:
# На Mac: brew services start postgresql
# На Linux: sudo service postgresql start
# На Windows: используй WSL или Docker
```

### Ошибка: "Invalid API key"
```bash
# Проверь:
# 1. PERPLEXITY_API_KEY установлен в .env
# 2. Ключ скопирован без пробелов
# 3. Ключ активный в Perplexity console
```

---

## 🚀 ДЕПЛОЙ В PRODUCTION

### Вариант 1: AWS EC2
```bash
# Запусти на EC2 instance с Docker
docker run -p 80:8000 \
  -e PERPLEXITY_API_KEY=$API_KEY \
  -e DATABASE_URL=$DB_URL \
  faberlic-satire-rag
```

### Вариант 2: Heroku
```bash
# Deploy с Dockerfile
heroku create faberlic-satire
heroku container:push web
heroku container:release web
```

### Вариант 3: Docker Compose (для локальной разработки)
```bash
docker-compose up
```

---

## 📞 КОНТАКТЫ & ПОДДЕРЖКА

- GitHub: https://github.com/Spirix198/faberlic-satire-rag
- Issues: https://github.com/Spirix198/faberlic-satire-rag/issues
- Discussions: https://github.com/Spirix198/faberlic-satire-rag/discussions

---

## 📝 ЛИЦЕНЗИЯ

MIT License - смотри [LICENSE](LICENSE) для деталей

---

**Готово! Попробуй запустить проект и создай свой первый сатирический пост! 🎉**
