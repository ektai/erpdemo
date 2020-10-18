frappe.ready(() => {
	$(".hero .btn-primary").on("click", (e) => {
		e.preventDefault();
		accueillogin("thierry@dokos.io", "tierslieux", "desk")
	});
	
	 $(".hero .btn-primary-light").on("click", (e) => {
		e.preventDefault();
		accueillogin("francis@dokos.io", "tierslieux", "me")
	});

	if (window.location.pathname == "/login") {
		if (localStorage.getItem("last_visited") && frappe.session.user == "Guest") {
			accueillogin("francis@dokos.io", "tierslieux", localStorage.getItem("last_visited")) 
		} else {
			window.location.href = "/";   
		}
	}
});

const accueillogin = (username, password, target) => {
	frappe.call({
		"method": "login",
		args: {
			usr: username,
			pwd: password
		}
	}).then(r => {
		if(r.exc) {
			alert(__("Error, please contact help@dokos.io"));
		} else {
			console.log("Logged in");
			window.location.href = target;
		}
	})
}