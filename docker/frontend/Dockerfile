# ---- Frontend ----
FROM node:24 AS build-stage

WORKDIR /app/frontend
COPY ./frontend/package*.json ./

RUN npm install

COPY ./frontend ./
RUN npm run build

# ---- Production Stage ----
FROM nginx:alpine AS production-stage
COPY --from=build-stage /app/frontend/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]