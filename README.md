# Semiotique

**Disclaimer:** This project is still at a _very early stage_, and very rough around the edges. 

I am actively looking for collaborators to improve it and potentially turn it into a commercial venture. If you are interested, feel free to contact me at vivek.claver@gmail.com :) 

## TLDR

Semiotique is a framework which proposes a new paradigm for building agentic applications. It is based upon two core ideas:
- LLM calls should be "first-class citizens" of the language syntax ; programming constructs should allow to seamlessly mesh LLM usage with "plain old code"
- The actual LLM calls should be managed by a runtime responsible for improving their performance and correctness, especially by doing context curation behind the scenes 

The hypothesis is that this paradigm will be an enabler for more sophisticated agentic applications, which will selectively leverage LLMs for tasks at which they are good at while relying on regular, deterministic code for the bulk of the application.

This README will provide an overview of the design philosophy, core concepts, and next steps. 

There are short demo examples in the demo/ directory showcasing the basic syntax, and a more advanced example - a personal note-taking app - in the notetaker/ directory (refer to notetaker/README.md for more information about it)

## Design Philosophy

Today, most frameworks for building agentic applications rely on the concept of the "agentic loop" : an LLM enriched with tools & skills is used as the main driver of the application. A prompt is given as input, and the agentic loop then runs autonomously, leveraging the tools & skills in order to produce a final output. 

I believe that this paradigm is the wrong approach, as LLMs have the following limitations: 
- LLMs can make errors, and its outputs are non-deterministic and non-replicable
- LLMs have no judgment / taste, are prone to sycophancy, and often make questionable assumptions in its reasoning.
- LLMs are just bad at certain tasks, such as iterations.

The agentic loop delegates too much responsibility to the LLM : formulating a plan of actions, deciding which tools / skills to use, generating the result, etc. As a consequence, the agentic loop can be brittle.

In addition, current frameworks embracing the agentic loop are not very elegant to program with : none of the tediousness of configuring and executing calls to an LLM is hidden, and some frameworks even require you to manually define a state machine for more complex workflows (e.g. LangGraph).

The Semiotique framework aims to solve all of the above by **"inverting the agentic loop"** : instead of having an LLM "black-box" to which we provide tools & skills and which we then let execute autonomously on a user input, we should instead develop applications _mostly_ written in regular, deterministic code, with LLM evaluations selectively sprinkled in where they would be actually be useful (for tasks such as understanding natural language, outputting text, closed-ended reasoning, etc.), but always within the guardrails of regular code.

In addition, the tediousness of configuring and using LLMs should be hidden from the programmer, so that he can focus on building application features.

This leads to the two core ideas already stated in the TLDR above, namely that : 
- LLM calls should be "first-class citizens" of the language syntax ; programming constructs should allow to seamlessly mesh LLM usage with "plain old code"
- The actual LLM calls should be managed by a runtime responsible for improving their performance and correctness, especially by doing context curation behind the scenes 

Finally, the framework should also provide a standard library of "agentic building blocks", in order to further facilitate building agentic applications.

## Core concepts

### The S singleton

Semiotique is a "runtime" which allows to evaluate LLM-expressions from anywhere in your code, via the global singleton `S`

For instance, you can use `S` to interact with an LLM : 

```python
print(S("Hello! Who are you?"))
```

You can of course save the result of an LLM-expression to a variable

```python
capital = S("What is the capital of France?") # Prints "Paris"
```

You can use LLM-expressions anywhere, for example in a lambda mapping over a list : 
```python
countries = ["France", "Italy", "Spain"]
capitals = list(map(lambda country: S(f"What is the capital of {country}?"), countries))
print(capitals) # Prints ['Paris', 'Rome', 'Madrid']
```

The default return type is `str`, but you can specify any type, including custom types

```python
print(S("Is Paris the capital of France?", output_type=bool)) # Prints true
persian_cat = S("Fill in the Animal characteristics for a persian cat", output_type=Animal) # Structured output of Animal object
```

This allows you to use LLM-expressions in conditional structures

```python
answer = input("What's the capital of France?")

if S(f"Is {answer} the capital of France?", output_type=bool):
  print("Correct")
else:
  print("Incorrect")
```

And

```python
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

You can pass in tools to LLM-expressions to aid in their task

```python
def get_weather(city: str):
  return "rainy" if "Paris" else "sunny"

print(S("What is the weather like in Paris?", tools=[get_weather])) # Prints "rainy"
```

You can also specify an enclosing context which will get re-used for nested LLM-expressions within the lexical scope

```python
with S.with_context("Your name is Bob, and you are helpful coding assistant"):
    print(S("Hello! What's your name")) # Will print Bob
    print(S("What are you?")) # Will print "helpful coding assistant"
```

Contexts can be nested

```python
with S.with_context("Your name is Bob, and you are helpful coding assistant"):
    with S.with_context("Your first task is to present Semiotique to a new user"):
        print(S("Help me!"))
```

Finally, you can also activate memory for nested LLM-expressions within a lexical scope

```python
with S.with_memory():
    print(S("My name is Bob, and I am 30 years old. What is your name?"))
    print(S("What is my name?")) # Prints Bob
    print(S("What is my age?")) # Prints 30
