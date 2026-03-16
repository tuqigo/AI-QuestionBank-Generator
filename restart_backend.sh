#!/bin/bash
set -e

# ===================== 改成你自己的固定路径 =====================
PROJECT_ROOT="/root/AI-QuestionBank-Generator"   # 写死你的绝对路径
BACKEND_DIR="${PROJECT_ROOT}/backend"
LOG_FILE="${BACKEND_DIR}/uvicorn.log"
LOG_BACKUP="${BACKEND_DIR}/uvicorn.log.$(date +%Y%m%d_%H%M%S)"
PORT=8000
HEALTH_CHECK_URL="http://127.0.0.1:${PORT}/health"  # 如有健康检查端点
# ===============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 清理临时文件函数
cleanup_temp() {
    rm -f /tmp/uvicorn_temp.log 2>/dev/null || true
}

# 陷阱处理：脚本异常退出时清理临时文件
trap cleanup_temp EXIT

echo -e "${YELLOW}===== 安全更新并重启后端（Python3.8 兼容性检测版）=====${NC}"

# 1. 拉代码
echo -e "\n1. 拉取最新代码..."
cd "${PROJECT_ROOT}"
git pull
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git 拉取失败，退出！旧服务仍在运行${NC}"
    exit 1
fi

# 2. 【新增】先检测 Python 版本是否为 3.8（防止环境错）
echo -e "\n2. 检测 Python 版本..."
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "${PY_VERSION}" != "3.8" ]; then
    echo -e "${RED}❌ 当前 Python 版本是 ${PY_VERSION}，要求 3.8！${NC}"
    echo -e "${RED}👉 旧服务继续运行，线上无影响${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 版本符合要求（3.8）${NC}"

# 3. 【增强】先运行代码语法/导入检测（比--check 更全面）
echo -e "\n3. 检测代码 Python3.8 兼容性（语法 + 导入）..."
cd "${BACKEND_DIR}"
# 先执行语法检查（不运行代码，只解析）
if ! python3 -m py_compile main.py; then
    echo -e "${RED}❌ 代码语法不兼容 Python3.8！${NC}"
    echo -e "${RED}👉 已终止部署，旧服务继续运行${NC}"
    exit 1
fi
# 验证 FastAPI 应用能否正常导入（替代 uvicorn --check，该参数不存在）
if ! python3 -c "from main import app; print('FastAPI app loaded successfully')"; then
    echo -e "${RED}❌ FastAPI 应用加载失败（Python3.8 不兼容）！${NC}"
    echo -e "${RED}👉 已终止部署，旧服务继续运行${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 代码 Python3.8 兼容性检测通过${NC}"

# 4. 【可选】轻量运行检测（启动 1 秒后退出，验证核心逻辑）
echo -e "\n4. 轻量启动验证（不占端口，不影响旧服务）..."
# 用临时端口启动，1 秒后自动退出，检测运行时问题
TEMP_PORT=8001  # 临时端口，不和正式端口冲突
nohup python3 -m uvicorn main:app --host 127.0.0.1 --port ${TEMP_PORT} > /tmp/uvicorn_temp.log 2>&1 &
TEMP_PID=$!
sleep 2  # 给 2 秒时间让服务启动，检测运行时错误

# 确保临时进程被清理
if kill -0 ${TEMP_PID} 2>/dev/null; then
    kill -9 ${TEMP_PID} 2>/dev/null || true
    wait ${TEMP_PID} 2>/dev/null || true
fi

# 检查临时日志是否有 Python 版本相关错误（修复正则表达式）
if grep -E "Python 3\.([9-9]|1[0-9])|requires Python|not supported in Python 3\.8|ModuleNotFoundError|ImportError" /tmp/uvicorn_temp.log 2>/dev/null; then
    echo -e "${RED}❌ 运行时检测到 Python3.8 不兼容问题！${NC}"
    echo -e "${RED}👉 已终止部署，旧服务继续运行${NC}"
    cleanup_temp
    exit 1
fi
cleanup_temp
echo -e "${GREEN}✅ 轻量运行验证通过${NC}"

