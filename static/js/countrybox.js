(function () {
    var ajaxurl="/demovibes/ajax/";

    if ((typeof $) == 'undefined') {
        $ = django.jQuery;
    }

    function addCountries (div, input) {
        div.empty ();
        div.html ("<div class='countrybox_loading'>Loading..</div>");

        div.load (ajaxurl + "countrybox/" ,function (html) {
            $(".countrybox-country").click (function () {
                var alpha2 = $(this).attr ('alpha2')
                input.val (alpha2);
                div.remove ();
                input.focus ();
            });
        });
    };

    $(window).load (function () {
        $(".country-alpha2-code-input").each (function (index) {
            var input_node = $(this);
            var mydiv = $("<div/>").addClass("countrybox-clicker").text("Country list");

            mydiv.click (function () {
                var list_holder = $("<div/>").addClass("countrybox-holder");
                var list_div = $("<div>hello</div>").addClass("countrybox");
                list_holder.append (list_div);

                addCountries (list_div, input_node);

                $("body").prepend (list_holder);

                list_holder.click (function () {
                    list_holder.remove();
                });
            });

            input_node.after (mydiv);
        });
    });
}) ();
