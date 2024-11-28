import graphene
from graphene_django import DjangoObjectType
from .models import Header
from users.schema import UserType
from django.db.models import Q

class HeaderType(DjangoObjectType):
    class Meta:
        model = Header

class Query(graphene.ObjectType):
    headers = graphene.List(HeaderType, search=graphene.String())
    headerById = graphene.Field(HeaderType, id_header=graphene.Int())
    
    def resolve_headerById(self, info, id_header, **kwargs):
        user = info.context.user 
        
        if user.is_anonymous:
            raise Exception ('Not logged in')
        
        print (user)
        
        filter = (
            Q(posted_by=user) & Q(id = id_header)
        )
        
        return Header.objects.filter(filter).first();

    def resolve_headers(self, info, search=None, **kwargs):
        user = info.context.user
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        print (user)
        
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            
            return Header.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(name__icontains=search)
            )
            
            return Header.objects.filter(filter)

class CreateHeader(graphene.Mutation):
    id_header    = graphene.Int()
    name         = graphene.String()
    description  = graphene.String()
    image_url    = graphene.String()
    email        = graphene.String()
    phone_number = graphene.String()
    location     = graphene.String()
    github       = graphene.String()
    posted_by    = graphene.Field(UserType)

    #2
    class Arguments:
        id_header    = graphene.Int()
        name         = graphene.String()
        description  = graphene.String()
        image_url    = graphene.String()
        email        = graphene.String()
        phone_number = graphene.String()
        location     = graphene.String()
        github       = graphene.String()

    #3
    def mutate(self, info, id_header, name, description, image_url, email, phone_number, location, github):
        user = info.context.user or None
        
        if user.is_anonymous:
            raise Exception('Not logged in !');
        
        print(user)

        currentHeader = Header.objects.first()
        
        if currentHeader:
            currentHeader.name = name
            currentHeader.description = description
            currentHeader.image_url = image_url
            currentHeader.email = email
            currentHeader.phone_number = phone_number
            currentHeader.location = location
            currentHeader.github = github
            currentHeader.posted_by = user
            
            currentHeader.save()
            
            return CreateHeader(
                id_header=currentHeader.id,
                name=currentHeader.name,
                description=currentHeader.description,
                image_url=currentHeader.image_url,
                email=currentHeader.email,
                phone_number=currentHeader.phone_number,
                location=currentHeader.location,
                github=currentHeader.github,
                posted_by=currentHeader.posted_by
            )
        
        header = Header(
            name=name,
            description=description,
            image_url=image_url,
            email=email,
            phone_number=phone_number,
            location=location,
            github=github,
            posted_by=user
        )






























        
        
        header.save()

        return CreateHeader(
            id_header=header.id,
            name=header.name,
            description=header.description,
            image_url=header.image_url,
            email=header.email,
            phone_number=header.phone_number,
            location=header.location,
            github=header.github,
            posted_by=header.posted_by
        )


class DeleteHeader(graphene.Mutation): 
    id_header = graphene.Int() 
    
    #2 
    class Arguments: 
        id_header = graphene.Int()
    
    #3
    def mutate(self, info, id_header): 
        user = info.context.user or None 
        
        if user.is_anonymous: 
            raise Exception('Not logged in!')
        
        print (user) 
        
        currentHeader = Header.objects.filter(id=id_header).first()
        print(currentHeader)
        
        if not currentHeader:
            raise Exception('Invalid Header id!')
        
        currentHeader.delete()
        
        return DeleteHeader(
            id_header = id_header,
        )

#4
class Mutation(graphene.ObjectType):
    create_header = CreateHeader.Field()
    delete_header = DeleteHeader.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)