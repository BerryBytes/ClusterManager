# Declare the base image
FROM node:16-alpine3.14

# Build step
# 1. Copy package.json and package-lock.json to /app dir
RUN mkdir /app
COPY package*.json /app

# 2. Change working directory to the newly created app dir
WORKDIR /app

# 3. Install dependencies
RUN npm install --legacy-peer-deps

# 4. Copy the source code to /app dir
COPY . .

# 5. Build the TypeScript code and then run vite build
RUN npm run build

# 6. Expose port 3000 on the container
EXPOSE 3000

# 7. Run the app
CMD ["npm", "run", "preview"]