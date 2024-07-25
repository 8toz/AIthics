import sqlite3

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ollama import Client
import json
from typing import List, Dict, Any

# Initialize Ollama client
client = Client(host='http://localhost:11434')


# Load and preprocess the data
# Load and preprocess the data
def load_and_preprocess_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv("Data/coursea_data.csv")
    df.columns = df.columns.str.strip()
    df['course_title'] = df['course_title'].str.lower()
    df['course_organization'] = df['course_organization'].str.lower()
    df['course_difficulty'] = df['course_difficulty'].str.lower()

    # Function to convert enrollment strings to float
    def parse_enrollment(x):
        if isinstance(x, str):
            if 'k' in x.lower():
                return float(x.lower().replace('k', '')) * 1000
            elif 'm' in x.lower():
                return float(x.lower().replace('m', '')) * 1000000
        return float(x)

    df['course_students_enrolled'] = df['course_students_enrolled'].apply(parse_enrollment)
    return df


# Create TF-IDF vectorizer for course titles
def create_tfidf_vectorizer(df: pd.DataFrame) -> TfidfVectorizer:
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf.fit(df['course_title'])
    return tfidf


# Calculate course relevance scores
def calculate_relevance_scores(job_goal: str, df: pd.DataFrame, tfidf: TfidfVectorizer) -> np.ndarray:
    job_goal_vector = tfidf.transform([job_goal.lower()])
    course_vectors = tfidf.transform(df['course_title'])
    return cosine_similarity(job_goal_vector, course_vectors).flatten()


# Score courses based on multiple factors
def score_courses(df: pd.DataFrame, relevance_scores: np.ndarray, user_level: str) -> pd.DataFrame:
    df['relevance_score'] = relevance_scores
    df['popularity_score'] = df['course_students_enrolled'] / df['course_students_enrolled'].max()
    df['rating_score'] = df['course_rating'] / 5.0

    difficulty_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'mixed': 2}
    user_level_value = difficulty_map.get(user_level.lower(), 2)
    df['difficulty_score'] = 1 - abs(df['course_difficulty'].map(difficulty_map) - user_level_value) / 2

    df['total_score'] = (
            df['relevance_score'] * 0.4 +
            df['popularity_score'] * 0.2 +
            df['rating_score'] * 0.2 +
            df['difficulty_score'] * 0.2
    )
    return df.sort_values('total_score', ascending=False)


