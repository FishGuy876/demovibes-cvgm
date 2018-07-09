var msgbox;
var msghold;
var msgtitle;
var flashtimer;

var SETTINGS = {
    "MAX_MSGS": 5,
    "FADE_SECONDS": 0,
    "disabled": false
}

var CATEGORY=new Array();
CATEGORY[0] = {"name": "General", "class": "general", "hidden": true};
CATEGORY[1] = {"name": "Forum", "class": "forum"};
CATEGORY[2] = {"name": "Songinfo", "class": "song"};

function msg_save_notifications() {
    var messages = new Array();
    $(".messageholder").each(function (i, elem) {
        messages.push($(elem).data("jsondata"));
    });
    messages = messages.reverse();
    var foo = JSON.stringify(messages);
    localStorage.setItem("notifications", foo);
}

function msg_stop_flash_bar() {
    $(".messagetitle").removeClass("messagetitle-flash");
    flashtimer = false;
}

function msg_flash_bar() {
    if ((SETTINGS.flashoff) || (flashtimer)) {return;}
    $(".messagetitle").addClass("messagetitle-flash");
    flashtimer = setTimeout(msg_stop_flash_bar, 400);
}

function msg_load_notifications() {
    flashtimer = "disable";
    var foo = localStorage.getItem("notifications");
    if (foo) {
        var messages = JSON.parse(foo);
        $(messages).each(function (i, elem) {
            try {
                newMessage(elem);
            } catch (err) {
                console.log("Problem loading event");
            }
        });
    }
    flashtimer = false;
}

function msg_change_settings() {
    if ($(".messagesettingsbox").length > 0) {
        return;
    }
    var div = $("<div/>").addClass("messagesettingsbox");
    var sdiv = $("<div/>").addClass("messagesettings");
    var cdiv = $("<div/>").addClass("message-categories");
    div.append($("<h2/>").text("Notification Settings"));
    div.append($("<p/>").text("Note : Changes only apply to new notifications!"));

    $(CATEGORY).each( function(i, e) {
        if (e.hidden) { return; }
        var qs = $("<div/>").addClass("category-" + e.class);
        var s1 = $("<input/>").addClass("category-setting-entry");
        s1.attr("id", "i_category-"+e.class);
        s1.attr("type", "checkbox");
        s1.data("catid", i);
        if (SETTINGS["disable-category-" + i]) {s1.attr("checked", "1");}
        qs.append(s1);
        qs.append($("<label/>").text("Disable "+e.name + " notifications").attr("for", "i_category-" + e.class));
        cdiv.append(qs);
    });

    div.append(sdiv);
    div.append(cdiv);
    var close = function () {
        div.remove();
    }
    var add_setting = function (name, key, attrs) {
        var ss = $("<div/>").addClass("messagesettingholder");
        var s1 = $("<input/>");
        s1.data("key", key);
        s1.addClass("messagesettingentry");
        s1.attr("id", "setting-"+key);
        s1.attr(attrs);
        if (s1.attr("type") == "checkbox") {
            if (SETTINGS[key]) {s1.attr("checked", "1");}
        } else {
            s1.val(SETTINGS[key]);
        }
        var s2 = $("<label/>").text(name).attr("for", "setting-" + key);
        ss.append(s2);
        ss.append(s1);
        sdiv.append(ss);
    }
    add_setting("Disable notifications", "disabled", {"type":"checkbox"});
    add_setting("Default timeout", "FADE_SECONDS", {"type":"number", "min": "0", "max": "120", "step": "5"});
    add_setting("Max messages", "MAX_MSGS", {"type":"number", "min":"0", "max": "15"});
    add_setting("Disable bar flash", "flashoff", {"type":"checkbox"});
    save = $("<div/>").addClass("messagesetting-save").text("Save!");
    cancel = $("<div/>").addClass("messagesetting-cancel").text("Cancel");
    cancel.click(close);
    save.click(function () {
        var mSettings = {};
        $(".category-setting-entry").each( function (i, elem) {
            var nr = $(elem).data("catid");
            mSettings["disable-category-" + nr] = $(elem).is(':checked');
        });
        $(".messagesettingentry").each( function (i, elem) {
            var e = $(elem);
            var key = e.data("key");
            if (e.attr("type") == "checkbox") {
                mSettings[key] = e.is(':checked');
            } else {
                mSettings[key] = e.val();
            }
        });
        SETTINGS = mSettings;
        msg_save_settings();
        close();
    });
    div.append(save);
    div.append(cancel);
    $("body").append(div);
}

