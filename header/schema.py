import graphene
from graphene_django import DjangoObjectType
from .models import Header
from users.schema import UserType

# Definimos el tipo HeaderType para la consulta
class HeaderType(DjangoObjectType):
    class Meta:
        model = Header

# Creamos la clase Query que Graphene requiere
class Query(graphene.ObjectType):
    header = graphene.Field(HeaderType)  # Definimos el campo `header` en la consulta

    def resolve_header(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        return Header.objects.filter(user=user).first()

# Definimos la mutación CreateHeader
class CreateHeader(graphene.Mutation):
    id_header = graphene.Int()
    name = graphene.String()
    phone = graphene.String()
    email = graphene.String()
    location = graphene.String()
    photo = graphene.String()  # URL de la foto (puedes cambiarlo para que devuelva la URL del archivo)
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        location = graphene.String()
        photo = graphene.String()  # URL de la foto

    def mutate(self, info, name, phone, email, location, photo):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        # Validar que el usuario no tenga ya un encabezado
        if Header.objects.filter(user=user).exists():
            raise Exception("User already has a header.")

        # Crear el encabezado
        header = Header(
            name=name,
            phone=phone,
            email=email,
            location=location,
            photo=photo,
            user=user
        )
        header.save()

        return CreateHeader(
            id_header=header.id,
            name=header.name,
            phone=header.phone,
            email=header.email,
            location=header.location,
            photo=header.photo.url if header.photo else None,
            user=header.user
        )

# Definimos la mutación UpdateHeader
class UpdateHeader(graphene.Mutation):
    id_header = graphene.Int()
    name = graphene.String()
    phone = graphene.String()
    email = graphene.String()
    location = graphene.String()
    photo = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        id_header = graphene.Int()
        name = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        location = graphene.String()
        photo = graphene.String()

    def mutate(self, info, id_header, name, phone, email, location, photo):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        # Buscar el encabezado y asegurarse de que pertenezca al usuario
        header = Header.objects.filter(id=id_header, user=user).first()
        if not header:
            raise Exception("Header not found or not authorized to edit.")
        
        # Actualizar encabezado
        header.name = name
        header.phone = phone
        header.email = email
        header.location = location
        header.photo = photo if photo else header.photo
        header.save()

        return UpdateHeader(
            id_header=header.id,
            name=header.name,
            phone=header.phone,
            email=header.email,
            location=header.location,
            photo=header.photo.url if header.photo else None,
            user=header.user
        )

# Clase Mutation para las operaciones de mutación
class Mutation(graphene.ObjectType):
    create_header = CreateHeader.Field()
    update_header = UpdateHeader.Field()

# Definir el esquema
schema = graphene.Schema(query=Query, mutation=Mutation)
