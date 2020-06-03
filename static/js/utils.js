function isDigit(c) {
    return '0' <= c && c <= '9';
}

function isLetter(c) {
    return ('a' <= c && c <= 'z') || ('A' <= c && c <= 'Z');
}

function capitalize(s) {
    return s[0].toUpperCase() + s.substr(1);
}
