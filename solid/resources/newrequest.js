$(document).ready(function() {

    $('#daterangepicker').daterangepicker({
	"showDropdowns": true,
	ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
	},
	"locale": {
            "format": "YYYY-MM-DD",
            "separator": " - ",
            "applyLabel": "Apply",
            "cancelLabel": "Cancel",
            "fromLabel": "From",
            "toLabel": "To",
            "customRangeLabel": "Custom",
            "weekLabel": "W",
            "daysOfWeek": [
		"Su",
		"Mo",
		"Tu",
		"We",
		"Th",
		"Fr",
		"Sa"
            ],
            "monthNames": [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December"
            ],
            "firstDay": 1
	},
    }, function(start, end, label) {
	console.log('New date range selected: ' + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD') + ' (predefined range: ' + label + ')');
    });


    $(".toggle").change(function(){
	$(".togglable[toggle~='" + this.id + "']").prop("disabled", !this.checked);
	$("select[toggle='" + this.id + "']").selectpicker("refresh");
	if (!this.checked){
	    $(".togglable[toggleoff~='" + this.id + "']").prop("disabled", true);    
	}
	else if (this.checked){
	    $(".togglable[toggleon~='" + this.id + "']").prop("disabled", false);    
	}
    });
    $.ajax({url: "/cvmfs/solidexperiment.egi.eu/el6/SolidSim",
            type: "POST",
	    data: JSON.stringify({"regex": "[vV].*", "type": "dirs"}),
	    contentType: "application/json; charset=utf-8",
	    error: function(request, status, error){
		console.warn(`Error getting SolidSim version!\nstatus: ${status}\nerror: ${error}\nrequest: ` + JSON.stringify(request))
		parent.bootstrap_alert("Attention!", `Error getting SolidSim version! status: ${status} error: ${error}`, "alert-danger");
	    },
            success: function(result) {
		console.log("successfully got SolidSim versions.");
		$.each(result, function(index, value){
		    $("#solidsim_version").append(`<option>${value}</option>`)
		});
//                $("#solidsim_version").html(result);
                $("#solidsim_version").selectpicker("refresh");
            }
	   });
    $.ajax({url: "/cvmfs/solidexperiment.egi.eu/el6/saffron2",
            type: "POST",
	    data: JSON.stringify({"regex": "[vV].*", "type": "dirs"}),
	    contentType: "application/json; charset=utf-8",
	    error: function(request, status, error){
		console.warn(`Error getting saffron2 version!\nstatus: ${status}\nerror: ${error}\nrequest: ` + JSON.stringify(request))
		parent.bootstrap_alert("Attention!", `Error getting saffron2 version! status: ${status} error: ${error}`, "alert-danger");
	    },
            success: function(result) {
		console.log("Successfully got saffron2 versions.");
		$.each(result, function(index, value){
		    $("#saffron2_ro_version").append(`<option>${value}</option>`)
		});
//                $("#saffron2_ro_version").html(result);
                $("#saffron2_ro_version").selectpicker("refresh");
            }
	   });
    $("#solidsim_version").change(function() {
//	var solidsim_macro = $("#solidsim_macro");
	var solidsim_version = $("#solidsim_version option:selected").text();
	$.ajax({url: `/cvmfs/solidexperiment.egi.eu/el6/SolidSim/${solidsim_version}/solid_g4_sim/input_macros`,
		type: "POST",
		data: JSON.stringify({"regex": ".*", "type": "files"}),
		contentType: "application/json; charset=utf-8",
		error: function(request, status, error){
		    console.warn(`Error getting macros!\nstatus: ${status}\nerror: ${error}\nrequest: ` + JSON.stringify(request))
		    parent.bootstrap_alert("Attention!", `Error getting macros! status: ${status} error: ${error}`, "alert-danger");
		},
		success: function(result) {
		    console.log("Successfully got SolidSim macros.");
		    $.each(result, function(index, value){
			$("#solidsim_macro").append(`<option>${value}</option>`)
		    });
//                    solidsim_macro.html(result);
                    $("#solidsim_macro").selectpicker("refresh");
                }
               });
    });

    $("form").submit(function(event){
	event.preventDefault();  // prevent default submission as doesn't create json content.
	var form_data = new Object();
	$.each($(this).serializeArray(), function(index, mapping){
	    form_data[mapping.name] = mapping.value;
	});

	var data = {"request":{"description": "new request"}, "parametricjobs": []};
/*	var run = 3;
	var num_jobs = 180;
	if (form_data["solidsim_inputfiletype"] == "muons-reduced"){
	    num_jobs = 100;
	}
//	for (var i=0; i<5; i++){
	for (var i=0; i<2; i++){
	    data["parametricjobs"].push({"num_jobs": 2,//num_jobs,
                        		 "solidsim_version": form_data["solidsim_version"],
					 "solidsim_macro": form_data["solidsim_macro"],
					 "solidsim_inputfiletype": form_data["solidsim_inputfiletype"],
					 "solidsim_output_lfn": form_data["solidsim_output_lfn"],
					 "seed": 310 + ((run-1) * 5) + (i+1),
//					 "jobnumber_start": run * 900 + (i*num_jobs)})
					 "jobnumber_start": run * 900 + (i*2)})
	}
*/
	var days = form_data["days"].split(" - ");
	var from_date = new Date(days[0]);
	var to_date = new Date(days[1]);
	var ndays = (to_date - from_date) / (1000 * 60 * 60 * 24);
	for (var i=0; i<(ndays+1); i++){
	    var d = new Date();
	    d.setDate(from_date.getDate() + i);
	    data["parametricjobs"].push({"num_jobs": 2,
					 "day": d.toISOString().split("T")[0]});
	}
	$.ajax({url: "/requests",
		type: "POST",
		data: JSON.stringify(data),
		contentType: "application/json; charset=utf-8",
		error: function(request, status, error){
		    console.warn(`Error submitting request!\nstatus: ${status}\nerror: ${error}\nrequest: ` + JSON.stringify(request));
		    parent.bootstrap_alert("Attention!", `Error submitting request! status: ${status} error: ${error}`, "alert-danger");
		},
		success: function(result){
		    console.log("Successfully posted request.");
		    parent.bootstrap_alert("Success!", "Request added", "alert-success");
		}
	       });
	parent.$.fancybox.close();
    });

});
