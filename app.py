import os

import openai
import random
import emoji

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per day", "5 per hour", "3 per minute"]
)


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
        Give me an idea for a basic web app involving {topic.choices[0].text}. The completion should be at least 3
        sentences long. The completion should be easy to read. The completion should start with the phrase 'You should
        make' or 'Why don't you make'. The completion must include some emojis.""",
        temperature=0.9,
        max_tokens=250
    )

    button_texts = [
        "that sounds boring (－_－) zzZ",
        "nope (ﾒ` ﾛ ´)",
        "ew gross (눈_눈)",
        "try again 	(╯︵╰,)"
    ]

    filtered = openai.Completion.create(
        engine="content-filter-alpha",
        prompt="<|endoftext|>"+response.choices[0].text+"\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=0,
        logprobs=10
    )

    output_label = filtered["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

    # if the most probable token is none of "0", "1", or "2"
    # this should be set as unsafe
    if output_label not in ["0", "1", "2"]:
        output_label = "2"
        return redirect(url_for('index.html'), try_again=True)

    else:
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


@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template(
        '429.html', error=e
    )


@app.errorhandler(404)
def ratelimit_handler(e):
    return render_template(
        '404.html', error=e
    )
