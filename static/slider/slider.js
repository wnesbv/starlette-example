    $('.card_i:first-of-type').addClass('run');
    $(() => {
        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.card_i').removeClass('run');
            }, 0);
        });
        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.card_i').removeClass('active');
            }, 0);
        });
        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.sl_content').append($('.card_i:first'));
            }, 800);
        });

        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.card_i:first-of-type').addClass('active');
            }, 800);
        });
    });
