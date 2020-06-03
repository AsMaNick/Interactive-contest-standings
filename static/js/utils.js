function isDigit(c) {
    return '0' <= c && c <= '9';
}

function isLetter(c) {
    return ('a' <= c && c <= 'z') || ('A' <= c && c <= 'Z');
}

function capitalize(s) {
    return s[0].toUpperCase() + s.substr(1);
}

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

function getError(s, name, min_length = 2, max_length = 50) {
    if (s == '') {
        return 'This field may not be blank';
    }
    if (s.length < min_length) {
        return name + ' should contain at least ' + min_length + ' characters';
    }
    if (s.length > max_length) {
        return name + ' should contain no more than ' + max_length + ' characters';
    }
    var ok_c = '_-@!#:/?&.,= ';
    for (var c of s) {
        if (isDigit(c) || isLetter(c) || ok_c.includes(c)) {
            continue;
        }
        return name + ' should consists of only latin letters, digits or sybmols "' + ok_c + '"';
    }
    return '';
}