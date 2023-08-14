(function (factory) {
    if (typeof define === 'function' && define.amd) {
        define(['jquery'], factory);
    } else if (typeof exports !== 'undefined') {
        module.exports = factory(require('jquery'));
    } else {
        factory(jQuery);
    }
}(($) => {
    let EvoCalendar = window.EvoCalendar || {};

    EvoCalendar = (function () {
        let instanceUid = 0;
        function EvoCalendar(element, settings) {
            const _ = this;
            _.defaults = {
                theme: null,
                format: 'mm/dd/yyyy',
                titleFormat: 'MM yyyy',
                eventHeaderFormat: 'MM d, yyyy',
                firstDayOfWeek: 0,
                language: 'en',
                todayHighlight: false,
                sidebarDisplayDefault: true,
                sidebarToggler: true,
                eventDisplayDefault: true,
                eventListToggler: true,
                calendarEvents: null,
            };
            _.options = $.extend({}, _.defaults, settings);

            _.initials = {
                default_class: $(element)[0].classList.value,
                validParts: /dd?|DD?|mm?|MM?|yy(?:yy)?/g,
                dates: {
                    en: {
                        days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                        daysShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                        daysMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
                        months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                        monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        noEventForToday: 'No event for today.. so take a rest! :)',
                        noEventForThisDay: 'No event for this day.. so take a rest! :)',
                        previousYearText: 'Previous year',
                        nextYearText: 'Next year',
                        closeSidebarText: 'Close sidebar',
                        closeEventListText: 'Close event list',
                    },
                    es: {
                        days: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                        daysShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
                        daysMin: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
                        months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                        monthsShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                        noEventForToday: 'No hay evento para hoy.. ¡así que descanse! :)',
                        noEventForThisDay: 'Ningún evento para este día.. ¡así que descanse! :)',
                        previousYearText: 'Año anterior',
                        nextYearText: 'El próximo año',
                        closeSidebarText: 'Cerrar la barra lateral',
                        closeEventListText: 'Cerrar la lista de eventos',
                    },
                    de: {
                        days: ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'],
                        daysShort: ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'],
                        daysMin: ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'],
                        months: ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
                        monthsShort: ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
                        noEventForToday: 'Keine Veranstaltung für heute.. also ruhen Sie sich aus! :)',
                        noEventForThisDay: 'Keine Veranstaltung für diesen Tag.. also ruhen Sie sich aus! :)',
                        previousYearText: 'Vorheriges Jahr',
                        nextYearText: 'Nächstes Jahr',
                        closeSidebarText: 'Schließen Sie die Seitenleiste',
                        closeEventListText: 'Schließen Sie die Ereignisliste',
                    },
                    pt: {
                        days: ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado'],
                        daysShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
                        daysMin: ['Do', '2a', '3a', '4a', '5a', '6a', 'Sa'],
                        months: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
                        monthsShort: ['Jan', 'Feb', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                        noEventForToday: 'Nenhum evento para hoje.. então descanse! :)',
                        noEventForThisDay: 'Nenhum evento para este dia.. então descanse! :)',
                        previousYearText: 'Ano anterior',
                        nextYearText: 'Próximo ano',
                        closeSidebarText: 'Feche a barra lateral',
                        closeEventListText: 'Feche a lista de eventos',
                    },
                    fr: {
                        days: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
                        daysShort: ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'],
                        daysMin: ['Di', 'Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa'],
                        months: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
                        monthsShort: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc'],
                        noEventForToday: "Rien pour aujourd'hui... Belle journée :)",
                        noEventForThisDay: 'Rien pour ce jour-ci... Profite de te réposer :)',
                        previousYearText: 'Année précédente',
                        nextYearText: "L'année prochaine",
                        closeSidebarText: 'Fermez la barre latérale',
                        closeEventListText: 'Fermer la liste des événements',
                    },
                    nl: {
                        days: ['Zondag', 'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag'],
                        daysShort: ['Zon', 'Maan', 'Din', 'Woe', 'Don', 'Vrij', 'Zat'],
                        daysMin: ['Zo', 'Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za'],
                        months: ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'],
                        monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'],
                        noEventForToday: 'Geen event voor vandaag.. dus rust even uit! :)',
                        noEventForThisDay: 'Geen event voor deze dag.. dus rust even uit! :)',
                        previousYearText: 'Vorig jaar',
                        nextYearText: 'Volgend jaar',
                        closeSidebarText: 'Sluit de zijbalk',
                        closeEventListText: 'Sluit de event lijst',
                    },
                },
            }
            _.initials.weekends = {
                sun: _.initials.dates[_.options.language].daysShort[0],
                sat: _.initials.dates[_.options.language].daysShort[6],
            }

            // Format Calendar Events into selected format
            if (_.options.calendarEvents != null) {
                for (let i = 0; i < _.options.calendarEvents.length; i++) {
                    // If event doesn't have an id, throw an error message
                    if (!_.options.calendarEvents[i].id) {
                        console.log(`%c Event named: "${_.options.calendarEvents[i].name}" doesn't have a unique ID `, 'color:white;font-weight:bold;background-color:#e21d1d;');
                    }
                    if (_.isValidDate(_.options.calendarEvents[i].number_on)) {
                        _.options.calendarEvents[i].number_on = _.formatDate(_.options.calendarEvents[i].number_on, _.options.format)
                    }
                }
            }

            // Global variables
            _.startingDay = null;
            _.monthLength = null;
            _.windowW = $(window).width();

            // CURRENT
            _.$current = {
                month: (
                    isNaN(this.month) || this.month == null
                ) ? new Date().getMonth() : this.month,
                year: (
                    isNaN(this.year) || this.year == null
                ) ? new Date().getFullYear() : this.year,
                number_on: _.formatDate(`${_.initials.dates[_.defaults.language].months[new Date().getMonth()]} ${new Date().getDate()} ${new Date().getFullYear()}`, _.options.format),
            }

            // ACTIVE
            _.$active = {
                month: _.$current.month,
                year: _.$current.year,
                number_on: _.$current.number_on,
                event_date: _.$current.number_on,
                events: [],
            }

            // LABELS
            _.$label = {
                days: [],
                months: _.initials.dates[_.defaults.language].months,
                days_in_month: [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
            }

            // HTML Markups (template)
            _.$markups = {
                calendarHTML: '',
                mainHTML: '',
                sidebarHTML: '',
                eventHTML: '',
            }
            // HTML DOM elements
            _.$elements = {
                calendarEl: $(element),
                innerEl: null,
                sidebarEl: null,
                eventEl: null,

                sidebarToggler: null,
                eventListToggler: null,

                activeDayEl: null,
                activeMonthEl: null,
                activeYearEl: null,
            }
            _.$breakpoints = {
                tablet: 768,
                mobile: 425,
            }
            _.$UI = {
                hasSidebar: true,
                hasEvent: true,
            }

            _.formatDate = $.proxy(_.formatDate, _);
            _.selectDate = $.proxy(_.selectDate, _);
            _.selectMonth = $.proxy(_.selectMonth, _);
            _.selectYear = $.proxy(_.selectYear, _);
            _.selectEvent = $.proxy(_.selectEvent, _);
            _.toggleSidebar = $.proxy(_.toggleSidebar, _);
            _.toggleEventList = $.proxy(_.toggleEventList, _);

            _.instanceUid = instanceUid++;

            _.init(true);
        }

        return EvoCalendar;
    }());

    // v1.0.0 - Initialize plugin
    EvoCalendar.prototype.init = function (init) {
        const _ = this;

        if (!$(_.$elements.calendarEl).hasClass('calendar-initialized')) {
            $(_.$elements.calendarEl).addClass('evo-calendar calendar-initialized');
            if (_.windowW <= _.$breakpoints.tablet) { // tablet/mobile
                _.toggleSidebar(false);
                _.toggleEventList(false);
            } else {
                if (!_.options.sidebarDisplayDefault) _.toggleSidebar(false);
                else _.toggleSidebar(true);

                if (!_.options.eventDisplayDefault) _.toggleEventList(false);
                else _.toggleEventList(true);
            }
            if (_.options.theme) _.setTheme(_.options.theme); // set calendar theme
            _.buildTheBones(); // start building the calendar components
        }
    };
    // v1.0.0 - Destroy plugin
    EvoCalendar.prototype.destroy = function () {
        const _ = this;
        // code here
        _.destroyEventListener();
        if (_.$elements.calendarEl) {
            _.$elements.calendarEl.removeClass('calendar-initialized');
            _.$elements.calendarEl.removeClass('evo-calendar');
            _.$elements.calendarEl.removeClass('sidebar-hide');
            _.$elements.calendarEl.removeClass('event-hide');
        }
        _.$elements.calendarEl.empty();
        _.$elements.calendarEl.attr('class', _.initials.default_class);
        $(_.$elements.calendarEl).trigger('destroy', [_])
    }

    // v1.0.0 - Limit title (...)
    EvoCalendar.prototype.limitTitle = function (title, limit) {
        const newTitle = [];
        limit = limit === undefined ? 18 : limit;
        if ((title).split(' ').join('').length > limit) {
            const t = title.split(' ');
            for (let i = 0; i < t.length; i++) {
                if (t[i].length + newTitle.join('').length <= limit) {
                    newTitle.push(t[i])
                }
            }
            return `${newTitle.join(' ')}...`
        }
        return title;
    }

    // v1.1.2 - Check and filter strings
    EvoCalendar.prototype.stringCheck = function (d) {
        return d.replace(/[^\w]/g, '\\$&');
    }

    // v1.0.0 - Parse format (date)
    EvoCalendar.prototype.parseFormat = function (format) {
        const _ = this;
        if (typeof format.toValue === 'function' && typeof format.toDisplay === 'function') { return format; }
        // IE treats \0 as a string end in inputs (truncating the value),
        // so it's a bad format delimiter, anyway
        const separators = format.replace(_.initials.validParts, '\0').split('\0');
            const parts = format.match(_.initials.validParts);
        if (!separators || !separators.length || !parts || parts.length === 0) {
            console.log('%c Invalid date format ', 'color:white;font-weight:bold;background-color:#e21d1d;');
        }
        return { separators, parts };
    };

    // v1.0.0 - Format date
    EvoCalendar.prototype.formatDate = function (number_on, format, language) {
        const _ = this;
        if (!number_on) { return ''; }
        language = language || _.defaults.language
        if (typeof format === 'string') { format = _.parseFormat(format); }
        if (format.toDisplay) { return format.toDisplay(number_on, format, language); }

        const ndate = new Date(number_on);
        // if (!_.isValidDate(ndate)) { // test
        //     ndate = new Date(date.replace(/-/g, '/'))
        // }

        const val = {
            d: ndate.getDate(),
            D: _.initials.dates[language].daysShort[ndate.getDay()],
            DD: _.initials.dates[language].days[ndate.getDay()],
            m: ndate.getMonth() + 1,
            M: _.initials.dates[language].monthsShort[ndate.getMonth()],
            MM: _.initials.dates[language].months[ndate.getMonth()],
            yy: ndate.getFullYear().toString().substring(2),
            yyyy: ndate.getFullYear(),
        };

        val.dd = (val.d < 10 ? '0' : '') + val.d;
        val.mm = (val.m < 10 ? '0' : '') + val.m;
        number_on = [];
        const seps = $.extend([], format.separators);
        for (let i = 0, cnt = format.parts.length; i <= cnt; i++) {
            if (seps.length) { number_on.push(seps.shift()); }
            number_on.push(val[format.parts[i]]);
        }
        return number_on.join('');
    };

    // v1.0.0 - Get dates between two dates
    EvoCalendar.prototype.getBetweenDates = function (dates) {
        const _ = this; const
betweenDates = [];
        for (let x = 0; x < _.monthLength; x++) {
            const active_date = _.formatDate(`${_.$label.months[_.$active.month]} ${x + 1} ${_.$active.year}`, _.options.format);
            if (_.isBetweenDates(active_date, dates)) {
                betweenDates.push(active_date);
            }
        }
        return betweenDates;
    };

    // v1.0.0 - Check if date is between the passed calendar date
    EvoCalendar.prototype.isBetweenDates = function (active_date, dates) {
        let sd; let
ed;
        if (dates instanceof Array) {
            sd = new Date(dates[0]);
            ed = new Date(dates[1]);
        } else {
            sd = new Date(dates);
            ed = new Date(dates);
        }
        if (sd <= new Date(active_date) && ed >= new Date(active_date)) {
            return true;
        }
        return false;
    }

    // v1.0.0 - Check if event has the same event type in the same date
    EvoCalendar.prototype.hasSameDayEventType = function (number_on, type_on) {
        const _ = this; let
eventLength = 0;

        for (let i = 0; i < _.options.calendarEvents.length; i++) {
            if (_.options.calendarEvents[i].number_on instanceof Array) {
                const arr = _.getBetweenDates(_.options.calendarEvents[i].number_on);
                for (let x = 0; x < arr.length; x++) {
                    if (number_on === arr[x] && type_on === _.options.calendarEvents[i].type_on) {
                        eventLength++;
                    }
                }
            } else if (number_on === _.options.calendarEvents[i].number_on && type_on === _.options.calendarEvents[i].type_on) {
                    eventLength++;
                }
        }

        if (eventLength > 0) {
            return true;
        }
        return false;
    }

    // v1.0.0 - Set calendar theme
    EvoCalendar.prototype.setTheme = function (themeName) {
        const _ = this;
        const prevTheme = _.options.theme;
        _.options.theme = themeName.toLowerCase().split(' ').join('-');

        if (_.options.theme) $(_.$elements.calendarEl).removeClass(prevTheme);
        if (_.options.theme !== 'default') $(_.$elements.calendarEl).addClass(_.options.theme);
    }

    // v1.0.0 - Called in every resize
    EvoCalendar.prototype.resize = function () {
        const _ = this;
        _.windowW = $(window).width();

        if (_.windowW <= _.$breakpoints.tablet) { // tablet
            _.toggleSidebar(false);
            _.toggleEventList(false);

            if (_.windowW <= _.$breakpoints.mobile) { // mobile
                $(window)
                    .off(`click.evocalendar.evo-${_.instanceUid}`)
            } else {
                $(window)
                    .on(`click.evocalendar.evo-${_.instanceUid}`, $.proxy(_.toggleOutside, _));
            }
        } else {
            if (!_.options.sidebarDisplayDefault) _.toggleSidebar(false);
            else _.toggleSidebar(true);

            if (!_.options.eventDisplayDefault) _.toggleEventList(false);
            else _.toggleEventList(true);

            $(window)
                .off(`click.evocalendar.evo-${_.instanceUid}`);
        }
    }

    // v1.0.0 - Initialize event listeners
    EvoCalendar.prototype.initEventListener = function () {
        const _ = this;

        // resize
        $(window)
            .off(`resize.evocalendar.evo-${_.instanceUid}`)
            .on(`resize.evocalendar.evo-${_.instanceUid}`, $.proxy(_.resize, _));

        // IF sidebarToggler: set event listener: toggleSidebar
        if (_.options.sidebarToggler) {
            _.$elements.sidebarToggler
            .off('click.evocalendar')
            .on('click.evocalendar', _.toggleSidebar);
        }

        // IF eventListToggler: set event listener: toggleEventList
        if (_.options.eventListToggler) {
            _.$elements.eventListToggler
            .off('click.evocalendar')
            .on('click.evocalendar', _.toggleEventList);
        }

        // set event listener for each month
        _.$elements.sidebarEl.find('[data-month-val]')
        .off('click.evocalendar')
        .on('click.evocalendar', _.selectMonth);

        // set event listener for year
        _.$elements.sidebarEl.find('[data-year-val]')
        .off('click.evocalendar')
        .on('click.evocalendar', _.selectYear);

        // set event listener for every event listed
        _.$elements.eventEl.find('[data-event-index]')
        .off('click.evocalendar')
        .on('click.evocalendar', _.selectEvent);
    };

    // v1.0.0 - Destroy event listeners
    EvoCalendar.prototype.destroyEventListener = function () {
        const _ = this;

        $(window).off(`resize.evocalendar.evo-${_.instanceUid}`);
        $(window).off(`click.evocalendar.evo-${_.instanceUid}`);

        // IF sidebarToggler: remove event listener: toggleSidebar
        if (_.options.sidebarToggler) {
            _.$elements.sidebarToggler
            .off('click.evocalendar');
        }

        // IF eventListToggler: remove event listener: toggleEventList
        if (_.options.eventListToggler) {
            _.$elements.eventListToggler
            .off('click.evocalendar');
        }

        // remove event listener for each day
        _.$elements.innerEl.find('.calendar-day').children()
        .off('click.evocalendar')

        // remove event listener for each month
        _.$elements.sidebarEl.find('[data-month-val]')
        .off('click.evocalendar');

        // remove event listener for year
        _.$elements.sidebarEl.find('[data-year-val]')
        .off('click.evocalendar');

        // remove event listener for every event listed
        _.$elements.eventEl.find('[data-event-index]')
        .off('click.evocalendar');
    };

    // v1.0.0 - Calculate days (incl. monthLength, startingDays based on :firstDayOfWeekName)
    EvoCalendar.prototype.calculateDays = function () {
        const _ = this; let nameDays; let weekStart; let
firstDay;
        _.monthLength = _.$label.days_in_month[_.$active.month]; // find number of days in month
        if (_.$active.month == 1) { // compensate for leap year - february only!
            if ((_.$active.year % 4 == 0 && _.$active.year % 100 != 0) || _.$active.year % 400 == 0) {
                _.monthLength = 29;
            }
        }
        nameDays = _.initials.dates[_.options.language].daysShort;
        weekStart = _.options.firstDayOfWeek;

        while (_.$label.days.length < nameDays.length) {
            if (weekStart == nameDays.length) {
                weekStart = 0;
            }
            _.$label.days.push(nameDays[weekStart]);
            weekStart++;
        }
        firstDay = new Date(_.$active.year, _.$active.month).getDay() - weekStart;
        _.startingDay = firstDay < 0 ? (_.$label.days.length + firstDay) : firstDay;
    }

    // v1.0.0 - Build the bones! (incl. sidebar, inner, events), called once in every initialization
    EvoCalendar.prototype.buildTheBones = function () {
        const _ = this;
        _.calculateDays();

        if (!_.$elements.calendarEl.html()) {
            let markup;

            // --- BUILDING MARKUP BEGINS --- //

            // sidebar
            markup = `${'<div class="calendar-sidebar">'
                        + '<div class="calendar-year">'
                        + '<button class="icon-button" role="button" data-year-val="prev" title="'}${_.initials.dates[_.options.language].previousYearText}">`
                                + '<span class="chevron-arrow-left"></span>'
                            + '</button>'
                            + '&nbsp;<p></p>&nbsp;'
                            + `<button class="icon-button" role="button" data-year-val="next" title="${_.initials.dates[_.options.language].nextYearText}">`
                                + '<span class="chevron-arrow-right"></span>'
                            + '</button>'
                        + '</div><div class="month-list">'
                        + '<ul class="calendar-months">';
                            for (var i = 0; i < _.$label.months.length; i++) {
                                markup += `<li class="month" role="button" data-month-val="${i}">${_.initials.dates[_.options.language].months[i]}</li>`;
                            }
                        markup += '</ul>';
            markup += '</div></div>';

            // inner
            markup += '<div class="calendar-inner">'
                            + '<table class="calendar-table">'
                                + '<tr><th colspan="7"></th></tr>'
                                + '<tr class="calendar-header">';
                                for (var i = 0; i < _.$label.days.length; i++) {
                                    let headerClass = 'calendar-header-day';
                                    if (_.$label.days[i] === _.initials.weekends.sat || _.$label.days[i] === _.initials.weekends.sun) {
                                        headerClass += ' --weekend';
                                    }
                                    markup += `<td class="${headerClass}">${_.$label.days[i]}</td>`;
                                }
                                markup += '</tr></table>'
                        + '</div>';

            // events
            markup += '<div class="calendar-events">'
                            + '<div class="event-header"><p></p></div>'
                            + '<div class="event-list"></div>'
                        + '</div>';

            // --- Finally, build it now! --- //
            _.$elements.calendarEl.html(markup);

            if (!_.$elements.sidebarEl) _.$elements.sidebarEl = $(_.$elements.calendarEl).find('.calendar-sidebar');
            if (!_.$elements.innerEl) _.$elements.innerEl = $(_.$elements.calendarEl).find('.calendar-inner');
            if (!_.$elements.eventEl) _.$elements.eventEl = $(_.$elements.calendarEl).find('.calendar-events');

            // if: _.options.sidebarToggler
            if (_.options.sidebarToggler) {
                $(_.$elements.sidebarEl).append(`<span id="sidebarToggler" role="button" aria-pressed title="${_.initials.dates[_.options.language].closeSidebarText}"><button class="icon-button"><span class="bars"></span></button></span>`);
                if (!_.$elements.sidebarToggler) _.$elements.sidebarToggler = $(_.$elements.sidebarEl).find('span#sidebarToggler');
            }
            if (_.options.eventListToggler) {
                $(_.$elements.calendarEl).append(`<span id="eventListToggler" role="button" aria-pressed title="${_.initials.dates[_.options.language].closeEventListText}"><button class="icon-button"><span class="chevron-arrow-right"></span></button></span>`);
                if (!_.$elements.eventListToggler) _.$elements.eventListToggler = $(_.$elements.calendarEl).find('span#eventListToggler');
            }
        }

        _.buildSidebarYear();
        _.buildSidebarMonths();
        _.buildCalendar();
        _.buildEventList();
        _.initEventListener(); // test

        _.resize();
    }

    // v1.0.0 - Build Event: Event list
    EvoCalendar.prototype.buildEventList = function () {
        const _ = this; let markup; let
hasEventToday = false;

        _.$active.events = [];
        // Event date
        const title = _.formatDate(_.$active.number_on, _.options.eventHeaderFormat, _.options.language);
        _.$elements.eventEl.find('.event-header > p').text(title);
        // Event list
        const eventListEl = _.$elements.eventEl.find('.event-list');
        // Clear event list item(s)
        if (eventListEl.children().length > 0) eventListEl.empty();
        if (_.options.calendarEvents) {
            for (let i = 0; i < _.options.calendarEvents.length; i++) {
                if (_.isBetweenDates(_.$active.number_on, _.options.calendarEvents[i].number_on)) {
                    eventAdder(_.options.calendarEvents[i])
                } else if (_.options.calendarEvents[i].everyYear) {
                    const d = `${new Date(_.$active.number_on).getMonth() + 1} ${new Date(_.$active.number_on).getDate()}`;
                    const dd = `${new Date(_.options.calendarEvents[i].number_on).getMonth() + 1} ${new Date(_.options.calendarEvents[i].number_on).getDate()}`;
                    // var dates = [_.formatDate(_.options.calendarEvents[i].date[0], 'mm/dd'), _.formatDate(_.options.calendarEvents[i].date[1], 'mm/dd')];

                    if (d == dd) {
                        eventAdder(_.options.calendarEvents[i])
                    }
                }
            }
        }
        function eventAdder(event) {
            hasEventToday = true;
            _.addEventList(event)
        }
        // IF: no event for the selected date
        if (!hasEventToday) {
            markup = '<div class="event-empty">';
            if (_.$active.number_on === _.$current.number_on) {
                markup += `<p>${_.initials.dates[_.options.language].noEventForToday}</p>`;
            } else {
                markup += `<p>${_.initials.dates[_.options.language].noEventForThisDay}</p>`;
            }
            markup += '</div>';
        }
        eventListEl.append(markup)
    }

    // v1.0.0 - Add single event to event list
    EvoCalendar.prototype.addEventList = function (event_data) {
        const _ = this; let
markup;
        const eventListEl = _.$elements.eventEl.find('.event-list');
        if (eventListEl.find('[data-event-index]').length === 0) eventListEl.empty();
        _.$active.events.push(event_data);
        markup = `<div class="event-container" role="button" data-event-index="${event_data.id}">`;
        markup += `<div class="event-icon"><div class="event-bullet-${event_data.type_on}"`;
        if (event_data.color) {
            markup += `style="background-color:${event_data.color}"`
        }
        markup += `></div></div><div class="event-info"><time>${event_data.there_is}</time><p class="event-title">${_.limitTitle(event_data.name)}`;

        markup += `<a class="btn btn-outline-primary btn-sm ms-3" href="/reserve/rsv-service/${detail}/${event_data.id}" role="button">&raquo;</a>`;

        if (event_data.badge) markup += `<span>${event_data.badge}</span>`;
        markup += '</p>'
        if (event_data.description) markup += `<p class="event-desc">${event_data.description}</p>`;
        markup += '</div>';
        markup += '</div>';
        eventListEl.append(markup);

        _.$elements.eventEl.find(`[data-event-index="${event_data.id}"]`)
        .off('click.evocalendar')
        .on('click.evocalendar', _.selectEvent);
    }
    // v1.0.0 - Remove single event to event list
    EvoCalendar.prototype.removeEventList = function (event_data) {
        const _ = this; let
markup;
        const eventListEl = _.$elements.eventEl.find('.event-list');
        if (eventListEl.find(`[data-event-index="${event_data}"]`).length === 0) return; // event not in active events
        eventListEl.find(`[data-event-index="${event_data}"]`).remove();
        if (eventListEl.find('[data-event-index]').length === 0) {
            eventListEl.empty();
            if (_.$active.number_on === _.$current.number_on) {
                markup += `<p>${_.initials.dates[_.options.language].noEventForToday}</p>`;
            } else {
                markup += `<p>${_.initials.dates[_.options.language].noEventForThisDay}</p>`;
            }
            eventListEl.append(markup)
        }
    }

    // v1.0.0 - Build Sidebar: Year text
    EvoCalendar.prototype.buildSidebarYear = function () {
        const _ = this;

        _.$elements.sidebarEl.find('.calendar-year > p').text(_.$active.year);
    }

    // v1.0.0 - Build Sidebar: Months list text
    EvoCalendar.prototype.buildSidebarMonths = function () {
        const _ = this;

        _.$elements.sidebarEl.find('.calendar-months > [data-month-val]').removeClass('active-month');
        _.$elements.sidebarEl.find(`.calendar-months > [data-month-val="${_.$active.month}"]`).addClass('active-month');
    }

    // v1.0.0 - Build Calendar: Title, Days
    EvoCalendar.prototype.buildCalendar = function () {
        const _ = this; let markup; let
title;

        _.calculateDays();

        title = _.formatDate(new Date(`${_.$label.months[_.$active.month]} 1 ${_.$active.year}`), _.options.titleFormat, _.options.language);
        _.$elements.innerEl.find('.calendar-table th').text(title);

        _.$elements.innerEl.find('.calendar-body').remove(); // Clear days

        markup += '<tr class="calendar-body">';
                    let day = 1;
                    for (let i = 0; i < 9; i++) { // this loop is for is weeks (rows)
                        for (let j = 0; j < _.$label.days.length; j++) { // this loop is for weekdays (cells)
                            if (day <= _.monthLength && (i > 0 || j >= _.startingDay)) {
                                let dayClass = 'calendar-day';
                                if (_.$label.days[j] === _.initials.weekends.sat || _.$label.days[j] === _.initials.weekends.sun) {
                                    dayClass += ' --weekend'; // add '--weekend' to sat sun
                                }
                                markup += `<td class="${dayClass}">`;

                                const thisDay = _.formatDate(`${_.$label.months[_.$active.month]} ${day} ${_.$active.year}`, _.options.format);
                                markup += `<div class="day" role="button" data-date-val="${thisDay}">${day}</div>`;
                                day++;
                            } else {
                                markup += '<td>';
                            }
                            markup += '</td>';
                        }
                        if (day > _.monthLength) {
                            break; // stop making rows if we've run out of days
                        } else {
                            markup += '</tr><tr class="calendar-body">'; // add if not
                        }
                    }
                    markup += '</tr>';
        _.$elements.innerEl.find('.calendar-table').append(markup);

        if (_.options.todayHighlight) {
            _.$elements.innerEl.find(`[data-date-val='${_.$current.number_on}']`).addClass('calendar-today');
        }

        // set event listener for each day
        _.$elements.innerEl.find('.calendar-day').children()
        .off('click.evocalendar')
        .on('click.evocalendar', _.selectDate)

        const selectedDate = _.$elements.innerEl.find(`[data-date-val='${_.$active.number_on}']`);

        if (selectedDate) {
            // Remove active class to all
            _.$elements.innerEl.children().removeClass('calendar-active');
            // Add active class to selected date
            selectedDate.addClass('calendar-active');
        }
        if (_.options.calendarEvents != null) { // For event indicator (dots)
            _.buildEventIndicator();
        }
    };

    // v1.0.0 - Add event indicator/s (dots)
    EvoCalendar.prototype.addEventIndicator = function (event) {
        const _ = this; let htmlToAppend; let
thisDate;
        let event_date = event.number_on;
        const type_on = _.stringCheck(event.type_on);

        if (event_date instanceof Array) {
            if (event.everyYear) {
                for (let x = 0; x < event_date.length; x++) {
                    event_date[x] = _.formatDate(new Date(event_date[x]).setFullYear(_.$active.year), _.options.format);
                }
            }
            const active_date = _.getBetweenDates(event_date);

            for (let i = 0; i < active_date.length; i++) {
                appendDot(active_date[i]);
            }
        } else {
            if (event.everyYear) {
                event_date = _.formatDate(new Date(event_date).setFullYear(_.$active.year), _.options.format);
            }
            appendDot(event_date);
        }

        function appendDot(number_on) {
            thisDate = _.$elements.innerEl.find(`[data-date-val="${number_on}"]`);

            if (thisDate.find('span.event-indicator').length === 0) {
                thisDate.append('<span class="event-indicator"></span>');
            }

            if (thisDate.find(`span.event-indicator > .type-bullet > .type-${type_on}`).length === 0) {
                htmlToAppend = '<div class="type-bullet"><div ';

                htmlToAppend += `class="type-${event.type_on}"`
                if (event.color) { htmlToAppend += `style="background-color:${event.color}"` }
                htmlToAppend += '></div></div>';
                thisDate.find('.event-indicator').append(htmlToAppend);
            }
        }
    };

    // v1.0.0 - Remove event indicator/s (dots)
    EvoCalendar.prototype.removeEventIndicator = function (event) {
        const _ = this;
        const event_date = event.number_on;
        const type_on = _.stringCheck(event.type_on);

        if (event_date instanceof Array) {
            const active_date = _.getBetweenDates(event_date);

            for (let i = 0; i < active_date.length; i++) {
                removeDot(active_date[i]);
            }
        } else {
            removeDot(event_date);
        }

        function removeDot(number_on) {
            // Check if no '.event-indicator', 'cause nothing to remove
            if (_.$elements.innerEl.find(`[data-date-val="${number_on}"] span.event-indicator`).length === 0) {
                return;
            }

            // // If has no type of event, then delete
            if (!_.hasSameDayEventType(number_on, type_on)) {
                _.$elements.innerEl.find(`[data-date-val="${number_on}"] span.event-indicator > .type-bullet > .type-${type_on}`).parent().remove();
            }
        }
    };

    /** **************
    *    METHODS    *
    *************** */

    // v1.0.0 - Build event indicator on each date
    EvoCalendar.prototype.buildEventIndicator = function () {
        const _ = this;

        // prevent duplication
        _.$elements.innerEl.find('.calendar-day > day > .event-indicator').empty();

        for (let i = 0; i < _.options.calendarEvents.length; i++) {
            _.addEventIndicator(_.options.calendarEvents[i]);
        }
    };

    // v1.0.0 - Select event
    EvoCalendar.prototype.selectEvent = function (event) {
        const _ = this;
        const el = $(event.target).closest('.event-container');
        const id = $(el).data('eventIndex').toString();
        const index = _.options.calendarEvents.map((event) => (event.id).toString()).indexOf(id);
        const modified_event = _.options.calendarEvents[index];
        if (modified_event.number_on instanceof Array) {
            modified_event.dates_range = _.getBetweenDates(modified_event.number_on);
        }
        $(_.$elements.calendarEl).trigger('selectEvent', [_.options.calendarEvents[index]])
    }

    // v1.0.0 - Select year
    EvoCalendar.prototype.selectYear = function (event) {
        const _ = this;
        let el; let
yearVal;

        if (typeof event === 'string' || typeof event === 'number') {
            if ((parseInt(event)).toString().length === 4) {
                yearVal = parseInt(event);
            }
        } else {
            el = $(event.target).closest('[data-year-val]');
            yearVal = $(el).data('yearVal');
        }

        if (yearVal == 'prev') {
            --_.$active.year;
        } else if (yearVal == 'next') {
            ++_.$active.year;
        } else if (typeof yearVal === 'number') {
            _.$active.year = yearVal;
        }

        if (_.windowW <= _.$breakpoints.mobile) {
            if (_.$UI.hasSidebar) _.toggleSidebar(false);
        }

        $(_.$elements.calendarEl).trigger('selectYear', [_.$active.year])

        _.buildSidebarYear();
        _.buildCalendar();
    };

    // v1.0.0 - Select month
    EvoCalendar.prototype.selectMonth = function (event) {
        const _ = this;

        if (typeof event === 'string' || typeof event === 'number') {
            if (event >= 0 && event <= _.$label.months.length) {
                // if: 0-11
                _.$active.month = (event).toString();
            }
        } else {
            // if month is manually selected
            _.$active.month = $(event.currentTarget).data('monthVal');
        }

        _.buildSidebarMonths();
        _.buildCalendar();

        if (_.windowW <= _.$breakpoints.tablet) {
            if (_.$UI.hasSidebar) _.toggleSidebar(false);
        }

        // EVENT FIRED: selectMonth
        $(_.$elements.calendarEl).trigger('selectMonth', [_.initials.dates[_.options.language].months[_.$active.month], _.$active.month])
    };

    // v1.0.0 - Select specific date
    EvoCalendar.prototype.selectDate = function (event) {
        const _ = this;
        const oldDate = _.$active.number_on;
        let number_on; let year; let month; let activeDayEl; let
isSameDate;

        if (typeof event === 'string' || typeof event === 'number' || event instanceof Date) {
            number_on = _.formatDate(new Date(event), _.options.format)
            year = new Date(number_on).getFullYear();
            month = new Date(number_on).getMonth();

            if (_.$active.year !== year) _.selectYear(year);
            if (_.$active.month !== month) _.selectMonth(month);
            activeDayEl = _.$elements.innerEl.find(`[data-date-val='${number_on}']`);
        } else {
            activeDayEl = $(event.currentTarget);
            number_on = activeDayEl.data('dateVal')
        }
        isSameDate = _.$active.number_on === number_on;
        // Set new active date
        _.$active.number_on = number_on;
        _.$active.event_date = number_on;
        // Remove active class to all
        _.$elements.innerEl.find('[data-date-val]').removeClass('calendar-active');
        // Add active class to selected date
        activeDayEl.addClass('calendar-active');
        // Build event list if not the same date events built
        if (!isSameDate) _.buildEventList();

        // EVENT FIRED: selectDate
        $(_.$elements.calendarEl).trigger('selectDate', [_.$active.number_on, oldDate])
    };

    // v1.0.0 - Return active date
    EvoCalendar.prototype.getActiveDate = function () {
        const _ = this;
        return _.$active.number_on;
    }

    // v1.0.0 - Return active events
    EvoCalendar.prototype.getActiveEvents = function () {
        const _ = this;
        return _.$active.events;
    }

    // v1.0.0 - Hide Sidebar/Event List if clicked outside
    EvoCalendar.prototype.toggleOutside = function (event) {
        const _ = this; let
isInnerClicked;

        isInnerClicked = event.target === _.$elements.innerEl[0];

        if (_.$UI.hasSidebar && isInnerClicked) _.toggleSidebar(false);
        if (_.$UI.hasEvent && isInnerClicked) _.toggleEventList(false);
    }

    // v1.0.0 - Toggle Sidebar
    EvoCalendar.prototype.toggleSidebar = function (event) {
        const _ = this;

        if (event === undefined || event.originalEvent) {
            $(_.$elements.calendarEl).toggleClass('sidebar-hide');
            _.$UI.hasSidebar = !_.$UI.hasSidebar;
        } else if (event) {
                $(_.$elements.calendarEl).removeClass('sidebar-hide');
                _.$UI.hasSidebar = true;
            } else {
                $(_.$elements.calendarEl).addClass('sidebar-hide');
                _.$UI.hasSidebar = false;
            }

        if (_.windowW <= _.$breakpoints.tablet) {
            if (_.$UI.hasSidebar && _.$UI.hasEvent) _.toggleEventList();
        }
    };

    // v1.0.0 - Toggle Event list
    EvoCalendar.prototype.toggleEventList = function (event) {
        const _ = this;

        if (event === undefined || event.originalEvent) {
            $(_.$elements.calendarEl).toggleClass('event-hide');
            _.$UI.hasEvent = !_.$UI.hasEvent;
        } else if (event) {
                $(_.$elements.calendarEl).removeClass('event-hide');
                _.$UI.hasEvent = true;
            } else {
                $(_.$elements.calendarEl).addClass('event-hide');
                _.$UI.hasEvent = false;
            }

        if (_.windowW <= _.$breakpoints.tablet) {
            if (_.$UI.hasEvent && _.$UI.hasSidebar) _.toggleSidebar();
        }
    };

    // v1.0.0 - Add Calendar Event(s)
    EvoCalendar.prototype.addCalendarEvent = function (arr) {
        const _ = this;

        function addEvent(data) {
            if (!data.id) {
                console.log(`%c Event named: "${data.name}" doesn't have a unique ID `, 'color:white;font-weight:bold;background-color:#e21d1d;');
            }

            if (data.number_on instanceof Array) {
                for (let j = 0; j < data.number_on.length; j++) {
                    if (isDateValid(data.number_on[j])) {
                        data.number_on[j] = _.formatDate(new Date(data.number_on[j]), _.options.format);
                    }
                }
            } else if (isDateValid(data.number_on)) {
                    data.number_on = _.formatDate(new Date(data.number_on), _.options.format);
                }

            if (!_.options.calendarEvents) _.options.calendarEvents = [];
            _.options.calendarEvents.push(data);
            // add to date's indicator
            _.addEventIndicator(data);
            // add to event list IF active.event_date === data.date
            if (_.$active.event_date === data.number_on) _.addEventList(data);
            // _.$elements.innerEl.find("[data-date-val='" + data.date + "']")

            function isDateValid(number_on) {
                if (_.isValidDate(number_on)) {
                    return true;
                }
                    console.log(`%c Event named: "${data.name}" has invalid date `, 'color:white;font-weight:bold;background-color:#e21d1d;');

                return false;
            }
        }
        if (arr instanceof Array) { // Arrays of events
            for (let i = 0; i < arr.length; i++) {
                addEvent(arr[i])
            }
        } else if (typeof arr === 'object') { // Single event
            addEvent(arr)
        }
    };

    // v1.0.0 - Remove Calendar Event(s)
    EvoCalendar.prototype.removeCalendarEvent = function (arr) {
        const _ = this;

        function deleteEvent(data) {
            // Array index
            const index = _.options.calendarEvents.map((event) => event.id).indexOf(data);

            if (index >= 0) {
                const event = _.options.calendarEvents[index];
                // Remove event from calendar events
                _.options.calendarEvents.splice(index, 1);
                // remove to event list
                _.removeEventList(data);
                // remove event indicator
                _.removeEventIndicator(event);
            } else {
                console.log(`%c ${data}: ID not found `, 'color:white;font-weight:bold;background-color:#e21d1d;');
            }
        }
        if (arr instanceof Array) { // Arrays of index
            for (let i = 0; i < arr.length; i++) {
                deleteEvent(arr[i])
            }
        } else { // Single index
            deleteEvent(arr)
        }
    };

    // v1.0.0 - Check if date is valid
    EvoCalendar.prototype.isValidDate = function (d) {
        return new Date(d) && !isNaN(new Date(d).getTime());
    }

    $.fn.evoCalendar = function () {
        const _ = this;
            const opt = arguments[0];
            const args = Array.prototype.slice.call(arguments, 1);
            const l = _.length;
            let i;
            let ret;
        for (i = 0; i < l; i++) {
            if (typeof opt === 'object' || typeof opt === 'undefined') { _[i].evoCalendar = new EvoCalendar(_[i], opt); } else { ret = _[i].evoCalendar[opt].apply(_[i].evoCalendar, args); }
            if (typeof ret !== 'undefined') return ret;
        }
        return _;
    };
}));
