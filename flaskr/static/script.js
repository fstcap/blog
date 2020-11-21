function like_click(ele, url, user_not_exist){
    var ajax_method = 'POST';
    var post_total_like = Number($(ele).text().replace(/[^0-9]/ig, ""));
    if (user_not_exist){
        window.location.href="/auth/login";
        return false;
    }
    if ($(ele).hasClass("like")){
        ajax_method = 'DELETE';
    }
    $.ajax({
        url: url,
        type: ajax_method,
        success: function(result){
            if ($(ele).hasClass("like")){
                $(ele).removeClass("like");
                $(ele).text("like:"+ (--post_total_like));
            }
            else{
                $(ele).addClass("like");
                $(ele).text("like:"+ (++post_total_like));
            }
            console.log('success', result);
        },
        error: function(result){
            console.log('error', result);
        }
    })
}

function md_switch(md_area, show_area) {
    var md_value = $(md_area).val();
    var converter = new showdown.Converter();
    var html = converter.makeHtml(md_value);
    $(show_area).html(html);
}
function md2html(md_area) {
    var eles = $(md_area);
    var converter = new showdown.Converter();
    for (var i=0; i<eles.length; i++){
        var md_value = $(eles[i]).text();
        var html = converter.makeHtml(md_value);
        $(eles[i]).html(html)
    }
}

$(window).load(function(){
    md2html('.markdown-body')
})
