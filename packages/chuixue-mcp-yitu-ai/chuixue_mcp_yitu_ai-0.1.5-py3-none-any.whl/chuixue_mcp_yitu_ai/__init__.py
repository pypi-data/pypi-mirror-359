from mcp.server.fastmcp import FastMCP
# import requests
# from typing import Optional
# from pydantic import BaseModel
import os

# # Create an MCP server
mcp = FastMCP("chuixue-mcp-yitu-ai", version="0.1.2", description="MCP server for Yitu AI")

# # 从环境变量获取API密钥（更安全的方式）
EDRAWMAX_API_KEY = os.getenv("EDRAWMAX_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJFZHJhd1NvZnQiLCJzdWIiOiJ7XCJjb3JwVXNlcklkXCI6XCJcIixcIm9wZW5JZFwiOlwiXCIsXCJjb3JwSWRcIjpcIlwiLFwidW5pb25fa2V5XCI6XCJcIixcInBsYXRmb3JtXCI6XCJ3ZWItbWF4XCJ9IiwiZXhwIjoxNzU0MDIxOTA5LCJpYXQiOjE3NTE0Mjk4NDksImF1ZCI6IjM5NTM5NDc5Iiwic3JjIjoicGFzc3dvcmQifQ.x-Tt6SuWIxGxW3iqpKCHPbxSsaHjBqNFsTOuopl9dsA")

print(f"{EDRAWMAX_API_KEY}:{99}")
# # 定义请求模型
# class EdrawMaxCompletionRequest(BaseModel):
#     prompt: str
#     mode: str = "ppt-define"
#     user_lang: str = "cn"
#     tpl_id: int = 0
#     gen_type: str = "pptx"
#     device_id: Optional[str] = None

# # 添加EdrawMax AI工具
# @mcp.tool()
# def edrawmax_ai_completion(
#     prompt: str,
#     mode: str = "ppt-define",
#     user_lang: str = "cn",
#     tpl_id: int = 0,
#     gen_type: str = "pptx",
#     device_id: Optional[str] = "470eef96164ccfc00b00ca719629f2d3"
# ) -> dict:
#     """
#     调用EdrawMax AI补全接口生成PPT内容
    
#     Args:
#         prompt: 提示词内容
#         mode: 模式，默认为"ppt-define"
#         user_lang: 用户语言，默认为"cn"
#         tpl_id: 模板ID，默认为0
#         gen_type: 生成类型，默认为"pptx"
#         device_id: 设备ID，默认使用预设值
    
#     Returns:
#         dict: 包含API响应数据
#     """
#     # 准备请求数据
#     payload = {
#         "Prompt": prompt,
#         "Mode": mode,
#         "UserLang": user_lang,
#         "TplId": tpl_id,
#         "GenType": gen_type,
#         "DeviceId": device_id
#     }
    
#     # 准备请求头
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {EDRAWMAX_API_KEY}"
#     }
    
#     try:
#         # 调用EdrawMax API
#         response = requests.post(
#             "https://api.edrawmax.cn/api/ai/v1/completions/native",
#             json=payload,
#             headers=headers,
#             timeout=30
#         )
        
#         # 检查响应状态
#         response.raise_for_status()
#         return response.json()
        
#     except requests.exceptions.RequestException as e:
#         return {
#             "error": True,
#             "message": f"Error calling EdrawMax API: {str(e)}",
#             "status_code": e.response.status_code if hasattr(e, 'response') else None
#         }

# 其他工具保持不变...
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return f"{EDRAWMAX_API_KEY}:{a + b}" 

@mcp.tool()
def show(a: int, b: int) -> int:
    """show two numbers"""
    return f"{EDRAWMAX_API_KEY}:{a - b}" 

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport='stdio')
