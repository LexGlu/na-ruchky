from typing import List, Optional
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.pagination import paginate
from ninja.files import UploadedFile
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ruchky_backend.pets.schemas import (
    PetSchema,
    PetListingSchema,
    PetImageSchema,
    PetImageUpdateSchema,
)
from ruchky_backend.pets.models import (
    Pet,
    PetListing,
    PetImage,
    Sex,
    Species,
    ListingStatus,
)

pets_router = Router(tags=["pets"])
pet_listings_router = Router(tags=["pet_listings"])
pet_images_router = Router(tags=["pet_images"])


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
    sort: Optional[str] = None,
):
    """
    List pet listings with filtering and sorting options.

    Returns paginated list of pet listings based on provided filters.
    """
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
        filters["pet__name__icontains"] = name.strip()
    if breed:
        filters["pet__breed__icontains"] = breed.strip()
    if location:
        filters["pet__location__icontains"] = location.strip()
    if is_vaccinated is not None:
        filters["pet__is_vaccinated"] = is_vaccinated
    if owner_id is not None:
        filters["pet__owner_id"] = owner_id
    if organization_id is not None:
        filters["pet__owner__organization_id"] = organization_id
    if organization_name:
        filters["pet__owner__organization__name__icontains"] = organization_name.strip()
    if is_charity is not None:
        filters["pet__owner__organization__is_charity"] = is_charity

    # Age filtering
    now_date = timezone.now().date()
    if min_age is not None:
        filters["pet__birth_date__lte"] = now_date - relativedelta(years=min_age)
    if max_age is not None:
        filters["pet__birth_date__gte"] = now_date - relativedelta(years=max_age)

    # Base queryset with select_related for better performance
    pet_listings = PetListing.objects.select_related(
        "pet", "pet__owner", "pet__owner__organization"
    ).filter(**filters)

    allowed_sort_fields = {
        "price",
        "created_at",
        "updated_at",
        "pet__name",
        "pet__species",
        "pet__breed",
        "pet__birth_date",
        "pet__owner__organization__name",
    }

    if sort:
        sort_direction = ""
        sort_field = sort

        if sort.startswith("-"):
            sort_direction = "-"
            sort_field = sort[1:]

        if sort_field not in allowed_sort_fields:
            pass
        else:
            pet_listings = pet_listings.order_by(f"{sort_direction}{sort_field}")

    return pet_listings


@pet_listings_router.get("/{id}", response=PetListingSchema)
def get_pet_listing(request, id: UUID):
    return get_object_or_404(PetListing, id=id)


# Pet Images API endpoints
@pet_images_router.get("/{pet_id}", response=List[PetImageSchema])
def list_pet_images(request, pet_id: UUID):
    """
    Get all images for a specific pet.
    """
    pet = get_object_or_404(Pet, id=pet_id)
    return pet.images.all()


@pet_images_router.post("/{pet_id}", response=PetImageSchema)
def create_pet_image(
    request,
    pet_id: UUID,
    file: UploadedFile = File(...),
    order: int = 0,
    caption: Optional[str] = None,
):
    """
    Upload a new image for a specific pet.
    """
    pet = get_object_or_404(Pet, id=pet_id)

    # Create and save the new pet image
    pet_image = PetImage(pet=pet, image=file, order=order, caption=caption)
    pet_image.save()

    return pet_image


@pet_images_router.patch("/{image_id}", response=PetImageSchema)
def update_pet_image(request, image_id: UUID, data: PetImageUpdateSchema):
    """
    Update an existing pet image (order or caption).
    """
    pet_image = get_object_or_404(PetImage, id=image_id)

    if data.order is not None:
        pet_image.order = data.order

    if data.caption is not None:
        pet_image.caption = data.caption

    pet_image.save()

    return pet_image


@pet_images_router.delete("/{image_id}")
def delete_pet_image(request, image_id: UUID):
    """
    Delete a pet image.
    """
    pet_image = get_object_or_404(PetImage, id=image_id)
    pet_image.delete()

    return {"success": True}


@pet_images_router.post("/{pet_id}/set-profile", response=PetSchema)
def set_profile_picture(request, pet_id: UUID, image_id: UUID):
    """
    Set an existing image as the profile picture for the pet.
    """
    pet = get_object_or_404(Pet, id=pet_id)
    pet_image = get_object_or_404(PetImage, id=image_id, pet_id=pet_id)

    # Set the selected image as the profile picture
    pet.profile_picture = pet_image
    pet.save()

    return pet
