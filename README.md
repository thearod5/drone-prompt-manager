# Getting Started
# Creation Prompt
- runner.py: Example / interactive playground for testing prompt building and parsing.
- core/drone_variables.py: The parameters to be included in the prompt.
- prompts/*: Stripped out version of the prompt code used in SAFA.
- prompts/drone_prompt_builder: Creates the prompts and parses the response from the models
- 
# Requirements
1. If a drone requires a minimum of x% of battery to reach a charging station then `cells_in_single_battery` should never result in a drone with less than x% of battery after searching this many cells