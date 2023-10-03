# AutoApplier 
#### by yusuf-wadi

- This repo helps you quickly apply to many {insert_here} in a smooth and efficient manner
- It also has useful utility modules
---
## Important

- run "pip install -r requirements.txt"
- setup Simplify extension for auto application to work
- fill in the example config.yml file and rename it to config.yml (from config.example.yml)
- to find paths, type chrome://version
- MAKE SURE THERE ARE NO INSTANCES OF YOUR TARGET BROWSER OPEN AT RUNTIME
---

## Changelog:
### button update _10/13/22_:

- clicks all buttons on a page, preferably redirect links (for internships)
- if the buttons are on simplify.com, clicking the "apply" button will automatically<br>
apply to the redirected link

### more robust querying/flexibility plus beginning implementation of LLM
- just clicks all the links it finds on google for your query then waits for the simplify popup (planning to in-house simplify function in the future)
- plans to implement LLM to create custom cover letter using your resume, the job descripton, and company name all as reference
---

![sped](misc/sped.jpg?raw=true "I am speed")

## Known Bugs

- [x] Can not activate Simplify yet (fixed)
- [ ] LLM buggin fr
