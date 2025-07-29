import random
from decimal import Decimal
from typing import Tuple

from flask import Blueprint, render_template

from .lessons import serve
from .stats import Statistics

bp = Blueprint('lesson1', __name__)

@bp.route('/')
def index():
    statistics = Statistics()
    return render_template(
        'lesson1/index.html',
        statistics=statistics,
    )


@bp.route('/addition', methods=['GET', 'POST'])
def addition():
    lesson = 'lesson1'
    section = 'addition'
    choices = '1'
    return serve(
        lesson=lesson,
        section=section,
        choices=choices,
        determine_problem=determine_problem,
        calculate_answer=calculate_answer,
        power=1,
        quantize=None,
    )


@bp.route('/subtraction', methods=['GET', 'POST'])
def subtraction():
    lesson = 'lesson1'
    section = 'subtraction'
    choices = '2'
    return serve(
        lesson=lesson,
        section=section,
        choices=choices,
        determine_problem=determine_problem,
        calculate_answer=calculate_answer,
        power=1,
        quantize=None,
    )


def determine_problem(choices: str, max_value: int) -> Tuple[int, str, Decimal, Decimal]:
    which = int(random.choice(choices.split(',')))
    first = Decimal(random.randint(1, max_value-1))
    second = Decimal(random.randint(1, max_value-1))
    if which == 1:
        problem = f'What is {first:,} + {second:,}?'
    else:
        problem = f'What is {first:,} - {second:,}?'
    return which, problem, first, second


def calculate_answer(
        which: int,
        first: Decimal,
        second: Decimal,
        answer: Decimal,
        attempt: int,
) -> Tuple[Decimal, str, list[str], list[str]]:
    if which == 1:
        real_answer = first + second
        explain = [
            f'Write the first number  {first:8,}',
            f'Write the second number {second:8,} below the first',
            f'Ensure that the two numbers are right aligned',
            f'Sum the digits from right to left',
            f'Remember to carry when the sum of digits exceeds 9',
        ]
    else:
        real_answer = first - second
        explain = [
            f'Write the first number  {first:8,}',
            f'Write the second number {second:8,} below the first',
            f'Ensure that the two numbers are right aligned',
            f'Subtract the digits from right to left',
            f'Subtract the digit of the second number from the digit of the first number',
            f'Remember to borrow if the second number digit is greater than the first number digit',
        ]
    if answer == real_answer:
        result_type = 'correct'
        if which == 1:
            results = [f"Correct. Well done! {first} + {second} = {real_answer} is correct."]
        else:
            results = [f"Correct. Well done! {first} - {second} = {real_answer} is correct."]
    else:
        result_type = 'incorrect'
        if attempt < 3:
            results = [
                f"Incorrect. I'm sorry but {answer} is not correct.",
                f"Please try again"
            ]
        else:
            if which == 1:
                results = [
                    f"Incorrect. I'm sorry but {answer} is not correct.",
                    f"The correct answer to {first} + {second} is {real_answer}"
                ]
            else:
                results = [
                    f"Incorrect. I'm sorry but {answer} is not correct.",
                    f"The correct answer to {first} - {second} is {real_answer}"
                ]
    return real_answer, result_type, results, explain
