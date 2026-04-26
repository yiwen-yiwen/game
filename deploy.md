# 大学生期末求生模拟器 - 部署指南

## 项目结构

```
final-survival-simulator/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   └── main.py   # 主应用入口
│   └── requirements.txt
├── frontend/          # 前端静态文件
│   ├── index.html    # 游戏主页面
│   └── images/       # 游戏图片资源
├── Dockerfile        # Docker 构建文件
├── docker-compose.yml # Docker Compose 配置
├── vercel.json       # Vercel 部署配置
└── deploy.md         # 本部署指南
```

## 部署方式

### 方式一：Vercel 部署（推荐，免费）

1. **注册 Vercel 账号**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

2. **安装 Vercel CLI**
   ```bash
   npm install -g vercel
   ```

3. **部署项目**
   ```bash
   cd final-survival-simulator
   vercel
   ```

4. **按照提示操作**
   - 登录 Vercel 账号
   - 选择项目配置
   - 等待部署完成

5. **访问部署后的网站**
   - Vercel 会提供一个 `.vercel.app` 的域名

### 方式二：Docker 部署

1. **安装 Docker**
   - 访问 https://docs.docker.com/get-docker/
   - 下载并安装 Docker Desktop

2. **构建并运行容器**
   ```bash
   cd final-survival-simulator
   docker-compose up -d
   ```

3. **访问应用**
   - 打开浏览器访问 http://localhost:8000

4. **停止服务**
   ```bash
   docker-compose down
   ```

### 方式三：本地部署

1. **安装 Python 依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **启动后端服务**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **访问应用**
   - 打开浏览器访问 http://localhost:8000

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| PORT | 8000 | 服务端口 |
| PYTHONPATH | /app | Python 路径 |

## 注意事项

1. **游戏数据存储**
   - 当前使用内存存储游戏状态
   - 重启服务后数据会丢失
   - 如需持久化，建议添加 Redis 或数据库

2. **静态文件**
   - 前端文件已集成到后端服务中
   - 访问根路径 `/` 即可看到游戏页面

3. **CORS 配置**
   - 当前允许所有跨域请求
   - 生产环境建议限制特定域名

## 故障排除

### 端口被占用
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 终止进程
kill -9 <PID>
```

### Docker 构建失败
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose up --build
```

## 技术支持

如有问题，请检查：
1. Python 版本 >= 3.8
2. 所有依赖已正确安装
3. 端口未被其他程序占用
