var data_folder = "data"; // change data folder
var num_files = 5; // possibly change num files in folder
var file_index = 0; // dont touch
var pic_folder = "imgs"; // set as null to use default

var rng = 256;
var total = rng * rng * rng;
var loaded = 0;
var current = [0,0,0];
var metadata;
var data = {};

var $load_data = $('.load_data');
var $load_progress = $('.load_progress');
var $loupe = $('#loupe');
var $img = $('#img');
var $box = $('.color-box');
var $ired = $('#input-red');
var $igreen = $('#input-green');
var $iblue = $('#input-blue');
var $jscolor;
var $inputstyle = $('#inputstyle');
var $meta = $('.info-text#metadata');
var $info = $('.info-text#img_info');

function parseData(data) {
    if(data) {
        var parsed = data.split('&');
        parsed[1] = parseInt(parsed[1]);
        parsed[2] = parseInt(parsed[2]);
        parsed[3] = parseInt(parsed[3]);
        parsed[4] = parseInt(parsed[4]);
        return parsed;
    }
    return null;
}

function map(value, srcMin, srcMax, tgtMin, tgtMax) {
    return tgtMin + (tgtMax - tgtMin) * ((value - srcMin) / (srcMax - srcMin));
}

function changeImageFolder(file) {
    var arr = file.split('/');
    return pic_folder+"/"+arr[arr.length-1];
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function extend(tgt, src) {  
    for (var key in src) tgt[key] = src[key];
}

function updateProgress(evt) {
   if (evt.lengthComputable) {
     var percentComplete = (((file_index*1.0) + (evt.loaded / evt.total))/num_files) * 100;
     $('div', $load_progress).html(Math.floor(percentComplete) + "%");
   } 
}

function loadData() {  
    var req = new XMLHttpRequest();   
    req.onprogress=updateProgress;
    req.open('GET', 'assets/'+data_folder+'/'+file_index+'.json', true);  
    // req.open('GET', 'data.json', true);
    req.onreadystatechange = function (e) {  
        if (req.readyState == 4) {
            setTimeout(function() {
                file_index++;
                if(file_index<num_files) setTimeout(loadData, 50);
                setTimeout(function() { 
                    extend(data, JSON.parse(req.responseText)); 
                    if(Object.keys(data).length == 256) {
                        setTimeout(function() { $('div', $load_progress).html("Starting..."); }, 250);
                        setTimeout(function() { init(true); }, 750);
                    } 
                }, 100);
            }, 50);
        }  
    };  
    req.send();
}

function init(loaded=false) {
    if(!loaded) {
        $load_data.fadeOut(500);
        setTimeout(function() {
            $load_progress.fadeIn(500);
        }, 500);
        // Random color init on load
        var random_r = Math.floor(Math.random() * 256);
        var random_g = Math.floor(Math.random() * 256);
        var random_b = Math.floor(Math.random() * 256);
        $jscolor = $('#colorpicker')[0].jscolor;
        $jscolor.fromRGB(random_r, random_g, random_b);

        var req = new XMLHttpRequest();   
        req.open('GET', 'assets/'+data_folder+'/metadata.json', true);  
        req.onreadystatechange = function (aEvt) {  
            if (req.readyState == 4) {  
                 metadata = JSON.parse(req.responseText);  
            }  
        };  
        req.send();
        loadData();
    }
    else {
        $load_progress.fadeOut(500);
        $meta.fadeOut(500, function() {
            updateDisplay(); 
            $img.fadeIn(500);
            $(".controls").css('height', '75vh');
            setTimeout(function() {
                $meta.html('<span class="heavy">'
                    + numberWithCommas(parseInt(metadata['assigned'])) 
                    + '</span> different color values<br>'
                    + 'represented in <span class="heavy">'
                    + numberWithCommas(parseInt(metadata['scanned'])) 
                    + '</span> different images.');
                
                $('.controls-content').fadeIn(500);
                $meta.fadeIn(500);
            },1000);
            setTimeout(function() {$('.info-text').fadeIn(500)}, 2000);
            setTimeout(updateDisplay, 500);
        });
    }       
}

function showLoupe(rgb, image) {
    if(current[0] != rgb[0] || current[1] != rgb[1] || current[2] != rgb[2]) return;
    $loupe.show();
    $loupe.css('left', $img.offset().left + parseInt($img.css('border-width')));
    $loupe.css('top', $img.offset().top + parseInt($img.css('border-width')));
    var x = map(parseInt(image[1]), 0, parseInt(image[3]), 0, $img.width());
    var y = map(parseInt(image[2]), 0, parseInt(image[4]), 0, $img.height());
    var points = "0,0 ";
    //bottom left
    points += "0," + $img.height() + " ";
    points += (x-5) + "," + $img.height() + " ";
    points += (x-5) + "," + (y-5) + " ";
    points += (x+5) + "," + (y-5) + " ";
    points += (x+5) + "," + (y+5) + " ";
    points += (x-5) + "," + (y+5) + " ";
    points += (x-5) + "," + $img.height() + " ";
    points += $img.width() + "," + $img.height() + " ";
    points += $img.width() + ",0 ";
    $('svg', $loupe).attr('height',$img.height());
    $('svg', $loupe).attr('width',$img.width());
    $($loupe).css('max-height',$img.height());
    $($loupe).css('max-width',$img.width());
    $('svg polygon#mask', $loupe).attr('points', points);

    points = (x-6) + "," + (y-6) + " ";
    points += (x+6) + "," + (y-6) + " ";
    points += (x+6) + "," + (y+6) + " ";
    points += (x-6) + "," + (y+6) + " ";
    points += (x-6) + "," + (y-6) + " ";
    $('svg polygon#outline', $loupe).attr('points', points);
    $('svg polygon#outline', $loupe).css('stroke', 'white');
}

function processImage(rgb) {
    var image = parseData(data[rgb[0]][rgb[1]][rgb[2]]);
    if(image) {
        if($img.is(':visible') && changeImageFolder(image[0]) == $img.attr('src')) {
            // same image source
            setTimeout(function() { showLoupe(rgb, image) }, 50);
        }
        else {
            // new image
            $img.remove();
            var new_src = image[0];
            if(pic_folder)
                new_src = changeImageFolder(new_src);
            $img = $("<img id='img'/>").attr('src', new_src).on('load', function() {
                if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
                    console.log('broken image!');
                } else {
                    $img.insertBefore($loupe);
                    setTimeout(function() { showLoupe(rgb, image) }, 50);
                    $meta.removeClass('info-text-freeze');
                    $info.html('<span class="lightx">X:</span><span class="heavy"> ' 
                        + image[1] + "</span>&nbsp;&nbsp;&nbsp;<span class='lightx'>Y:</span><span class='heavy'> "
                        + image[2] + "</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='heavy'>"
                        + image[0].replace(pic_folder+'/','').replace('.jpg','')+"</span><span class='lightx'>.jpg</span>");
                }
            });
        }
    }
    else {
        $img.remove();
        $loupe.hide();
    }
}

