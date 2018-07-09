var oldprefix="";
var tabwords=new Array();
var e = null;

function getWords(data, object, info) {
    tabwords=data.split(',').reverse();
    setNextWord(object, info);
}

function canceltab(keycode) {
    if (keycode!=9) {
        return true;
    }
    return false;
}

function tc(obj,keycode) {
    if (keycode!=9) {
        oldprefix="";
        return true;
    }
    info = obj.value.split(" ");
    prefix = info.pop();
    if (prefix) {
        if (prefix == e) {
            setNextWord(obj, info);
        } else {
            oldprefix = prefix;
            $.get('/demovibes/ajax/words/'+prefix+'/', function(data){
                getWords(data, object=obj, info=info);
            });
        }
    }
    return false;
}

function setNextWord(obj, info) {
    if (tabwords.length > 0) {
        e = tabwords.pop();
        if (!e) { e = oldprefix;}
        info.push(e);
        obj.value = info.join(" ");
    } else {
        $.get('/demovibes/ajax/words/'+oldprefix+'/', function(data){
            getWords(data, object=obj, info=info);
        });
    }
}
