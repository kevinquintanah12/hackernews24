# schema.py

import graphene
from graphene_django import DjangoObjectType
from .models import Language
from users.schema import UserType
from django.db.models import Q

class LanguageType(DjangoObjectType):
    class Meta:
        model = Language

class Query(graphene.ObjectType):
    languages = graphene.List(LanguageType, search=graphene.String())
    language_by_id = graphene.Field(LanguageType, id_language=graphene.Int())

    def resolve_languages(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        print(user)  # Debugging output to see the user

        if search:
            filter_condition = Q(posted_by=user) & Q(name__icontains=search)
        else:
            filter_condition = Q(posted_by=user)
        
        return Language.objects.filter(filter_condition)[:10]

    def resolve_language_by_id(self, info, id_language, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        print(user)  # Debugging output to see the user

        filter_condition = Q(posted_by=user) & Q(id=id_language)
        return Language.objects.filter(filter_condition).first()

class CreateLanguage(graphene.Mutation):
    id_language = graphene.Int()
    name = graphene.String()
    proficiency = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    posted_by = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        proficiency = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()

    def mutate(self, info, name, proficiency, start_date, end_date):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        language = Language(
            name=name,
            proficiency=proficiency,
            start_date=start_date,
            end_date=end_date,
            posted_by=user
        )
        language.save()

        return CreateLanguage(
            id_language=language.id,
            name=language.name,
            proficiency=language.proficiency,
            start_date=language.start_date,
            end_date=language.end_date,
            posted_by=language.posted_by
        )

class DeleteLanguage(graphene.Mutation):
    id_language = graphene.Int()

    class Arguments:
        id_language = graphene.Int()

    def mutate(self, info, id_language):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        current_language = Language.objects.filter(id=id_language, posted_by=user).first()
        if not current_language:
            raise Exception("Invalid Language ID or not authorized to delete this entry.")
        
        current_language.delete()
        return DeleteLanguage(id_language=id_language)

class Mutation(graphene.ObjectType):
    create_language = CreateLanguage.Field()
    delete_language = DeleteLanguage.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
