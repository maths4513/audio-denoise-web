# audio-denoise-web

🔧 环境要求
Linux (Ubuntu 20.04/22.04 测试通过)

Docker >= 20.10

docker-compose >= 1.29

🛠 部署与运行
1️⃣ 克隆项目
bash
Copy
Edit
git clone <你的github仓库地址>
cd audio-denoise-web
2️⃣ 构建并启动服务
使用 docker-compose 一键启动 Flask Web + Celery Worker + Redis：

bash
Copy
Edit
docker-compose up --build
首次启动会拉取 Python、Redis 镜像并安装依赖，耗时约 3-5 分钟。

3️⃣ 访问 Web 界面
浏览器打开：

cpp
Copy
Edit
http://<你的服务器IP>:5000