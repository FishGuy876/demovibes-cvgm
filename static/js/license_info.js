var il = $("#id_license");
var txt = "Select a license for more information about it.";

il.closest("form").before($("<div id='lic-info'>"+txt+"</div>"));
il.change( function(i) {
    if ($(this).val()) {
        $("#lic-info").text("Fetching..");
        $("#lic-info").load("/demovibes/ajax/license/"+$(this).val()+"/");
    } else {
        $("#lic-info").text(txt);
    }
});
