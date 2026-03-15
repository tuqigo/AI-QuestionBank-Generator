from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from models.user import UserGradeUpdate
from services.user.user_store import update_user_grade
from api.v1.auth import get_current_user_email
from utils.logger import api_logger

router = APIRouter(prefix="/api/users", tags=["users"])


@router.put("/grade")
async def update_grade(
    data: UserGradeUpdate,
    email: str = Depends(get_current_user_email)
):
    """更新当前用户年级"""
    # 验证年级格式
    valid_grades = [f"grade{i}" for i in range(1, 10)]  # grade1~grade9
    if data.grade not in valid_grades:
        api_logger.warning(f"更新年级失败 - 无效的年级：{data.grade}")
        raise HTTPException(status_code=400, detail="无效的年级格式")

    # 获取用户 ID
    from services.user.user_store import get_user
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新年级
    success = update_user_grade(user.id, data.grade)
    if success:
        api_logger.info(f"用户年级更新成功：email={email}, grade={data.grade}")
        return {"message": "年级更新成功", "grade": data.grade}
    else:
        raise HTTPException(status_code=500, detail="更新失败")
