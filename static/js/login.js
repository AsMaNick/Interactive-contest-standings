function setError(id, error) {
    $(id + ' .help-block').text(error);
    if (error == '') {
        $(id).removeClass('has-error');
        return false;
    } else {
        $(id).addClass('has-error');
        return true;
    }
}

function getError(s, name) {
    if (s == '') {
        return 'This field may not be blank';
    }
    if (s.length < 2) {
        return name + ' should contain at least 2 characters';
    }
    if (s.length > 50) {
        return name + ' should contain no more than 50 characters';
    }
    for (var c of s) {
        if (isDigit(c) || isLetter(c) || ['_', '-', '@', '!', '#'].includes(c)) {
            continue;
        }
        return name + ' should consists of only latin letters, digits or sybmols "_-@!#"';
    }
    return '';
}

function signUp() {
    var username = $('#username_input').val();
    var firstname = $('#firstname_input').val();
    var secondname = $('#secondname_input').val();
    var password = $('#password_input').val();
    var repeat_password = $('#repeat_password_input').val();
    var has_error = false;
    has_error |= setError('#username_div', getError(username, 'Username'));
    has_error |= setError('#firstname_div', getError(firstname, 'First name'));
    has_error |= setError('#secondname_div', getError(secondname, 'Second name'));
    has_error |= setError('#password_div', getError(password, 'Password'));
    if (password != repeat_password) {
        has_error |= setError('#repeat_password_div', 'Passwords don\'t match');
    } else {
        setError('#repeat_password_div', '');
    }
    if (has_error) {
        return;
    }
    var data = {
        username: username,
        firstname: firstname,
        secondname: secondname,
        password: password
    };
    $.ajax('http://' + document.domain + ':' + location.port + '/api/signup', {
        data: JSON.stringify(data),
        contentType: 'application/json',
        type: 'POST', success: function (data) {
            if (data.status == 'ok') {
                document.location.href = 'http://' + document.domain + ':' + location.port + '/home';
            } else {
                setError('#username_div', capitalize(data.status));
            }
        }
    });
}

function login() {
    var username = $('#username_input').val();
    var password = $('#password_input').val();
    var has_error = false;
    has_error |= setError('#username_div', getError(username, 'Username'));
    has_error |= setError('#password_div', getError(password, 'Password'));
    if (has_error) {
        return;
    }
    var data = {
        username: username,
        password: password
    };
    $.ajax('http://' + document.domain + ':' + location.port + '/api/login', {
        data: JSON.stringify(data),
        contentType: 'application/json',
        type: 'POST', success: function (data) {
            if (data.status == 'ok') {
                document.location.href = 'http://' + document.domain + ':' + location.port + '/home';
            } else {
                setError('#password_div', capitalize(data.status));
            }
        }
    });
}