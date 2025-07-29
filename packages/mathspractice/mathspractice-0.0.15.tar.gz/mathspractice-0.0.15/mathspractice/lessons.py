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
        determine_problem: Callable[[str,int], Tuple[int, str, Decimal, Decimal]],
        calculate_answer: Callable[[int, Decimal, Decimal, Decimal, int], Tuple[Decimal, str, list[str], list[str]]],
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
        which, problem, first, second = determine_problem(choices, max_value)
    else:
        first = Decimal(request.form.get('first'))
        second = Decimal(request.form.get('second'))
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
            real_answer, result_type, results, explain = calculate_answer(which, first, second, answer, attempt)
            stats['seconds'] += elapsed
            if answer == real_answer:
                stats['correct'] += 1
                explain = []
                max_value = int(math.pow(10, power + stats['correct'] // 20))
                which, problem, first, second = determine_problem(choices, max_value)
                attempt = 0
            else:
                if attempt < 3:
                    attempt += 1
                else:
                    max_value = int(math.pow(10, power + stats['correct'] // 20))
                    which, problem, first, second = determine_problem(choices, max_value)
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
        first=first, second=second,
        which=which, problem=problem,
        now=now, statistics=statistics,
        explain=explain,
        result_type=result_type,
        results=results,
        attempt=attempt,
        form_url=form_url,
    )
