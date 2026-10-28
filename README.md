# semiotique
- Do multi-turn conversation content curation
    - Open question on how to do nested multi-turn conversations
      - For now, I can just disallow, aka allow a single S.open() at a time
- Move the context curation strategy into its own method of runtime class
- Move calling the LLM client into its own method of runtime class
  - And implement the split between using a generic LLM and using a decision model
- Then build a small demo
  - Personal note taker demo