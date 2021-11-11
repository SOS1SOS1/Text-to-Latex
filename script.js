function uploadImage() {
    document.getElementById('fileid').click();
}

var loadFile = function(event) {
	var image = document.getElementById('output');
	image.src = URL.createObjectURL(event.target.files[0]);
};