// ****************************************************
// Insert GPL header here.
// ****************************************************

// ****************************************************
// Compatability matrix (as far as I can guess)
//
// IE5+, Mozilla 1.0+, and Netscape 6+
//

GMTDiff = 0;

function requestsong(no) {
    $.get(ajaxurl+'song/'+no+'/queue/?'+ajaxeventid);
}

function format_time(s) {
            var r = "NaN";
            var h=Math.round(Math.floor(s/(60.0*60.0)));
            s%=(60*60);
            var m=Math.round(Math.floor(s/60.0));
            s%=(60);
            if (s<10) {
                s="0"+s;
            }
            if (h>0 && m<10) {
                m="0"+m;
            }
            try {
                if (h>0) {
                   r = h+":"+m+":"+s;
                }else{
                   r = m+":"+s;
                }
            }catch(err){} // ignore error
            return r;
        }

// added support for multiple counter spans with arbitrary direction
function counter() {
    $("[data-name='counter']").each( function (n) {
        i = $(this);
        var counter=1*i.attr("data-sec");
        var inc=1*i.attr("data-inc");
        if ((inc<0 && counter>0) || inc>0) {
            counter=counter+inc;

            i.attr("data-sec",counter);
            var s=counter;
            var h=Math.round(Math.floor(s/(60.0*60.0)));
            s%=(60*60);
            var m=Math.round(Math.floor(s/60.0));
            s%=(60);
            if (s<10) {
                s="0"+s;
            }
            if (h>0 && m<10) {
                m="0"+m;
            }
            try {
                if (h>0) {
                    i.text(h+":"+m+":"+s);
                }else{
                    i.text(m+":"+s);
                }
            }catch(err){} // ignore error
        }
    });
}

// Added try/catch to prevent errors, if updates occur while this runs.
function countdown() {
    var txt='0:00';
    if (counter>=0) {
        counter=counter-1;
    }
    if (counter>=0) {
        var s=counter;
        var h=Math.round(Math.floor(s/(60.0*60.0)));
        s%=(60*60);
        var m=Math.round(Math.floor(s/60.0));
        s%=(60);
        if (s<10) {
        s="0"+s;
        }
        if (h>0) {
            txt=h+":"+m+":"+s;
        }else{
            txt=m+":"+s;
        }
    } else {
        iscounting=0;
        clearInterval(Timer);
    }
    var divs=ajaxfindobjs('counter');
    for (var i=0;i<divs.length;i++) {
        var obj=divs[i];
        try {
            obj.innerHTML=txt;
        } catch(err) {} // ignore errors
    }
}

// Added try/catch to prevent errors, if updates occur while this runs.
function voteshow(id,value)
{
    for (i=1;i<=5;i++)
    {
        var objs=$("#"+id+'-'+i);
        for (var j=0;j<objs.length;j++)
        {
            var obj=objs[j];
            if (obj)
            {
                if (i>value)
                {
                    diff=(i-value);
                    if (diff>=1)
                    {
                        try
                        {
                            // Spaces AFTER the selected star (if on 3, 4 and 5 use this)
                            obj.src='/static/star-white.png';
                            obj.style.width='100%';
                        } catch(err) {} // ignore errors
                    } else
                    {
                        try
                        {
                            // This only gets called if value has decimals!
                            obj.src='/static/star-gold.png';
                            obj.style.width=100-(diff*100)+'%';
                        } catch(err) {} // ignore errors
                    }
                } else
                {
                    try
                    {
                        // Voting up to and under mouse pointer, or default value if not on img
                        obj.src='/static/star-red.png';
                        obj.style.width='100%';
                    } catch(err) {} // ignore errors
                }
            }
        }
    }
}

function hookAjaxForms() {
    $(".ajaxify").each(function (i, element) {
        var E = $(element);
        E.unbind("submit");
        E.submit(function (eo) {
            E.parent().addClass("ajax-working");
            var url = E.attr("action");
            $.post(url, E.serialize(), function(data) {
                E.parent().removeClass("ajax-working");
                if (data) { E.parent().replaceWith(data); }
                hookAjaxForms();
                hookStarHover();
            });
            return false;
        });
    });
}

function hookStarHover() {
    $(".starbutton").unbind("hover");
    $(".starbutton").hover(function () {
        // Mouse hover
        var t = $(this);
        t.parent().find(".ajaxhax").val(t.val());
        t.prevAll().andSelf().addClass("star-selected");
        t.nextAll().removeClass("star-selected");
    },
    function () {
        // Mouse out
        var t = $(this);
        var parent = t.parent();
        var vote = parseInt(parent.data("vote"));
        var elements = parent.find(".starbutton");
        elements.removeClass("star-selected");

        elements.each(function (i, elem) {
            var E = $(elem);
            if (i < vote) {
                E.addClass("star-selected");
            }
        });
    });
}

function applyHooks() {
    //updateOnelinerLinks();
    hookAjaxForms();
    hookStarHover();
    changeTime();
}

function intToStr(val) {
    var val2 = val.toString();
    if (val2.length < 2) { val2 = "0" + val2 }
    return val2;
}

function changeTime() {
    var d = new Date()
    var gmtHours = -d.getTimezoneOffset()/60;
    $(".tzinfo").each(function (i, elem) {
        var E = $(elem);
        var Eo = E.text();

        var split = Eo.split(":");
        var hr = parseInt(split[0], 10);
        var min = parseInt(split[1], 10);

        // Modulo js bug workaround
        hr = (((hr - GMTDiff + gmtHours) % 24) + 24 ) % 24;

        var str = intToStr(hr) + ":" + intToStr(min)
        if ( split.length == 3 ) {
            var sec = parseInt(split[2], 10);
            str = str + ":" + intToStr(sec)
        }
        E.text(str);
        var GMTmod = "";
        if (GMTDiff > 0) {
             GMTmod = "+";
        }
        E.attr("title", "Server time: " + Eo + " GMT " + GMTmod + GMTDiff);

        E.removeClass("tzinfo");
    });
}

$(document).ready( function() {
    applyHooks();
});


