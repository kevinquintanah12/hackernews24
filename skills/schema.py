# schema.py

import graphene
from graphene_django import DjangoObjectType
from .models import Skill
from users.schema import UserType

class SkillType(DjangoObjectType):
    class Meta:
        model = Skill

class Query(graphene.ObjectType):
    skills = graphene.List(SkillType)
    skill_by_id = graphene.Field(SkillType, id_skill=graphene.Int())

    def resolve_skills(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        return Skill.objects.filter(user=user)

    def resolve_skill_by_id(self, info, id_skill, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        return Skill.objects.filter(user=user, id=id_skill).first()

class CreateSkill(graphene.Mutation):
    id_skill = graphene.Int()
    name = graphene.String()
    level = graphene.String()
    description = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        level = graphene.String()
        description = graphene.String()

    def mutate(self, info, name, level, description):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        skill = Skill(
            name=name,
            level=level,
            description=description,
            user=user
        )
        skill.save()

        return CreateSkill(
            id_skill=skill.id,
            name=skill.name,
            level=skill.level,
            description=skill.description,
            user=skill.user
        )

class UpdateSkill(graphene.Mutation):
    id_skill = graphene.Int()
    name = graphene.String()
    level = graphene.String()
    description = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        id_skill = graphene.Int()
        name = graphene.String()
        level = graphene.String()
        description = graphene.String()

    def mutate(self, info, id_skill, name, level, description):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        skill = Skill.objects.filter(id=id_skill, user=user).first()
        if not skill:
            raise Exception("Skill not found or not authorized to edit.")
        
        skill.name = name
        skill.level = level
        skill.description = description
        skill.save()

        return UpdateSkill(
            id_skill=skill.id,
            name=skill.name,
            level=skill.level,
            description=skill.description,
            user=skill.user
        )

class DeleteSkill(graphene.Mutation):
    id_skill = graphene.Int()

    class Arguments:
        id_skill = graphene.Int()

    def mutate(self, info, id_skill):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        
        skill = Skill.objects.filter(id=id_skill, user=user).first()
        if not skill:
            raise Exception("Skill not found or not authorized to delete.")
        
        skill.delete()
        return DeleteSkill(id_skill=id_skill)

class Mutation(graphene.ObjectType):
    create_skill = CreateSkill.Field()
    update_skill = UpdateSkill.Field()
    delete_skill = DeleteSkill.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
