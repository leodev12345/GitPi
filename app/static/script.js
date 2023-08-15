//function to copy specified text to clipboard that works in all browsers
function copy(text) {
	var textArea = document.createElement("textarea");
	//create a text label containing text to copy and place it in a non visible location
	textArea.value = text;

	textArea.style.top = "0";
	textArea.style.left = "0";
	textArea.style.position = "fixed";

	document.body.appendChild(textArea);
	textArea.focus();
	textArea.select();

	//copy text label contents to clipboard
	try {
		var successful = document.execCommand('copy');
		var msg = successful ? 'successful' : 'unsuccessful';
		console.log('Fallback: Copying text command was ' + msg);
	} 
	catch (err) {
		console.error('Fallback: Oops, unable to copy', err);
	}
		
	//remove text label after copied
	document.body.removeChild(textArea);
}
