/**
 * Created by Tirthraj on 7/19/2016.
 */

$('.url').click(function () {
        url = $(this).attr("data-value");
        url_id = $(this).text();
        $('#url_address').text(url_id + ' >> ' + url).attr("href", url);
        $('#view_frame').attr("src",url);
    });
