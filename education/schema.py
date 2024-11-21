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


class CreateEducation(graphene.Mutation):
    id = graphene.Int()
    degree = graphene.String()
    university = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    posted_by = graphene.Field(UserType)

    class Arguments:
        degree = graphene.String()
        university = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()

    def mutate(self, info, degree, university, start_date, end_date):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        # Create and save the education record
        education = Education(
            degree=degree,
            university=university,
            start_date=start_date,
            end_date=end_date,
            posted_by=user
        )
        education.save()

        return CreateEducation(
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
    create_education = CreateEducation.Field()
    delete_education = DeleteEducation.Field()


# Complete GraphQL schema
schema = graphene.Schema(query=Query, mutation=Mutation)
