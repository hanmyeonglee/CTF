from pydantic import BaseModel

from .team import token2team_id


class Query(BaseModel):
    team_token: str
    material0: str
    material1: str
    material2: str
    material3: str
    material4: str
    material5: str
    material6: str
    material7: str

    async def team_id(self) -> int | None:
        return await token2team_id(self.team_token)

    @property
    def sorted_materials(self) -> tuple[str, str, str, str, str, str, str, str]:
        return tuple(sorted([
            self.material0,
            self.material1,
            self.material2,
            self.material3,
            self.material4,
            self.material5,
            self.material6,
            self.material7,
        ]))


class Bounty(BaseModel):
    class Recipe(BaseModel):
        product: str
        materials: tuple[str, str, str, str, str, str, str, str]

        @property
        def sorted_materials(self) -> tuple[str, str, str, str, str, str, str, str]:
            return tuple(sorted(self.materials))

    team_token: str
    target_product: str
    recipes: list[Recipe]

    async def team_id(self) -> int | None:
        return await token2team_id(self.team_token)

    @property
    def length(self) -> int:
        return len(self.recipes)

    async def validate(self, initial_items, check_recipe):
        if await self.team_id() is None:
            raise ValueError('invalid team token')

        # check if recipes is not empty
        if len(self.recipes) == 0:
            raise ValueError('empty recipes')

        # check if all products are unique
        products = set()
        for recipe in self.recipes:
            if recipe.product in products:
                raise ValueError('duplicate product: ' + recipe.product)
            products.add(recipe.product)

        # check if the last recipe produces the target product
        if self.recipes[-1].product != self.target_product:
            raise ValueError('target product mismatch')

        # emulate the crafting process
        discovered_items = set([item['english_name'] for item in initial_items])
        used_items = discovered_items.copy()
        for recipe in self.recipes:
            # check if all materials are in discovered_items
            if not all(material in discovered_items for material in recipe.materials):
                raise ValueError('missing material: ' + '|'.join(set(recipe.materials) - discovered_items))

            # check if the recipe is valid
            if not await check_recipe(recipe):
                raise ValueError('invalid recipe: ' + recipe.product + ' <- ' + '|'.join(recipe.materials))

            discovered_items.add(recipe.product)
            for material in recipe.materials:
                used_items.add(material)

        # check if there is any unused material
        if len(used_items) + 1 != len(discovered_items):
            raise ValueError('unused material: ' + '|'.join(discovered_items - used_items - {self.target_product}))

