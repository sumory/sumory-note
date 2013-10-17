var request = require('request');
var helper = require('./helper.js');

exports.sendSMS = function(telphone, msg) {
    var content = escape(msg);
    var now = helper.now();

    var url = "http://si.800617.com:4400/SendSms.aspx?un=shyzxx-1&pwd=44d167&mobile=" + telphone + "&msg=" + content;
    request({
        url : url,
        method : "GET",
        headers : {
            'content-type' : 'application/x-www-form-urlencoded'
        },
        body : ""
    }, function(e, r, body) {
        if (!e) {
            console.log(now + ' 短信发送成功: ' + telphone + ' '+msg,  body);
        }
        else {
            console.error(now + ' 短信发送失败: ' + telphone + ' '+msg);
            console.error(now + ' 短信发送失败Error: ', e);
        }
    });
};
