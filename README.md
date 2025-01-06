# LLM_Performance_Analyzer

## Run Backend

```bash
docker build -t my-django-app -f ./server/dockerfile .
docker run -p 8080:8080 my-django-app
```

## Run Frontend

```bash
cd client
npm install
npm run dev
```