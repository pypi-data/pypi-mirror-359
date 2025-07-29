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
    choices = '1,2'
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
    choices = '3,4'
    return serve(
        lesson=lesson,
        section=section,
        choices=choices,
        determine_problem=determine_problem,
        calculate_answer=calculate_answer,
        power=1,
        quantize=None,
    )


def determine_problem(choices: str, max_value: int) -> Tuple[int, str, list[Decimal]]:
    which = int(random.choice(choices.split(',')))
    if which in (1, 2):
        if which == 1:
            numbers = [
                Decimal(random.randint(1, max_value - 1)),
                Decimal(random.randint(1, max_value - 1)),
            ]
        else:
            numbers = [
                Decimal(random.randint(1, max_value - 1)),
                Decimal(random.randint(1, max_value - 1)),
                Decimal(random.randint(1, max_value - 1)),
            ]
        sequence = " + ".join([f'{n:,}' for n in numbers])
        problem = f'What is {sequence}?'
    else:
        if which == 3:
            numbers = [
                Decimal(random.randint(1, max_value - 1)),
                Decimal(random.randint(1, max_value - 1)),
            ]
        else:
            numbers = [
                Decimal(random.randint(1, max_value * 2 - 1)),
                Decimal(random.randint(1, max_value - 1)),
                Decimal(random.randint(1, max_value - 1)),
            ]
        sequence = " - ".join([f'{n:,}' for n in numbers])
        problem = f'What is {sequence}?'
    return which, problem, numbers


def calculate_answer(
        which: int,
        numbers: list[Decimal],
        answer: Decimal,
        attempt: int,
        problem: str,
) -> Tuple[Decimal, str, list[str], list[str]]:
    if which in (1, 2):
        real_answer = sum(numbers, start=Decimal(0))
        explain = [
            f'Write the first number  {numbers[0]:8,}',
            f'Write the second number {numbers[1]:8,} below the first'
        ]
        if len(numbers) > 2:
            explain.append(f'Write the third number  {numbers[2]:8,} below the second')
        explain.extend([
            f'Ensure that the numbers are right aligned',
            f'Sum the digits in vertical columns from right to left',
            f'Remember to carry when the sum of digits exceeds 9',
        ])
    else:
        real_answer = numbers[0] - sum(numbers[1:], start=Decimal(0))
        explain = [
            f'Write the first number  {numbers[0]:8,}',
            f'Write the second number {numbers[1]:8,} below the first',
        ]
        if len(numbers) > 2:
            explain.append(f'Write the third number  {numbers[2]:8,} below the second')
        explain.extend([
            f'Ensure that the numbers are right aligned',
            f'Subtract the digits in vertical columns from right to left and top to bottom',
            f'Remember to borrow if the second number digit is greater than the first number digit',
        ])
    if answer == real_answer:
        result_type = 'correct'
        if which in (1,2):
            sequence = " + ".join([f'{n}' for n in numbers])
            results = [f"Correct. Well done! {sequence} = {real_answer} is correct."]
        else:
            sequence = " - ".join([f'{n}' for n in numbers])
            results = [f"Correct. Well done! {sequence} = {real_answer} is correct."]
    else:
        if attempt < 3:
            result_type = 'incorrect'
            results = [
                f"Incorrect. I'm sorry but {answer} is not correct.",
                f"Please try again."
            ]
        else:
            result_type = 'failed'
            if which in (1, 2):
                results = [
                    f"Incorrect. I'm sorry but {answer} is not correct.",
                    f'The correct answer to "{problem}"  is {real_answer}',
                ]
            else:
                results = [
                    f"Incorrect. I'm sorry but {answer} is not correct.",
                    f'The correct answer to "{problem}"  is {real_answer}',
                ]
    return real_answer, result_type, results, explain
