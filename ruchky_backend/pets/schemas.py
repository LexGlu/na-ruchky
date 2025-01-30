from typing import List

from ninja import ModelSchema

from ruchky_backend.pets.models import Pet, PetListing, PetSocialLink


class PetSocialLinkSchema(ModelSchema):
    class Meta:
        model = PetSocialLink
        fields = ["platform", "url"]


class PetSchema(ModelSchema):
    social_links: List[PetSocialLinkSchema]
    tags: List[str] = []

    class Meta:
        model = Pet
        fields = "__all__"
        exclude = ["tags", "tagged_items"]

    @staticmethod
    def resolve_tags(obj: Pet) -> List[str]:
        return obj.tags.names()


class PetListingSchema(ModelSchema):
    pet: PetSchema

    class Meta:
        model = PetListing
        fields = "__all__"
