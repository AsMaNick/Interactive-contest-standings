from lxml import etree, html
import requests
from contest_standings import *


def get_text_content(item, sep=' '):
    content = ''
    for text in item.itertext():
        content += text + sep
    return content.strip()


def get_time(content, time_format):
    if time_format == 'minutes':
        pos = content.find(':')
        if pos != -1:
            content = content[:pos]
        if content.isdigit():
            return int(content)
        return -1
    else:
        pos = content.find(':')
        hours = content[:pos]
        minutes = content[pos + 1:]
        if hours.isdigit() and minutes.isdigit():
            return int(hours) * 60 + int(minutes)
        return -1


def parse_cell(content, time_format):
    if content == '' or content == '.' or content == '-':
        return 'ok', False, -1, -1
    upd = ''
    for c in content:
        if c.isspace():
            upd += ' '
        else:
            upd += c
    content = upd
    has_minus, has_plus, has_digit, has_other = False, False, False, False
    for c in content:
        if c.isspace():
            continue
        if c == '-':
            has_minus = True
        elif c == '+':
            has_plus = True
        elif c.isdigit():
            has_digit = True
        elif c not in '(:)[]':
            has_other = True
    if has_other:
        return 'fail', False, -1, -1
    wrong_attempts = -1
    if has_plus and content.find('+ ') != -1:
        wrong_attempts = 0
    else:
        for i in range(len(content)):
            if content[i].isdigit():
                pos = i
                while pos < len(content) and content[pos].isdigit():
                    pos += 1
                wrong_attempts = int(content[i:pos])
                content = content[:i] + content[pos:]
                break
    if wrong_attempts == -1:
        return 'fail', False, -1, -1
    upd = ''
    for c in content:
        if c.isdigit() or c == ':':
            upd += c
    time = get_time(upd, time_format)
    if has_minus:
        return 'ok', False, wrong_attempts, time
    if time == -1:
        return 'fail', False, -1, -1
    return 'ok', True, wrong_attempts, time
    

def get_result(solved, wrong_attempts, time):
    if solved:
        if wrong_attempts == 0:
            return '+', '({}:{:02d})'.format(time // 60, time % 60)
        return '+{}'.format(wrong_attempts), '({}:{:02d})'.format(time // 60, time % 60)
    if wrong_attempts == -1:
        return '', ''
    return '-{}'.format(wrong_attempts), ''
    
    
def parse_standings(link, n_problems, team_column, region_column, first_problem_column, time_format):
    content = requests.get(link).text
    parsed_body = html.fromstring(content)
    tables = parsed_body.xpath('//table[@class="standings"]')
    if len(tables) == 0:
        tables = parsed_body.xpath('//table[@id="standings"]')
    if len(tables) == 0:
        return "fail, cann't find table standings", None
    table = tables[0]
    rows_path = './tr'
    if len(table.xpath(rows_path)) < 2:
        rows_path = './*/tr'
    if len(table.xpath(rows_path)) < 2:
        return "fail, cann't find rows in standings table", None
    bad_rows = []
    first_ok_row = -1
    last_ok_row = -1
    show_regions = False
    if region_column != -1:
        show_regions = True
    regions_to_ignore = {}
    standings = Standings(show_regions, regions_to_ignore)
    problem_openers = ['' for i in range(n_problems)]
    time_openers = [1e9 for i in range(n_problems)]
    for row in table.xpath(rows_path):
        problem_results = ['' for i in range(n_problems)]
        problem_times = ['' for i in range(n_problems)]
        problem_datas = ['' for i in range(n_problems)]
        total, penalty = 0, 0
        team_name = ''
        region = ''
        bad_row = False
        for column, item in enumerate(row, 1):
            if column == team_column:
                team_name = get_text_content(item)
            elif column == region_column:
                region = get_text_content(item)
            elif first_problem_column <= column < first_problem_column + n_problems:
                status, solved, wrong_attempts, time = parse_cell(get_text_content(item), time_format)
                if status != 'ok':
                    bad_row = True
                    break
                if solved:
                    total += 1
                    penalty += 20 * wrong_attempts + time
                problem_results[column - first_problem_column], \
                problem_times[column - first_problem_column] = get_result(solved, wrong_attempts, time)
                problem_datas[column - first_problem_column] = solved, wrong_attempts, time
        bad_rows.append(bad_row)
        if bad_row:
            continue
        for problem_id, (solved, wrong_attempts, time) in enumerate(problem_datas):
            if solved and time_openers[problem_id] > time:
                problem_openers[problem_id] = team_name
                time_openers[problem_id] = time
        if first_ok_row == -1:
            first_ok_row = len(bad_rows) - 1
        last_ok_row = len(bad_rows) - 1
        team_result = Result(team_name, region, problem_results, problem_times, total, penalty)
        standings.add(team_result)
    standings.set_problem_openers(problem_openers)
    standings.sort()
    for bad in bad_rows[first_ok_row:last_ok_row + 1]:
        if bad:
            return "fail, cann't parse cell with results", None
    return 'ok', standings
