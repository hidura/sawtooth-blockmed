var types={};

var medicalboard = {
    route:"http://localhost:8041/api/",
    type:types,
    postServerCall: function(data, callback, route) {
        $.ajax({
                url: route,
                data: JSON.stringify(data),
                contentType: "application/json",
                type: 'POST',
                success: callback
            }
        );

    },
    postSyncServerCall: function(data, callback) {
        $.ajax({
                url: sugelico.route,
                data:  JSON.stringify(data),
                contentType: "application/json",
                type: 'POST',
                success: callback
            }
        );
    },
    getServerCall: function(data, callback) {
        $.get(data, callback);
    },
    openDialog:function (title, message, buttons, classname, afterload){
            /*
            This function, receives the title, the message(can be html or string), and the buttons.
             */

            if (classname==undefined){
                    classname="medium"
                }
                bootbox.dialog({
                        title: title,
                        message: message,
                        buttons: buttons,
                        size: classname
                    }
                );
                if (afterload!==undefined){
                    afterload()
                }

        },
    getTypes:function(target, type) {
        success=function (result,status,xhr) {
            if (target != null){
                JSON.parse(result).forEach(function (field, index) {
                    $(target).append($('<option />').val(field.code).html(field.tpname));
                });

            }
            $(target).select2({
                    height: "40px"
            });
        };
        error = function (xhr,status,error){
            console.log(error);
        };
        sugelico.getServerCall("classname=Types.Get&level="+type,success, error);
    },
    activateTableWithDataTable: function(table_name, tableTitle, printableColumns){
        $(table_name).DataTable({
            "language": {
                "lengthMenu": "Mostrar _MENU_ registros por pagina",
                "zeroRecords": "No se encontraron registros. Verificar que el text esta bien escrito.",
                "info": "Mostrando pagina _PAGE_ of _PAGES_",
                "infoEmpty": "No hay registros disponibles.",
                "infoFiltered": "(De _MAX_ registros existentes.)",
                "search": "Buscar",
                "paginate": {
                    "first": "Primero",
                    "last": "Último",
                    "next": "Siguiente",
                    "previous": "Anterior"
                }
            },
            dom: 'B<"clear">lfrtip',

            buttons: {
                name: 'primary',
                buttons: [ 
                    'copy', 'csv', 'excel',
                    {
                        extend: 'pdf',
                        title: tableTitle,
                        text: 'PDF',
                        exportOptions: {
                            columns: printableColumns
                        }
                    },
                    {
                        extend: 'print',
                        title: tableTitle,
                        text: 'Print',
                        autoPrint: true,
                        exportOptions: {
                            columns: printableColumns
                        }
                    }
                ]
            }

        });
    },
    getCookie:function(cname)
{
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
},
    activateTableWithDataTableWithoutBtns: function(table_name){
        $(table_name).DataTable({
            "language": {
                "lengthMenu": "Mostrar _MENU_ por página",
                "zeroRecords": "No se encontraron registros. Verificar que el text está bien escrito.",
                "info": "Mostrando página _PAGE_ of _PAGES_",
                "infoEmpty": "No hay registros disponibles.",
                "infoFiltered": "(De _MAX_ registros existentes.)",
                "search": "Buscar",
                "paginate": {
                    "first": "Primero",
                    "last": "Último",
                    "next": "Siguiente",
                    "previous": "Anterior"
                }
            }
        });
    },
    addInputDateSupport: function(){
        $(".date").each(function(index, input){
            $(input).datepicker({
              dateFormat: "dd/mm/yy",
              altFormat: "dd/mm/yy"
            });
        });
    },
    webservices:{user_get:"login.Get"},
    numberWithCommas:function (x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    numberWithOutCommas:function (x) {
        return x.toString().replace(",", "");
    },

    getParameterByName:function(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    },

    loadCategories:function(target, type) {
        var catype="";
        if (type!==undefined){
            catype+='&cat_type='+type;
        }
        $.ajax({
            url: '/?classname=Categories.Get'+catype,
            type: 'get',
            processData: false,
            contentType: false,
            success: function (data) {
                $(target).empty().append("<option value='0'>Seleccione uno</option>");

                JSON.parse(data).forEach(function(piece, index){
                    $(target).append($("<option/>").val(piece.code).html(piece.cat_name));
                });
            }
        });
    },
    getSelectedValue:function (select) {
            var result = {};
            var options = select && select.options;
            var opt;

            for (var i=0, iLen=options.length; i<iLen; i++) {
                opt = options[i];

                if (opt.selected) {
                    result[opt.value] = opt.text;
                }
            }
            return result;
    }
};

$(document).ready(function() {


    
});
