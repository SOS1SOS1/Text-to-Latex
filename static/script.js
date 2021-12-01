var file = null;
var image = document.getElementById('inputImage');
var embed = document.getElementById('inputPDF');

function uploadImage() {
    document.getElementById('fileid').click();
}

function clearFile() {
	if (file != null) {
		// Clear last image/pdf display
		image.src = "";
		embed.src = "";
		embed.style.height = "0%";
	}
}

function clearAndDisable() {
	clearFile();
	document.getElementById('clear').disabled = true;
}

var loadFile = async function(event) {
	clearFile();
	file = event.target.files[0];
	let src = URL.createObjectURL(file);
	if (file.type.substring(0, 5) == "image") {
		// Display image
		image.src = src;
	} else {
		// Display pdf
		embed.src = src;
		embed.style.height = "90%";
	}

	const reader = new FileReader();
	let blob = await fetch(src).then(r => r.blob());
	reader.readAsDataURL(blob);
	reader.onloadend = async function() {
		base64data = reader.result;
		console.log(base64data);
		makeRequest(base64data, file.type);
	}

	document.getElementById('clear').disabled = false;

};

function makeRequest(base64data, filetype) {
	fetch('/test', {
		method: 'POST', // or 'PUT'
		headers: {
		  'Content-Type': 'application/json',
		},
		body: JSON.stringify({data: base64data, filetype: filetype}),
	})
	.then(function (response) {
		return response.json();
	}).then(function (textObj) {
		console.log('response:');
		var node = document.getElementById('containsMath');
		MathJax.typesetClear([node]);
		node.innerHTML = textObj.latex;
		MathJax.typesetPromise([node]).then(() => {
		// the new content is has been typeset
		});
	});
}
