var file = null;

function uploadImage() {
    document.getElementById('fileid').click();
}

var loadFile = function(event) {
	var image = document.getElementById('inputImage');
	var embed = document.getElementById('inputPDF');

	if (file != null) {
		// Clear last image/pdf display
		image.src = "";
		embed.src = "";
		embed.style.height = "0%";
	}

	file = event.target.files[0];

	if (file.type.substring(0, 5) == "image") {
		// Display image
		image.src = URL.createObjectURL(file);
	} else {
		// Display pdf
		embed.src = URL.createObjectURL(file);
		embed.style.height = "90%";
	}

	// displays loading animation
	document.getElementById('loading').classList.remove("hide");
	setTimeout(displayLatex, 2000);
};

function displayLatex() {
	// hides loading animation
	document.getElementById('loading').classList.add("hide");
}

