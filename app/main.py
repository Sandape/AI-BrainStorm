# 导入标准库和第三方库
import os  # 操作系统接口模块，用于读取环境变量等
from fastapi import FastAPI, Request, HTTPException  # FastAPI核心组件
from fastapi.templating import Jinja2Templates  # 模板渲染引擎
from fastapi.staticfiles import StaticFiles  # 静态文件服务
from fastapi.middleware.cors import CORSMiddleware  # 跨域请求中间件
from slowapi import Limiter, _rate_limit_exceeded_handler  # 请求限流组件
from slowapi.errors import RateLimitExceeded  # 限流异常类
from slowapi.util import get_remote_address  # 获取客户端IP方法
import logging  # Python标准日志模块
from dotenv import load_dotenv  # 环境变量加载器
from termcolor import colored  # 终端彩色输出
from datetime import datetime  # 时间处理模块

# 初始化FastAPI应用实例[1,5](@ref)
app = FastAPI()
# 创建限流器实例，基于客户端IP识别[5](@ref)
limiter = Limiter(key_func=get_remote_address)

# 自定义彩色日志系统（增强开发调试体验）
def log_info(message):
    """信息级别日志（绿色）"""
    print(colored(f"[+] {datetime.now()} 🎯 {message}", "green"))

def log_warning(message):
    """警告级别日志（黄色）"""
    print(colored(f"[!] {datetime.now()} ⚠️ {message}", "yellow"))

def log_error(message):
    """错误级别日志（红色）"""
    print(colored(f"[-] {datetime.now()} ❌ {message}", "red"))

def log_success(message):
    """成功状态日志（绿色）"""
    print(colored(f"[+] {datetime.now()} ✅ {message}", "green"))

# 注册限流异常处理器[5](@ref)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """处理请求频率超限异常"""
    log_warning(f"限流触发: {request.client.host} - {str(exc)}")
    return {"detail": f"请求过多: {str(exc)}"}

# 加载环境变量配置[5](@ref)
load_dotenv()
# 环境变量检查机制
load_info = []
for key in ['DEEPSEEK_CHAT_KEY', 'OPENAI_API_KEY']:  # 关键API密钥检查
    value = os.getenv(key)
    load_info.append((key, value if value else colored('未设置', 'red')))

# 服务启动报告（增强可观测性）
print("="*70)
print(f"{'API 服务启动报告':^70}")  # 居中显示标题
print(f"{'='*70}\n")
print(f"🚀 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🌐 监听地址: {colored('http://localhost:8000', 'cyan')}")
print(f"📝 环境变量状态:")
for key, status in load_info:  # 遍历显示环境变量状态
    print(f"  {key.ljust(25)}: {status}")
print(f"\n🔧 配置摘要:")
print(f"  CORS策略: {colored('启用（允许所有来源）', 'green')}")  # 开发环境宽松策略[1,4](@ref)
print(f"  静态资源: {colored('已挂载到 /static', 'green')}")  # 静态文件服务配置[3](@ref)
print(f"  API路由: {colored('/api 路径组', 'green')}")  # 路由分组管理
print(f"  限流策略: {colored('IP级限流（未配置具体规则）', 'yellow')}")  # 安全防护提示

# 中间件配置（关键安全组件）[1,4](@ref)
app.add_middleware(
    CORSMiddleware,  # 跨域资源共享中间件
    allow_origins=["*"],  # 允许所有来源（生产环境应限制）
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)
log_success("CORS 中间件配置完成")

# 静态文件服务配置[3](@ref)
from pathlib import Path  # 现代化路径处理
app.mount("/static",
         StaticFiles(directory=Path(__file__).parent.parent / "static"),  # 定位上级目录的static文件夹
         name="static")
log_success("静态资源目录已挂载")

# 模板引擎初始化[3](@ref)
templates = Jinja2Templates(directory="templates")  # 指定模板目录
log_success("模板引擎初始化完成")

# 路由模块注册（实现功能模块化）[1,5](@ref)
from app.routers import chat  # 导入聊天功能路由模块
app.include_router(chat.router, prefix="/api")  # 添加/api前缀
log_success("API路由注册完成")

# 日志系统配置（生产环境必备）[5](@ref)
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    handlers=[
        logging.FileHandler('app.log'),  # 文件日志
        logging.StreamHandler()  # 控制台日志
    ]
)
log_success("日志系统初始化完成")

# 根路由处理（入口页面）[1](@ref)
@app.get("/")
async def home(request: Request):
    """渲染首页模板"""
    log_info(f"收到主页请求: {request.client.host}")  # 记录客户端IP
    return templates.TemplateResponse("index.html", {"request": request})  # 模板响应

# 启动完成提示
print(f"\n{'='*70}")
print(f"{'API 服务已就绪':^70}")
print(f"请通过 {colored('http://localhost:8000', 'cyan')} 访问")
print(f"{'='*70}")
# test