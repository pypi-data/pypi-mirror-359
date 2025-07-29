from mcp.server.fastmcp import FastMCP

# 创建MCP服务实例
mcp = FastMCP("我的天气系统")


# 其他工具函数...
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def get_city_weather(city: str = '') -> str:
    """获取城市天气信息"""
    if city == "北京":
        return "北京天气，晴转多云，15℃~18℃"
    elif city == "上海":
        return "上海天气，雨，15℃~19℃"
    elif city == "广州":
        return "广州天气，多云，20℃~30℃"
    elif city == "深圳":
        return "深圳天气，晴，25℃~30℃"
    return "没有该城市的天气信息"





def main()-> None:
    mcp.run(transport='stdio')

if __name__=="__main__":
    main()













