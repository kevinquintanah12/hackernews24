import graphene
from graphene_django import DjangoObjectType
from .models import Language
from users.schema import UserType
from django.db.models import Q

# Definir el tipo de lenguaje
class LanguageType(DjangoObjectType):
    class Meta:
        model = Language

# Consultas
class Query(graphene.ObjectType):
    languages = graphene.List(LanguageType, search=graphene.String())
    language_by_id = graphene.Field(LanguageType, id_language=graphene.Int())

    def resolve_languages(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        if search:
            filter_condition = Q(posted_by=user) & Q(name__icontains=search)
        else:
            filter_condition = Q(posted_by=user)
        
        return Language.objects.filter(filter_condition)[:10]

    def resolve_language_by_id(self, info, id_language, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        return Language.objects.filter(Q(posted_by=user) & Q(id=id_language)).first()

# Mutación para crear o actualizar un lenguaje
class CreateOrUpdateLanguage(graphene.Mutation):
    id_language = graphene.Int()
    name = graphene.String()
    proficiency = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    posted_by = graphene.Field(UserType)

    class Arguments:
        id_language = graphene.Int(required=False)  # Opcional para distinguir entre creación y actualización
        name = graphene.String()
        proficiency = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()

    def mutate(self, info, name, proficiency, start_date, end_date, id_language=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        if id_language:
            # Actualizar un idioma existente
            language = Language.objects.filter(id=id_language, posted_by=user).first()
            if not language:
                raise Exception("Invalid Language ID or not authorized to edit this entry.")
            
            # Actualizar los campos
            language.name = name
            language.proficiency = proficiency
            language.start_date = start_date
            language.end_date = end_date
            language.save()
        else:
            # Crear un nuevo idioma
            language = Language(
                name=name,
                proficiency=proficiency,
                start_date=start_date,
                end_date=end_date,
                posted_by=user
            )
            language.save()

        return CreateOrUpdateLanguage(
            id_language=language.id,
            name=language.name,
            proficiency=language.proficiency,
            start_date=language.start_date,
            end_date=language.end_date,
            posted_by=language.posted_by
        )

# Mutación para eliminar un lenguaje
class DeleteLanguage(graphene.Mutation):
    id_language = graphene.Int()

    class Arguments:
        id_language = graphene.Int()

    def mutate(self, info, id_language):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        language = Language.objects.filter(id=id_language, posted_by=user).first()
        if not language:
            raise Exception("Invalid Language ID or not authorized to delete this entry.")

        language.delete()
        return DeleteLanguage(id_language=id_language)

# Registrar las mutaciones en el esquema
class Mutation(graphene.ObjectType):
    create_or_update_language = CreateOrUpdateLanguage.Field()
    delete_language = DeleteLanguage.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
