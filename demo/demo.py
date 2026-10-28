from semiotique.semiotique import S


def demo():
    animal = None
    print(S("Hello, how are you?", output_type=str))
    print(S("2 + 2 = 5?", output_type=bool))
    print(S("2 + 2 = 4?", output_type=bool))
    if S("A panther is a type of animal", output_type=bool):
        print("Indeed it is")
    else:
        print("Nope")
