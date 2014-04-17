$(function() {

    var resourceDescriptors = $.Deferred();
    $.ajax({
        cache: true,
        url: "http://tdt-001.iminds.openminds.be/discovery",
        dataType: "json",
        success: function(data) {
            resourceDescriptors.resolve(data.resources.definitions.methods.put.body)
        }
    });

    /*
    ResourceDescriptors of the form:
    {
     description: "A language of the resource."
     group: "dc"
     list: "api/languages"
     list_option: "name"
     name:
     required: true|false
     type: "list"
     default_value :
     }

     */

    var displayFields = function(format) {
        resourceDescriptors.then(function(descriptors) {
            var formatDescr = descriptors[format]
            if (formatDescr) {
                $("#tdt_inputs").empty()
                $.each(formatDescr.parameters, function(name, param) {
                    if ($.inArray(name, ["type", "uri", "description", "title"]) == -1) {
                        var id = "field-tdt-" + name
                        var inputField = $("<input type='text'>").attr("id", id).attr("name", name).attr("placeholder", param.description)
                        var inputDiv = $('<div class="control-group control-full"/>')
                            .append($('<label class="control-label"/>').attr("for", id).text(name))
                            .append($('<div class="controls"/>').append(inputField))

                        $("#tdt_inputs").append(inputDiv)
                    }
                })
            }
        })
    }

    $("#field-format").change(function(e) {
        displayFields(e.val)
    })
})