function getPlaceOverTime(submissions_data, team_id, times) {
    var all_results = []
    for (var i = 0; i < submissions_data.n_teams; ++i) {
        all_results.push(new Result(-1));
    }
    var places = [];
    var cur = 0;
    for (var cur_time of times) {
        while (cur < submissions_data.all_submissions.length && submissions_data.all_submissions[cur].time <= '(' + cur_time + ')') {
            var id = submissions_data.all_submissions[cur].id;
            var time = submissions_data.all_submissions[cur].time;
            var submission_result = submissions_data.all_submissions[cur].result;
            var problem_id = submissions_data.all_submissions[cur].problem_id;
            all_results[id].submissions += 1;
            if (submission_result[0] == '+') {
                all_results[id].total += 1;
                all_results[id].penalty += timeInMinutes(time);
                if (submission_result.length > 1) {
                    all_results[id].penalty += contest_penalty * parseInt(submission_result.substr(1));
                    all_results[id].dirt_submissions += parseInt(submission_result.substr(1));
                }
            }
            ++cur;
        }
        var place = 1;
        for (var i = 0; i < all_results.length; ++i) {
            if (i != team_id && compareResultByTotal(all_results[i], all_results[team_id]) == -1) {
                ++place;
            }
        }
        places.push(place);
    }
    return places;
}

function team_dblclick(event) {
    if (!loaded) {
        console.log('Page is not loaded yet');
        return;
    }
    var elem = event.target;
    var team_id = getTeamId(elem);
    var div_team_statistic = $('<div id="team_statistic" class="team_statistic" style="top: ' + (50 + event.pageY - event.clientY).toString() + '"><canvas id="place_over_time_chart"></canvas></div>');
    $('#main-cont').append(div_team_statistic);
    $('#container').addClass('disabled_content');
    buildChart(team_id);
}

function buildChart(team_id) {
    var duration = getContestDuration();
    var labels = [];
    for (var i = 0; i <= duration; ++i) {
        labels.push(parseInt(i / 60) + ':' + String(i % 60).padStart(2, '0'));
    }
    var submissions_data = getSubmissionsData();
    var places = getPlaceOverTime(submissions_data, team_id, labels);

    var context = document.getElementById('place_over_time_chart').getContext('2d');
    var myChart = new Chart(context, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Place over time',
                pointRadius: 2,
                data: places,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function(value, index, values) {
                            if (Math.abs(value - parseInt(value) > 0.0001)) {
                                return '';
                            }
                            return value;
                        }
                    }
                }],
                xAxes: [{
                    ticks: {
                        callback: function(value, index, values) {
                            return value;
                        },
                        maxTicksLimit: 20
                    }
                }]
            }
        }
    });
}

function getTeamId(elem) {
    var id = -1;
    for (var i = 0; i < all_teams_elem.length; ++i) {
        if (all_teams_elem[i].hidden) {
            continue;
        }
        id += 1;
        if (all_teams_elem[i].getElementsByClassName('st_team')[0] == elem) {
            return id;
        }
    }
    return -1;
}

function getSubmissionsData() {
    var all_submissions = [];
    var id = -1;
    if (document.getElementById('submissionsLog') === null) {
        for (var i = 0; i < all_teams_elem.length; ++i) {
            if (all_teams_elem[i].hidden) {
                continue;
            }
            id += 1;
            var probs = all_teams_elem[i].getElementsByClassName('st_prob');
            var all_ac_times = [];
            var all_was = [];
            for (var j = 0; j < probs.length; ++j) {
                var last_time = contest_duration - 1;
                var prob_res = getSubmissionResult(probs[j]);
                if (getTime(probs[j]) != '(9:99)') {
                    all_submissions.push(new Submission(id, j,
                                                        getTime(probs[j]), 
                                                        prob_res, 
                                                        probs[j].style.background == 'rgb(176, 255, 176)', 
                                                        probs[j]));
                    last_time = Math.max(0, timeInMinutes(getTime(probs[j])) - 1);
                    all_ac_times.push(timeInMinutes(getTime(probs[j])));
                }
                if (prob_res.length > 1 && (prob_res[0] == '+' || prob_res[0] == '-')) {
                    var wa = parseInt(prob_res.substr(1));
                    all_was.push([last_time, wa, j, probs[j]]);
                }
            }
            all_ac_times.sort(function(x, y) { return x - y; } );
            all_was.sort(function(x, y) { return x[0] - y[0]; } );
            var pos_ac = 0;
            for (var j = 0; j < all_was.length; ++j) {
                var last_time = all_was[j][0];
                var wa = all_was[j][1];
                var problem_id = all_was[j][2];
                var elem = all_was[j][3];
                while (pos_ac < all_ac_times.length && all_ac_times[pos_ac] <= last_time) {
                    ++pos_ac;
                }
                var pos_from = pos_ac - 2;
                if (last_time == contest_duration - 1) {
                    --pos_from;
                }
                var from_time = 0;
                if (pos_from >= 0) {
                    from_time = all_ac_times[pos_from];
                }
                var rnds;
                if (last_time == contest_duration - 1) {
                    rnds = new Array(wa + 1);
                    rnds[0] = 0;
                    for (var k = 1; k <= wa; ++k) {
                        rnds[k] = (Math.random() - 0.5) * 0.2
                    }
                    rnds.sort(function(a, b) { return a - b; });
                }
                for (var k = 1; k <= wa; ++k) {
                    var coef = k / (k + 1);
                    if (last_time == contest_duration - 1) {
                        coef += rnds[k];
                        coef = Math.max(coef, 0);
                        coef = Math.min(coef, 1);
                    }
                    var time = parseInt(from_time + (last_time - from_time) * coef);
                    all_submissions.push(new Submission(id, problem_id,
                                                        timeInStr(time), 
                                                        '-' + k.toString(), 
                                                        false, 
                                                        elem));
                }
            }
        }
        all_submissions.sort(compareSubmissionByTime);
    }
    return {
        all_submissions: all_submissions,
        n_teams: id + 1
    }
}

window.addEventListener('click', function(e) { 
    var elem = document.getElementById('team_statistic');
    if (!elem) {
        return;
    }
    if (!elem.contains(e.target)){
        elem.remove();
        $('#container').removeClass('disabled_content');
    }
});