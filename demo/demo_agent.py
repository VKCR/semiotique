from semiotique.agent import Agent
from semiotique.semiotique import S


class Animal(Agent[str]):
    """Describe how the animal reacts, using animal sounds and behavior."""

    def __init__(self, description: str) -> None:
        """Initialize the animal with its description."""
        self.__doc__ = f"{type(self).__doc__}\n\nThe animal is a {description}."

    def __call__(self, prompt: str, **kwargs) -> str:
        """Describe the animal's reaction to the person's action."""
        return S(prompt, **kwargs)

    def pet(self):
        """Describe how the animal reacts to being gently petted."""
        return S("The person gently pets the animal")

    def feed(self):
        """Describe how the animal reacts to being offered food."""
        return S("The person offers the animal food")

    def play(self):
        """Describe how the animal reacts to an invitation to play."""
        return S("The person invites you to play")


class Person(Agent[str]):
    """A person is about to interact with an animal."""

    def __init__(self, description: str) -> None:
        """Initialize the person with their description."""
        self.__doc__ = f"{type(self).__doc__}\n\nThe kind of person : {description}"

    def __call__(self, prompt: str, **kwargs) -> str:
        """Pass the person's action to the animal if it describes an interaction."""
        if 'animal' in kwargs and S(f"The following prompt describes an action of the person on the animal : {prompt}"):
            return kwargs['animal'](prompt)
        else:
            return "Action not allowed"

    def approach_pet(self, pet: Animal) -> None:
        """Pet, feed, and play with the animal, printing each reaction."""
        print(pet.pet())
        print(pet.feed())
        print(pet.play())


def demo():
    dog = Animal("dog")
    cat = Animal("cat")
    pet_owner = Person("Pet owner")
    suspicious_stranger = Person("A suspicious stranger")

    for person in (pet_owner, suspicious_stranger):
        for animal in (dog, cat):
            person.approach_pet(animal)

    print(pet_owner("Eat a burger"))
    print(pet_owner("The person throws a ball", animal=dog))

def demo2(): # agentic loop
    dog = Animal("dog")
    while (True):
        action = input("What do you do to the dog?")
        print(dog(f"The following describes the action of the person on the dog : {action}"))
