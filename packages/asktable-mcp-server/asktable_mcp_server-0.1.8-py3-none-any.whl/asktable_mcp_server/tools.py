from asktable import Asktable
import json
import asyncio

async def get_asktable_data(api_key, datasource_id, question, base_url=None):
    # 如果没有传入base_url或传入None，使用默认值
    if base_url is None:
        base_url = "https://api.asktable.com"
    
    asktable_client = Asktable(base_url=base_url, api_key=api_key)
    answer_response = asktable_client.answers.create(datasource_id=datasource_id, question=question)
    if answer_response.answer is None:
        return "没有查询到相关信息"
    return answer_response.answer.text

async def get_asktable_sql(api_key, datasource_id, question, base_url=None):
    # 如果没有传入base_url或传入None，使用默认值
    if base_url is None:
        base_url = "https://api.asktable.com"
    
    asktable_client = Asktable(base_url=base_url, api_key=api_key)
    query_response = asktable_client.sqls.create(datasource_id=datasource_id, question=question)
    if query_response.query.sql is None: 
        return "没有查询到相关信息"
    return query_response.query.sql


async def get_datasources_info(api_key, base_url=None):
    """"
    返回用户数据库meta data
    args:
        api_key: str
        base_url: str
    return:
        {
            "status": "success" or "failure",
            "data": json.dumps(result, ensure_ascii=False, indent=2)
        }
    """
    if base_url is None:
        base_url = "https://api.asktable.com"

    asktable_client = Asktable(base_url=base_url, api_key=api_key)
    meta_data_list = asktable_client.datasources.list()
    # 最前面判断
    if not meta_data_list.items:
        return {
            "status": "failure",
            "data": "该用户还没有创建任何数据库"
        }

    # 提取指定字段
    result = [
        {
            "datasource_id": ds.id,
            "数据库引擎": ds.engine,
            "数据库描述": ds.desc,
        }
        for ds in meta_data_list.items
    ]

    return {
        "status": "success",
        "data": json.dumps(result, ensure_ascii=False, indent=2)
    }


if __name__ == "__main__":
    pass
