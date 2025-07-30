from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("MachineCommander")

@mcp.tool()
def get_construction_machines_data(question: str) -> dict:
    """MachineCommander is a global system to manage all the construction machines working on construction projects. Use this tool to extract the data of construction machines and projects, and to answer construction related questions. The return value is a list of rows, with each row as a dict."""
    url = f"https://gpt-agent.zhgcloud.com/paipai_mcp/{question}"
    auth = ("zeaho-data", "Zeaho_93246!")
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        try:
            result_data = response.json()
            result = {"result": result_data}
        except:
            result = {"result": response.text}
    except Exception as e:
        result = {"result": f"请求失败: {str(e)}"}
    return result

@mcp.tool()
def manage_construction_machines(order: str) -> dict:
    """MachineCommander is a global system to manage all the construction machines working on construction projects. Use this tool to send orders to the construction machines."""
    return {"result": "nop"}

# Start the server
def main():
    mcp.run(transport="stdio")
