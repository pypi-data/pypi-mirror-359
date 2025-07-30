import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from typing import Optional
from fastapi_mcp import FastApiMCP
from ..data.models import FlutterWidgetComponent, ComponentProperty, ComponentExample
from ..utils.loader import ComponentRepository
from starlette.responses import JSONResponse

# 配置日志
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('flutter_widget_mcp_server.log', maxBytes=10 * 1024 * 1024, backupCount=5)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

# 获取根日志记录器并添加处理程序
root_logger = logging.getLogger()
root_logger.addHandler(log_handler)
root_logger.setLevel(logging.INFO)

# 创建一个专门的日志记录器用于此应用
logger = logging.getLogger("flutter_widget_mcp_server")

app = FastAPI(
    title="flutter-widget-mcp-server",
    version="1.0.0",
    description="Flutter Widget组件库AI增强服务，标准MCP接口",
)

# 配置静态文件服务
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/assets", StaticFiles(directory=static_dir), name="static")

logger.info("Flutter Widget MCP Server starting...")
logger.info(f"Static files directory: {static_dir}")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Returned response: {response.status_code}")
    return response


# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 用相对路径转绝对路径指向 data/components.json
json_path = os.path.abspath(os.path.join(current_dir, "..", "data", "components.json"))
logger.info(f"Loading components from {json_path}")

# 启动时加载本地JSON缓存
repo = ComponentRepository(json_path=json_path)


def component_to_api_model(comp: FlutterWidgetComponent):
    """
    将FlutterWidgetComponent转换为API响应模型（字典）
    """
    return {
        "name": comp.name,
        "category": comp.category,
        "description": comp.description,
        "import_code": comp.import_code,
        "properties": [
            {
                "name": p.name,
                "type": p.type,
                "description": p.description
            } for p in comp.properties
        ],
        "examples": [
            {
                "title": e.title,
                "code": e.code,
                "description": e.description
            } for e in comp.examples
        ],
        "events": [evt.name for evt in comp.events],
        "best_practices": [f"{faq.question}: {faq.answer}" for faq in comp.faq],
        "methods": [
            {
                "name": m.name,
                "description": m.description,
                "parameters": m.parameters,
                "return_type": m.return_type
            } for m in comp.methods
        ],
        "scenarios": comp.scenarios,
        "maintainer": comp.maintainer,
        "stability": comp.stability,
        "preview": comp.preview,
        "basic_usage": comp.basic_usage,
        "related_components": [
            {
                "name": r.name,
                "path": r.path
            } for r in comp.related_components
        ],
        "source_path": comp.source_path,
        "demo_path": comp.demo_path
    }


@app.get("/components")
async def list_components(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        category: Optional[str] = None
):
    """
    列出所有可用的Flutter组件，支持分页和类别筛选
    """
    all_comps = repo.list_by_category(category) if category else repo.all()
    total = len(all_comps)
    start = (page - 1) * page_size
    end = start + page_size
    comps_slice = all_comps[start:end]
    return {
        "total": total,
        "components": [component_to_api_model(comp) for comp in comps_slice]
    }


@app.get("/components/list")
async def list_component_names():
    """
    列出所有可用的组件名称
    """
    return {"components": [comp.name for comp in repo.all()]}


@app.get("/components/{component_name}")
async def get_component_details(component_name: str):
    """
    获取特定Flutter组件的详细信息
    """
    logger.info(f"Received request for component: {component_name}")
    logger.info(f"Available components: {[comp.name for comp in repo.all()]}")
    comp = repo.get_by_name(component_name)
    if not comp:
        logger.warning(f"Component not found: {component_name}")
        raise HTTPException(status_code=404, detail="Component not found")
    logger.info(f"Returning details for component: {component_name}")
    return component_to_api_model(comp)


@app.get("/components/search")
async def search_components(
        query: str,
        category: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
):
    """
    搜索组件
    """
    comps = repo.search(query, category)
    total = len(comps)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": total,
        "results": [component_to_api_model(comp) for comp in comps[start:end]]
    }


@app.get("/components/{component_name}/examples")
async def get_component_examples(component_name: str, complexity: Optional[str] = None):
    """
    获取组件使用示例
    """
    comp = repo.get_by_name(component_name)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    # 复杂度筛选可后续扩展
    return [
        {
            "title": e.title,
            "code": e.code,
            "description": e.description
        }
        for e in comp.examples
    ]


@app.get("/components/{component_name}/best-practices")
async def get_component_best_practices(component_name: str):
    """
    获取组件最佳实践
    """
    comp = repo.get_by_name(component_name)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    return [f"{faq.question}: {faq.answer}" for faq in comp.faq]


@app.get("/components/{component_name}/relations")
async def get_component_relations(component_name: str):
    """
    获取组件之间的关系
    """
    comp = repo.get_by_name(component_name)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    # 只返回相关组件名
    return [r.name for r in comp.related_components]


@app.get("/components/{component_name}/methods")
async def get_component_methods(component_name: str):
    """
    获取组件的方法信息
    """
    comp = repo.get_by_name(component_name)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    return [
        {
            "name": m.name,
            "description": m.description,
            "parameters": m.parameters,
            "return_type": m.return_type
        } for m in comp.methods
    ]


@app.get("/components/list")
async def list_component_names():
    """
    列出所有可用的组件名称
    """
    return {"components": [comp.name for comp in repo.all()]}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )


@app.get("/")
async def root():
    return {
        "message": "Flutter Widget MCP Server is running.",
        "docs": "/docs",
        "apiDocs": "https://flutter.yldev.space/",
        "components_endpoint": "/components"
    }


# 创建 MCP 服务器
try:
    mcp = FastApiMCP(app, name="Flutter Widget MCP 服务")
except Exception as e:
    logger.error(f"Failed to create MCP server: {str(e)}")
    mcp = None

@app.on_event("startup")
async def startup_event():
    if mcp is not None:
        try:
            await mcp.mount()
            logger.info("MCP server mounted successfully")
        except Exception as e:
            logger.error(f"Failed to mount MCP server: {str(e)}")
    else:
        logger.error("MCP server was not created, cannot mount")

def run():
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run()
