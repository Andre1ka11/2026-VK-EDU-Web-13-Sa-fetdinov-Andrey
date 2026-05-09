$(function () {
    function getCsrfToken() {
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    $.ajaxSetup({
        headers: { 'X-CSRFToken': getCsrfToken() }
    });

    // ── Голосование за вопрос / ответ ──────────────────────────────────────
    $(document).on('click', '.vote-btn', function () {
        var $btn = $(this);
        if ($btn.prop('disabled')) return;

        var $group = $btn.closest('.vote-group');
        var type   = $group.data('type');   // 'question' или 'answer'
        var id     = $group.data('id');
        var value  = $btn.data('value');    // 1 или -1
        var $count = $group.find('.vote-count');

        var url = type === 'question'
            ? '/question/like/'
            : '/answer/like/';

        $.ajax({
            url: url,
            method: 'POST',
            data: { id: id, value: value },
            success: function (data) {
                $count.text(data.rating);

                var $like    = $group.find('.vote-btn[data-value="1"]');
                var $dislike = $group.find('.vote-btn[data-value="-1"]');

                $like.removeClass('voted').prop('disabled', false).css('opacity', '0.7');
                $dislike.removeClass('voted').prop('disabled', false).css('opacity', '0.7');

                if (data.status !== 'removed') {
                    $btn.addClass('voted').css('opacity', '1');
                    var $other = value === 1 ? $dislike : $like;
                    $other.prop('disabled', false).css('opacity', '0.7');
                }
            },
            error: function (xhr) {
                var data = xhr.responseJSON || {};
                if (xhr.status === 401) {
                    window.location.href = data.login_url || '/login/';
                } else if (xhr.status === 400) {
                    alert('Ошибка валидации: ' + JSON.stringify(data.error));
                } else if (xhr.status === 405) {
                    alert('Неверный метод запроса.');
                } else {
                    alert('Произошла ошибка. Попробуйте снова.');
                }
            }
        });
    });

    // ── Отметить правильный ответ ──────────────────────────────────────────
    $(document).on('click', '.mark-correct-btn', function () {
        var $btn       = $(this);
        var answerId   = $btn.data('answer-id');
        var questionId = $btn.data('question-id');

        $.ajax({
            url: '/answer/correct/',
            method: 'POST',
            data: { answer_id: answerId, question_id: questionId },
            success: function (data) {
                // Снимаем отметку со всех ответов
                $('.correct-badge').addClass('d-none');
                $('.mark-correct-btn')
                    .text('Отметить правильным')
                    .removeClass('btn-warning')
                    .addClass('btn-outline-secondary');

                if (data.is_correct) {
                    $('#answer-' + data.answer_id + ' .correct-badge').removeClass('d-none');
                    $btn.text('Снять отметку')
                        .removeClass('btn-outline-secondary')
                        .addClass('btn-warning');
                }
            },
            error: function (xhr) {
                var data = xhr.responseJSON || {};
                if (xhr.status === 401) {
                    window.location.href = data.login_url || '/login/';
                } else if (xhr.status === 403) {
                    alert('Только автор вопроса может отмечать правильные ответы.');
                } else if (xhr.status === 400) {
                    alert('Ошибка валидации: ' + JSON.stringify(data.error));
                } else if (xhr.status === 405) {
                    alert('Неверный метод запроса.');
                } else {
                    alert('Произошла ошибка. Попробуйте снова.');
                }
            }
        });
    });
});
