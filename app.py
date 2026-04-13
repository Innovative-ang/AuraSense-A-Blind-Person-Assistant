import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from duckduckgo_search import DDGS

app = Flask(__name__)

# GROQ SETUP
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Global variables for settings (Backend state)
sensitivity = 0.5
process_frames = 10

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_settings', methods=['POST'])
def update_settings():
    global sensitivity, process_frames
    data = request.json
    sensitivity = float(data.get('sensitivity', 0.5))
    process_frames = int(data.get('frames', 10))
    # You can also pass these settings back to Android via JS interface later
    return jsonify({"status": "success", "sensitivity": sensitivity})

@app.route('/ask_assistant', methods=['POST'])
def ask_assistant():
    data = request.json
    prompt = data.get('prompt', '')
    
    try:
        print(f"\n[AURA HEARD]: {prompt}") 
        live_context = ""
        try:
            results = DDGS().text(prompt, max_results=2)
            if results:
                search_text = " ".join([res['body'] for res in results])
                live_context = f"\n\nHere is real-time internet data to help you answer accurately: {search_text}"
        except Exception:
            pass

        system_instruction = (
            "You are Aura Sense, an AI assistant built to help a blind person navigate the world. "
            "Answer the user's query clearly, conversationally, and keep it very brief (1-2 sentences maximum)."
            + live_context
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.4,
        )
        
        raw_text = chat_completion.choices[0].message.content
        clean_text = raw_text.replace('*', '') 
        return jsonify({"response": clean_text})
    
    except Exception as e:
        return jsonify({"response": "I'm sorry, I am having trouble connecting to my brain right now."})

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