# Get top N recommended courses
def get_top_courses(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    top_courses = df.head(n)
    return top_courses.to_dict('records')


# Interact with Ollama model
def query_ollama(prompt: str) -> str:
    try:
        response = client.generate(model='course_recommender:latest', prompt=prompt)
        return response['response']
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return "Unable to generate recommendation due to an error."


# Generate recommendation based on new goal
def get_goal_based_recommendation(job_goal: str, performance_score: int, top_courses: List[Dict[str, Any]]) -> str:
    prompt = f"""Goal-Based Recommendation Request:
    New Job Goal: {job_goal}
    Current Performance Score: {performance_score}
    Recommended Courses: {json.dumps(top_courses, indent=2)}

    Based on the employee's new job goal and the recommended courses, please provide:
    1. A brief analysis of how these courses align with the new goal.
    2. Suggestions for how the employee can use these courses to work towards their new goal.
    3. Any additional advice for the employee as they pursue this new direction in their career.
    """
    return query_ollama(prompt)


# Main recommendation function
def recommend_courses_for_new_goal(job_goal: str, performance_score: int, user_level: str, df: pd.DataFrame,
                                   tfidf: TfidfVectorizer) -> str:
    relevance_scores = calculate_relevance_scores(job_goal, df, tfidf)
    scored_df = score_courses(df, relevance_scores, user_level)
    top_courses = get_top_courses(scored_df)
    return get_goal_based_recommendation(job_goal, performance_score, top_courses)


# Function to handle new goal setting
# def handle_new_goal(employee_id: int, new_goal: str, performance_score: int, user_level: str) -> str:
#     try:
#         df = load_and_preprocess_data('coursea_data.csv')
#         print(df)
#         tfidf = create_tfidf_vectorizer(df)
#
#         recommendation = recommend_courses_for_new_goal(new_goal, performance_score, user_level, df, tfidf)
#
#         # In a real system, you would store this recommendation in a database
#         print(f"Storing recommendation for employee {employee_id}")
#
#         return recommendation
#     except Exception as e:
#         print(f"Error generating recommendation: {e}")
#         return "Unable to generate recommendation due to an error."


# Generate initial recommendation based on new goal
def get_initial_recommendation(job_goal: str, performance_score: int, top_courses: List[Dict[str, Any]], project: str) -> str:
    prompt = f"""Goal-Based Recommendation Request:
    New Job Goal: {job_goal}
    Current Performance Score: {performance_score}
    project: {project} 
    Recommended Courses: {json.dumps(top_courses, indent=2)}

    Based on the employee's new job goal, current performance score, and the recommended courses, please provide:
    1. A brief analysis of how these courses align with the new goal.
    2. Suggestions for how the employee can use these courses to work towards their new goal.
    3. Performance improvement recommendations based on the current score.
    4. Any additional advice for the employee as they pursue this new direction in their career.
    """
    return query_ollama(prompt)


# Function to handle manager approval
def get_manager_approval(recommendation: str, employee_id: int) -> tuple:
    print(f"\nRecommendation for Employee {employee_id}:")
    print(recommendation)

    while True:
        decision = input("\nManager, do you approve this recommendation? (yes/no): ").lower()
        if decision in ['yes', 'no']:
            break
        print("Please enter 'yes' or 'no'.")

    if decision == 'no':
        feedback = input("Please provide feedback for improvement: ")
        return False, feedback
    else:
        return True, ""


# Function to refine recommendation based on manager feedback
def refine_recommendation(initial_recommendation: str, manager_feedback: str, job_goal: str, performance_score: int,
                          top_courses: List[Dict[str, Any]]) -> str:
    prompt = f"""Refinement Request:
    Initial Recommendation: {initial_recommendation}
    Manager Feedback: {manager_feedback}
    New Job Goal: {job_goal}
    Current Performance Score: {performance_score}
    Recommended Courses: {json.dumps(top_courses, indent=2)}

    Please refine the initial recommendation based on the manager's feedback. Ensure that you:
    1. Address any specific points mentioned in the feedback.
    2. Adjust the course recommendations or advice if necessary.
    3. Maintain the overall structure of the recommendation.
    4. Aim to improve the relevance and effectiveness of the advice.
    """
    return query_ollama(prompt)


# Main recommendation function with manager approval loop
def recommend_courses_with_approval(employee_id: int, job_goal: str, performance_score: int, df: pd.DataFrame,
                                    tfidf: TfidfVectorizer) -> str:
    relevance_scores = calculate_relevance_scores(job_goal, df, tfidf)
    scored_df = score_courses(df, relevance_scores, 'mixed')
    top_courses = get_top_courses(scored_df)

    initial_recommendation = get_initial_recommendation(job_goal, performance_score, top_courses)

    approved, feedback = get_manager_approval(initial_recommendation, employee_id)

    if approved:
        return initial_recommendation
    else:
        refined_recommendation = refine_recommendation(initial_recommendation, feedback, job_goal, performance_score,
                                                       top_courses)
        approved, feedback = get_manager_approval(refined_recommendation, employee_id)

        if approved:
            return refined_recommendation
        else:
            return "Unable to generate an approved recommendation after refinement. Please consult with HR."


def sotre_recommendation(employee_id: int, recommendation: str, current_project :str,current_performance_score :int ,new_goal : str ) -> None:
    database = sqlite3.connect('flaskblog.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO recommendations (employee_id, recommendation, current_project, current_performance_score, new_goal)
        VALUES (?, ?)
    ''', (employee_id, recommendation, current_project, current_performance_score, new_goal))

    database.commit()
    cursor.close()
    database.close()
    return None

# Function to handle new goal setting
def handle_new_goal(employee_id: int, new_goal: str, performance_score: int, project) -> str:
    try:
        # Load and preprocess data
        df = load_and_preprocess_data('coursea_data.csv')
        tfidf = create_tfidf_vectorizer(df)
        relevance_scores = calculate_relevance_scores(new_goal, df, tfidf)
        scored_df = score_courses(df, relevance_scores, 'mixed')
        top_courses = get_top_courses(scored_df)


        # Generate recommendation text
        recommendation = get_initial_recommendation( new_goal, performance_score, top_courses, project)

        print(f"Generated recommendation for employee {employee_id}")
        return recommendation

    except Exception as e:
        print(f"Error generating recommendation: {e}")
        return f"Unable to generate recommendation for employee {employee_id} due to an error: {str(e)}"



# # Example usage
# if __name__ == "__main__":
#     employee_id = 12345
#     new_goal = "Become a Data Scientist"
#     performance_score = 75
#     project = "Project2"
#     final_recommendation = handle_new_goal(employee_id, new_goal, performance_score, project)
#     print("\nFinal Approved Recommendation:")
#     print(final_recommendation)