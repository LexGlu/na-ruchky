from typing import List, Optional
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ruchky_backend.pets.schemas import PetSchema, PetListingSchema
from ruchky_backend.pets.models import Pet, PetListing, Sex, Species, ListingStatus

pets_router = Router(tags=["pets"])
pet_listings_router = Router(tags=["pet_listings"])


@pets_router.get("", response=List[PetSchema])
@paginate
def list_pets(
    request: HttpRequest,
    species: Species = None,
    sex: Sex = None,
    min_age: int = None,
    max_age: int = None,
    name: str = None,
    breed: str = None,
    location: str = None,
    is_vaccinated: bool = None,
    owner_id: UUID = None,
    organization_id: UUID = None,
):
    pets = Pet.objects

    if species:
        pets = pets.filter(species=species)
    if sex:
        pets = pets.filter(sex=sex)
    if min_age:
        pets = pets.filter(age__gte=min_age)
    if max_age:
        pets = pets.filter(age__lte=max_age)
    if name:
        pets = pets.filter(name__icontains=name)
    if breed:
        pets = pets.filter(breed__icontains=breed)
    if location:
        pets = pets.filter(location__icontains=location)
    if is_vaccinated is not None:
        pets = pets.filter(is_vaccinated=is_vaccinated)
    if owner_id:
        pets = pets.filter(owner_id=owner_id)
    if organization_id:
        pets = pets.filter(owner__organization_id=organization_id)

    return pets.all()


@pets_router.get("/{id}", response=PetSchema)
def get_pet(request, id: UUID):
    return get_object_or_404(Pet, id=id)


@pet_listings_router.get("", response=List[PetListingSchema])
@paginate
def list_pet_listings(
    request,
    status: Optional[ListingStatus] = ListingStatus.ACTIVE,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    species: Optional[Species] = None,
    sex: Optional[Sex] = None,
    name: Optional[str] = None,
    breed: Optional[str] = None,
    location: Optional[str] = None,
    is_vaccinated: Optional[bool] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    owner_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    organization_name: Optional[str] = None,
    is_charity: Optional[bool] = None,
):
    filters = {}

    if status is not None:
        filters["status"] = status
    if min_price is not None:
        filters["price__gte"] = min_price
    if max_price is not None:
        filters["price__lte"] = max_price
    if species is not None:
        filters["pet__species"] = species
    if sex is not None:
        filters["pet__sex"] = sex
    if name:
        filters["pet__name__icontains"] = name
    if breed:
        filters["pet__breed__icontains"] = breed
    if location:
        filters["pet__location__icontains"] = location
    if is_vaccinated is not None:
        filters["pet__is_vaccinated"] = is_vaccinated
    if owner_id is not None:
        filters["pet__owner_id"] = owner_id
    if organization_id is not None:
        filters["pet__owner__organization_id"] = organization_id
    if organization_name:
        filters["pet__owner__organization__name__icontains"] = organization_name
    if is_charity is not None:
        filters["pet__owner__organization__is_charity"] = is_charity

    now_date = timezone.now().date()
    if min_age is not None:
        filters["pet__birth_date__lte"] = now_date - relativedelta(years=min_age)
    if max_age is not None:
        filters["pet__birth_date__gte"] = now_date - relativedelta(years=max_age)

    pet_listings = PetListing.objects.filter(**filters)
    return pet_listings


@pet_listings_router.get("/{id}", response=PetListingSchema)
def get_pet_listing(request, id: UUID):
    return get_object_or_404(PetListing, id=id)
