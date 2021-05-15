from model_bakery.recipe import Recipe
from members.models import User

trainer1 = Recipe(
    User,
    username='first_trainer',
    first_name='First',
    last_name='Trainer',
)
trainer2 = Recipe(
    User,
    username='second_trainer',
    first_name='Second',
    last_name='Trainer',
)
trainer1 = Recipe(
    User,
    username='third_trainer',
    first_name='Third',
    last_name='Trainer',
)
