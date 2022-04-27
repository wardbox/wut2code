import os

import openai
import random
import emoji

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/")
def index():
    topic = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Give me a topic that many people will be familiar with.",
        temperature=0.9
    )

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"""
        Give me a single idea for a basic web app involving {topic.choices[0].text}. It should be at least 3 sentences
        long. It should be easy to read. It should start with the phrase 'You should make' or 'Why don't you make'. The
        completion must include some emojis.""",
        temperature=0.9,
        max_tokens=200
    )

    button_texts = [
        "that sounds boring (－_－) zzZ",
        "nope (ﾒ` ﾛ ´)",
        "ew gross (눈_눈)",
        "try again 	(╯︵╰,)"
    ]

    return render_template(
        'index.html',
        response=emoji.emojize(
            response.choices[0].text, use_aliases=True).lower(),
        button_text=random.choice(button_texts),
        topic=topic.choices[0].text
    )
    # return render_template(
    #     'index.html',
    #     response="""
    #     Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
    #     magna aliqua. Pellentesque nec nam aliquam sem. Curabitur gravida arcu ac tortor dignissim convallis aenean et.
    #     Lacinia at quis risus sed vulputate odio ut enim blandit.""",
    #     button_text=random.choice(button_texts),
    #     topic="lorem ipsum"
    # )
