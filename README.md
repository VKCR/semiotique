# Semiotique

**Disclaimer:** I am actively looking for collaborators to improve this project and potentially turn it into a commercial venture. If you are interested, feel free to contact me at vivek.claver@gmail.com :) 

## TLDR

Semiotique aims to propose a new way to build "LLM-enhanced" applications, based on two core concepts : 
- Allow seamless integration between LLM evaluations and "plain old code"
- Only leverage LLMs for **targeted tasks** for which they are demonstrably good at, through careful context curation

This project is still at a _very early stage_, and is still very rough around the edges. This README will provide an overview of the design philosophy, core concepts, and next steps. 

There are short demo examples in the demo/ directory showcasing the basic syntax, and a more advanced example - a personal note-taking app - in the notetaker/ directory, showcasing how Semiotique can be used to build applications (refer to notetaker/README.md for more information about it)

## Design Philosophy

Most frameworks today for building agentic applications rely on the concept of the "agentic loop" : an LLM enriched with tools & skills is used as the main driver of the application, with the end goal of functioning fully autonomously. I believe that this is a mistake:
- LLMs can make errors, and its outputs are non-deterministic and non-replicable
- LLMs have no judgment / taste, are prone to sycophancy, and often make questionable assumptions in its reasoning.

I believe that the above is due to fundamental limitations with LLMs, and will not be ever fixed through further scaling them.

In addition, current frameworks are usually not very elegant to use : none of the tediousness of configuration and executing calls to LLMs is hidden. Many frameworks even require you to manually define a state machine (such as LangGraph).

The fundamental design idea underlying Semiotique is to **invert the agentic loop** : rather than having an LLM black-box to which we provide (deterministic) tools, and then let "execute" the application based on a system prompt, we should aim to have an application _mostly_ written in deterministic code, with LLM evaluations sprinkled in where they would actually be useful (for tasks such as understanding natural language, outputting text, closed-ended reasoning, etc.)

This leads to the two concepts already stated in the TLDR, namely that Semiotique should :
- Allow seamless integration between LLM evaluations and "plain old code"
- Only leverage LLMs for **targeted tasks** for which they are demonstrably good at, through careful context curation

The end-goal of this project is to be an enabler for the development of new kinds of agentic applications.

## Core concepts

### The S singleton

Semiotique (today) is a "runtime" which allows to evaluate LLM-expressions from anywhere in your code, via the global singleton `S`

For instance, you can use `S` to interact with an LLM : 

```
print(S("Hello! Who are you?"))
```

You can of course save the result of an LLM-expression to a variable

```
capital = S("What is the capital of France?")
```

You can use LLM-expressions anywhere, for example in a lambda mapping over a list : 
```
countries = ["France", "Italy", "Spain"]
capitals = list(map(lambda country: S(f"What is the capital of {country}?"), countries))
print(capitals) # prints ['Paris', 'Rome', 'Madrid']
```

The default return type is `str`, but you can specify any type, including custom types

```
print(S("Is Paris the capital of France?", output_type=bool)) # Prints true
persian_cat = S("Fill in the Animal characteristics for a persian cat", output_type=Animal) # Structured output of Animal object
```

This allows you to use LLM-expressions in conditional structures

```
answer = input("What's the capital of France?")

if S(f"Is {answer} the capital of France?", output_type=bool):
  print("Correct")
else:
  print("Incorrect")
```

And

```
animal = input("What kind of animal do you have? ")
animal_type = S(
    f"Classify the type of animal {animal}?",
    output_type=Literal[
        "mammal", "bird", "fish", "reptile", "amphibian", "invertebrate", "other"
    ],
)

match animal_type:
  case "mammal": ...
```

You can also specify an enclosing context which will get re-used for nested LLM-expressions within the lexical scope

```
with S.with_context("Your name is Bob, and you are helpful coding assistant"):
    print(S("Hello! What's your name")) # Will print Bob
    print(S("What are you?")) # Will print "helpful coding assistant"
```

Contexts can be nested

```
with S.with_context("Your name is Bob, and you are helpful coding assistant"):
    with S.with_context("Your first task is to present Semiotique to a new user"):
        print(S("Help me!"))
```

Finally, you can also activate memory for nested LLM-expressions within a lexical scope

```
with S.with_memory():
    print(S("My name is Bob, and I am 30 years old. What is your name?"))
    print(S("What is my name?")) # Prints Bob
    print(S("What is my age?")) # Prints 30
```

### The Agent base class

Semiotique also proposes an Agent abstract class, which can be used as the base class for defining "Agents", aka objects whose methods are LLM-enhanced.

Conceptually, Agents are meant to be the building blocks for agentic applications. They are meant satisfy the paradigm of object-oriented programming : each agent object satisfies a "contract", implementing some behavior in a specific scope. An agentic application should then be built "constructively" through a collection of agents.

When you create a new class which inherits from Agent, you must define its docstring describing the Agent's behavior, and you must redefine its \_\_call\_\_(self, prompt: str, **kwargs) method, which should define the Agent's behavior when called on an arbitrary prompt.

A basic "agentic" loop can then be easily defined in a few lines : 

```
my_agent = MyAgent()
while (True):
    prompt = input("Input your instructions")
    my_agent(prompt)
```

From inheriting from the Agent base class, any LLM-expression evaluated in the derived agent's methods will be automatically "wrapped" with a context containing the agent's docstring, in order to steer the LLM. Furthermore, when agent A calls agent B's method, the Semiotique runtime does **context chaining**, and any LLM-expression evaluated in one of B's methods called from one of A's method will contain both the docstrings of agent A and agent B.

SHOW DIAGRAM OF CONTEXT CHAINING

Say how it's implemented right now, aka super simple

## Next steps and ideas
As this project is very early stage, there's still a lot of room for improvement. Off the top of my head: 
- 



