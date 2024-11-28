

from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType

# Definir el tipo de objeto GraphQL para el modelo de usuario
class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()  # Usamos el modelo de usuario configurado en Django

# Mutación para crear un usuario
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        # Crear un nuevo usuario
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)

# Consulta para obtener el usuario autenticado
class Query(graphene.ObjectType):
    users = graphene.List(UserType)  # Lista de usuarios
    current_user = graphene.Field(UserType)  # Usuario autenticado

    def resolve_users(self, info):
        # Devuelve todos los usuarios
        return get_user_model().objects.all()

    def resolve_current_user(self, info):
        # Obtener el usuario actual desde el contexto (requiere autenticación)
        user = info.context.user
        if user.is_authenticated:
            return user
        return None  # Si el usuario no está autenticado, retorna None

# Mutaciones disponibles en el esquema
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()  # Mutación para crear un nuevo usuario

# Esquema completo de GraphQL
schema = graphene.Schema(query=Query, mutation=Mutation)
