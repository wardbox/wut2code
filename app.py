import os

import openai
import random

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/")
def index():
    topic = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Give me a one word topic that many people will be familiar with.",
        temperature=0.9
    )

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"""
        Give me an idea for a basic web app involving {topic.choices[0].text}.
        The answer has to be easy to read and at most 4 sentences long.
        The completion has to start with the phrase 'You should make' or 'Why don't you make'
        The completion has to include 2 emoji.""",
        temperature=0.9,
        max_tokens=150
    )

    button_texts = [
        "that sounds boring (－_－) zzZ",
        "nope (ﾒ` ﾛ ´)",
        "ew gross (눈_눈)",
        "try again 	(╯︵╰,)"
    ]

    return render_template('index.html', response=response.choices[0].text, button_text=random.choice(button_texts))
