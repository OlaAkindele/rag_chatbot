# frontend/Dockerfile


# multi-stage Dockerfile to build the frontend using Node 18 on Alpine, generates the production build, 
# then serves those static files with Nginx (replacing its default config) on port 80.

#  build stage
FROM node:18-alpine AS builder
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# run stage
FROM nginx:alpine
COPY --from=builder /usr/src/app/build /usr/share/nginx/html
# remove default config and use a minimal one 
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
