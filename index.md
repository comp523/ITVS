---
layout: default
show_header: true
---

## General Materials
 - [Project Introduction, including Tweet](#project-introduction)
 - Schedule of Standing Meetings
 - [Contact Information and Team Roles](#contact-information-and-team-roles)
 - [Team Rules](#team-rules)
 - Link to Journal of Meetings and Decisions
 - Related Links

## Requirements Deliverables
 - Project Concept
 - User Stories
 - Personas
 - [Platform Analysis and Selection](#platform-analysis-and-selection)
 - Prototype

## Sprint Deliverables
 - Functional Specification
 - Design Doc, which includes the architecture diagram
 - Test Plan
 - User Manual
 - [Version-controlled Repository]({{ site.git.project_url }})
 - Executable Code and Instructions

***

# Project Introduction

**Tweet:** Our aim is to provide utilities aiding in the process of scraping, caching, and identifying internet tobacco vending websites.

# Standing Meetings

Group Meeting: **Monday/Wednesday 2:45**  
Client Meeting: **Friday 1:25**
 
# Contact Information and Team Roles
 
**Architect**: Rourke Creighton - [Email](mailto:racreigh@live.unc.edu)  
**Client Liaison**: Daniel Chiquito - [Email](mailto:daniel.chiquito@gmail.com)  
**Project Manager**: Lukas O'Daniel - [Email](mailto:odani@live.unc.edu)  
**Writer**: Bryan Iddings - [Email](mailto:iddings@cs.unc.edu)

# Team Rules

 - Primary Contact Channel: **Slack**
 - Expected Response Time: **<24 hours, <12 hours if @ mentioned**
 - Maximum Wait for Late Meeting Arrival: **5 minutes**
 - Requests for Decision: **Indicate default choice and response window (minimum 12 hours)**
 - Slippages: **Endeavor to avoid getting stuck on one issue:**
   - Utilize outside resources (peers, professors, the internet, etc.).
   - Ask a teammate to review the issue.
 - Minimum Warning for Missed Deadline: **24 hours**
 - Python Style Guide: **[Google Style Guide](https://google.github.io/styleguide/pyguide.html)**
 
***

# Platform Analysis and Selection

### Programming Language/Libraries

**[Python 3](https://docs.python.org/3/):** Selected over Python 2 due to nearing end-of-life of Python 2.  
**[Selenium](http://docs.seleniumhq.org/projects/webdriver/):** Headless browser package for automated scraping of dynamically generated sites.  
**Machine Learning Library:** *[scikit-learn](http://scikit-learn.org/)* and *[TensorFlow](https://www.tensorflow.org/)* are potential candidates under review.

### Code Quality Assurance

**[PyUnit](https://docs.python.org/3.5/library/unittest.html)/[nosetests](http://nose.readthedocs.io/en/latest/):** Reduce bug severity with test-driven development.  
**[Travis CI](https://travis-ci.org/):** Continuous integration, namely automated unit testing.  
**[CodeClimate](https://codeclimate.com/):** Ensure style-guide adherence and best coding practices.  
**Manual Code Review:** All code is peer-reviewed prior to incorporation.