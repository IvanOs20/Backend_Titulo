import graphene
from graphene_django import DjangoObjectType
from users.schema import UserType
from .models import Link, Vote, Alumno
from graphql import GraphQLError
from django.db.models import Q

class LinkType(DjangoObjectType):
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote

class AlumnoType(DjangoObjectType):
    class Meta:
        model = Alumno

class Query(graphene.ObjectType):
    links = graphene.List(LinkType, search=graphene.String())
    votes = graphene.List(VoteType)
    all_alumnos = graphene.List(AlumnoType)

    def resolve_links(self, info, search=None, **kwargs):
        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            return Link.objects.filter(filter)
        return Link.objects.all()

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()

    def resolve_all_alumnos(self, info, **kwargs):
        return Alumno.objects.all()

class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None
        link = Link(
            url=url,
            description=description,
            posted_by=user
        )
        link.save()
        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=user
        )

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('You must be logged to vote!')
        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')
        Vote.objects.create(
            user=user,
            link=link,
        )
        return CreateVote(user=user, link=link)

class CreateCarrera(graphene.Mutation):  # Cambia el nombre de la mutación aquí
    id = graphene.Int()
    carrera = graphene.String()
    matricula = graphene.String()

    class Arguments:
        carrera = graphene.String()
        matricula = graphene.String()

    def mutate(self, info, carrera, matricula):
        alumno = Alumno(carrera=carrera, matricula=matricula)
        alumno.save()
        return CreateCarrera(  # Cambia el nombre de la mutación aquí también
            id=alumno.id,
            carrera=alumno.carrera,
            matricula=alumno.matricula
        )

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
    create_carrera = CreateCarrera.Field()  # Cambia el nombre de la mutación aquí también



