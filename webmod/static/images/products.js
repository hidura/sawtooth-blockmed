$(document).ready(function() {

    // GET ALL PRODUCTS
    if ($('#products_table').val() == "") {
        var data = {
            "classname": "Items.Get",
            "category": "62"
        }

        sugelico.getServerCall(data, function(data, status){
            var currentTable;
            var editDeleteBtnTemplate = '<button class="btn btn-success edit_product left" data-id="\{id\}" data-toggle="modal" data-target="#edit_product"><i class="glyphicon glyphicon-pencil"></i></button>' +
                                        '<button class="btn btn-default delete_product" data-id="\{id\}" data-toggle="modal" data-target="#delete_product"><i class="glyphicon glyphicon-remove"></i></button>';
            
            if ($('#products_table').val() == "") {
                currentTable = $('#products_table').DataTable();

                data.forEach(function(product){
                    currentTable.row.add([
                        product.item_name,
                        product.cat_name,
                        product.status_name,
                        editDeleteBtnTemplate.replace("\{id\}", product.code).replace("\{id\}", product.code)
                    ]).draw( false );
                });

                $("#product_cat").val("62").trigger("change");
            }
        });
    }

    var data = {
        "classname": "Types.Get",
        "level": 6
    }
    sugelico.getServerCall(data, function(data, status){
        var type_options = '<option value="">Seleccione categoria</option>';

        data.forEach(function(category_type){

            type_options += '<option value="'+ category_type.code +'">'+ category_type.tpname +'</option>';
        });

        $("#product_cat").html(type_options);
    });

    if ($("#product_add_form").length > 0) {
        var data = {
            "classname": "Types.Get",
            "level": 5
        }
        sugelico.getServerCall(data, function(data, status){
            var product_units = '<option value="">Seleccione unidad</option>';

            data.forEach(function(product_unit){
                product_options += '<option value="'+ product_unit.code +'">'+ product_unit.tpname +'</option>';
            });

            $("#sale_unit").html(product_options);
        });
    
        var data = {
            "classname": "Types.Get",
            "level": 4
        }
        sugelico.getServerCall(data, function(data, status){
            var product_options = '<option value="">Seleccione tipo producto</option>';

            data.forEach(function(product_type){
                product_options += '<option value="'+ product_type.code +'">'+ product_type.tpname +'</option>';
            });

            $("#item_type").html(product_options);
        });
    }

    $("#product_add_form").submit(function(event){
        event.preventDefault();

        var data = {
            "classname": "",
            "amount": $("#amount").val(),
            "category": $("#product_cat").val(),
            "price": $("#price").val(),
            "unit_name": $("#sale_unit").val(),
            "item_type": $("#item_type").val(),
            "tax": $("#tax").val(),
            "description": $("#description").val(),
            "status": $("#status").val(),
            "item_name": $("#item_name").val()
        }

        sugelico.postServerCall(data, function(data, status){
            console.log(data);
            console.log(status);
            $("#error_alert").removeClass("hidden");
        });
    });


    // EDIT PRODUCT
    $(".edit_product").click(function () {
        var currentPruduct = $(this);
        var editProductModal = $("#edit_product");

        var callback = function(data, status){
            console.log(data);
            console.log(status);
            editProductModal.find("#item_name").val("Advil");
            editProductModal.find("#amount").val("12");
            editProductModal.find("#item_type").val("72").trigger("change");
            editProductModal.find("#product_cat").val("71").trigger("change");
        }

        sugelico.getServerCall({}, callback);

        var editProductCallback = function(data, status){
            var form = editProductModal.find("#edit_product_form");
            console.log(form.serialize());
        }

        $("#edit_product_btn").click(function(){
            sugelico.postServerCall({}, editProductCallback);
        });
    });

    $(".delete_product").click(function () {
        var currentUser = $(this);
        var deleteProductModal = $("#delete_product");

        var deleteProductCallback = function(data, status){
            console.log("eliminado");
        }

        $("#delete_product_btn").click(function(){
            deleteProductModal.modal("hide");
            var data = {
                "classname":"Users.Handle",
                "status":13, 
                code:14
            }
            sugelico.postServerCall(data, deleteProductCallback);
        });
    });

    // Filter by type and category
    $("#filter_product_report").click(function(event) {
        event.preventDefault();
        var data = {
            "product_type": $("#product_type").val(),
            "product_cat": $("#product_cat").val()
        }

        var callback = function(data, status){
            console.log(data);
        }

        sugelico.getServerCall(data, callback);

    });
});