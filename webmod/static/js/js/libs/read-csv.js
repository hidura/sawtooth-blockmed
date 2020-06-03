var lines = [];
var datatype="";
function handleFiles(files) {
	// Check for the various File API support.
	if (window.FileReader) {
		// FileReader are supported.
		getAsText(files[0]);
	} else {
		alert('FileReader are not supported in this browser.');
	}
}

function getAsText(fileToRead) {
	var reader = new FileReader();
	// Handle errors load
	reader.onload = loadHandler;
	reader.onerror = errorHandler;
	// Read file into memory as UTF-8
	reader.readAsText(fileToRead);
}

function loadHandler(event) {
	var csv = event.target.result;
	processData(csv);
}

function processData(csv) {
    var allTextLines = csv.split(/\r\n|\n/);
    while (allTextLines.length) {
        lines.push(allTextLines.shift().split(';'));
    }
	drawOutput(lines);
}

function errorHandler(evt) {
	if(evt.target.error.name == "NotReadableError") {
		alert("Canno't read file !");
	}
}

function save(target_btn) {
	if (datatype==="products"){
		$.each(lines, function (index, line) {
			if (index>0){
				data = {status:11,amount:0,
				item_name:line[0],barcode:line[1],
				category:line[2],price:parseFloat(line[7]),
					supplier:line[8],description:line[10],
				price1:parseFloat(line[11]),price2:parseFloat(line[12]),
				price3:parseFloat(line[13]),price4:parseFloat(line[14]),
					initial_cost:parseFloat(line[15]),
				"classname":"Items.create_massive"};
				sugelico.postSyncServerCall(data, function(data, status){
					if (data.code){
						$('tbody').children()[index].insertCell(0).appendChild($('<button class="btn btn-success" ><i class="glyphicon glyphicon-check"></i></button>')[0])
					}else{
						$('tbody').children()[index].insertCell(0).appendChild($('<button class="btn btn-danger" ><i class="glyphicon glyphicon-remove"></i></button>')[0])
						console.log(data);
					}



				});
			}

		});
	}else {
		$.each(lines, function (index, line) {
			if (index>0){
				console.log(datatype);
				data = {status:11,
				cl_name:line[0],price:parseInt(line[8]),
				"classname":"Clients.create"};
				sugelico.postSyncServerCall(data, function(data, status){
					if (data.code){
						$('tbody').children()[index].insertCell(0).appendChild($('<button class="btn btn-success" ><i class="glyphicon glyphicon-check"></i></button>')[0])
					}else{
						$('tbody').children()[index].insertCell(0).appendChild($('<button class="btn btn-danger" ><i class="glyphicon glyphicon-remove"></i></button>')[0])
						console.log(data);
					}



				});
			}

		});
	}


}

function drawOutput(lines){
	//Clear previous data
	document.getElementById("output").innerHTML = "";
	var table = document.createElement("table");
	for (var i = 0; i < lines.length; i++) {
		var row = table.insertRow(-1);

		for (var j = 0; j < lines[i].length; j++) {
			var firstNameCell = row.insertCell(-1);
			firstNameCell.appendChild(document.createTextNode(lines[i][j]));
		}
	}
	document.getElementById("output").appendChild(table);

	$(table).addClass("table table-hover display dataTable");
}