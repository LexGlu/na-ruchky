from ninja import NinjaAPI
from django.contrib.admin.views.decorators import staff_member_required

from ruchky_backend.users.api import router as users_router

api = NinjaAPI(
    title="Na Ruchky API",
    version="0.1.0",
    description="API for Na Ruchky project",
    docs_decorator=staff_member_required,
)

api.add_router("/users/", users_router)
