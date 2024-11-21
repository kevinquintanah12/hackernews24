import graphene
from graphene_django import DjangoObjectType
from .models import WorkExperience
from users.schema import UserType

# Definir el tipo de objeto GraphQL para WorkExperience
class WorkExperienceType(DjangoObjectType):
    class Meta:
        model = WorkExperience

# Definir la consulta para obtener experiencias laborales
class Query(graphene.ObjectType):
    work_experience = graphene.List(WorkExperienceType)
    work_experience_by_id = graphene.Field(WorkExperienceType, id_work_experience=graphene.Int())

    # Resolver para obtener todas las experiencias laborales de un usuario
    def resolve_work_experience(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        return WorkExperience.objects.filter(user=user)

    # Resolver para obtener una experiencia laboral por su ID
    def resolve_work_experience_by_id(self, info, id_work_experience, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        return WorkExperience.objects.filter(user=user, id=id_work_experience).first()

# Definir la mutación para crear una nueva experiencia laboral
class CreateWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()
    job_title = graphene.String()
    company = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    accomplishments = graphene.List(graphene.String)  # Cambiar a lista de cadenas
    user = graphene.Field(UserType)

    class Arguments:
        job_title = graphene.String()
        company = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()
        description = graphene.String()
        accomplishments = graphene.List(graphene.String)  # Cambiar a lista de cadenas

    def mutate(self, info, job_title, company, start_date, end_date, description, accomplishments=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        # Si no hay logros, asignamos una lista vacía
        accomplishments = accomplishments if accomplishments is not None else []

        # Guardamos la nueva experiencia laboral
        work_experience = WorkExperience(
            job_title=job_title,
            company=company,
            start_date=start_date,
            end_date=end_date,
            description=description,
            accomplishments=accomplishments,  # Guardamos la lista de logros
            user=user
        )
        work_experience.save()

        return CreateWorkExperience(
            id_work_experience=work_experience.id,
            job_title=work_experience.job_title,
            company=work_experience.company,
            start_date=work_experience.start_date,
            end_date=work_experience.end_date,
            description=work_experience.description,
            accomplishments=work_experience.accomplishments,  # Devolvemos los logros
            user=work_experience.user
        )

# Definir la mutación para actualizar una experiencia laboral existente
class UpdateWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()
    job_title = graphene.String()
    company = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    accomplishments = graphene.List(graphene.String)  # Cambiar a lista de cadenas
    user = graphene.Field(UserType)

    class Arguments:
        id_work_experience = graphene.Int()
        job_title = graphene.String()
        company = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()
        description = graphene.String()
        accomplishments = graphene.List(graphene.String)  # Cambiar a lista de cadenas

    def mutate(self, info, id_work_experience, job_title, company, start_date, end_date, description, accomplishments=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        # Buscar la experiencia laboral
        work_experience = WorkExperience.objects.filter(id=id_work_experience, user=user).first()
        if not work_experience:
            raise Exception("Work Experience not found or not authorized to edit.")
        
        # Si no hay logros, asignamos una lista vacía
        accomplishments = accomplishments if accomplishments is not None else []

        # Actualizamos los valores
        work_experience.job_title = job_title
        work_experience.company = company
        work_experience.start_date = start_date
        work_experience.end_date = end_date
        work_experience.description = description
        work_experience.accomplishments = accomplishments  # Actualizamos los logros
        work_experience.save()

        return UpdateWorkExperience(
            id_work_experience=work_experience.id,
            job_title=work_experience.job_title,
            company=work_experience.company,
            start_date=work_experience.start_date,
            end_date=work_experience.end_date,
            description=work_experience.description,
            accomplishments=work_experience.accomplishments,  # Devolvemos los logros actualizados
            user=work_experience.user
        )

# Definir la mutación para eliminar una experiencia laboral
class DeleteWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()

    class Arguments:
        id_work_experience = graphene.Int()

    def mutate(self, info, id_work_experience):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        work_experience = WorkExperience.objects.filter(id=id_work_experience, user=user).first()
        if not work_experience:
            raise Exception("Work Experience not found or not authorized to delete.")
        
        work_experience.delete()
        return DeleteWorkExperience(id_work_experience=id_work_experience)

# Definir las mutaciones en el esquema
class Mutation(graphene.ObjectType):
    create_work_experience = CreateWorkExperience.Field()
    update_work_experience = UpdateWorkExperience.Field()
    delete_work_experience = DeleteWorkExperience.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
