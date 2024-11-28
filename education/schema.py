import graphene
from graphene_django import DjangoObjectType
from .models import Education
from users.schema import UserType
from django.db.models import Q


class EducationType(DjangoObjectType):
    class Meta:
        model = Education


class Query(graphene.ObjectType):
    degrees = graphene.List(EducationType, search=graphene.String())
    degree_by_id = graphene.Field(EducationType, id=graphene.Int())

    def resolve_degrees(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        if search:
            filter_condition = Q(posted_by=user) & Q(degree__icontains=search)
        else:
            filter_condition = Q(posted_by=user)
        
        return Education.objects.filter(filter_condition)[:10]

    def resolve_degree_by_id(self, info, id, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        filter_condition = Q(posted_by=user) & Q(id=id)
        return Education.objects.filter(filter_condition).first()


class CreateOrUpdateEducation(graphene.Mutation):
    id = graphene.Int()
    degree = graphene.String()
    university = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    posted_by = graphene.Field(UserType)

    class Arguments:
        id = graphene.Int(required=False)  # ID opcional para actualización
        degree = graphene.String()
        university = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()

    def mutate(self, info, degree, university, start_date, end_date, id=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        # Si se proporciona un ID, intentamos actualizar
        if id:
            education = Education.objects.filter(id=id, posted_by=user).first()
            if not education:
                raise Exception("Invalid Education ID or not authorized to edit this entry.")
            
            # Actualizar los campos
            education.degree = degree
            education.university = university
            education.start_date = start_date
            education.end_date = end_date
            education.save()
        else:
            # Crear un nuevo registro
            education = Education(
                degree=degree,
                university=university,
                start_date=start_date,
                end_date=end_date,
                posted_by=user
            )
            education.save()

        return CreateOrUpdateEducation(
            id=education.id,
            degree=education.degree,
            university=education.university,
            start_date=education.start_date,
            end_date=education.end_date,
            posted_by=education.posted_by
        )


class DeleteEducation(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        # Validate that the education exists and belongs to the user
        current_education = Education.objects.filter(id=id, posted_by=user).first()
        if not current_education:
            raise Exception("Invalid Education ID or not authorized to delete this entry.")

        current_education.delete()
        return DeleteEducation(id=id)


class Mutation(graphene.ObjectType):
    create_or_update_education = CreateOrUpdateEducation.Field()
    delete_education = DeleteEducation.Field()


# Complete GraphQL schema
schema = graphene.Schema(query=Query, mutation=Mutation)
