---
layout: default
show_header: true
---

## General Materials
 - [Project Introduction, including Tweet](#project-introduction)
 - [Schedule of Standing Meetings](#standing-meetings)
 - [Contact Information and Team Roles](#contact-information-and-team-roles)
 - [Team Rules](#team-rules)
 - Link to Journal of Meetings and Decisions
 - Related Links

## Requirements Deliverables
 - Project Concept
 - [User Stories](#user-stories)
 - [Personas](#personas)
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

# User stories
 - Jason needs a list of Internet Tobacco Vendors in order to conduct research for the ITVS project. To generate this list, the internet must be searched for websites that sell tobacco and tobacco related products. It is essential that no vendors are mistakenly eliminated, although any false positives must be identified and removed manually, which is a time consuming process. 
 - Jason has a list of ITVs, but websites change and go out of business all the time. To ensure a solid baseline, all sites on Jason's list must be cached to be examined at a later date. The site should be preserved as accurately as possible to ensure that it is an accurate representation of the original site.
 - Jason has a cache of potential ITVs, but is concerned about false positives. To remove them, Jason needs a way to manually inspect every ITV as efficiently as possible, as there are more than cached 10,000 ITVs. Identifying suspicous ITVs first and providing a quick summary of data-mined site characteristics would be useful in this process.
 - ITVS has won a new grant that changes the scope of the project. Dmitriy already knows how to use our tools, but they are inadequate for the new grant. Dmitriy needs to modify our tools quickly so that ITVS can harvest and process the new data of interest.
 - Mysterio has joined the project for the year and has been assigned to assist Jason with a portion of the data collection. Mysterio is not very computer savvy, and Jason has other responsibilites besides training. Mysterio needs a comprehensive manual describing all the tools Jason needs her to use.

# Personas
*Jason*: Mid level management for the ITVS project. Jason is in charge of coordinating the more technical aspects of ITVS data processing. As such, he needs a thorough understanding of how to use every aspect of every tool, as well as the basic principles the tools are employing. Jason must be capable of performing every step in the process himself. Jason also needs the ability to train newcomers (Mysterio) to the project in order to delegate steps in the data processing pipeline. 
*Dmitriy*: Staffer responsible for maintaining our tools long term. In addition to being able to use our tools, Dmitriy needs a complete understanding of the inner workings of our product to be able to modify and update them as necessary. Dmitriy will be involved in our design process so that he is fully up to date with our project at the end of the semester. Dmitriy needs comprehensive documentation for as much functionality as possible, as well as any design decisions we make.
*Mysterio*: Anyone who uses our tools. Mysterio will be a person subbordinate to Jason who will take at least partial responsibility for using some component of our tools. Mysterio is assumed to have basic computing experience. Mysterio will be replacing Jason, and so Jason is assumed to be present for basic training and allocation of responsibilities. For any further questions, Mysterio needs a basic user manual that describes the function of all of our tools. Mysterio is not concerned with the implementation of our tools.

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
