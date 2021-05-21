from flask import Blueprint, render_template, session, request, redirect, url_for
import math

index = Blueprint('index', __name__)


@index.route('/', methods=['GET'])
def home():
    return render_template('index.html')
