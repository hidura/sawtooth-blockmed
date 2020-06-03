var labels=[];
var values=[];
var data=[];

$(function () {


});

function addConsent(target){
    //LOAD all Users
	var consent = function (data, status) {
		console.log(data)
	}

	var data = {
        "idcard_patient": $("#_idcard_user").val(),
        "idcard_doctor":$("#consent_to_give").val(),
        "permission":$("#permission").val(),
        "time_exp":45
    }

	medicalboard.postServerCall(data, addConsent,"/grant_consent");
}