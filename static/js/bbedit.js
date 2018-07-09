var bbOptions = {
    "buttons": [
        {"name": "Bold", "button": "explicit.gif", "content": "[b]%s[/b]", "description": "Marks text as <strong>bold</strong>"},
        {"name": "Italic", "button": "page_white_edit.png", "content": "[i]%s[/i]", "description": "Marks text as <i>italic</i>"},
        {"name": "Big", "button": "add.png", "content": "[big]%s[/big]", "description": "Marks text as big"},
        {"name": "Small", "button": "find.png", "content": "[small]%s[/small]", "description": "Marks text as small"},
        {"name": "Code tag", "button": "comment.png", "content": "[code]%s[/code]", "description": "Marks text as code"},
        {"name": "Quote", "button": "script.png", "content": "[quote]%s[/quote]", "description": "Marks text as quote"},
        {"name": "YouTube link", "button": "youtube_icon.png", "content": "[yt]%s[/yt]", "description": "Creates a link to a YouTube video <br/>Use video ID that is after v= in the URL"},
        {"name": "HTTP Url", "button": "world_link.png", "content": "[url]%s[/url]", "description": "Creates a web link. <br/>Link MUST start with http or ftp"},
        {"name": "Image embed", "button": "icon_screenshot.png", "content": "[img]%s[/img]", "description": "Embeds an image into the page"},
        {"name": "Song link", "button": "music.png", "content": "[song]%s[/song]", "description": "Creates a link to given song ID"},
        {"name": "Song queue link", "button": "control_play.png", "content": "[queue]%s[/queue]", "description": "Creates a link to given song ID, with queue button"},
        {"name": "User link", "button": "user.png", "content": "[user]%s[/user]", "description": "Creates a link to given user"},
        {"name": "Artist link", "button": "user_green.png", "content": "[artist]%s[/artist]", "description": "Creates a link to given artist ID"},
        {"name": "Thread link", "button": "newspaper.png", "content": "[thread]%s[/thread]", "description": "Creates a link to given thread ID"}
    ]
};

function createField(element) {
    var editarea = $(element);
    editarea.wrap('<div class="editdiv" />');
    var target = editarea.parent();
    var editbar = $("<div/>").addClass("editbar");
    $.each(bbOptions.buttons, function (i, b) {
        var button = $("<img/>").attr("src", STATIC_URL + b.button).addClass("editButton");
        button.qtip({
            "content": {
                "text": b.description,
                "title": {
                    "text": b.name
                }
            },
            "position": {
                "my" : "top center",
                "at" : "bottom center"
            },
               "style": {
                   "classes": 'ui-tooltip-shadow ui-tooltip-jtools'
            }
        });
        button.click(function (i) {
            var editval = editarea.val();
            var selstart = editarea[0].selectionStart;
            var sellen = editarea[0].selectionEnd - selstart;
            var selected = editval.substr(selstart, sellen);
            if (!selected) {
                var inp2 = prompt("Value for "+ b.name + " tag");
                if (inp2) {
                    selected = inp2;
                }
            }
            if (selected) {
             var input = b.content.replace("%s", selected);
             editval = editval.substr(0, selstart) + input + editval.substr(selstart + sellen);
             editarea.val(editval);
             editarea[0].selectionStart = selstart;
             editarea[0].selectionEnd = selstart + input.length;
            }
        });
        editbar.append(button);
    });
    target.append(editbar);
}

$(document).ready( function () {
    $("textarea").each( function (i, v) {
        createField(v);
    });
});
