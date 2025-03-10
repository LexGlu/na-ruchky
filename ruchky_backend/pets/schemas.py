from typing import List, Optional

from ninja import ModelSchema, Schema

from ruchky_backend.pets.models import Pet, PetListing, PetSocialLink, PetImage


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
    social_links: List[PetSocialLinkSchema]
    images: List[PetImageSchema]
    tags: List[str] = []
    profile_picture_id: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Meta:
        model = Pet
        fields = "__all__"
        exclude = ["tags", "tagged_items"]

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


class PetListingSchema(ModelSchema):
    pet: PetSchema

    class Meta:
        model = PetListing
        fields = "__all__"
