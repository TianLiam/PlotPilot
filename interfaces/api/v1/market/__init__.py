from .crawler_routes import router as crawler_router
from .analyzer_routes import router as analyzer_router
from .recommender_routes import router as recommender_router
from .template_routes import router as template_router

__all__ = [
    "crawler_router",
    "analyzer_router",
    "recommender_router",
    "template_router",
]