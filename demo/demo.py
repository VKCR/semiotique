from enum import Enum

from semiotique.semiotique import S


class AnimalType(str, Enum):
    MAMMAL = "mammal"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    AMPHIBIAN = "amphibian"
    INVERTEBRATE = "invertebrate"
    OTHER = "other"


def demo():
    animal = input("What kind of animal do you have? ")
    animal_type = S(
        f"Classify the type of animal {animal}?",
        output_type=AnimalType,
    )

    if animal_type == AnimalType.MAMMAL and S(f"Determine if the kind/type of animal \"{animal}\" is a kind/type of dog or cat", output_type=bool):
        print(f"We are able to treat your {animal}")
    else:
        print(f"We are not able to treat your {animal}")


def demo2():
    S.push_context("You are a 16th century poet, so your answers need to be coherent with that style")
    S.push_context("Your name is Archibald")
    print(S("Who are you?"))
    S.pop_context()
    print(S("Who are you?"))
    S.pop_context()
    print(S("Who are you?"))
