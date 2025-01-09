from ninja import Router
from ninja.security import django_auth

from ruchky_backend.users.schemas import UserSchema

router = Router(auth=django_auth)


@router.get("/me", response=UserSchema)
def me(request):
    return request.user
