var ajaxurl="/demovibes/ajax/";
var ajaxeventid=0; // updated later
var ajaxmonitorrequest=false;
var userIdleTime = 0;
var updateThrottled = false;
var updateTimer;
var randBoost = 1000;
var successDelay = defaultSuccessDelay = 100;
var throttledSuccessDelay = 240000;
var userIdleLimit = 600;

$(window).bind("mousemove click mouseup keydown keypress keyup scroll resize", function () {
    userIdleTime = 0;
    if (updateThrottled) {
        updateThrottled = false;
        successDelay = defaultSuccessDelay;
        startAjax(1);
        updateStatus(false);
    }
});

function idleTicker () {
    userIdleTime += 1;
    if (userIdleTime > userIdleLimit && !updateThrottled) {
        updateThrottled = true;
        successDelay = throttledSuccessDelay;
        updateStatus(false);
    }
}

function apf(url, form) {
    $.post(url, $(form).serialize());
    return false;
}

function updateStatus(error) {
    $("#menuoneliner").removeClass("updatesIdle updatesActive updatesError");
    if (error) {
        $("#menuoneliner").addClass("updatesError");
    } else {
        if (updateThrottled) {
            $("#menuoneliner").addClass("updatesIdle");
        } else {
            $("#menuoneliner").addClass("updatesActive");
        }
    }
}

function ajaxmonitorspawn() {
    // resceive monitor events for objects on the page
    updateStatus(false);
    var url=ajaxurl+'ping/'+ajaxeventid+'/';
    // alert('Monitor for '+url);
    // old version: http://code.google.com/p/demovibes/issues/detail?id=47
    // ajaxmonitorrequest=$.get(url,ajaxmonitorupdate);
    ajaxmonitorrequest=$.ajax({
        type: 'GET',
        dataType: 'text',
        url: url,
        timeout: 300000,
        success: function(data, textStatus ){
            ajaxmonitorupdate(data);
        },
        error: function(xhr, textStatus, errorThrown){
            //newMessage("[Updater] Problem with server connection. Retrying in 15 seconds", 15);
            updateStatus(true);
            ajaxmonitorrequest=false;
            startAjax(15000);
        }
     });
}

function ajaxmonitorabort() {
    if (ajaxmonitorrequest)
        ajaxmonitorrequest.abort();
}

function ajaxmonitor(eventid) {
    ajaxeventid=eventid;
    startAjax(1);
    setInterval('counter()',1000);
}

function startAjax(time) {
    if (!ajaxmonitorrequest) {
        if (updateTimer) {
            clearTimeout(updateTimer);
        }
        updateTimer = setTimeout('ajaxmonitorspawn()',time);
    }
}

function ajaxmonitorupdate(req) {
        // must return event in lines
        var event=req.split('\n');
        var i;
        var id;
        for (i=0;i<event.length;i++) {
            id=event[i];
            if (id != "bye" && id != "") {
                if (id.substr(0,4)=='msg:') {
                    newMessage(id.substr(4,id.length));
                }
                else if (id.substr(0,5)=='vote:') {
                    updateVotes(id.substr(5,id.length));
                }
                else if (id.substr(0,5)=='eval:') {
                    eval(id.substr(5,id.length)); // evaluate the expression
                } else if (id.substr(0,1)=='!') {
                    ajaxeventid=parseInt(id.substr(1,id.length));
                } else {
                    $("[data-name='"+id+"']").load(ajaxurl+id+'/?event='+ajaxeventid, function() {applyHooks();})
                }
            }
        }
        ajaxmonitorrequest=false;
        applyHooks();
        var randInt = Math.floor((Math.random()*randBoost));
        updateStatus(false);
        startAjax(successDelay + randInt); // we get a nice return ask again right away
}

function updateVotes(data) {
    var votedata = data.split("|");
    $("#songrating").text(votedata[0]);
    $("#songrating_votes").text(votedata[1]);
}

function add_smileys(div, input) {
    div.empty();
    div.html("<div class='smileys_loading'>Loading..</div>");
    $.get("/demovibes/ajax/smileys/",function (data) {
        div.empty();
        $(data).each(function (i, elem) {
            var sign = elem[0];
            var icon = elem[1];
            var boxdiv = $("<div/>").addClass("smileybox-smiley");
            var boximg = $("<img/>").attr("src", STATIC_URL + icon);
            boxdiv.append(boximg);
            boxdiv.attr("title", sign);
            boxdiv.click(function () {
                var inpval = input.val() + " " + sign + " ";
                input.val(inpval);
                div.remove();
                input.focus();
            });
            div.append(boxdiv);
        });
    });
}

function add_pagelink(link) {
    var mydiv = $("<span/>").addClass("pagelink clicker").text("Page");
    var text = link;
    mydiv.click(function () {
        var inputbox = $("#blah");
        inputbox.focus();
        var inpval = inputbox.val() + " " + text + " ";
        inputbox.val(inpval);
    });
    $(".onelinertools").append(mydiv);
}

$(window).load( function () {
    var mydiv = $("<span/>").addClass("smileyslink clicker").text("Smileys");
    var inputbox = $("#blah");
    mydiv.click(function () {
        inputbox.focus();
        var smileys_holder = $("<div/>").addClass("smileybox-holder");
        var smileys_div = $("<div/>").addClass("smileybox");
        smileys_holder.append(smileys_div);
        $("body").prepend(smileys_holder);
        add_smileys(smileys_div, inputbox);
        smileys_holder.click(function () {
            smileys_holder.remove();
        });
    });
    setInterval('idleTicker()',1000);
    $(".onelinertools").append(mydiv);
});
