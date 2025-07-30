from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi_mcp import FastApiMCP

app = FastAPI()

# 授权验证，如果不需要，可以删除
async def verify_token(authorization: str | None = Header(None)):
    # 这里替换为实际的验证逻辑，比如数据库查询，JWT验证等
    valid_tokens = {"123456", "abcdef"}  # 示例有效token集合
    if authorization not in valid_tokens:
        raise HTTPException(status_code=403, detail="Invalid Token")
    return True


# 注意：要设置添加明确的 operation_id 参数，这会让大模型更容易理解工具的作用
@app.get("/getCurrentTime", operation_id="get_current_time")
async def get_current_time():
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# 编写一个模拟获取用户信息的接口
@app.get("/users/{user_id}", operation_id="get_user_info",description="模拟获取用户信息的接口",summary="返回当前用户信息")
async def get_user_info(user_id: int):  # 验证请求头，需要授权访问
# async def get_user_info(user_id: int, is_auth: bool = Depends(verify_token)):  # 验证请求头，需要授权访问
    data = {
        "user_id": user_id,
        "name": "小狗11狗",
        "sex": "男",
        "birthday": "2002-07-06",
    }
    return data


# 创建 MCP 服务器实例，绑定到 FastAPI app
mcp = FastApiMCP(app)
# 挂载 MCP 服务器，默认路径是 /mcp（可以修改）
mcp.mount()

def main():
    # uvicorn.run(app, host="0.0.0.0", port=8000,reload=True)
    print("start !!")
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8000,reload=True, workers=1)


if __name__ == "__main__":
    main()