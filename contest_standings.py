from participants_identification import team_identifier


statistic_team_number = 5


def get_time_str(time):
    h = time // 60
    m = time % 60
    return '{:1d}:{:02d}:00'.format(h, m)
    
    
class Result:
    def __init__(self, name, region, problem_results, problem_times, total, penalty):
        self.name = name
        self.problem_results = problem_results
        self.problem_times = problem_times
        self.total = int(total)
        self.penalty = int(penalty)
        self.region = region
        
    def __lt__(self, other):
        return self.total > other.total or (self.total == other.total and self.penalty < other.penalty)
        
    def get_dirt(self):
        dirt = 0
        for res in self.problem_results:
            if len(res) > 1 and res[0] == '+':
                dirt += int(res[1:])
        if dirt == 0:
            return 0
        return dirt / (dirt + self.total)
        
    def try_problems(self):
        res = 0
        for prob_res in self.problem_results:
            if len(prob_res) > 0 and (prob_res[0] == '+' or prob_res[0] == '-' or prob_res[0] == '?'):
                res += 1
        return res
        
    def write(self, place, open_times, problem_openers, team_members, identification, f):
        print('<tr class="participant_result">', file=f)
        print('<td class="st_place"><input style="width: 100%; outline: none; border:none" readonly type="text" value={}></input></td>'.format(place), file=f)
        team_title = self.name
        if self.name in team_members:
            team_title = team_members[self.name]
        updated_name = team_identifier.identify(self.name, identification)
        print('<td class="st_team" title="{}" ondblclick="team_dblclick(event)">{}</td>'.format(team_title, updated_name), file=f)
        print('<td class="st_extra">{}</td>'.format(self.region), file=f)
        for prob_res, prob_time, open_time, problem_opener in zip(self.problem_results, self.problem_times, open_times, problem_openers):
            background = ''
            if len(prob_res) > 0:
                if prob_res[0] == '+':
                    background = '#e0ffe0'
                    if (problem_opener == '' and prob_time == open_time) or self.name == problem_opener:
                        background = '#b0ffb0'
                elif prob_res[0] == '-':
                    background = '#ffd0d0'
            if background != '':
                background = 'background: ' + background
            print('<td style="{}" class="st_prob">{}'.format(background, prob_res, prob_time), end='', file=f)
            if prob_time != '':
                print('<div class="st_time">{}</div>'.format(prob_time), end='', file=f)
            print('</td>', file=f)
        print('<td class="st_total"><input style="width: 100%; outline: none; border:none" readonly type="text" value={}></input></td>'.format(self.total), file=f)
        print('<td class="st_pen"><input style="width: 100%; outline: none; border:none" readonly type="text" value={}></input></td>'.format(self.penalty), file=f)
        print('<td class="st_pen"><input style="width: 100%; outline: none; border:none" readonly type="text" value={:.2f}></input></td>'.format(self.get_dirt()), file=f)
        print('</tr>', file=f)
        print(file=f)
        
        
