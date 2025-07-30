import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from Base.selectLLM import selectLLM
from Base.Constant.runConfig import RUN_MODE


llm = selectLLM(str(RUN_MODE.value))

async def run_agent(messages):
    async with MultiServerMCPClient(
        {
            # "math": {
            #     "command": "python",
            #     # Make sure to update to the full absolute path to your math_server.py file
            #     "args": ["/path/to/math_server.py"],
            #     "transport": "stdio",
            # },
            "ARLMCP": {
                # make sure you start your weather server on port 8000
                "url": "http://127.0.0.1:8000/sse", #  需要考虑鉴权
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(llm, client.get_tools())
        math_response = await agent.ainvoke({"messages": messages})
        return math_response

if __name__ == "__main__":
    result = asyncio.run(run_agent("扫描www.vulbox.com，输出文件泄露。"))  # 用户输入语句,AI将自行理解并调用对应工具
    print(result["messages"][len(result["messages"]) - 1].content)