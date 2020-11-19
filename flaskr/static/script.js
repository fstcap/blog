function like_click(ele, url, user_not_exist){
    var ajax_method = 'POST'
    var post_total_like = Number($(ele).text().replace(/[^0-9]/ig, ""))
    if (user_not_exist){
        window.location.href="/auth/login"
        return false
    }
    if ($(ele).hasClass("like")){
        ajax_method = 'DELETE'
    }
    $.ajax({
        url: url,
        type: ajax_method,
        success: function(result){
            if ($(ele).hasClass("like")){
                $(ele).removeClass("like")
                $(ele).text("like:"+ (--post_total_like))
            }
            else{
                $(ele).addClass("like")
                $(ele).text("like:"+ (++post_total_like))
            }
            console.log('success', result) 
        },
        error: function(result){
            console.log('error', result)
        }
    })
}
