$(document).ready(() => {
    const max = 200;
    let tot; let
str;
    $('.lighter').each(function () {
    str = String($(this).html());
    tot = str.length;
    str = (tot <= max)
    ? str
    : `${str.substring(0, (max + 1))}...`;
    $(this).html(str);
    });
});
