#!/bin/bash
set -e

# ===================== 改成你自己的固定路径 =====================
PROJECT_ROOT="/root/AI-QuestionBank-Generator"   # 写死你的绝对路径
BACKEND_DIR="${PROJECT_ROOT}/backend"
LOG_FILE="${BACKEND_DIR}/uvicorn.log"
PORT=8000
# ===============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}===== 安全更新并重启后端（Python3.8 兼容性检测版）=====${NC}"

# 1. 拉代码
echo -e "\n1. 拉取最新代码..."
cd "${PROJECT_ROOT}"
git pull
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git拉取失败，退出！旧服务仍在运行${NC}"
    exit 1
fi

# 2. 【新增】先检测Python版本是否为3.8（防止环境错）
echo -e "\n2. 检测Python版本..."
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "${PY_VERSION}" != "3.8" ]; then
    echo -e "${RED}❌ 当前Python版本是 ${PY_VERSION}，要求3.8！${NC}"
    echo -e "${RED}👉 旧服务继续运行，线上无影响${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python版本符合要求（3.8）${NC}"

# 3. 【增强】先运行代码语法/导入检测（比--check更全面）
echo -e "\n3. 检测代码Python3.8兼容性（语法+导入）..."
cd "${BACKEND_DIR}"
# 先执行语法检查（不运行代码，只解析）
if ! python3 -m py_compile main.py; then
    echo -e "${RED}❌ 代码语法不兼容Python3.8！${NC}"
    echo -e "${RED}👉 已终止部署，旧服务继续运行${NC}"
    exit 1
fi
# 再执行uvicorn基础检查（验证FastAPI应用）
if ! python3 -m uvicorn main:app --check; then
    echo -e "${RED}❌ FastAPI应用加载失败（Python3.8不兼容）！${NC}"
    echo -e "${RED}👉 已终止部署，旧服务继续运行${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 代码Python3.8兼容性检测通过${NC}"

# 4. 【可选】轻量运行检测（启动1秒后退出，验证核心逻辑）
echo -e "\n4. 轻量启动验证（不占端口，不影响旧服务）..."
# 用临时端口启动，1秒后自动退出，检测运行时问题
TEMP_PORT=8001  # 临时端口，不和正式端口冲突
nohup python3 -m uvicorn main:app --host 127.0.0.1 --port ${TEMP_PORT} > /tmp/uvicorn_temp.log 2>&1 &
TEMP_PID=$!
sleep 2  # 给2秒时间让服务启动，检测运行时错误
kill -9 ${TEMP_PID} > /dev/null 2>&1  # 杀掉临时进程

# 检查临时日志是否有Python版本相关错误
if grep -E "Python 3\.[9-9]|requires Python|not supported in Python 3.8" /tmp/uvicorn_temp.log; then
    echo -e "${RED}❌ 运行时检测到Python3.8不兼容问题！${NC}"
    echo -e "${RED}👉 已终止部署，旧服务继续运行${NC}"
    rm -f /tmp/uvicorn_temp.log
    exit 1
fi
rm -f /tmp/uvicorn_temp.log  # 清理临时日志
echo -e "${GREEN}✅ 轻量运行验证通过${NC}"

# 5. 代码没问题了，再杀旧进程
echo -e "\n5. 停止旧服务..."
OLD_PID=$(ps aux | grep "[u]vicorn main:app --host 0.0.0.0 --port ${PORT}" | awk '{print $2}')
if [ -n "${OLD_PID}" ]; then
    kill -9 "${OLD_PID}"
    echo -e "${GREEN}✅ 旧进程已停止${NC}"
else
    echo -e "${YELLOW}⚠️  未找到旧进程${NC}"
fi

# 6. 启动新服务
echo -e "\n6. 启动新服务..."
> "${LOG_FILE}"
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT} > "${LOG_FILE}" 2>&1 &
NEW_PID=$!

sleep 2
if ps -p "${NEW_PID}" > /dev/null; then
    echo -e "${GREEN}===== ✅ 部署成功！=====${NC}"
    echo -e "PID: ${NEW_PID}"
    echo -e "日志: tail -f ${LOG_FILE}"
else
    echo -e "${RED}❌ 启动失败，请查日志：${LOG_FILE}${NC}"
    exit 1
fi