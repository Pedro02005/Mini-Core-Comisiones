FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY Fronted/package*.json ./
RUN npm ci
COPY Fronted/ ./
RUN npm run build

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/Backend
COPY Backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY Backend/ ./
COPY --from=frontend /frontend/dist /app/Fronted/dist
RUN DJANGO_DEBUG=true python manage.py collectstatic --noinput
ENV DJANGO_DEBUG=false SEED_DEMO=false
EXPOSE 10000
CMD ["sh", "start.sh"]