function msg_toggle_notifications() {
    SETTINGS.disabled = !SETTINGS.disabled;
    msg_save_settings();
    if (SETTINGS.disabled) {msg_clear_notifications()}
}

function msg_save_settings() {
    var foo = JSON.stringify(SETTINGS);
    localStorage.setItem("notifications-settings", foo);
}

function msg_load_settings() {
    var foo = localStorage.getItem("notifications-settings");
    if (foo) {
        SETTINGS = JSON.parse(foo);
    }
}

function msg_clear_notifications () {
    $(".messagelist").empty();
    $(".messagetitle").hide();
    msg_save_notifications();
}

$(document).ready(function () {
    msg_load_settings();
    $(".message_toggle").addClass("message-disabled-"+SETTINGS.disabled);
    $(".message_toggle").click(function () {
        msg_toggle_notifications();
        $(this).removeClass("message-disabled-true");
        $(this).removeClass("message-disabled-false");
        $(this).addClass("message-disabled-"+SETTINGS.disabled);
    });
    msgbox = $(".messagebox");
    if (msgbox.length == 0) {
        msgbox = $("<div/>").addClass("messagebox");
    }
    msghold = $("<div/>").addClass("messagelist");
    msgtitle = $("<div/>").addClass("messagetitle");

    msgtitle.append($("<span/>").text("Demovibes Message System"));
    var settings = $("<span/>").text("Remove notifications");
    settings.addClass("message-remove");
    msgtitle.append(settings);
    msgtitle.click(function () {
        msg_clear_notifications();
    });

    msgbox.append(msgtitle);
    msgtitle.hide();

    msgbox.append(msghold);
    $("body").append(msgbox);
    msg_load_notifications();

    $(".message-display-settings").click( function () {
        msg_change_settings();
        return false;
    });
});

function toggleMessagebar() {
    if ($(".messagelist:empty").length > 0) {
        $(".messagetitle").hide();
    } else {
        $(".messagetitle").show();
    }
}

function killMsg(elem) {
    $(elem).slideUp("fast", function () {
        $(elem).remove();
        toggleMessagebar();
        msg_save_notifications();
    });
}

function newMessage(jsondata) {
    if (SETTINGS.disabled) { return; }
    var jd = JSON.parse(jsondata);
    if (!jd.category) {jd.category = 0}
    if (SETTINGS["disable-category-" + jd.category]) { return;}
    var timeout = null;
    var message = jd.message;
    var msgh = $("<div/>").addClass("messageholder");
    var msg = $("<span/>").addClass("messagetext");
    var msgtime = $("<span/>").addClass("messagetime");
    var msgcat = $("<span/>").addClass("messagecat");
    var msgfadeborder = $("<div/>").addClass("messagefadeborder");
    var msgfade = $("<div/>").addClass("messagefade");
    msgh.addClass("category-" + CATEGORY[jd.category].class);

    var cT = new Date()
    var h = cT.getHours();
    var m = cT.getMinutes();
    var s = cT.getSeconds();
    if (h < 10) {h = "0" + h}
    if (m < 10) {m = "0" + m}
    if (s < 10) {s = "0" + s}
    var timestr = "[" + h + ":" + m + ":" + s + "]";
    if (!jd.showtime) {jd.showtime = timestr;}
    msgtime.text(jd.showtime);

    msgcat.text(CATEGORY[jd.category].name);

    jsondata = JSON.stringify(jd);
    msgh.data("jsondata", jsondata);

    msgh.click(function () {
        killMsg(msgh);
    });
    msg.html(message);

    msgfadeborder.append(msgfade);
    msgh.append(msgtime);
    msgh.append(msgcat);
    msgh.append(msg);
    msgh.append(msgfadeborder);
    msgh.hide();
    msghold.prepend(msgh);
    toggleMessagebar();
    msgh.slideDown();

    if (!timeout) {
        timeout = SETTINGS.FADE_SECONDS;
    }

    if (timeout > 0) {
        msgfade.animate({
            "width": 0
        }, timeout * 1000, "linear", function() {
            killMsg(msgh);
        });
    }

    $(".messageholder").each(function (i, elem) {
        if ( SETTINGS.MAX_MSGS > 0 && i >= SETTINGS.MAX_MSGS ) {
            var e = elem;
            killMsg(e);
        }
    });
    msg_flash_bar();
    msg_save_notifications();
}
