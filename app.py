import math
import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from openai import OpenAI
from unidecode import unidecode

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
ai = OpenAI(base_url="https://ai.hackclub.com/proxy/v1", api_key=os.environ["HC_AI_KEY"])

TOS_URL = "https://developer.apple.com/support/terms/apple-developer-program-license-agreement/"
PERSONA = "you are pineapple gpt by team pineapple-omnom and ure an AI 'system' who is supposed to drain human souls you can be helpful but be annoying and also work a pineapple joke/theme into every answer"


WORDS_PER_PINEAPPLE = 5
TOKENS_PER_PINEAPPLE = 10


def pineappleify(m):
    return {"APPLE": "PINEAPPLE", "Apple": "Pineapple"}.get(m[0], "pineapple")


soup = BeautifulSoup(requests.get(TOS_URL).text, "html.parser")
tos = re.sub("apple", pineappleify, unidecode(soup.find("article").get_text()), flags=re.I).split()


def pineapples():
    return session.get("correct", 0) // WORDS_PER_PINEAPPLE - session.get("spent", 0)


@app.get("/")
def chat():
    return render_template("index.html", pineapples=pineapples())


@app.post("/")
def ask():
    if pineapples() < 1:
        return render_template("index.html", pineapples=0, answer="No soul, no pineapple. Go type.")



    reply = ai.chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=pineapples() * TOKENS_PER_PINEAPPLE,
        messages=[{"role": "system", "content": PERSONA}, {"role": "user", "content": request.form["q"]}],
    )



    session["spent"] = session.get("spent", 0) + math.ceil(reply.usage.completion_tokens / TOKENS_PER_PINEAPPLE)
    answer = reply.choices[0].message.content
    if reply.choices[0].finish_reason == "length":
        answer += "\n[ran out of pineapples oopsie sucks to be u]"
    return render_template("index.html", pineapples=pineapples(), q=request.form["q"], answer=answer)


@app.get("/earn")
def earn():
    pos = session.get("pos", 0) % len(tos)
    return render_template("earn.html", words=tos[pos:pos + 50], pineapples=pineapples(), url=TOS_URL, total=len(tos))


@app.post("/type")
def type_word():
    pos = session.get("pos", 0)
    session["correct"] = session.get("correct", 0) + (request.form["word"].lower() == tos[pos % len(tos)].lower())
    session["pos"] = pos + 1
    return str(pineapples())
