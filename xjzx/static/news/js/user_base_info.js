function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender:checked").val()
        var csrf_token = $("#csrf_token").val()

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
            return
        }

        // TODO 修改用户信息接口
        $.post('/user/base',{
            'signature':signature,
            'nick_name':nick_name,
            'gender':gender,
            'csrf_token':csrf_token
        },function (data) {
            if(data.result==1){
                //修改成功后，需要将页面中昵称的地方改为新值
                $('.user_center_name',parent.document).text(nick_name);
                $('#nick_name',parent.document).text(nick_name);
            }
        });
    })
})