class Standings:
    def __init__(self, show_regions, ignore_regions):
        self.show_regions = show_regions
        self.ignore_regions = ignore_regions
        self.all_results = []
        self.problem_openers = None
        
    def set_meta_information(self, title, contest_duration, problems, path_to_scripts, identification):
        self.title = title
        self.contest_duration = contest_duration
        self.problems = problems
        self.path_to_scripts = path_to_scripts
        self.identification = identification
        
        self.problem_ids = [chr(ord('A') + problem_id) for problem_id in range(problems)]
        self.problem_names = ['' for problem_id in range(problems)]
        self.team_members = {}
        self.penalty_points = 20
        self.max_length_place = '7771777'
        
    def set_problem_openers(self, problem_openers):
        self.problem_openers = problem_openers
    
    def add(self, result):
        self.all_results.append(result)
        
    def sort(self):
        self.all_results = sorted(self.all_results)
    
    def get_problem_title(self, problem_id):
        if problem_id < len(self.problem_names):
            if self.problem_names[problem_id] == '':
                return self.problem_ids[problem_id]
            return self.problem_ids[problem_id] + ' - ' + self.problem_names[problem_id]
        return ''
    
    
    def get_total(self):
        total = [0] * self.problems
        for res in self.all_results:
            for num, prob_res in enumerate(res.problem_results):
                if len(prob_res) == 0:
                    continue
                if prob_res[0] == '+':
                    total[num] += 1
                    if len(prob_res) > 1:
                        total[num] += int(prob_res[1:])
                elif prob_res[0] == '-':
                    total[num] += int(prob_res[1:])
        total.append(sum(total))
        return total
    
    def get_ok(self):
        total = [0] * self.problems
        for res in self.all_results:
            for num, prob_res in enumerate(res.problem_results):
                if len(prob_res) == 0:
                    continue
                if prob_res[0] == '+':
                    total[num] += 1
        total.append(sum(total))
        return total
        
    def write_stats(self, f):
        print('<tr class="submissions_statistic">', file=f)
        print('<td class="st_place"><output style="color: transparent">{}</output></td>'.format(self.max_length_place), file=f)
        print('<td class="st_team">Submissions:</td>', file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        for problem_id, x in enumerate(self.get_total()):
            print('<td title="{}" class="st_prob">{}</td>'.format(self.get_problem_title(problem_id), x), file=f)
        print('<td class="st_pen"><output style="color: transparent">9999</output></td>', file=f)
        print('<td class="st_pen"><output style="color: transparent">0.99</output></td>', file=f)
        print('</tr>', file=f)
        
        print('<tr class="submissions_statistic">', file=f)
        print('<td class="st_place"></td>', file=f)
        print('<td class="st_team">Accepted:</td>', file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        for problem_id, x in enumerate(self.get_ok()):
            print('<td title="{}" class="st_prob">{}</td>'.format(self.get_problem_title(problem_id), x), file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        print('</tr>', file=f)
        
        print('<tr class="submissions_statistic">', file=f)
        print('<td class="st_place">&nbsp;</td>', file=f)
        print('<td class="st_team">%:</td>', file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        for problem_id, (total, ok) in enumerate(zip(self.get_total(), self.get_ok())):
            perc = 0
            if total > 0:
                perc = 100 * ok / total
            print('<td title="{}" class="st_prob">{:.0f}%</td>'.format(self.get_problem_title(problem_id), perc), file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        print('<td class="st_team">&nbsp;</td>', file=f)
        print('</tr>', file=f)
        
    def get_region_statistic(self, region):
        teams = 0
        problems_solved = 0
        sum_place = 0
        solved_by_twentiest_team = 0
        for place, result in enumerate(self.all_results):
            if result.region == region or region == 'All':
                teams += 1
                if teams <= statistic_team_number:
                    problems_solved += result.total
                    sum_place += place + 1
                if teams <= statistic_team_number:
                    solved_by_twentiest_team = result.total
        return region, teams, problems_solved / min(statistic_team_number, max(1, teams)), sum_place / min(statistic_team_number, max(1, teams)), solved_by_twentiest_team
        
    def write_regions(self, f):
        print('''<table class="region_statistic" width="50%"> <tr> <th>Show</th> <th>Region</th><th>Teams</th> <th>Average problems solved by top {} teams</th> <th>Average place taken by top {} teams</th> <th>Problems solved by {}<sup>th</sup> team </th> </tr>'''.format(statistic_team_number, statistic_team_number, statistic_team_number), file=f)
        regions = set()
        for result in self.all_results:
            regions.add(result.region)
        all_regions = []
        all_teams = 0
        for region in regions:
            all_regions.append(self.get_region_statistic(region))
        all_regions = sorted(all_regions, key=lambda region: region[3])
        all_regions.append(self.get_region_statistic('All'))
        for region in all_regions:
            if region[0] == '':
                pass
                #continue
            print('<tr class="row_region">', file=f)
            if region[0] == 'All':
                print('<td class="st_region" id="region_all" align="center"> <input type="checkbox" checked onchange="checkAll()"> </input> </td>', file=f)
            else:
                print('<td class="st_region" align="center"> <input type="checkbox" checked onchange="filter()"> </input> </td>', file=f)
            print('<td class="st_region" align="center">{}</td>'.format(region[0]), file=f)
            print('<td class="st_region" align="center">{}</td>'.format(region[1]), file=f)
            print('<td class="st_region" align="center">{:.1f}</td>'.format(region[2]), file=f)
            print('<td class="st_region" align="center">{:.1f}</td>'.format(region[3]), file=f)
            print('<td class="st_region" align="center">{}</td>'.format(region[4]), file=f)
            print('</tr>', file=f)
        print('</table>', file=f)
        
    def write(self, f):
        print('<div id="standingsSettings"><!--', file=f)
        print('contestDuration {}'.format(self.contest_duration), file=f)
        print('--></div>', file=f)
        
        print('<title>Contest standings</title>', file=f)
        print('{{% assets output="gen/interactive_standings.css", "{}styles/unpriv.css", "{}styles/unpriv3.css", "{}styles/animate.css", "{}styles/styles.css", "{}styles/cf_styles.css" %}}'.format(self.path_to_scripts, self.path_to_scripts, self.path_to_scripts, self.path_to_scripts, self.path_to_scripts), file=f)
        print('<link rel="stylesheet" href="{{ ASSET_URL }}">', file=f)
        print('{% endassets %}', file=f)
        
        print('<style id="styles"> table.standings td { height: 40px; } </style>', file=f)
            
        print('<body onload=loadResults()>', file=f)
        print('{{% assets output="gen/interactive_standings.js", "third-party/js/Chart.bundle.min.js", "{}scripts/jquery.js", "{}scripts/filter_regions.js", "{}scripts/animate.js", "{}scripts/parse_submissions.js", "{}scripts/team_statistic.js"  %}}'.format(self.path_to_scripts, self.path_to_scripts, self.path_to_scripts, self.path_to_scripts, self.path_to_scripts), file=f)
        print('<script type="text/javascript" src="{{ ASSET_URL }}"></script>', file=f)
        print('{% endassets %}', file=f)
        
        print('<div id="main-cont">', file=f)
        print('<div id="container">', file=f)
        print(self.title, file=f)
        print('<div id="l13">', file=f)
        print('<div class="l14" id="contestTable" />', file=f)
        if self.show_regions:
            self.write_regions(f)
        
        #contest managing
        print('<table class="region_statistic" width="50%"> <tr> <th> Start time </th> <th> Contest speed </th> <th>Penalty for wrong submission</th> <th> Start the contest </th> <th> Finish the contest </th> <th> Suspend the contest </th> </tr>', file=f)
        print('<tr>', file=f)
        print('<td class="st_region" align="center"> <input type="text" id="contest_start_time" value="0:00:00" maxlength=7 style="width:100%"> </input> </td>', file=f)
        print('<td class="st_region" align="center"> <input type="range" id="contest_speed" min="1" max="60" value="10"> </input> </td>', file=f)
        print('<td class="st_region" align="center"> <input style="width: 50px" type="number" id="penalty_points" min="1" max="20" value="{}"> </input> </td>'.format(self.penalty_points), file=f)
        print('<td class="st_region" align="center"> <button onclick=go()> Start </button> </td>', file=f)
        print('<td class="st_region" align="center"> <button disabled="true" onclick=finish()> Finish </button> </td>', file=f)
        print('<td class="st_region" align="center"> <button disabled="true" id="pause" onclick=pause()>Pause</button> </td>', file=f)
        print('</tr>', file=f)
        print('</table>', file=f)

        print('<center style="font-size: 25px" id="standings_time"> Standings [{}] </center>'.format(get_time_str(self.contest_duration)), file=f)
        
        print('<input type="range" min="0" max="{}" value="{}" class="slider" id="slider" oninput="updateSliderFill()" onchange="updateSliderFill()" onmousedown="sliderMouseDown()" onmouseup="sliderMouseUp()">'.format(self.contest_duration, self.contest_duration), file=f)
        
        print('<table style="border-collapse: separate; border-spacing: 1px;" width="100%" class="standings">', file=f)
        print('<tr>', file=f)
        print('<th class="st_place">{}</th>'.format('Place'), file=f)
        print('<th class="st_team" style="min-width: 185px">{}</th>'.format('User'), file=f)
        print('<th class="st_extra">{}</th>'.format('Region'), file=f)
        for prob_id in range(self.problems):
            print('<th title="{}" class="st_prob" style="min-width: 32px">{}</th>'.format(self.get_problem_title(prob_id), self.problem_ids[prob_id]), file=f)
        print('<th  class="st_total">{}</th>'.format('Total'), file=f)
        print('<th  class="st_pen">{}</th>'.format('Penalty'), file=f)
        print('<th  class="st_pen">{}</th>'.format('Dirt'), file=f)
        print('</tr>', file=f)
        open_times = ['(9:99)' for i in range(self.problems)]
        for place, result in enumerate(self.all_results):
            num = 0
            for prob_res, prob_time in zip(result.problem_results, result.problem_times):
                if len(prob_res) > 0 and prob_res[0] == '+':
                    open_times[num] = min(open_times[num], prob_time)
                num += 1
        places = []
        real_place = 0
        cur_res = 0
        while cur_res < len(self.all_results):
            start_real_place = real_place
            cur = cur_res
            while cur < len(self.all_results) and (self.all_results[cur].region in self.ignore_regions or (self.all_results[cur].total == self.all_results[cur_res].total and self.all_results[cur].penalty == self.all_results[cur_res].penalty)):
                if self.all_results[cur].region not in self.ignore_regions:
                    real_place += 1
                cur += 1
            place = str(start_real_place + 1)
            if start_real_place + 1 != real_place:
                place += '-' + str(real_place)
            for i in range(cur_res, cur):
                places.append(place)
            cur_res = cur
            
        place = 0
        for place, result in zip(places, self.all_results):
            if result.region in self.ignore_regions:            
                result.write('-', open_times, self.problem_openers, self.team_members, self.identification, f)
            else:
                result.write(place, open_times, self.problem_openers, self.team_members, self.identification, f)
            if True:
                num = 0
                for prob_res, prob_time in zip(result.problem_results, result.problem_times):
                    if len(prob_res) > 0 and prob_res[0] == '+' and open_times[num] == prob_time:
                        open_times[num] = '(9:99)'
                    num += 1
        self.write_stats(f)
        print('</table>', file=f)
        print('</div>', file=f)
        print('</div>', file=f)
        print('</div>', file=f)
        print('</div>', file=f)