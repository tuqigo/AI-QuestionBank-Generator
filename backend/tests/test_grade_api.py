#!/usr/bin/env python
"""测试年级选择功能"""

import requests

BASE_URL = "http://localhost:8000"

def test_register_and_grade():
    # 1. 发送验证码
    email = f"test_{requests.utils.default_user_agent().replace(' ', '_')}@example.com"
    # 使用固定测试邮箱
    email = "test_grade_001@example.com"

    print(f"测试邮箱：{email}")

    # 2. 发送 OTP
    res = requests.post(f"{BASE_URL}/api/auth/send-otp", json={
        "email": email,
        "purpose": "register"
    })
    print(f"发送验证码：{res.status_code} - {res.json()}")

    # 注意：实际测试需要手动获取验证码
    # 这里只演示流程
    code = input("请输入收到的验证码：")

    # 3. 注册
    res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "password": "Test1234",
        "code": code
    })
    print(f"注册：{res.status_code} - {res.json()}")

    if res.status_code != 200:
        print("注册失败")
        return

    token = res.json()["access_token"]
    print(f"Token: {token[:20]}...")

    # 4. 获取用户信息（检查 grade 字段）
    res = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"用户信息：{res.status_code} - {res.json()}")

    # 5. 更新年级
    res = requests.put(
        f"{BASE_URL}/api/users/grade",
        headers={"Authorization": f"Bearer {token}"},
        json={"grade": "grade1"}
    )
    print(f"更新年级：{res.status_code} - {res.json()}")

    # 6. 再次获取用户信息（验证 grade 已保存）
    res = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"用户信息（更新后）：{res.status_code} - {res.json()}")

if __name__ == "__main__":
    test_register_and_grade()
