import graphene
from graphene_django import DjangoObjectType
from .models import WorkExperience
from users.schema import UserType
from django.db.models import Q

# Definir el tipo GraphQL para WorkExperience
class WorkExperienceType(DjangoObjectType):
    class Meta:
        model = WorkExperience

# Consultas GraphQL
class Query(graphene.ObjectType):
    experiences = graphene.List(WorkExperienceType, search=graphene.String())
    experienceById = graphene.Field(WorkExperienceType, id_work_experience=graphene.Int())
    
    def resolve_experienceById(self, info, id_work_experience, **kwargs):
        user = info.context.user 
        
        if user.is_anonymous:
            raise Exception ('Not logged in')
        
        # Filtra la experiencia por el usuario y el ID
        filter = (
            Q(posted_by=user) & Q(id=id_work_experience)
        )
        
        return WorkExperience.objects.filter(filter).first()

    def resolve_experiences(self, info, search=None, **kwargs):
        user = info.context.user
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        # Si la búsqueda es "*", obtiene todas las experiencias
        if search == "*":
            filter = Q(posted_by=user)
            return WorkExperience.objects.filter(filter)[:10]
        else:
            filter = Q(posted_by=user) & Q(role__icontains=search)
            return WorkExperience.objects.filter(filter)

# Mutaciones GraphQL

# Crear o Editar una experiencia laboral
class CreateWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()
    role               = graphene.String()
    company            = graphene.String()
    accomplishments    = graphene.List(graphene.String)
    start_date         = graphene.Date()
    end_date           = graphene.Date()
    location           = graphene.String()
    posted_by          = graphene.Field(UserType)

    class Arguments:
        id_work_experience = graphene.Int()  # Para editar una experiencia existente
        role               = graphene.String()
        company            = graphene.String()
        accomplishments    = graphene.List(graphene.String)
        start_date         = graphene.Date()
        end_date           = graphene.Date()
        location           = graphene.String()

    def mutate(self, info, id_work_experience, role, company, accomplishments, start_date, end_date, location):
        user = info.context.user or None
        
        if user.is_anonymous:
            raise Exception('Not logged in !')
        
        # Verifica si existe la experiencia laboral
        currentWorkExperience = WorkExperience.objects.filter(id=id_work_experience, posted_by=user).first()

        if currentWorkExperience:
            # Si la experiencia laboral existe, actualizamos los valores
            currentWorkExperience.role = role
            currentWorkExperience.company = company
            currentWorkExperience.accomplishments = accomplishments
            currentWorkExperience.start_date = start_date
            currentWorkExperience.end_date = end_date
            currentWorkExperience.location = location
            currentWorkExperience.save()  # Guardamos los cambios
        else:
            # Si no existe, creamos una nueva experiencia laboral
            currentWorkExperience = WorkExperience(
                role=role,
                company=company,
                accomplishments=accomplishments,
                start_date=start_date,
                end_date=end_date,
                location=location,
                posted_by=user
            )
            currentWorkExperience.save()  # Guardamos la nueva experiencia

        return CreateWorkExperience(
            id_work_experience=currentWorkExperience.id,
            role=currentWorkExperience.role,
            company=currentWorkExperience.company,
            accomplishments=currentWorkExperience.accomplishments,
            start_date=currentWorkExperience.start_date,
            end_date=currentWorkExperience.end_date,
            location=currentWorkExperience.location,
            posted_by=currentWorkExperience.posted_by
        )

# Eliminar una experiencia laboral
class DeleteWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()

    class Arguments:
        id_work_experience = graphene.Int()

    def mutate(self, info, id_work_experience):
        user = info.context.user or None
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        # Buscar la experiencia laboral por ID y usuario
        currentWorkExperience = WorkExperience.objects.filter(id=id_work_experience, posted_by=user).first()

        if not currentWorkExperience:
            raise Exception('Invalid Work Experience id!')
        
        # Eliminar la experiencia laboral
        currentWorkExperience.delete()
        
        return DeleteWorkExperience(
            id_work_experience=id_work_experience,
        )

# Mutación de creación y eliminación
class Mutation(graphene.ObjectType):
    create_work_experience = CreateWorkExperience.Field()
    delete_work_experience = DeleteWorkExperience.Field()

# Esquema GraphQL que incluye las consultas y mutaciones
schema = graphene.Schema(query=Query, mutation=Mutation)
