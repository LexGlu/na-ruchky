from typing import Any, Dict, List, Optional
from uuid import UUID

from ninja import ModelSchema, Schema
from django.utils.encoding import (
    force_str,
)

from ruchky_backend.pets.models import (
    Breed,
    Pet,
    PetListing,
    PetSocialLink,
    PetImage,
    Species,
)


class BreedSchema(ModelSchema):
    image_url: Optional[str] = None

    class Meta:
        model = Breed
        fields = [
            "id",
            "name",
            "species",
            "description",
            "origin",
            "life_span",
            "weight",
            "is_active",
            "image",
        ]

    @staticmethod
    def resolve_image_url(obj: Breed) -> Optional[str]:
        """Return the URL for the breed image if available"""
        if obj.image:
            return obj.image.url
        return None


class PetSocialLinkSchema(ModelSchema):
    class Meta:
        model = PetSocialLink
        fields = ["platform", "url"]


class PetImageSchema(ModelSchema):
    class Meta:
        model = PetImage
        fields = ["id", "image", "order", "caption", "created_at"]


class PetImageCreateSchema(Schema):
    image: str  # base64 encoded image will be handled in the API
    order: int = 0
    caption: Optional[str] = None


class PetImageUpdateSchema(Schema):
    order: Optional[int] = None
    caption: Optional[str] = None


class PetSchema(ModelSchema):
    """
    Schema for the Pet model with both breed reference and basic breed information.
    """

    social_links: List[PetSocialLinkSchema]
    images: List[PetImageSchema]
    tags: List[str] = []
    profile_picture_id: Optional[str] = None
    profile_picture_url: Optional[str] = None

    # Breed-related fields
    breed_id: Optional[UUID] = None
    breed_name: Optional[str] = None
    breed_info: Optional[BreedSchema] = None

    class Meta:
        model = Pet
        fields = [
            "id",
            "name",
            "species",
            "sex",
            "birth_date",
            "location",
            "is_vaccinated",
            "short_description",
            "description",
            "health",
            "owner",
            "created_at",
            "updated_at",
        ]

    @staticmethod
    def resolve_tags(obj: Pet) -> List[str]:
        return obj.tags.names()

    @staticmethod
    def resolve_profile_picture_id(obj: Pet) -> Optional[str]:
        if obj.profile_picture:
            return str(obj.profile_picture.id)
        return None

    @staticmethod
    def resolve_profile_picture_url(obj: Pet) -> Optional[str]:
        if obj.profile_picture:
            return obj.profile_picture.image.url
        return None

    @staticmethod
    def resolve_breed_id(obj: Pet) -> Optional[UUID]:
        if obj.breed:
            return obj.breed.id
        return None

    @staticmethod
    def resolve_breed_name(obj: Pet) -> str:
        """Returns the breed name from either the breed model or custom field"""
        # Use force_str to convert any lazy translation objects to strings
        breed_name = obj.get_breed_name()
        return force_str(breed_name) if breed_name is not None else ""

    @staticmethod
    def resolve_breed_info(obj: Pet) -> Optional[Dict[str, Any]]:
        """Return the basic breed information if a standardized breed is selected"""
        if obj.breed:
            return obj.breed
        return None


class BreedFilterParams(Schema):
    """Parameters for filtering breeds"""

    species: Optional[Species] = None
    search: Optional[str] = None
    origin: Optional[str] = None
    min_life_span: Optional[str] = None
    max_life_span: Optional[str] = None
    weight_range: Optional[str] = None


class PetListingSchema(ModelSchema):
    pet: PetSchema

    class Meta:
        model = PetListing
        fields = "__all__"
