# schema.py

import graphene
from graphene_django import DjangoObjectType
from .models import Interest
from users.schema import UserType
from django.db.models import Q

class InterestType(DjangoObjectType):
    class Meta:
        model = Interest

class Query(graphene.ObjectType):
    interests = graphene.List(InterestType, search=graphene.String())
    interest_by_id = graphene.Field(InterestType, id_interest=graphene.Int())

    def resolve_interests(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        print(user)  # Debugging output to see the user

        if search:
            filter_condition = Q(posted_by=user) & Q(name__icontains=search)
        else:
            filter_condition = Q(posted_by=user)
        
        return Interest.objects.filter(filter_condition)[:10]

    def resolve_interest_by_id(self, info, id_interest, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        print(user)  # Debugging output to see the user

        filter_condition = Q(posted_by=user) & Q(id=id_interest)
        return Interest.objects.filter(filter_condition).first()

class CreateInterest(graphene.Mutation):
    id_interest = graphene.Int()
    name = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        description = graphene.String()

    def mutate(self, info, name, description):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        interest = Interest(
            name=name,
            description=description,
            posted_by=user
        )
        interest.save()

        return CreateInterest(
            id_interest=interest.id,
            name=interest.name,
            description=interest.description,
            posted_by=interest.posted_by
        )

class DeleteInterest(graphene.Mutation):
    id_interest = graphene.Int()

    class Arguments:
        id_interest = graphene.Int()

    def mutate(self, info, id_interest):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        current_interest = Interest.objects.filter(id=id_interest, posted_by=user).first()
        if not current_interest:
            raise Exception("Invalid Interest ID or not authorized to delete this entry.")
        
        current_interest.delete()
        return DeleteInterest(id_interest=id_interest)

class Mutation(graphene.ObjectType):
    create_interest = CreateInterest.Field()
    delete_interest = DeleteInterest.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