function updateDisplay(jscolor=$jscolor) {
    var red = Math.round(jscolor.rgb[0]);
    var green = Math.round(jscolor.rgb[1]);
    var blue = Math.round(jscolor.rgb[2]);
    $box.css('background','rgb('+red+','+green+','+blue+')');
    $ired.val(red);
    $igreen.val(green);
    $iblue.val(blue);
    current[0] = red;
    current[1] = green;
    current[2] = blue;
    processImage([red,green,blue]);
}

$box.on('mouseenter', function() { $jscolor.show(); });

$('.display-wrapper').on('mouseenter', function() {
    if($('.controls-content').is(':visible'))
        $jscolor.hide();
});

$loupe.on('mouseenter mouseleave', function() {
    updateDisplay();
});

function inputColor($input) {
    var val = $input.val();
    var rgb = 'rgb(rval,gval,bval)';
    if($input.attr('id') == $ired.attr('id')) {
        rgb = rgb.replace('rval', val);
        rgb = rgb.replace('gval', 0);
        rgb = rgb.replace('bval', 0);
    }
    if($input.attr('id') == $igreen.attr('id')) {
        rgb = rgb.replace('rval', 0);
        rgb = rgb.replace('gval', val);
        rgb = rgb.replace('bval', 0);
    }
    if($input.attr('id') == $iblue.attr('id')) {
        rgb = rgb.replace('rval', 0);
        rgb = rgb.replace('gval', 0);
        rgb = rgb.replace('bval', val);
    }
    $inputstyle.html('<style>.color-text ul li:before{background-color:'+rgb+'}</style>');
}

$('.controls-content li').on('mouseenter click', function() {
    if($('.controls-content').is(':visible')) {
        $jscolor.hide();
        var $input = $('input', $(this));
        $input.trigger('focus');
        inputColor($input);
    }
});

$('.controls-content li').on('mouseleave', function() {
    $('input', $(this)).trigger('blur');
});

$('.color-text li input').on('change', function() {
    var $input = $(this);
    var val = $input.val();
    if(val < 0) $input.val(0);
    if(val > 255) $input.val(255);
    inputColor($input);
    $jscolor.fromRGB($ired.val(), $igreen.val(), $iblue.val());
    updateDisplay();
});

$load_data.on('click', function(e) {
    e.preventDefault();
    init();
});