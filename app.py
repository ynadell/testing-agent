import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Define constants
GEMINI_MODEL = "gemini-2.0-flash"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
MAX_RETRIES = 3
DELAY_MS = 2000  # Delay between retries in milliseconds

# Utility function to call the Gemini API
def call_gemini_api(model: str, prompt: str) -> str:
    try:
        gemini_api_key = "AIzaSyB9G6eE9fESU2RHTfI8leiNxQF-Kpa9juE"
        response = requests.post(
            f"{API_URL}?key={gemini_api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "topK": 40, "topP": 0.8}
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    except Exception as e:
        print(f"Error during API call: {e}")
        return "Error generating story."


# Step 1: Story Generator Agent
def generate_story(specification: str) -> str:
    prompt = f"""
    Please generate a short therapeutic story for children aged 5-8 years old who experience the issue mentioned.
    The story should feature a relatable child character who experiences feelings of worry or fear related to this situation. The narrative should gently introduce a simple coping mechanism or positive way of thinking that the character can use to manage their feelings.

    Please use clear and simple language, incorporating a comforting and encouraging tone. The story should include a clear beginning, a moment where the character experiences the problem, the introduction and use of the coping strategy, and a hopeful or positive resolution where the child feels more empowered or comfortable.

    Feel free to use age-appropriate metaphors or analogies to explain anxiety or the coping mechanism. The story should be approximately 300-500 words and have a title that reflects the theme of the story.

    Avoid overly complex plots or scary scenarios. The focus should be on providing comfort, validation, and a sense of possibility for managing feelings.

    Specification: {specification}
    """
    return call_gemini_api(GEMINI_MODEL, prompt)


# Step 2: Story Reviewer Agent
def review_story(generated_story: str) -> str:
    prompt = f"""
    You are an expert story editor. You should vet the stories to make sure that they are kid-friendly and easy to understand.
    Here is the story:
    ```python
    {generated_story}
    ```
    Please provide feedback on how to improve the story, ensuring that it is comforting, clear, and suitable for children.
    """
    return call_gemini_api(GEMINI_MODEL, prompt)


# Step 3: Story Polish Agent
def polish_story(review_comments: str) -> str:
    prompt = f"""
    You are an expert story generation agent that takes feedback and writes good therapeutic stories for children.
    Take the feedback provided by the story reviewer and generate a new story based on it.
    ```python
    {review_comments}
    ```
    Please rewrite the story based on the feedback, improving clarity, comfort, and appropriateness for children. Please return just the story and it's title and nothing else.
    """
    return call_gemini_api(GEMINI_MODEL, prompt)


# Step 4: Orchestrating the Pipeline
@app.route("/generate", methods=["POST"])
def generate_story_pipeline():
    specification = request.json.get("specification")

    # Step 1: Generate the initial story
    generated_story = generate_story(specification)

    # Step 2: Review the generated story
    review_comments = review_story(generated_story)

    # Step 3: Polish the story based on review comments
    polished_story = polish_story(review_comments)

    return jsonify({"story": polished_story})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
