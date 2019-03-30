$( document ).ready(function() {

    function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });



    $('[name=start_date]').datepicker({
        format: "dd.mm.yyyy",
        autoclose: true
    });


    // on preview

    $("#timetable_preview").on('click', function(){
        var data = {};
        data['start_date'] = $("#form_timetable [name=start_date]").val();
        data['day_count'] = $("#form_timetable [name=day_count]").val();

        data['category_ids'] = [];
        $("#form_timetable [name=category_ids]:checked").each(function(i){
            data['category_ids'][i] = $(this).val();
        });

        data['weekdays'] = [];
        $("#form_timetable [name=weekdays]:checked").each(function(i){
            data['weekdays'][i] = $(this).val();
        });

        data['cpm'] = $("#form_timetable [name=cpm]").val();

        // data['csrfmiddlewaretoken'] = $("#form_timetable [name=csrfmiddlewaretoken]").val()

        var url = $("#form_timetable").attr('action')+'preview_json';


        $.ajax({
            method:"POST",
            url: url,
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(data),
            dataType:"json",
            processData: false,
            success: function(resp) {
                console.log('POST success ', resp);
                $("#previewBody").html("");

                $("<p>Охват расписания: " + resp.views_total + "просмотров </p>").appendTo($("#previewBody"));

                for (var w in resp.warnings) {
                    var warn = resp.warnings[w];
                    $("<div class=\"alert alert-danger\" role=\"alert\">"+warn['date']+" в категории <strong>"+warn['category']+"</strong> рекомендуется поднять цену до "+warn['recommended_cpm']+"</div>").appendTo($("#previewBody"));
                }

                $("#previewModal").modal('show');
            }
        });
        console.log('preview click ', data);
        return false;
    })

});