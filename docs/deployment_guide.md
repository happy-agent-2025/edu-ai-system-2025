# 部署指南

## 1. 系统要求

### 1.1 硬件要求

#### 最低配置
- CPU: 2核
- 内存: 4GB
- 磁盘空间: 20GB可用空间
- 网络: 100Mbps网络连接

#### 推荐配置
- CPU: 4核或以上
- 内存: 8GB或以上
- 磁盘空间: 50GB可用空间
- 网络: 1Gbps网络连接

### 1.2 软件要求

- 操作系统: Linux (Ubuntu 18.04+/CentOS 7+) / Windows Server 2016+ / macOS 10.14+
- Python版本: 3.8或以上
- 数据库: SQLite 3.5+ (默认) 或 PostgreSQL 12+ / MySQL 8+
- Docker: 20.10+ (可选，用于容器化部署)
- Node.js: 14+ (用于前端构建，可选)

## 2. 环境准备

### 2.1 Python环境设置

```bash
# 安装Python虚拟环境
python3 -m venv edu-ai-env
source edu-ai-env/bin/activate  # Linux/macOS
# 或
edu-ai-env\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip
```

### 2.2 依赖安装

```bash
# 克隆项目代码
git clone <repository-url>
cd edu-ai-system

# 安装Python依赖
pip install -r requirements.txt
```

### 2.3 数据库初始化

```bash
# 运行数据库初始化脚本
python scripts/setup_db.py --setup
```

### 2.4 模型下载

```bash
# 下载所需模型
python scripts/model_downloader.py --all
```

## 3. 配置文件设置

### 3.1 配置文件位置

所有配置文件位于 `configs/` 目录下：
- `audio.yaml`: 音频相关配置
- `agent.yaml`: Agent相关配置
- `web.yaml`: Web服务相关配置
- `logging.yaml`: 日志相关配置
- `security.yaml`: 安全相关配置

### 3.2 环境变量设置

创建 `.env` 文件或设置系统环境变量：

```bash
# 数据库配置
DATABASE_URL=sqlite:///edu_ai.db

# JWT密钥
JWT_SECRET_KEY=your-super-secret-jwt-key

# Flask配置
FLASK_ENV=production
FLASK_APP=backend/app.py

# 日志配置
LOG_LEVEL=INFO
```

## 4. 启动服务

### 4.1 直接运行

```bash
# 启动后端服务
python run.py

# 或者直接运行Flask应用
cd backend
python app.py
```

### 4.2 使用Gunicorn (生产环境推荐)

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### 4.3 启动前端

```bash
# 安装Streamlit
pip install streamlit

# 启动Streamlit应用
streamlit run streamlit_ui/main_app.py
```

## 5. Docker部署

### 5.1 构建Docker镜像

```bash
# 构建后端服务镜像
docker build -t edu-ai-backend .

# 构建前端服务镜像
docker build -f Dockerfile.streamlit -t edu-ai-frontend .
```

### 5.2 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs
```

### 5.3 Docker Compose配置

docker-compose.yml示例：

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=sqlite:///data/edu_ai.db
      - JWT_SECRET_KEY=your-super-secret-jwt-key
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:5000

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=edu_ai
      - POSTGRES_USER=edu_user
      - POSTGRES_PASSWORD=edu_password
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  db_data:
```

## 6. 反向代理配置

### 6.1 Nginx配置

```nginx
server {
    listen 80;
    server_name edu-ai.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 6.2 Apache配置

```apache
<VirtualHost *:80>
    ServerName edu-ai.yourdomain.com
    
    ProxyPreserveHost On
    
    ProxyPass /api/ http://localhost:5000/api/
    ProxyPassReverse /api/ http://localhost:5000/api/
    
    ProxyPass / http://localhost:8501/
    ProxyPassReverse / http://localhost:8501/
</VirtualHost>
```

## 7. 安全配置

### 7.1 SSL证书配置

使用Let's Encrypt获取免费SSL证书：

```bash
# 安装certbot
sudo apt-get install certbot

# 获取证书
sudo certbot certonly --standalone -d edu-ai.yourdomain.com
```

### 7.2 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 8. 监控和日志

### 8.1 系统监控

```bash
# 运行系统监控脚本
python scripts/system_monitor.py --monitor --duration 3600
```

### 8.2 日志管理

日志文件位置：
- 应用日志: `logs/edu_ai.log`
- 错误日志: `logs/error.log`
- API日志: `logs/api.log`
- 数据库日志: `logs/database.log`

### 8.3 日志轮转

配置logrotate (Linux):

```bash
# /etc/logrotate.d/edu-ai
/path/to/edu-ai-system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        /usr/bin/killall -HUP edu-ai-app
    endscript
}
```

## 9. 备份和恢复

### 9.1 数据库备份

```bash
# SQLite备份
cp data/edu_ai.db data/edu_ai.db.backup.$(date +%Y%m%d)

# PostgreSQL备份
pg_dump -U edu_user -h localhost edu_ai > backup/edu_ai_$(date +%Y%m%d).sql
```

### 9.2 数据恢复

```bash
# SQLite恢复
cp data/edu_ai.db.backup.20230101 data/edu_ai.db

# PostgreSQL恢复
psql -U edu_user -h localhost edu_ai < backup/edu_ai_20230101.sql
```

## 10. 性能调优

### 10.1 Gunicorn配置

```bash
# 根据CPU核心数调整worker数量
gunicorn -w $(nproc) -b 0.0.0.0:5000 backend.app:app
```

### 10.2 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX idx_safety_logs_user_id ON safety_logs(user_id);
```

### 10.3 缓存配置

在 `configs/web.yaml` 中配置缓存：

```yaml
cache:
  type: "redis"
  redis_host: "localhost"
  redis_port: 6379
  default_timeout: 300
```

## 11. 故障排除

### 11.1 常见问题

#### 启动失败
```bash
# 检查端口占用
netstat -tlnp | grep :5000

# 检查日志
tail -f logs/error.log
```

#### 数据库连接问题
```bash
# 检查数据库服务
systemctl status postgresql

# 测试连接
python -c "import sqlite3; print(sqlite3.connect('edu_ai.db').execute('SELECT 1').fetchone())"
```

#### 内存不足
```bash
# 检查内存使用
free -h

# 重启服务
systemctl restart edu-ai-backend
```

### 11.2 性能问题

```bash
# 监控系统资源
python scripts/system_monitor.py --health

# 分析慢查询
python -m cProfile -o profile.out run.py
```

## 12. 升级维护

### 12.1 代码更新

```bash
# 拉取最新代码
git pull origin main

# 安装新依赖
pip install -r requirements.txt

# 运行数据库迁移
# (如果有的话)

# 重启服务
systemctl restart edu-ai-backend
```

### 12.2 数据库迁移

```bash
# 运行迁移脚本
# (如果有数据库结构变更)
```

## 13. 联系支持

如有部署问题，请联系技术支持：
- 邮箱: support@edu-ai-system.com
- 电话: 400-xxx-xxxx
- 在线文档: https://docs.edu-ai-system.com