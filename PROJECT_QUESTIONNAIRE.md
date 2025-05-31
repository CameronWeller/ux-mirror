# UX Mirror Project Questionnaire
## Purpose: Define clear project scope and prevent feature creep

Please answer each question to help clarify the project direction. Be as specific as possible.

---

## 1. CORE PROJECT DEFINITION

### 1.1 Primary Goal
- [ ] What is the ONE primary problem UX Mirror solves?
- [ ] Who is the target user? (developers, designers, product managers, etc.)
developers 
- [ ] What specific pain point does it address?
ai code writers have no way of receiving visual feedback for systems they are building. Particularly in the case of game development. 

### 1.2 Success Metrics
- [ ] How do we measure if the prototype is successful?
for a first prototype. Lets be able to hook into a vulkan or opengl game and be able to get current screen output. Then second prototype will be able to take that image, send it away to an openai or anthropic server to get a description of what is being seen- and we may want to add pre and post processing in and out- as a pseudo-return to the function
- [ ] What's the minimum viable functionality for v1.0?
see what i said about first prototype. then second prototype is minimum viable product demo. 
- [ ] What would make a user say "this is useful"?
if it creates a loop in which the input is usefully read, properly assessed, and actually helpful for development, say the ui is cluttered or the button layout is gliched as an example. 
---

## 2. PROTOTYPE SCOPE

### 2.1 Must-Have Features (MVP)
- [ ] List only the absolutely essential features for the first working prototype:
  1. api hook-in for 3dgame of life project that was started elsewhere.
  2.  access to remote hosts with bigger models, properly selected so the model we are sending and receiving from is acutally usefull
  3. reasonable asssessment of user metrics outside of simply visual as well. there should be simple mouse and keyboard logging as well for assist

### 2.2 Nice-to-Have Features (Future)
- [ ] What features are tempting but should wait until after MVP?
  1. one day we might want to be able to do videos, short clips of the game to help assess live-behavior.
  2. local processing for beefy computers 
  3. custom tertiary ai models that are more specialized and trained for this ux design stuff. 
  super nice, but very future state would be also being able to tie this into opengl and vulkan validation pipelines to get the 'layers' beneath what is being seen on screen. 

### 2.3 Explicitly Out of Scope
- [ ] What should we definitely NOT build in v1.0?
  1. not an agentic project, agents exist in this project to help the author write the code and nothing else 
  2. 
  3. 

---

## 3. TECHNICAL IMPLEMENTATION

### 3.1 Input/Output
- [ ] What does the system take as input? (URLs, screenshots, code files, etc.)
game window screenshots, user io 
- [ ] What does it produce as output? (reports, code changes, visualizations, etc.)
assessment of ui information, quality, attributes, layout, general pleasantness 
- [ ] What format should outputs be in?
as a helpful and constructive return for the information we are feeding it. probaby will need some pre-and post processing and training analysis tools eventually

### 3.2 User Interaction
- [ ] Is this a CLI tool, web app, desktop app, or API?
mostly cli and desktop. api is important as well. 
- [ ] Does it run continuously or on-demand?
continuously as part of an agents workflow. 
- [ ] How does a user trigger analysis?
analysis can be ongoing and live as part of testing for fully autonomous modes. or they can submit screenshots manually with descriptive problems with what they are seeing (eg. hey this button doesnt look right. fix the relevant code)

### 3.3 Integration Points
- [ ] Does it need to integrate with existing tools? Which ones?
some sort of opengl and vulkan framework so that its integrateable. primarily vulkan.
- [ ] Does it need to work with specific frameworks/platforms?
vulkan, and all the tools that surround that
- [ ] Are there any authentication/authorization requirements?
as long as it uses openai or anthropic tools safely. 

---

## 4. VISUAL ANALYSIS SPECIFICS

### 4.1 Analysis Scope
- [ ] What specific UI/UX issues should it detect? (List in priority order)
  1. poor functionality 
  2. poor design 
  3. incorrect implementation, contrast from correct and expected behaviors. 

### 4.2 Platform Support
- [ ] Which platforms must be supported in MVP? (web, mobile, desktop)
 desktop only, with some groundwork for other platforms as this is for games and 3d development and needs beefy processing 
- [ ] Which browsers/devices are priority?
- [ ] Do we need responsive design analysis?
yes probably. not sure what you mean by this question

### 4.3 Accuracy vs Speed
- [ ] Is it better to be fast with 80% accuracy or slow with 95% accuracy?
slow at first. turnaround time should be within a minute ideally. no time constrains for first prototype. 
- [ ] What's the acceptable analysis time for a typical page/screen?
3 min tops. 

---

## 5. METRICS & INTELLIGENCE

