import random
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

from flask import Blueprint, render_template

from .lessons import serve
from .stats import Statistics

bp = Blueprint('lesson11', __name__)

@bp.route('/')
def index():
    statistics = Statistics()
    return render_template(
        'lesson11/index.html',
        statistics=statistics,
    )


@bp.route('/tips', methods=['GET', 'POST'])
def tips():
    lesson = 'lesson11'
    section = 'tips'
    choices = '1'
    return serve(
        lesson=lesson, section=section, choices=choices,
        determine_problem=determine_problem,
        calculate_answer=calculate_answer,
    )


@bp.route('/discount', methods=['GET', 'POST'])
def discount():
    lesson = 'lesson11'
    section = 'discount'
    choices = '2,3,4'
    return serve(
        lesson=lesson,
        section=section,
        choices=choices,
        determine_problem=determine_problem,
        calculate_answer=calculate_answer,
    )


@bp.route('/income_tax', methods=['GET', 'POST'])
def income_tax():
    lesson = 'lesson11'
    section = 'income_tax'
    choices = '5'
    return serve(
        lesson=lesson,
        section=section,
        choices=choices,
        determine_problem=determine_problem,
        calculate_answer=calculate_answer,
    )


def quantize(number: Decimal) -> Decimal:
    return number.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def determine_problem(choices: str, max_value: int) -> Tuple[int, str, list[Decimal]]:
    which = int(random.choice(choices.split(',')))
    if which == 1:
        numbers = [
            Decimal(random.randint(10, 50)),
            quantize(Decimal(random.randint(1, max_value)) / Decimal(100))
        ]
        problem = f'What is a {numbers[0]:,}% tip on a ${numbers[1]:,} restaurant bill?'
    elif which == 2:
        what = random.choice([('dealer', 'car'), ('agent', 'house')])
        numbers = [
            quantize(Decimal(random.randint(1, max_value))),
            Decimal(random.randint(10, 50))
        ]
        problem = (f'The original price of a {what[1]} was ${numbers[0]:,}. '
                   f'Then, the {what[0]} decided to give a {numbers[1]:,}% discount off the price of the {what[1]}. '
                   f'What is the price of the {what[1]:,} now?')
    elif which == 3:
        what = random.choice(['electric', 'gas', 'phone', 'water'])
        numbers = [
            quantize(Decimal(random.randint(1, max_value)) / Decimal(100)),
            Decimal(random.randint(5, 50))
        ]
        problem = (f"Last month’s {what} bill was ${numbers[0]}. "
                   f"Then, the company decided to give a {numbers[1]}% discount to its customers. "
                   f"How much is the bill now?")
    elif which == 4:
        what = random.choice([
            ('restaurant', 'students', 'lunch'),
            ('dry cleaners', 'office workers', 'laundry'),
            ('golf club', 'players', 'golfing')
        ])
        numbers = [
            quantize(Decimal(random.randint(1, max_value)) / Decimal(100)),
            Decimal(random.randint(5, 20))
        ]
        problem = (f"A {what[0]} offers a {numbers[1]}% discount to all {what[1]}, "
                   f"including your friend. Their recent {what[2]} bill "
                   f"should have cost ${numbers[0]}. "
                   f"What was the actual cost once the {numbers[1]}% discount was taken?")
    elif which == 5:
        numbers = [
            Decimal(random.randint(40, 180)) / Decimal(4),
            quantize(Decimal(random.randint(1, max_value)) * Decimal(10))
        ]
        problem = (f"The federal income tax is {numbers[0]}%. "
                   f"You earned ${numbers[1]:,} last year. "
                   f"How much tax will you have to pay?")
    else:
        problem=''
        numbers = [
            Decimal(0),
            Decimal(0),
        ]
    return which, problem, numbers


def calculate_answer(
        which: int,
        numbers: list[Decimal],
        answer: Decimal,
        attempt: int,
        problem: str,
) -> Tuple[Decimal, str, list[str], list[str]]:
    explain = []
    rules = []
    real_answer = Decimal(0)
    if which == 1:
        real_answer = quantize(numbers[0] / Decimal(100) * numbers[1])
        explain = [
            f'Calculate {numbers[0]:,} divided by 100, then multiplied by {numbers[1]:,}',
            f'Step 1 - Calculate {numbers[0]:,} divided by 100',
            f'Step 2 - Calculate the answer from Step 1 multiplied by {numbers[1]:,}',
        ]
        rules = [
            f'Rules:',
            f' (1) to divide by 100 you simply move the decimal place two places to the left.',
            f' (2) always align the decimal point of each number vertically when multiplying.',
            f' (3) sum the number of decimal places of each number to get the number of decimal places in the answer.',
        ]
    if which in (2, 3, 4):
        real_answer = quantize(numbers[0] - numbers[0] * numbers[1] / Decimal(100))
        explain = [
            f'First calculate the discount amount, then calculate the actual cost.',
            f'Calculate the discount amount by dividing {numbers[1]:,} by 100, then multiplied by {numbers[0]:,}',
            f'Step 1 - Calculate {numbers[1]:,} divided by 100',
            f'Step 2 - Calculate the discount amount as the answer to Step 1 multiplied by {numbers[0]:,}',
            f'Next calculate the actual cost by subtracting the discount amount from {numbers[0]:,}',
            f'Step 3 - Calculate the actual cost by subtracting the answer in Step 2 from {numbers[0]:,}',
        ]
        rules = [
            f'Rules:',
            f' (1) to divide by 100 you simply move the decimal place two places to the left.',
            f' (2) always align the decimal point of each number vertically when multiplying.',
            f' (3) sum the number of decimal places of each number to get the number of decimal places in the answer.',
            f' (4) always align the decimal point of each number vertically when subtracting.',
        ]
    if which == 5:
        real_answer = quantize(numbers[0] / Decimal(100) * numbers[1])
        explain = [
            f'Calculate {numbers[0]:,} divided by 100, then multiplied by {numbers[1]:,}',
            f'Step 1 - Calculate {numbers[0]:,} divided by 100',
            f'Step 2 - Calculate the answer in Step 1 multiplied by {numbers[1]:,}',
        ]
        rules = [
            f'Rules:',
            f' (1) to divide by 100 you simply move the decimal place two places to the left.',
            f' (2) always align the decimal point of each number vertically when multiplying.',
            f' (3) sum the number of decimal places of each number to get the number of decimal places in the answer.',
        ]
    explain.extend([
        f'Round the answer to the nearest cent.',
        f'Rounding down if the fractional amount is less than 0.5 cents',
        f'Rounding up if the fractional amount is 0.5 cents or greater',
    ])
    explain.extend(rules)
    if answer == real_answer:
        result_type = 'correct'
        results = [f"Correct. Well done! ${real_answer} is correct."]
    else:
        if attempt < 3:
            result_type = 'incorrect'
            results = [
                f"Incorrect. I'm sorry but ${answer} is not correct.",
                f"Please try again."
            ]
        else:
            result_type = 'failed'
            results = [
                f"Incorrect. I'm sorry but ${answer} is not correct.",
                f'The correct answer to "{problem}" is ${real_answer:,}',
            ]
    return real_answer, result_type, results, explain
