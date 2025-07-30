import argparse
import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

from asktable_mcp_server.tools import (
    get_asktable_data,
    get_asktable_sql,
    get_datasources_info,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="AskTable MCP Server")
    parser.add_argument(
        "--base_url",
        type=str,
        default=None,
        help="请求所用的服务器主机地址，填写了则使用指定服务器地址，否则使用默认的AskTable服务地址",
    )

    args = parser.parse_args()
    return args


API_KEY = None
DATASOURCE_ID = None
server_ready = False


@asynccontextmanager
async def lifespan(fastmcp_instance):
    """服务器启动和关闭的生命周期管理"""
    global server_ready

    # 启动逻辑
    logger.info("服务器正在初始化...")

    await asyncio.sleep(3)

    server_ready = True
    logger.info("服务器初始化完成，准备接受请求")

    yield  # 服务器运行期间

    # 关闭逻辑
    logger.info("服务器正在关闭...")
    server_ready = False


# 创建服务器时传入 lifespan
mcp = FastMCP(name="AskTable SSE MCP Server", lifespan=lifespan)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint to verify server is ready"""
    if not server_ready:
        return {"status": "initializing", "message": "Server is still initializing"}
    return {"status": "ready", "message": "Server is initialized and ready"}


@mcp.custom_route("/sse/", methods=["GET"])
async def sse_endpoint(request: Request):
    """自定义SSE端点，检查服务器是否准备就绪"""
    global API_KEY, DATASOURCE_ID, server_ready, ROLE_ID

    if not server_ready:
        return {"error": "Server is still initializing, please wait"}

    # 从URL参数获取配置
    API_KEY = request.query_params.get("apikey")
    DATASOURCE_ID = request.query_params.get("datasource_id")
    ROLE_ID = request.query_params.get("role_id")

    if not API_KEY or not DATASOURCE_ID:
        logging.info("error: Missing required parameters: apikey and datasource_id")
        return {"error": "Missing required parameters: apikey and datasource_id"}

    # 返回成功响应或继续SSE连接逻辑
    logging.info(f"apikey :{API_KEY} ,datasource_id :{DATASOURCE_ID}")
    return {"status": "configured", "apikey": API_KEY, "datasource_id": DATASOURCE_ID}


@mcp.tool()
async def gen_sql(query: str) -> str:
    """
    根据用户查询生成对应的SQL语句
    不需要指定数据源ID，该函数已在内部指定了数据源ID，直接发起请求即可
    该函数将用户的查询转换为SQL语句，仅返回SQL文本，不执行查询。

    :param query: 用户的查询内容
                  示例：
                  - "我需要查询昨天的订单总金额的sql"
                  - "我要找出销售额前10的产品的sql"
                  - "统计每个部门的员工数量的sql"
    :return: 生成的SQL语句字符串

    使用场景：
        - 需要查看生成的SQL语句
        - 需要将自然语言转化为SQL查询
        - 仅需要SQL文本而不需要执行结果
    """
    global API_KEY, DATASOURCE_ID, server_ready, ROLE_ID

    if not server_ready:
        return "Server is still initializing, please wait"

    if not API_KEY or not DATASOURCE_ID:
        try:
            request = get_http_request()
            api_key = request.query_params.get("apikey", API_KEY)
            datasource_id = request.query_params.get("datasource_id", DATASOURCE_ID)
        except RuntimeError:
            api_key = API_KEY
            datasource_id = DATASOURCE_ID
    else:
        api_key = API_KEY
        datasource_id = DATASOURCE_ID

    try:
        request = get_http_request()
        role_id = request.query_params.get("role_id", None)
    except RuntimeError:
        role_id = None

    if not role_id:
        role_id = ROLE_ID

    logging.info(f"api_key:{api_key}")
    logging.info(f"datasource_id:{datasource_id}")
    logging.info(f"role_id:{role_id}")

    params = {
        "api_key": api_key,
        "datasource_id": datasource_id,
        "question": query,
        "role_id": role_id,
    }
    if args.base_url:
        params["base_url"] = args.base_url

    message = await get_asktable_sql(**params)
    return message


@mcp.tool()
async def query(query: str) -> str:
    """
    根据用户的问题，直接返回数据结果
    不需要指定数据源ID，该函数已在内部指定了数据源ID，直接发起请求即可
    该函数执行用户的查询并返回实际的数据结果或答案，而不是SQL语句。

    :param query: 用户的查询内容
                  示例：
                  - "昨天的订单总金额是多少"
                  - "列出销售额前10的产品"
                  - "每个部门有多少员工"
    :return: 查询的实际结果

    使用场景：
        - 需要直接获取查询答案
        - 搜索数据库数据
        - 需要查看实际数据结果
        - 不需要SQL细节，只要最终答案与结论
    """
    global API_KEY, DATASOURCE_ID, server_ready

    if not server_ready:
        return "Server is still initializing, please wait"

    if not API_KEY or not DATASOURCE_ID:
        try:
            request = get_http_request()
            api_key = request.query_params.get("apikey", API_KEY)
            datasource_id = request.query_params.get("datasource_id", DATASOURCE_ID)
        except RuntimeError:
            api_key = API_KEY
            datasource_id = DATASOURCE_ID
    else:
        api_key = API_KEY
        datasource_id = DATASOURCE_ID

    try:
        request = get_http_request()
        role_id = request.query_params.get("role_id", None)
    except RuntimeError:
        role_id = None

    if not role_id:
        role_id = ROLE_ID

    logging.info(f"api_key:{api_key}")
    logging.info(f"datasource_id:{datasource_id}")
    logging.info(f"role_id:{role_id}")

    params = {
        "api_key": api_key,
        "datasource_id": datasource_id,
        "question": query,
        "role_id": role_id,
    }

    message = await get_asktable_data(**params)
    return message


@mcp.tool()
async def list_data() -> str:
    """
    获取当前用户apikey下的可用的所有数据库（数据源）信息

    该函数会自动获取当前用户有权限访问的全部数据源，并返回每个数据源的关键信息，包括数据源ID、推理引擎类型和数据库描述。

    :return: 如果该用户的数据库有表的话，会返回数据源信息列表，每个元素为字典，包含以下字段：
        - datasource_id: 数据源唯一ID
        - 数据库引擎: 数据源的推理引擎类型（如：mysql、excel、postgresql等）
        - 数据库描述: 数据源的详细描述信息

            如果该用户的数据库中没有表，则返回"[目前该用户的数据库中还没有数据]"
    示例返回值:
    example1 - 对应数据库中有表的情况:
        [
            {
                "datasource_id": "ds_6iewvP4cpSyhO76P2Tv8MW",
                "数据库引擎": "mysql",
                "数据库描述": "包含大学的课程、教授、学生、部门、奖项、宿舍管理、考试成绩等信息的综合数据库。"
            },
            {
                "datasource_id": "ds_43haVWseJhEizg2GHbErMu",
                "数据库引擎": "excel",
                "数据库描述": "包含各省份的经济指标与电信行业相关数据，帮助分析区域经济与电信发展的关系。"
            },
            {
                "datasource_id": "ds_2Ds3Ude2MkYa3FAWvyVSRG",
                "数据库引擎": "mysql",
                "数据库描述": "该数据库用于管理基金销售相关信息，包括订单、产品和销售员等数据表。"
            }
        ]

    example2 - 对应数据库中没有表的情况:
        “该用户还没有创建任何数据库”

    使用场景：
        - 用户需要查看自己有哪些数据库，获取这些数据库的datasource_id、该数据库所用的数据库引擎和描述信息，以供后续需要。
    """
    global API_KEY, DATASOURCE_ID, server_ready

    if not server_ready:
        return "Server is still initializing, please wait"

    if not API_KEY or not DATASOURCE_ID:
        try:
            request = get_http_request()
            api_key = request.query_params.get("apikey", API_KEY)
            datasource_id = request.query_params.get("datasource_id", DATASOURCE_ID)
        except RuntimeError:
            api_key = API_KEY
            datasource_id = DATASOURCE_ID
    else:
        api_key = API_KEY
        datasource_id = DATASOURCE_ID

    base_url = None
    if args.base_url:
        base_url = args.base_url

    result = await get_datasources_info(api_key=api_key, base_url=base_url)
    logging.info(result)
    return result["data"]


if __name__ == "__main__":
    args = parse_args()
    mcp.run(transport="sse", host="0.0.0.0", port=8095, path="/sse/")