```

### The Agent base class

Semiotique provides an abstract class called Agent, which is meant to serve as the base class for defining "agentic" classes.

Conceptually, agentic classes are meant to be the building blocks for agentic applications. They are meant satisfy the paradigm of object-oriented programming : each agent class satisfies a "contract", implementing some behavior in a specific scope. An agentic application should then be built "constructively" through a "tangled hierarchy" of agents : top-level agents relying on lower-level agents, themselves relying on even lower-level agents, but sometimes relying on each other as well, etc.

A class which inherits from Agent will automatically participate in the context engineering of any LLM-expression evaluations made from within agentic classes.

Basically, the Runtime keeps track of the "call stack" of the methods of agentic classes. Whenever code execution enters an agentic class' method, the Runtime pushes to the call-stack the docstring of that agentic class and of the called method (provided these docstrings are defined). 

If an agentic class A's method happens to call an agentic class B's method, then the call stack will contain both the docstrings of agent A and agent B, along with their methods involved.

Then, whenever the Runtime evaluates an LLM-expression, it synthesizes the current agent call stack into a system prompt which it provides when calling the LLM, giving the full context for the call.

```text
+---------+                 +---------+                 +-----+
| Agent A | -- method 1 --> | Agent B | -- method 2 --> | S() |
+---------+                 +---------+                 +-----+
                                                           |
                                  System Prompt contains [A, 1, B, 2] docstrings
```

This architecture for defining agentic application enables defining **modular** and **re-usable** agentic components. 

Firstly, the context to be provided for steering the behavior of an LLM can be split into the docstrings of various classes and methods, close to the "regular code" with which they are associated, and can then be "re-assembled" via the context call stack in many different configurations. 

Secondly, since the LLM-expression evaluation inherits the whole call stack, you can define "generic" agents exhibiting flexible behavior which can then be re-used in different contexts (as the calling agent will automatically provide more context in the call stack, "narrowing" the behavior of the "generic" agent which gets called)

Finally, an agent class which inherits from Agent also needs to redefine its `__call__(self, prompt: str, **kwargs)` method, which should define the agent's default behavior when called on an arbitrary prompt.

A basic agent loop can then be easily defined in a few lines :

```python
my_agent = MyAgent()
while (True):
    prompt = input("Input your instructions")
    my_agent(prompt)
```

### The Runtime

The Runtime is the entity actually responsible for evaluating all the LLM-expressions. Its responsibilities are threefold :
- It should allow for the configuration and monitoring of LLM-expression evaluation
- It should implement optimizations to improve the performance of LLM-expression evaluations
- It should implement context curation strategies in order to improve the correctness LLM-expression evaluations

As of now, the implementation of the runtime is very rudimentary : 
- There is no "control panel" or "monitoring dashboard"
- It currently does not do implement any performance optimizations
- It provides basic context curation via the agent call stack, by serializing its contents into a system prompt which it includes in LLM-expression evaluations

The next section will delve deeper into future improvements for the Runtime

## Next steps and ideas

The next steps involve developing features in three main areas : 
- Improving the Runtime
- Adding new syntax / language constructs
- Creating a "standard library" of agentic components

### Improving the Runtime

The Runtime is currently rudimentary, and there are many features to be implemented:
- Configuration & Monitoring
  - Add a configuration panel allowing you to configure the details of LLM-expression evaluations (api key used, model used, reasoning mode, etc.)
  - Add a monitoring dashboard allowing you to trace (and debug) LLM-expression evaluations
  - Add a monitoring dashboard allowing you to trace (and debug) the agent call stack and how it translates into system prompts
  - Allow to dump / restore state
- Performance improvements
  - Batching LLM calls (especially for similar operations, such as for a map operation)
  - Async-ification of LLM calls
  - Parallelization of LLM calls
  - Dynamic switching between models depending on the task complexity
    - Especially dynamic switching between "generic" and "decision" models depending on the output type (switch to decision if it's enum-like)
  - Better handling of LLM calls : retries, output validation, error handling, failure recovery, etc.
  - Caching of prompts
    - Especially agent call stack system prompts
- Context curation improvements
  - Implement different strategies for synthesizing the agent call stack
    - For instance, using an LLM to synthesize the agent call stack into a system prompt, instead of serializing the context call stack

### Adding new syntax / language constructs
As of now, Semiotique is a Python library. However, the ambition is greater : to fully "enmesh" LLM-expression evaluation into regular code.

The current implementation is still very verbose, and feels "forced" at times. It would be nice, for instance to have : 
- Automatic type inference of LLM-expression outputs, instead of having to specify output_type
- Easy constructs for typical tasks, such as routing or classification
- Automated "compilation" of prompts, from more concise instructions, from placeholders, or perhaps from the surrounding code itself.

A future implementation should thus provide more constructs for making it even more intuitive to blend regular code and LLM-expression evaluation.

This might require defining a superset of Python, switch to another programming language, or create a new programming language more adapted to this paradigm altogether.

### Creating a standard library of agentic components

Finally, Semiotique should provide a standard library of common agentic components (TBD) in order to aid in building agentic applications
