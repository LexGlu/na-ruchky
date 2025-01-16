from ninja import ModelSchema

from ruchky_backend.pets.models import Pet, PetListing


class PetSchema(ModelSchema):
    class Meta:
        model = Pet
        fields = "__all__"


class PetListingSchema(ModelSchema):
    pet: PetSchema

    class Meta:
        model = PetListing
        fields = "__all__"
