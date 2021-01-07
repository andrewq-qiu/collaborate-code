/*JS File for adding the Whiteboard to the code editor*/

var wb_elem = document.createElement('div');
wb_elem.classList.add('whiteboard');
// Add the whiteboard to the body
document.body.appendChild(wb_elem);

// Initialize the WhiteBoard object
var wb = new WhiteBoard(wb_elem);

// ===============================

// Create a toggle to switch between
// the whiteboard and editor

var toggle = document.createElement('div');
toggle.classList.add('toggle');
document.body.appendChild(this.toggle);

// Enable the editor first
wb.freeze();
toggle.state = true;
wb.toolbar.element.classList.add('hide');
wb.toolbar.color_button.classList.add('hide');

/*Toggle between using the editor and whiteboard*/
function toggleEditorAndBoard(){
    // Toggle state
    toggle.state = !toggle.state;
    
    if (!toggle.state){
        toggle.classList.add('toggle-off');
        wb.toolbar.element.classList.remove('hide');
        wb.toolbar.color_button.classList.remove('hide');
        wb.unfreeze();
    }else{
        toggle.classList.remove('cb-toggle-off');
        wb.toolbar.element.classList.add('hide');
        wb.toolbar.color_button.classList.add('hide');
        wb.freeze();
    }
}


/*Add Listeners for toggle*/
toggle.addEventListener('click', toggleEditorAndBoard);
document.addEventListener("keydown", function(event) {
    const key = event.key;

    if (key === "Escape") {
        toggleEditorAndBoard();
    }
});