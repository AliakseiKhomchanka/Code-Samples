# Aliaksei Khomchanka's code samples

This repository contains some of my code samples. Most of my recent code samples from my current job (except for one particular script that can be useful for others) can't be included here at the moment as those are internal company tools and I can't publish them. However, this repository includes some of source codes for my personal projects and links to other things.

## What can you find in this repository
---

### ICS parser

This tool was written by me during an internship at a startup called Minute Hero GmbH in late 2017, before the company closed the following year. The company was developing a virtual voice-controlled secretary for business meetings. I was involved in different aspects of the product, but this script in particular was made to automatically parse invites to meetings in various conferencing platforms like Zoom, Skype For Business etc. It had a built-in tool to manually prepare templates for parsing different kind of invites as there were language differences as well as different layouts for different versions of same platforms.

### Text statistics equalizer

Just a little script I've written in mid-2018 for fun after studying cryptography during my exchange at NTU. I wanted to see how much I could abuse a text string so that it would be readable to humans but online decyphering tools for substitution-type ciphers wouldn't be able to make any sense of it. The script would adjust test statystics to completely normalize the frequencies at which each character occurs. The result would be a normal string with added pseudowords of nonsensical character sequences that could be filtered out manually or via nlp tools. Length and distribution of those pseudowords was also adjusted to be more or less uniform to not give away their positions.

### TeamCity GitHub status reporter

This script was an emergency measure I've implemented to bypass a failing TeamCity plugin responsible for posting build statuses (queued/running/success/failure) to GitHub as the failure of that plugin has slowed down development across the company almost to a halt since developers had to manually search for their builds in TC and manually force merges on their PRs. This script complately bypassed the failing plugin and ensured our development could proceed normally while a long investigation into the source of our problems was underway. 

### AWS Student Voting Platform

Scripts for three Lambda functions that were handling the logic of a completely serverless tampering-detecting AWS-based voting platform (only the backend part) for student elections that I have designed and implemented as a part of my Bachelor thesis at HAW Hamburg. The thesis itself, including description of how those Lambda functions interacted with other AWS components, for those interested, can be found at:

https://aliaksei-khomchanka-portfolio-files.s3.eu-central-1.amazonaws.com/THESIS.pdf

## Links to other projects not included in this repository
___

### Braille II

This project aims to provide an affordable and portable Braille display to a wide audience and solve decades-long challenge of providing affordable and simple full-page Braille displays. Different designs have been tried since early 2016, each getting closer to the end goal. A honorary mention at the Create The Future 2019 contest.

https://contest.techbriefs.com/2019/entries/consumer-products/9836

https://www.youtube.com/watch?v=S93mF58pzu8