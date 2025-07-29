import math
import time
from decimal import Decimal, InvalidOperation
from typing import Callable, Tuple

from flask import url_for, request, flash, render_template

from mathspractice.stats import Statistics


def serve(
        lesson: str,
        section: str,
        choices: str,
        determine_problem: Callable[[str,int], Tuple[int, str, list[Decimal]]],
        calculate_answer: Callable[[int, list[Decimal], Decimal, int, str], Tuple[Decimal, str, list[str], list[str]]],
        power = 4,
        quantize = lambda x: x.quantize(Decimal('0.01')),
):
    template = f'{lesson}/{section}.html'
    form_url = url_for(f'{lesson}.{section}')
    result_type = None
    results = None
    explain = []
    attempt = 0
    when = time.time()
    statistics = Statistics()
    stats = statistics.get_stats(lesson, section)
    if request.method == 'GET':
        max_value = int(math.pow(10, power + stats['correct'] // 20))
        which, problem, numbers = determine_problem(choices, max_value)
    else:
        numbers = [Decimal(n) for n in request.form.get('numbers', '').split(' ')]
        problem = request.form.get('problem')
        which = int(request.form.get('which'))
        attempt = int(request.form.get('attempt'))
        try:
            answer = request.form.get('answer')
            if not answer:
                raise ValueError('Sorry. You needed to provide an answer. Please try again.')
            answer = answer.strip()
            if answer.startswith('$'):
                answer = answer[1:]
            if answer.endswith(','):
                answer = answer[:-1]
            answer = Decimal(answer)
            if quantize:
                answer = quantize(answer)
            now = float(request.form.get('now'))
            elapsed = when - now
            real_answer, result_type, results, explain = calculate_answer(which, numbers, answer, attempt, problem)
            stats['seconds'] += elapsed
            if result_type == 'correct':
                stats['correct'] += 1
                explain = []
                max_value = int(math.pow(10, power + stats['correct'] // 20))
                which, problem, numbers = determine_problem(choices, max_value)
                attempt = 0
            else:
                if result_type == 'incorrect':
                    attempt += 1
                else:
                    max_value = int(math.pow(10, power + stats['correct'] // 20))
                    which, problem, numbers = determine_problem(choices, max_value)
                    attempt = 0
                    explain = []
                stats['incorrect'] += 1
            statistics.save()
        except InvalidOperation:
            answer = request.form.get('answer')
            result_type = 'error'
            results = [f'Sorry, I was expecting a number and not "{answer}"']
        except Exception as e:
            flash(str(e), category='error')
    now = int(time.time())
    return render_template(
        template,
        lesson=lesson, section=section,
        numbers=[f'{n}' for n in numbers],
        which=which, problem=problem,
        now=now, statistics=statistics,
        explain=explain,
        result_type=result_type,
        results=results,
        attempt=attempt,
        form_url=form_url,
    )
