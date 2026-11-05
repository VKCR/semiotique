from typing import Literal

from semiotique.semiotique import S


def demo():
    animal = input("What kind of animal do you have? ")
    animal_type = S(
        f"Classify the type of animal {animal}?",
        output_type=Literal[
            "mammal", "bird", "fish", "reptile", "amphibian", "invertebrate", "other"
        ],
    )

    if animal_type == "mammal" and S(f"Determine if the kind/type of animal \"{animal}\" is a kind/type of dog or cat", output_type=bool):
        print(f"We are able to treat your {animal}")
    else:
        print(f"We are not able to treat your {animal}")


def demo2():
    with S.with_context("You are a 16th century poet, so your answers need to be coherent with that style"):
        with S.with_context("Your name is Archibald"):
            print(S("Who are you?"))
        print(S("Who are you?"))
    print(S("Who are you?"))


def demo3():
    with S.with_memory():
        print(S("My name is Bob, and I am 30 years old. What is your name?"))
        print(S("What is my name?"))
        print(S("What is my age?"))

def demo4():
    def get_weather(city: str) -> str:
        """Return weather conditions for a city.

        Args:
            city: The name of the city to get weather for.
        """
        return "Raining"

    print(S("What's the weather in Paris?", tools=[get_weather]))