### 5.1 User Behavior Tracking
- [ ] What specific user behaviors need tracking? (clicks, scrolls, time on page, etc.)
whatever drives usability. so probably all of the above. 
- [ ] Is this retrospective analysis or real-time monitoring?
retrospective. with future hopes for real time. real time should not be considered a goal for first prototypes and such. 
- [ ] Privacy considerations - what data can we collect?
mostly just dont mishandle the data we do collect. 

### 5.2 Performance Metrics
- [ ] Which performance metrics matter most? (load time, FPS, memory, etc.)
performance will be best if we dont slow down the host program. 
- [ ] How do we prioritize performance vs. functionality?
functionality first. this only needs to take a screenshot once and user user input tracking should be light enough to not worry about
- [ ] Do we need historical trending?
maybe some analysis of click usage. 

---

## 6. AUTONOMOUS IMPLEMENTATION

### 6.1 Code Generation Boundaries
- [ ] Should it generate actual code fixes or just recommendations?
should feed into agents that are planning on code fixes, recommendations inform that so its kinda the same thing to me. 
- [ ] What types of changes can it make autonomously? (CSS only? JS too?)
just feeds back into a cursor or other ai-driven ide agent. 
- [ ] How do we ensure generated code is safe?
ci cl tools out the wazzu 

### 6.2 Deployment Automation
- [ ] Should the MVP include any deployment features?
please use whatever is convenient
- [ ] Or should it just generate files for manual review?
---

## 7. DEVELOPMENT PRIORITIES

### 7.1 First Milestone
- [ ] What's the first tangible thing we should build to validate the concept?
hook into the following github project, might want to make a clone of as a sub-module to work with it nicely. 
https://github.com/CameronWeller/3DGameOfLife-Vulkan-Edition.git
- [ ] What would constitute a "proof of concept"?
idk you tell me
- [ ] Target completion: ___ days/weeks
undefined

### 7.2 Build Order
Please rank these components by implementation priority (1 = first):
- [ 1] Visual screenshot analysis
- [ 7] Metrics collection
- [2 ] Report generation
- [ 6] Code fix suggestions
- [5 ] User interface
- [3 ] API endpoints
- [4 ] Integration connectors

---

## 8. CONSTRAINTS & REQUIREMENTS

### 8.1 Technical Constraints
- [ ] Any specific technology requirements? (must use Python, etc.)
just vulkan, pytorch, and a cli screenshot utility maybe ffmpeg idk. 
- [ ] Performance requirements? (must analyze page in < X seconds)
stated earlier 
- [ ] Resource constraints? (RAM, GPU requirements)

### 8.2 User Constraints  
- [ ] Technical skill level of target users?
devs
- [ ] Expected usage frequency?
often
- [ ] Price point considerations?
none, dont go crazy with api key usage. 

---

## 9. RISK MITIGATION

### 9.1 Biggest Risks
- [ ] What could cause this project to fail?
my coding inadequacy. 
- [ ] What technical challenges worry you most?
idk
- [ ] What features might be too ambitious?
idk

### 9.2 Fallback Plans
- [ ] If GPU acceleration isn't available, then what?
dont plan on it. py
- [ ] If accuracy is too low, then what?
train better, preprocess better, post process better 
- [ ] If it's too slow, then what?
idk 

---

## 10. DEFINITION OF DONE

### 10.1 Prototype Completion
- [ ] What specific criteria must be met to consider the prototype "done"?
specified in general already.
- [ ] What demo scenario would best showcase the value?
working prototype feeding into the 3d game of life build. 

### 10.2 Next Steps After MVP
- [ ] Assuming MVP is successful, what's the very next feature to add?
cross that bridge when we get there.
- [ ] How do we gather user feedback?
this is kinda already built as this project can be summarized as a fancy a cursor plugin. 
- [ ] What would trigger a pivot vs. continuing current direction?
idk

---

## QUICK DECISIONS SECTION
For each item, choose ONE:

**Primary Use Case:**
- [this one  ] Automated UI testing
- [ ] Real-time UX monitoring  
- [ this one] Design system compliance
- [ ] Performance optimization
- [ ] Accessibility checking
- [ ] Other: ___________

**Deployment Model:**
- [ ] SaaS web service
- [ ] On-premise installation
- [ this one] CI/CD integration
- [ ] Browser extension
- [ ] Desktop application
- [ ] Other: ___________

**Analysis Depth:**
- [ ] Surface-level quick scans
- [ ] Deep comprehensive analysis
- [this one ] Configurable based on need

**Output Priority:** - im picking two because i want these to be prioritized.
- [ this one] Actionable fix recommendations
- [ ] Detailed problem reports
- [ this one] Visual annotated screenshots
- [ ] Performance metrics dashboards
- [ ] Other: ___________

---

## NOTES SECTION
Any additional thoughts, concerns, or ideas that don't fit above:




---
*After completing this questionnaire, we'll have a clear, focused path to a working prototype.* 