function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $('.pic_info').submit(function (e) {
        e.preventDefault();

        //post+ajax+上传文件==>在jquery.form中提供的函数：ajaxSubmit()
        e.preventDefault();
        $(this).ajaxSubmit({
            url: "/user/pic",
            type: "post",
            dataType: "json",
            success: function (data) {
                if(data.result==1){
                    //在页面上更换用户头像
                    $('.now_user_pic').attr('src',data.avatar);
                    $('.user_center_pic>img',parent.document).attr('src',data.avatar);
                    $('.login_pic',parent.document).attr('src',data.avatar);
                }
            }
        });
    });
})