# 5. 备份旧日志（可选，方便回滚排查）
echo -e "\n5. 备份旧日志..."
if [ -f "${LOG_FILE}" ]; then
    mv "${LOG_FILE}" "${LOG_BACKUP}"
    echo -e "${GREEN}✅ 旧日志已备份：${LOG_BACKUP}${NC}"
else
    echo -e "${YELLOW}⚠️  无旧日志可备份${NC}"
fi

# 6. 代码没问题了，再杀旧进程
echo -e "\n6. 停止旧服务..."
# 方法 1：优先用 lsof 检测端口占用（更可靠）
if command -v lsof >/dev/null 2>&1; then
    OLD_PID=$(lsof -ti :${PORT} 2>/dev/null || echo "")
elif command -v netstat >/dev/null 2>&1; then
    # 方法 2：用 netstat（Windows/Linux）
    OLD_PID=$(netstat -ano 2>/dev/null | grep ":${PORT} " | grep LISTENING | awk '{print $NF}' | head -1 || echo "")
else
    # 方法 3：降级用 ps grep（原逻辑，增强匹配）
    OLD_PID=$(ps aux | grep "[u]vicorn.*main:app.*--port.*${PORT}" | awk '{print $2}' | head -1 || echo "")
fi

if [ -n "${OLD_PID}" ]; then
    kill -9 "${OLD_PID}" 2>/dev/null || true
    # 等待进程完全退出
    sleep 1
    if ps -p "${OLD_PID}" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  旧进程仍在运行，尝试强制终止...${NC}"
        kill -KILL "${OLD_PID}" 2>/dev/null || true
        sleep 1
    fi
    echo -e "${GREEN}✅ 旧进程已停止（PID: ${OLD_PID}）${NC}"
else
    echo -e "${YELLOW}⚠️  未找到占用端口 ${PORT} 的进程${NC}"
fi

# 7. 启动新服务
echo -e "\n7. 启动新服务..."
> "${LOG_FILE}"
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT} > "${LOG_FILE}" 2>&1 &
NEW_PID=$!

# 等待服务启动
sleep 3

# 方法 1：优先用健康检查端点验证（如果有）
SERVICE_READY=false
if curl --version >/dev/null 2>&1; then
    # 尝试健康检查端点（如果后端实现了/health）
    if curl -s --connect-timeout 2 "${HEALTH_CHECK_URL}" >/dev/null 2>&1; then
        SERVICE_READY=true
        echo -e "${GREEN}✅ 健康检查通过${NC}"
    fi
fi

# 方法 2：降级用进程检查 + 日志检查
if [ "${SERVICE_READY}" = false ]; then
    if ps -p "${NEW_PID}" > /dev/null 2>&1; then
        # 进程存在，再检查日志是否有启动成功标志
        if grep -q "Uvicorn running on http://0.0.0.0:${PORT}" "${LOG_FILE}" 2>/dev/null; then
            SERVICE_READY=true
            echo -e "${GREEN}✅ 服务启动日志验证通过${NC}"
        elif grep -q "Started server process" "${LOG_FILE}" 2>/dev/null; then
            SERVICE_READY=true
            echo -e "${GREEN}✅ 服务进程启动验证通过${NC}"
        fi
    fi
fi

# 方法 3：最后降级方案，只检查进程是否存在
if [ "${SERVICE_READY}" = false ]; then
    if ps -p "${NEW_PID}" > /dev/null 2>&1; then
        SERVICE_READY=true
        echo -e "${YELLOW}⚠️  使用降级方案验证（仅进程检查）${NC}"
    fi
fi

# 最终判断
if [ "${SERVICE_READY}" = true ]; then
    echo -e "${GREEN}===== ✅ 部署成功！=====${NC}"
    echo -e "PID: ${NEW_PID}"
    echo -e "端口：${PORT}"
    echo -e "日志：tail -f ${LOG_FILE}"
    echo -e "备份日志：${LOG_BACKUP}"
else
    echo -e "${RED}❌ 启动失败，请查日志：${LOG_FILE}${NC}"
    echo -e "${RED}最后日志内容：${NC}"
    tail -20 "${LOG_FILE}" 2>/dev/null || echo "日志为空"
    exit 1
fi
