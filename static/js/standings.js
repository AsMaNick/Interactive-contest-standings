function checkSeason(season) {
    if (season.length != 9) {
        return false;
    }
    var y1 = parseInt(season.substr(0, 4));
    var y2 = parseInt(season.substr(5));
    if (isNaN(y1) || isNaN(y2)) {
        return false;
    }
    return y1 + 1 == y2;
}

function checkDate(date) {
    if (date.length != 10) {
        return false;
    }
    var y = parseInt(date.substr(0, 4));
    var m = parseInt(date.substr(5, 2));
    var d = parseInt(date.substr(8));
    console.log(d, m, y);
    if (isNaN(d) || isNaN(m) || isNaN(y)) {
        return false;
    }
    return 1 <= d && d <= 31 && 1 <= m && m <= 12 && 1000 <= y && y <= 9999;
}

function createStandings() {
    var season = $('#season_input').val();
    var date = $('#date_input').val();
    var title = $('#title_input').val();
    var venue = $('#venue_input').val();
    var link = $('#link_input').val();
    var duration = $('#duration_select').val();
    var identification = $('#identification_select').val();
    var has_error = false;
    if (!checkSeason(season)) {
        has_error |= setError('#season_div', 'Season should have format yyyy-yyyy');
    } else {
        setError('#season_div', '');
    }
    if (!checkDate(date)) {
        has_error |= setError('#date_div', 'Date should have format dd-mm-yyyy');
    } else {
        setError('#date_div', '');
    }
    has_error |= setError('#title_div', getError(title, 'Title'));
    has_error |= setError('#venue_div', getError(venue, 'Venue'));
    has_error |= setError('#link_div', getError(link, 'Link', 2, 256));
    if (has_error) {
        return;
    }
    var logos = $("#logo_input").prop("files");    
    var form_data = new FormData();
	form_data.append('season', season);
	form_data.append('date', date);
	form_data.append('title', title);
	form_data.append('venue', venue);
	form_data.append('link', link);
	form_data.append('duration', duration);
	form_data.append('identification', identification);
	if (logos.length > 0) {
		form_data.append('logo', logos[0]);
	}
    console.log(form_data);
    $.ajax('http://' + document.domain + ':' + location.port + '/api/standings/create', {
        data: form_data,
        processData: false,
        contentType: false,
        cache: false,
        enctype: 'multipart/form-data',
        type: 'POST', 
        success: function (data) {
            if (data.status == 'ok') {
                document.location.href = 'http://' + document.domain + ':' + location.port + '/standings/my';
            } else {
                setError('#link_div', capitalize(data.status));
            }
        }
    });
}