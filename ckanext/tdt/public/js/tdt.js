$(function() {

    var resourceDescriptors = $.Deferred();

    var resource_content = $.parseJSON($("#resource_content").text())

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
        format = format && format.toLowerCase()
        resourceDescriptors.then(function(descriptors) {
            var formatDescr = descriptors[format]
            if (formatDescr) {
                $("#tdt_inputs").empty()
                $.each(formatDescr.parameters, function(name, param) {
                    if ($.inArray(name, ["type", "uri", "description", "title"]) == -1) {
                        var tdtname = "tdt-" + name
                        var id = "field-" + tdtname
                        var inputField = $("<input type='text'>").attr("id", id).attr("name", tdtname).attr("placeholder", param.description)
                        if (resource_content[tdtname] && resource_content[tdtname].length>0) inputField.val(resource_content[tdtname])
                        var inputDiv = $('<div class="control-group control-full"/>')
                            .append($('<label class="control-label"/>').attr("for", id).text(name))
                            .append($('<div class="controls"/>').append(inputField))

                        $("#tdt_inputs").append(inputDiv)
                    }
                })
            }
        })
    }

    var TDT = this.TDT = {
        initTDT: function(tdtRootUrl) {
            $.ajax({
                cache: true,
                url: tdtRootUrl+'discovery',
                dataType: "json",
                success: function(data) {
                    resourceDescriptors.resolve(data.resources.definitions.methods.put.body)
                }
            });

            this.checkTDTFieldsDisplay()
            displayFields($("#field-format").val())

            $("#field-format").change(function(e) {
                displayFields(e.val)
            })
        },

        checkTDTFieldsDisplay: function() {
            if ($("#field-enable-tdt").is(':checked')) $("#tdt_inputs").show()
            else $("#tdt_inputs").hide()
        }
    }

    TDT.initTDT(TDT_HOST)

})