/*This file handles adding the whiteboard.js
implementation of an HTML/CS/JS whiteboard
onto the editor.

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
*/

/*=================================================

** Whiteboard Creation **
*/

// Create the whiteboard HTML element 
// and attach it to the page
var wb_elem = document.createElement('div');
wb_elem.classList.add('whiteboard');
document.body.appendChild(wb_elem);

// Initialize the WhiteBoard object
var wb = new WhiteBoard(wb_elem);

/*=================================================

** Toggle Implementation **
*/

// Create a toggle to switch between the whiteboard
// and the code editor
var toggle = document.createElement('div');
toggle.classList.add('toggle');
document.body.appendChild(this.toggle);

// Enable the editor first
wb.freeze();
toggle.state = true;
wb.toolbar.element.classList.add('hide');
wb.toolbar.color_button.classList.add('hide');

/**
 * Toggle between the code editor
 * and the whiteboard
 */
function toggleEditorAndBoard(){
    // Toggle state
    toggle.state = !toggle.state;
    
    if (!toggle.state){
        toggle.classList.add('toggle-off');
        wb.toolbar.element.classList.remove('hide');
        wb.toolbar.color_button.classList.remove('hide');
        wb.unfreeze();
    }else{
        toggle.classList.remove('toggle-off');
        wb.toolbar.element.classList.add('hide');
        wb.toolbar.color_button.classList.add('hide');
        wb.freeze();
    }
}

// Add event listeners for the toggle activation
toggle.addEventListener('click', toggleEditorAndBoard);
document.addEventListener("keydown", function(event) {
    const key = event.key;

    if (key === "Escape") {
        toggleEditorAndBoard();
    }
});