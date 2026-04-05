# Frontend

## Запуск локально

1. Создайте `.env` на основе `.env.example`.
2. Установите зависимости:

```bash
npm install
```

3. Запустите dev-сервер:

```bash
npm run dev
```

Приложение будет доступно на `http://localhost:5173`.

## Production build

```bash
npm run build
npm run preview
```

## Docker

```bash
docker build -t procurement-frontend .
docker run --rm -p 8080:80 procurement-frontend
```

## Backend

По умолчанию frontend обращается к FastAPI backend по адресу `http://localhost:8000`.
