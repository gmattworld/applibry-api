from fastapi import APIRouter

from applibry_api.domain.schemas.common_schema import RouteResponseSchema, RouteResponseSchemaExt


router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
    dependencies=[]
)


# @router.get("/nattypad/articles", response_model=RouteResponseSchemaExt[AppArticleSchema], status_code=status.HTTP_200_OK)
# async def get_articles(search: str = None, page: int = 1, per_page: int = 20):
#     data = await nattypad_articles.get_articles(search, page, per_page)
#     return data


# @router.get("/nattypad/articles/{slug}", response_model=RouteResponseSchema[AppArticleSchema], status_code=status.HTTP_200_OK)
# async def get_articles(slug: str):
#     data = await nattypad_articles.get_article(slug)
#     return data


# @router.get("/nattypad/categories", response_model=RouteResponseSchemaExt[AppCategorySchema], status_code=status.HTTP_200_OK)
# async def get_categories(search: str = None, page: int = 1, per_page: int = 20):
#     data = await nattypad_categories.get_categories(search, page, per_page)
#     return data


# @router.get("/nattypad/categories/{id}", response_model=RouteResponseSchema[AppCategorySchema], status_code=status.HTTP_200_OK)
# async def get_category(id: UUID):
#     data = await nattypad_categories.get_category(id)
#     return data



# @router.get("/nattypad/quotes", response_model=RouteResponseSchemaExt[AppQuoteSchema], status_code=status.HTTP_200_OK)
# async def get_quotes(search: str = None, page: int = 1, per_page: int = 20):
#     data = await nattypad_quotes.get_quotes(search, page, per_page)
#     return data


# @router.get("/nattypad/quotes/{id}", response_model=RouteResponseSchema[AppQuoteSchema], status_code=status.HTTP_200_OK)
# async def get_quote(id: UUID):
#     data = await nattypad_quotes.get_quote(id)
#     return data
