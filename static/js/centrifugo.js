(function () {
    var el = document.getElementById('centrifugo-data');
    if (!el) return;

    var wsUrl       = el.dataset.wsUrl;
    var token       = el.dataset.token;
    var channel     = el.dataset.channel;
    var currentPage = parseInt(el.dataset.page, 10);

    var centrifuge = new Centrifuge(wsUrl, { token: token });
    var sub = centrifuge.newSubscription(channel);

    sub.on('publication', function (ctx) {
        var answer = ctx.data;

        if (currentPage !== 1) {
            alert('Новый ответ от ' + answer.author + ': «' + answer.text.substring(0, 60) + '…»');
            return;
        }

        var $list = $('#answers-list');

        // Убираем заглушку «пока нет ответов», если она есть
        $list.find('.no-answers').remove();

        // Экранируем текст через jQuery для защиты от XSS
        var authorSafe = $('<span>').text(answer.author).html();
        var textSafe   = $('<span>').text(answer.text).html();

        var html = '<div id="answer-' + answer.id + '" class="answer-card p-3 p-md-4 mb-3">' +
            '<div class="row align-items-start g-3">' +
            '<div class="col-2 col-md-1 text-center">' +
            '<div class="username small">' + authorSafe + '</div>' +
            '</div>' +
            '<div class="col-10 col-md-11">' +
            '<p>' + textSafe + '</p>' +
            '<div class="text-muted small">' + answer.created_at + '</div>' +
            '</div></div></div>';

        $list.prepend(html);
    });

    centrifuge.connect();
    sub.subscribe();
}());
