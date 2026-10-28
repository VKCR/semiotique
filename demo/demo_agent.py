from semiotique.agent import Agent
from semiotique.semiotique import S


class Animal(Agent):
    """Describe how the animal reacts, using animal sounds and behavior."""

    def __init__(self, description: str) -> None:
        self.__doc__ = f"{type(self).__doc__}\n\nThe animal is a {description}."

    def __call__(self, prompt: str, **kwargs) -> None:
        print(S(prompt, **kwargs))

    def pet(self):
        return S("The person gently pets the animal")

    def feed(self):
        return S("The person offers the animal food")

    def play(self):
        return S("The person invites you to play")


class Person(Agent):
    """A person is about to interact with an animal."""

    def __init__(self, description: str) -> None:
        self.__doc__ = f"{type(self).__doc__}\n\nThe kind of person : {description}"

    def __call__(self, prompt: str, **kwargs) -> None:
        if 'animal' in kwargs and S(f"The following prompt describes an action of the person on the animal : {prompt}"):
            kwargs['animal'](prompt)
        else:
            print("Action not allowed")

    def approach_pet(self, pet: Animal) -> None:
        print(pet.pet())
        print(pet.feed())
        print(pet.play())


def demo():
    dog = Animal("dog")
    cat = Animal("cat")
    pet_owner = Person("Pet owner")
    unknown_burglar = Person("Unknown burglar dressed all in black")

    for person in (pet_owner, unknown_burglar):
        for animal in (dog, cat):
            person.approach_pet(animal)

    pet_owner("Eat a burger")
    pet_owner("The person throws a ball", animal=dog)

def demo2(): # agentic loop
    dog = Animal("dog")
    while (True):
        action = input("What do you do to the dog?")
        dog(f"The following describes the action of the person on the dog : {action}")
