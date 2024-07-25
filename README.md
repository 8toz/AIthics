# AIthics
Bizhack solution for Infosys Instep hackathon

# AI-driven HR Solution

An intelligent system designed to enhance operational efficiency in Human Resources by providing gentle nudges to both employees and managers for routine tasks.

## Table of Contents
1. [Installation](#installation)
2. [Problem Statement](#problem-statement)
3. [Our Solution](#our-solution)

## Installation

### Prerequisites
- Python 3.10.7 or higher
- pip (Python package manager)
- ollama

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/ai-driven-hr-solution.git
   cd ai-driven-hr-solution
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Load the model files into ollama:
   ```
   ollama create model_name1 --file .\AIthics\Modelfiles\nudges.modelfile
   ollama create model_name2 --file .\AIthics\Modelfiles\insights.modelfile
   ```
   Replace `absolute_model_path_nudges` and `absolute_model_path_insights` with the appropriate model names for your project.

## Problem Statement

In today's fast-paced work environment, HR departments face challenges in maintaining efficient communication between managers and employees, integrating various HR platforms, and optimizing goal-setting processes. These issues can lead to decreased productivity, miscommunication, and misalignment of objectives within the organization.

## Our Solution

Our AI-driven HR solution addresses these challenges by:

1. **Improving manager-employee feedback loop:**
   - Automated reminders for regular check-ins and performance reviews
   - AI-generated insights based on communication patterns and performance data

2. **Integrating different HR platforms:**
   - Seamless data flow between various HR tools and systems
   - Centralized dashboard for easy access to all HR-related information

3. **Enhancing goal planning process:**
   - AI-assisted goal setting and tracking
   - Personalized suggestions for skill development and career growth

By leveraging artificial intelligence, our solution provides gentle nudges to both employees and managers, ensuring that routine tasks are completed efficiently and important HR processes are streamlined.

---

For more information or support, please contact our team at AIthics@infosys.bizhack.com.
