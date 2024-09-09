from flask import Flask, render_template, request, jsonify
from datetime import datetime
from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import random

# Download necessary NLTK data
nltk.download('vader_lexicon')

# Initialize Flask app
app = Flask(__name__)

# Initialize NLP tools
sia = SentimentIntensityAnalyzer()  # NLTK sentiment analyzer
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=False)  # Emotion detection

# Initialize conversation context and user information
conversation_context = []
user_name = None

# AI logic for responses with emotion and sentiment detection
def generate_response(user_input):
    global conversation_context, user_name

    # Check if the user is signaling the end of the conversation
    if user_input.lower() in ["i'm done", "thank you", "goodbye", "no more", "that's all", "bye", "no", "No", "nope", "Nope"]:
        return f"No problem, {user_name}. Come back anytime if you need to talk. Take care!"

    # Check if we're expecting the user's name
    if user_name is None:
        if "my name is" in user_input.lower() or "i'm" in user_input.lower() or "i am" in user_input.lower():
            user_name = user_input.split()[-1]  # Assuming the name is the last word in the input
            return f"Nice to meet you, {user_name}! How can I assist you today?"
        elif len(user_input.split()) == 1:  # Assuming the name is a single word input
            user_name = user_input.strip()
            return f"Nice to meet you, {user_name}! How can I assist you today?"
        else:
            return "Before we continue, could you please tell me your name?"

    # Analyze sentiment
    sentiment = sia.polarity_scores(user_input)
    sentiment_type = 'neutral'
    if sentiment['compound'] > 0.5:
        sentiment_type = 'positive'
    elif sentiment['compound'] < -0.5:
        sentiment_type = 'negative'

    # Detect emotion
    emotions = emotion_classifier(user_input)
    primary_emotion = emotions[0]['label']

    # Add the current input to context
    conversation_context.append({
        "user_input": user_input,
        "primary_emotion": primary_emotion,
        "sentiment": sentiment_type
    })

    # Define varied responses for each emotion with supportive follow-ups
    responses = {
        "joy": [
            f"I'm glad to hear that you're feeling joyful, {user_name}! 😊 What’s making you feel this way?",
            f"That's wonderful, {user_name}! Keep spreading that positivity. 😊",
            f"Joy is such a great feeling, {user_name}. Do you want to share what brought this happiness?"
        ],
        "sadness": [
            f"I'm sorry to hear that you're feeling sad, {user_name}. 😔 I understand, you can tell me anything. Is there anything else you would like to add?",
            f"Sadness can be tough, {user_name}. I'm here for you if you want to talk. Is there something specific on your mind?",
            f"It's okay to feel sad sometimes, {user_name}. How can I support you? You can share more if you’d like."
        ],
        "anger": [
            f"It sounds like you're upset, {user_name}. 😡 I’m here to listen if you need to vent. Is there anything else bothering you?",
            f"I'm sorry that you're feeling angry, {user_name}. Would it help to talk about it? I'm here for you.",
            f"Anger is a strong emotion, {user_name}. Let’s talk through it together. Feel free to share more."
        ],
        "fear": [
            f"It seems like you're feeling afraid or anxious, {user_name}. 😨 What’s causing this feeling? You can tell me anything.",
            f"Fear can be overwhelming, {user_name}. I'm here to help you calm down. Is there anything else you’d like to share?",
            f"If you want to talk about what’s making you anxious, {user_name}, I'm here to listen. You can always share more."
        ],
        "love": [
            f"I'm happy to hear that you're feeling love or affection, {user_name}. 💖 Who or what are you feeling this for?",
            f"Love is a beautiful feeling, {user_name}. How can I help you with it? Is there anything else you'd like to share?",
            f"It’s wonderful that you’re feeling love, {user_name}. Do you want to share more about it?"
        ],
        "surprise": [
            f"Something unexpected happened? 😲 Tell me more, {user_name}!",
            f"Surprises can be fun or shocking, {user_name}. What happened? Feel free to share more details.",
            f"I’m curious to hear more about this surprise, {user_name}. Want to share?"
        ]
    }

    # Choose a response based on the detected emotion and context
    if primary_emotion in responses:
        response = random.choice(responses[primary_emotion])
    else:
        response = f"I'm here to support you no matter what, {user_name}. You can tell me anything."

    # Use previous context for tailored follow-ups
    if len(conversation_context) > 1:
        previous_context = conversation_context[-2]
        if previous_context['primary_emotion'] == 'sadness' and primary_emotion == 'joy':
            response += " It’s great to see that you’re feeling better now. What changed?"
        elif previous_context['primary_emotion'] == 'anger' and primary_emotion == 'calm':
            response += " I'm glad you were able to calm down. Is there anything else I can help you with?"

    # Cap the context length to avoid memory overload
    if len(conversation_context) > 5:
        conversation_context.pop(0)

    return response

# Home route - serves the HTML page
@app.route('/')
def home():
    return render_template('index.html')

# API route to handle chat responses
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get("message")
    response = generate_response(user_input)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return jsonify({"response": response, "timestamp": timestamp})

# Automatic introduction when the chat starts
@app.route('/get_intro', methods=['GET'])
def get_intro():
    intro_message = "Hello! I'm your mental health chatbot. Before we begin, what is your name?"
    timestamp = datetime.now().strftime("%H:%M:%S")
    return jsonify({"response": intro_message, "timestamp": timestamp})

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
