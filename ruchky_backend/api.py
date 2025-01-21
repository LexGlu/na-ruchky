from ninja import NinjaAPI
from django.contrib.admin.views.decorators import staff_member_required

from ruchky_backend.auth.api import router as auth_router
from ruchky_backend.users.api import router as users_router
from ruchky_backend.pets.api import pets_router, pet_listings_router


api = NinjaAPI(
    title="Na Ruchky API",
    version="0.1.0",
    description="API for Na Ruchky project",
    docs_decorator=staff_member_required,
    csrf=True,
)

api.add_router("/auth/", auth_router)
api.add_router("/users/", users_router)
api.add_router("/pets/", pets_router)
api.add_router("/pet-listings/", pet_listings_router)
