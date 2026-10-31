# Build de produção do PWA servido por nginx (homologação).
#
# A URL da API é embutida no build pelo Vite, por isso entra como build-arg.

FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .
ARG VITE_API_URL=http://localhost:8000/api/v1
ENV VITE_API_URL=$VITE_API_URL
# Testes do domínio e checagem de tipos rodam no build: imagem quebrada não sobe.
RUN npm run teste && npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
