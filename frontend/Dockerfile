FROM node:22 as builder
WORKDIR /app
COPY . .
RUN npm install -g @angular/cli
RUN npm install
RUN ng build

FROM nginx:latest
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html
