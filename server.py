#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sept 11 13:23:10 2020
@author: luc michalski
"""
import argparse
import os
import numpy as np

from questiongenerator import QuestionGenerator
# from questiongenerator import print_qa

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request

# taken from https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def parse_bool_string(s):
    if isinstance(s, bool):
        return s
    if s.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif s.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Script arguments can include path of the config
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "--model_dir",
    default=None,
    type=str,
    help="The folder that the trained model checkpoints are in.",
)
arg_parser.add_argument(
    "--num_questions",
    default=10,
    type=int,
    help="The desired number of questions to generate.",
)
arg_parser.add_argument(
    "--answer_style",
    default="all",
    type=str,
    help="The desired type of answers. Choose from ['all', 'sentences', 'multiple_choice']",
)
arg_parser.add_argument(
    "--show_answers",
    default='True',
    type=parse_bool_string,
    help="Whether or not you want the answers to be visible. Choose from ['True', 'False']",
)
arg_parser.add_argument(
    "--use_qa_eval",
    default='True',
    type=parse_bool_string,
    help="Whether or not you want the generated questions to be filtered for quality. Choose from ['True', 'False']",
)
arg_parser.add_argument('--host', type=str, default="0.0.0.0")
arg_parser.add_argument('--port', type=str, default="6012")
arg_parser.add_argument('--log', type=str, default="../logs/question-generator.log")
args = arg_parser.parse_args()

app = Flask(__name__)
print("Loading the model")
qg = QuestionGenerator(args.model_dir)

@app.route('/query', methods=['POST'])
def query():
    if request.args.get('text'):
        text = request.args.get('text')
    else:
        result = {"status": 400, "msg": "Question cannot be empty"}
        return jsonify(result)

    qa_list = qg.generate(
        text,
        num_questions=int(args.num_questions),
        answer_style=args.answer_style,
        use_evaluator=args.use_qa_eval
    )
    # print_qa(qa_list, show_answers=args.show_answers)
    # result = que_generator.generate(text)
    app.logger.info('result: %s', qa_list)
    return jsonify(qa_list)

if __name__ == '__main__':
    handler = RotatingFileHandler(args.log, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    print("Starting the server")
    app.run(host=args.host, port=args.port)
