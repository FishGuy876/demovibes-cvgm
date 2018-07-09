function gen_uuid() {
    var uuid = ""
    for (var i=0; i < 32; i++) {
        uuid += Math.floor(Math.random() * 16).toString(16); 
    }
    return uuid
}

$(function() {
    $('form').submit(function(){ 
        // Prevent multiple submits
        if ($.data(this, 'submitted')) return false;

        var freq = 1000; // freqency of update in ms
        var uuid = gen_uuid(); // id for this upload so we can fetch progress info.
        var progress_url = '/webview/upload_progress/'; // ajax view serving progress info

        // Append X-Progress-ID uuid form action
        this.action += (this.action.indexOf('?') == -1 ? '?' : '&') + 'X-Progress-ID=' + uuid;
        
        var $progress = $('<div id="upload-progress" class="upload-progress"></div>').
            appendTo($("#uploadinfo")).append('<div class="progress-container"><span class="progress-info">Uploading file : 0%</span><div class="progress-bar"></div></div>');
        
        // progress bar position
        $progress.show();

        // Update progress bar
        function update_progress_info() {
            $progress.show();
            $.getJSON(progress_url, {'X-Progress-ID': uuid}, function(data, status){
                if (data) {
                    var progress = parseInt(data.uploaded) / parseInt(data.length);
                    var width = $progress.find('.progress-container').width()
                    var progress_width = width * progress;
                    $progress.find('.progress-bar').width(progress_width);
                    $progress.find('.progress-info').text('Uploading file : ' + parseInt(progress*100) + '%');
                }
                window.setTimeout(update_progress_info, freq);
            });
        };
        window.setTimeout(update_progress_info, freq);

        $.data(this, 'submitted', true); // mark form as submitted.
    });
});