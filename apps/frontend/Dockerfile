# 前端 Dockerfile - React + Mantine + Vite

# 使用 Node.js 18 作為基礎映像
FROM node:18-alpine

# 安裝 pnpm
#RUN npm install -g pnpm@8

# 設定工作目錄
WORKDIR /app

# 複製 package 文件
#COPY package.json pnpm-lock.yaml* ./

# 複製 package 文件
COPY package.json package-lock.json* ./

# 安裝依賴
#RUN pnpm install

# 使用 npm 安裝依賴
RUN npm ci

# 複製源碼
COPY . .

# 暴露端口
EXPOSE 3000

# 開發模式啟動命令
#CMD ["pnpm", "dev", "--host", "0.0.0.0"]
CMD ["npm", "run", "dev","--host","0.0.0.0"]