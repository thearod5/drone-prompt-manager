# Getting Started
1. Install pip requirements
```commandline
$ pip3 install -r requirements.txt
```
2. Add .env file
```
OPEN_AI_ORG=[YOUR_ORG_HERE]
OPEN_AI_KEY=[YOUR_ORG_KEY]
```
# Creation Prompt
- examples/**: Prompt and response from OpenAI (gpt-4)
- runner.py: Example / interactive playground for testing prompt building and parsing.
- core/drone_variables.py: The parameters to be included in the prompt.
- prompts/*: Stripped out version of the prompt code used in SAFA.
- prompts/drone_prompt_builder: Creates the prompts and parses the response from the models
- 
# Requirements
1. If a drone requires a minimum of x% of battery to reach a charging station then `cells_in_single_battery` should never result in a drone with less than x% of battery after searching this many cells