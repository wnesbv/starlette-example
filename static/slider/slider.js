    $('.card_item:first-of-type').addClass('plug_time');
    $(() => {
        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.card_item').removeClass('plug_time');
            }, 0);
        });
        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.card_item').removeClass('active');
            }, 0);
        });

        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.sl_content').append($('.card_item:first'));
            }, 800);
        });

        $('.sld_trigger').click(() => {
            setTimeout(() => {
                $('.card_item:first-of-type').addClass('active');
            }, 800);
        });
    });
