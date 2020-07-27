# question_generator
Question Generator is an NLP system for generating reading comprehension-style questions from texts such as news articles or pages excerpts from books. The system is built using pretrained models [HuggingFace Transformers](https://github.com/huggingface/transformers). There are two models: the question generator, and the QA evaluator.

## Usage
The easiest way to generate some questions is to clone the github repo and then run `qg_run.py` like this:
```
!git clone https://github.com/iarfmoose/question_generator
!python 'question_generator/run_qg.py' --text_dir 'question_generator/articles/twitter_hack.txt'
```

The `QuestionGenerator` class can also be instantiated and used like this:
```python
from questiongenerator import QuestionGenerator
question_generator = QuestionGenerator()
question_generator.generate_questions(text, num_questions=10)
```
This returns a list of dictionaries containing question and answer pairs. In the case of multiple choice questions, the answer will contain a list of dictionaries containing the answers and a boolean value stating if the answer is correct or not. The output can be easily printed using the `print_qa()` function.

### Choosing the number of questions
The desired number of questions can be passed as a command line argument using `--num_qeustions`  or as an argument when calling `qg.generate(text, num_questions=20`. If the chosen number of questions is too large, then the model may not be able to generate enough. The maximum number of questions will depend on the length of the input text, or more specifically the number of sentences and named entities containined within text.

Calling `generate()` will cause the question generator to split the text and generate questions. The generated questions will then be fed into the QA evaluator. The final output will be the top n questions according to the QA evaluator's predictions.

### Answer types types
The system can generate questions with full-sentence answers (`'sentences'`), questions with multiple-choice answers (`'multiple_choice'`), or a mix of both (`'all'`). This can be selected using the `--answer_style` or `qg.generate(answer_style=<style>)` arguments.

## Question Generator
The question generator model takes a text as input and outputs a series of question and answer pairs. The answers are sentences and phrases extracted from the input text. The extracted phrases can be either full sentences or named entities extracted using [spaCy](https://spacy.io/). The questions are generated by concatenating the extracted answer with the full text (up to a maximum of 512 tokens) as context in the following format:
```
answer_token <extracted answer> context_token <context>
```
The concatenated string is then encoded and fed into the question generator model. The model architecture is `t5-small`. The pretrained model was finetuned as a sequence-to-sequence model on a dataset made up several well-known QA datasets ([SQuAD](https://rajpurkar.github.io/SQuAD-explorer/), [CoQA](https://stanfordnlp.github.io/coqa/), and [MSMARCO](https://microsoft.github.io/msmarco/)). The datasets were restructured by concatenating the answer and context fields into the previously mentioned format. The concatenated answer and context was then used as an input for training, and the question field became the targets.

## QA Evaluator
The QA evaluator takes a question answer pair as an input and outputs a value representing its prediction about whether the input was a valid question and answer pair or not. The model architecture is ``bert-base`` with a sequence classification head. The pretrained model was finetuned on the same data as the question generator model, but the context was removed. The question and answer were concatenated 50% of the time. In the other 50% of the time a corruption operation was performed. The model was then trained to predict whether the input sequence represented one of the original QA pairs or a corrupted input.

The input for the QA evaluator follows the format for `BertForSequenceClassification` from HuggingFace, but using the question and answer as the two sequences. It is the following format:
```
[CLS] <question> [SEP] <answer [SEP]
```
