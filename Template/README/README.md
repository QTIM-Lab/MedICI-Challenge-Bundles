# General Challenge Useage

## Overview
A general classification challenge, this demo will ask you to guess the answers to a random answer key. There will be 2 classes {'a', 'b'}

Participants will be evaluated against 3 metrics (% correct, sensitivity and specificity), and are expected to submit docker containers for their evaulation.

## Get Data
The dataset consists of fake data that will be evaluated. It will have an answer key.

Participants are asked to submit files that contain the key, representing classification cases, and class (one of three choices within set {'a','b'}). The contents of an example sumission file is shown below:

|key|class |
|---|------|
|1  |a     |
|2  |a     |
|3  |b     |
|4  |a     |
|5  |b     |
|6  |b     |
|7  |a     |
|8  |a     |
|9  |b     |
|10 |b     |

## Evaluation
The challenge will consist of three phases: a training phase, a validation (or fine-tuning) phase, and a final test phase.

Each will have the same scoring mechanism looking for:  
1. % Correct  
2. Sensitivity  
3. Specificity  

## Terms and Conditions
Docker image is the submission medium of choice.
Must have a partnersID to participate in the challenge

## Non Docker Submission

### Register for the challenge:
Sign up for the website in general in the upper right on the Sign Up link.
![Sign Up](sign_up.png)

> You will have to verify email on prod environment

### Register for the Challenge
On the main page find the challenge and select it:  
![challenge_card](challenge_card.png)

The challenge landing page should have intitive tabs with the same content you saw at the beginning of this tutorial.  
![challenge_landing_page](challenge_landing_page.png)

Select the *Participate* tab to begin registgration.
![Register](register.png)

## Docker Submission
