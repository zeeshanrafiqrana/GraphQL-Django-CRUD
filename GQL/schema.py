from unicodedata import category
import graphene
from graphene_django import DjangoObjectType

from gql_app.models import Category, Ingredient

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")


#---------------------------- FETCHING QUERIES ----------------------------------------
class Query(graphene.ObjectType):
    #fetch the list of all ingredients
    all_ingredients = graphene.List(IngredientType)
    
    specific = graphene.Field(IngredientType, id=graphene.String(required=True))
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

    def resolve_all_ingredients(root, info):
        # We can easily optimize query count in the resolve method
        return Ingredient.objects.select_related("category").all()
    
    def resolve_specific(root, info, id):
        # We can easily optimize query count in the resolve method
        return Ingredient.objects.get(id=id)

    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None
        
#--------------------------------------- CATEGORY TABLE MUTATIONS ----------------------------------------
class CreateCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String(required=True)
    category = graphene.Field(CategoryType)
        
    @classmethod
    def mutate(cls, root, info, name):
        category = Category(name=name)
        category.save()
        return CreateCategoryMutation(category=category)
    
class UpdateCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String(required=True)
    category = graphene.Field(CategoryType)
    
    @classmethod
    def mutate(cls, root, info, id, name):
        user = Category.objects.get(id=id)
        user.name = name
        user.save()
        return UpdateCategoryMutation(category=user)
    
class DeleteCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
    category = graphene.Field(CategoryType)
    
    @classmethod
    def mutate(cls, root, info, id):
        user = Category.objects.get(id=id)
        user.delete()
        return

#----------------------------------------- INGREDIENT TABLE MUTATION -----------------------------------------
class CreateIngredientsMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        notes = graphene.String(required=True)
        category_id = graphene.Int()
    ingredients = graphene.Field(IngredientType)
    
    @classmethod
    def mutate(cls, root, info, name, notes, category_id):
        category = Category.objects.get(id=category_id)
        ingredient = Ingredient(name=name, notes=notes, category=category)
        ingredient.save()
        return CreateIngredientsMutation(ingredients=ingredient)
            
class UpdateIngredientsMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String(required=True)
        notes = graphene.String()
    Ingredient = graphene.Field(IngredientType)
    
    @classmethod
    def mutate(cls, root, info, id, name, notes):
        user = Ingredient.objects.get(id=id)
        user.name = name
        user.notes = notes
        user.save()
        return UpdateIngredientsMutation(Ingredient=user)
    
class DeleteIngredientsMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
    Ingredient = graphene.Field(IngredientType)
    
    @classmethod
    def mutate(cls, root, info, id):
        get_ingredient = Ingredient.objects.get(id=id)
        get_ingredient.delete()
        return
            
            
class Mutation(graphene.ObjectType):
    #CATEGORY MUTATION
    create_category = CreateCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()
    #INGREDIENT MUTATION
    create_ingredients = CreateIngredientsMutation.Field()
    update_ingredients = UpdateIngredientsMutation.Field()
    delete_ingredients = DeleteIngredientsMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)