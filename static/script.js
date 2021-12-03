var file = null;
var src = null;
var image = document.getElementById('inputImage');
var embed = document.getElementById('inputPDF');

function clearFile() {
	// Clear last image/pdf display
	image.src = "";
	embed.src = "";
	embed.style.height = "0%";
	document.getElementById('fileElem').value = '';
	document.getElementById('inputPDF').style.display = 'none';
	document.getElementById('run_and_clear').style.display = 'none';
	document.getElementById('upload').style.display = 'inline-block';
}

function loadFile(f) {
	clearFile();
	file = f;
	src = URL.createObjectURL(file);
	if (file.type.substring(0, 5) == "image") {
		// Display image
		image.src = src;
	} else {
		// Display pdf
		embed.src = src;
		embed.style.height = "90%";
	}

	document.getElementById('inputPDF').style.display = 'inline-block';
	document.getElementById('run_and_clear').style.display = 'inline-flex';
	document.getElementById('upload').style.display = 'none';
}

var runModel = async function() {
	// convert image src to base64data
	const reader = new FileReader();
	let blob = await fetch(src).then(r => r.blob());
	reader.readAsDataURL(blob);
	reader.onloadend = async function() {
		base64data = reader.result;
		console.log(base64data);
		makeRequest(base64data, file.type);
	}
		
	// displays loading animation and hides latex
	document.getElementById('loading').classList.remove("hide");
	document.getElementById('containsMath').classList.add("hide");
	setTimeout(displayLatex, 2000);
};

function displayLatex() {
	// hides loading animation and displays latex
	document.getElementById('loading').classList.add("hide");
	document.getElementById('containsMath').classList.remove("hide");
}

function makeRequest(base64data, filetype) {
	fetch('/test', {
		method: 'POST', // or 'PUT'
		headers: {
		  'Content-Type': 'application/json',
		},
		body: JSON.stringify({data: base64data, filetype: filetype}),
	}).then(function (response) {
		return response.json();
	}).then(function (textObj) {
		// render new LaTeX
		var node = document.getElementById('containsMath');
		MathJax.typesetClear([node]);
		node.innerHTML = textObj.latex;
		MathJax.typesetPromise([node]).then(() => {
		});
	});
}

let dropArea = document.getElementById('drop-area');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
	dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults (e) {
	e.preventDefault();
	e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
	dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
	dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
	dropArea.classList.add('highlight');
}

function unhighlight(e) {
	dropArea.classList.remove('highlight');
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
	let dt = e.dataTransfer
	let files = dt.files

	handleFiles(files)
}

function handleFiles(files) {
	([...files]).forEach(loadFile)
}