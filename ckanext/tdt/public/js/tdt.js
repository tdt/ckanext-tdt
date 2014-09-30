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

    var displayFields = function(format, mandatoryParams) {
        format = format && format.toLowerCase()
        resourceDescriptors.then(function(descriptors) {
            var formatDescr = descriptors[format]
            if (formatDescr) {
                $("#tdt_block").show()
                $("#tdt_required_inputs").empty()
                $("#tdt_optional_inputs").empty()
                $.each(formatDescr.parameters, function(name, param) {
                    if ($.inArray(name, ["type", "uri", "description", "title"]) == -1) {
                        var tdtname = "tdt-" + name
                        var id = "field-" + tdtname
                        var inputField = $("<input type='text'>").attr("id", id).attr("name", tdtname).attr("placeholder", param.description)

                        inputField.change(createInputValidator(param))

                        if (resource_content[tdtname] && resource_content[tdtname].length>0) inputField.val(resource_content[tdtname])
                        inputField.change()

                        var inputDiv = $('<div class="control-group control-full"/>')
                            .append($('<label class="control-label"/>').attr("for", id).text(param.name || name))
                            .append($('<div class="controls"/>').append(inputField))

                        inputDiv.toggleClass('optional', !param.required);


                        if (param.required || (mandatoryParams && $.inArray(name, mandatoryParams) != -1))
                            $("#tdt_required_inputs").append(inputDiv)
                        else
                            $("#tdt_optional_inputs").append(inputDiv)
                    }
                })
            } else
                $("#tdt_block").hide()

            toggleOptionalInputs($("#tdt_required_inputs").children().length == 0)
        })
    }

    var toggleOptionalInputs = function(toggle) {

        if (toggle === undefined) toggle = !$("#tdt_optional_inputs").is(":visible")

        if (toggle) {
            $("#tdt_optional_toggle").toggleClass('displayed', true)
            $("#tdt_optional_inputs").show()
        } else {
            $("#tdt_optional_toggle").toggleClass('displayed', false)
            $("#tdt_optional_inputs").hide()
        }
    }

    var createInputValidator = function(paramDescriptor) {
         return function(evt) {
             var val = $(this).val()
             var msg
             if (paramDescriptor.required && (!val || val == '')) msg = 'Value required'
             else if (paramDescriptor.type == 'integer' && val && isNaN(parseInt(val))) msg = 'Value must be an integer'

             $(this).toggleClass("missingValue",  msg !== undefined)
             $(this).prop('title',msg)
         }
    }

    var TDT = this.TDT = {
        initTDT: function(tdtRootUrl, mandatoryParams) {
            this.mandatoryParams = mandatoryParams

            $.ajax({
                cache: true,
                url: tdtRootUrl+'discovery',
                dataType: "json",
                success: function(data) {
                    resourceDescriptors.resolve(data.resources.definitions.methods.put.body)
                }
            });

            this.checkTDTFieldsDisplay()
            displayFields($("#field-format").val(), this.mandatoryParams)

            var _this = this

            $("#field-format").change(function(e) {
                displayFields(e.val, _this.mandatoryParams)
            })

        },

        checkTDTFieldsDisplay: function() {
            if ($("#field-enable-tdt").is(':checked')) $("#tdt_inputs").show()
            else $("#tdt_inputs").hide()
        },

        displayOptionalInputs: function(toggle) {

            toggleOptionalInputs(toggle)
        }
    }

    TDT.initTDT(TDT_HOST, TDT_MANDATORY_PARAMS)

})