# Dockerfile for frontend

# Stage 1: Build the React application
FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend application code
COPY frontend/ ./

# Build the application
RUN npm run build

# Stage 2: Serve the application using a lightweight server
FROM node:18-alpine

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy the build output from the build stage
COPY --from=build /app/dist ./dist

# Expose port 3000
EXPOSE 3000

# Serve the application
CMD ["serve", "-s", "dist", "-l", "3000"]
