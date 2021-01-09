/*This file implements a working smooth-line
drawing canvas (whiteboard) using HTML/CSS/JS.

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
*/


/**
 * @class
 * A class representing a two dimensional position
 */
class Pos{
    constructor(x, y){
        this.x = x;
        this.y = y;
    }
}

/**
 * @class
 * A class representing a whiteboard
 */
class WhiteBoard{

    /**
     * Construct a new whiteboard
     * @param {HTMLElement} wb_elem - The HTML div for the whiteboard
     */
    constructor(wb_elem){
        // Draw Functions

        this.container = wb_elem;
        this.container.classList.add('wb-container');
        this.initializeCanvas();
        this.initializeToolbar();

        this.color = '#d1d1d1';
        this.selectedColor = '#d1d1d1';

        this.strokeIndex = 0;

        this.initializeListeners();
        this.last_mouse_state = 0;

        this.fillScreen();
        this.recentPoints = [];
    }

    /**
     * Initialize the canvas of the whiteboard
     * This method should only be used in the initialization
     * process of the whiteboard and should not be called outside
     * the class constructor.
     */
    initializeCanvas(){
        this.canvas = document.createElement('canvas');
        this.canvas.classList.add('wb-canvas');
        this.canvas.classList.add('wb-canvas-cursor-mode');
        this.container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');

        this.memCanvas = document.createElement('canvas');
        this.memCtx = this.memCanvas.getContext('2d');
        this.memCanvas.width = 8000;
        this.memCanvas.height = 8000;
    }

    /**
     * Initialize the toolbar of the whiteboard
     * This method should only be used in the initialization
     * process of the whiteboard and should not be called outside
     * the class constructor.
     */
    initializeToolbar(){
        this.toolbar = {};
        this.toolbar.element = document.createElement('div');
        this.toolbar.element.classList.add('wb-toolbar')
        this.toolbar.buttonElements = {};

        let button_types = [
            'wb-move-button',
            'wb-brush-button',
            'wb-eraser-button'
        ]

        for (let button of button_types){
            var button_element = document.createElement('div');
            button_element.classList.add(button);
            button_element.toolbar = this.toolbar;
            button_element.whiteboard = this;
            button_element.tool_type = button;

            button_element.onclick = function(e){
                var source = e.target;
                source.toolbar.buttonElements[source.toolbar.selected_tool].classList.remove('wb-button-selected');
                source.toolbar.selected_tool = source.tool_type;
                source.classList.add('wb-button-selected');
                
                if (source.tool_type == 'wb-eraser-button' || source.tool_type == 'wb-brush-button'){
                    source.whiteboard.canvas.classList.add('wb-canvas-cursor-mode');
                }else{
                    source.whiteboard.canvas.classList.remove('wb-canvas-cursor-mode');
                }
            }

            this.toolbar.buttonElements[button] = button_element;
            this.toolbar.element.appendChild(button_element);
        }
        
        this.toolbar.selected_tool = button_types[1];
        this.toolbar.buttonElements[button_types[1]].classList.add('wb-button-selected');

        this.container.appendChild(this.toolbar.element);

        // Add Color Picking Button
        var color_button = document.createElement('div');
        color_button.classList.add('wb-color-button');
        
        var color_circle = document.createElement('div');
        color_circle.classList.add('wb-color-circle');
        color_circle.style.backgroundColor = '#d1d1d1';

        color_button.appendChild(color_circle);
        
        color_button.colors = ['#d1d1d1', '#f54542', '#42a4f5', '#5af542'];
        color_button.index = 0;
        color_button.whiteboard = this;
        
        color_button.onclick = function(e){
            var source = e.target.className == 'wb-color-circle' ? e.target.parentElement : e.target;
            let colors = source.colors;
            source.index = (source.index + 1) % colors.length;

            source.firstChild.style.backgroundColor = colors[source.index];
            source.whiteboard.selectedColor = colors[source.index];

            if(source.whiteboard.recentPoints.length == 0){
                source.whiteboard.color = colors[source.index];
            }
        };

        this.toolbar.color_button = color_button;
        this.container.appendChild(color_button);
        
    }

    /**
     * Fill the screen to the window
     */
    fillScreen = e => {
        this.resize(window.innerWidth, window.innerHeight);
    }

    /**
     * Initialize the event listeners of the whiteboard
     * This method should only be used in the initialization
     * process of the whiteboard and should not be called outside
     * the class constructor.
     */
    initializeListeners(){
        this.canvas.addEventListener('mousemove', this.handleMouseMove);
        this.canvas.addEventListener('mousedown', this.handleMouseDown);
        this.canvas.addEventListener('mouseup', this.handleMouseUp);
        this.canvas.addEventListener('mouseenter', this.setPosition);
        // this.canvas.addEventListener('wheel', this.zoom);
        window.addEventListener('resize', this.fillScreen);
    }

    /**
     * Handle the mousedown event on the whiteboard
     * 
     * @param {any} e - The mouse event
     */
    handleMouseDown = e => {
        if(this.toolbar.selected_tool != 'wb-brush-button' && this.toolbar.selected_tool != 'wb-eraser-button'){return;}

        this.setPosition(e);
        this.last_mouse_state = 1;
        this.recentPoints.push(this.pos);
    }

    /**
     * Handle the mouseup event on the whiteboard
     * 
     * @param {any} e - The mouse event
     */
    handleMouseUp = e => {
        // Add new line to push to server

        if (this.toolbar.selected_tool == 'wb-brush-button'){
            var points = [];
            for(let point of this.recentPoints){points.push([point.x, point.y]);}

            this.lines_to_send.push(['DRAW', points, this.color]);

            this.smoothDraw(this.memCtx, 'source-over', this.recentPoints, 6, this.color);
        }else{
            var points = [];
            for(let point of this.recentPoints){points.push([point.x, point.y]);}

            this.lines_to_send.push(['ERASE', points]);

            this.smoothDraw(this.memCtx, 'destination-out', this.recentPoints, 25);
        }

        this.recentPoints = [];
        this.color = this.selectedColor;
        this.last_mouse_state = 0;
    }

    /**
     * Update the mouse position saved into the whiteboard
     * using an event.
     * 
     * @param {any} e - The mouse event
     */
    setPosition = e =>{
        let rect = e.target.getBoundingClientRect();
        this.pos = new Pos(e.clientX - rect.left, e.clientY - rect.top);
    }

    /**
     * Resize the whiteboard given
     * a width and height.
     * 
     * @param {any} w - The width to resize to
     * @param {any} h - The height to resize to
     */
    resize(w, h){
        this.container.width = w;
        this.container.height = h;

        this.canvas.width = w;
        this.canvas.height = h;

        this.ctx.drawImage(this.memCanvas, 0, 0);
    }

    /**
     * Disable the controls of the whiteboard
     */
    freeze(){
        this.frozen = true;
        this.container.classList.add('clickthrough');
    }

    /**
     * Enable the controls of the whiteboard
     */
    unfreeze(){
        this.frozen = false;
        this.container.classList.remove('clickthrough');
    }

    /**
     * Erase a part of the whiteboard givne
     * a new mouse event
     * 
     * @param {any} e - The mouse event
     */
    erase = e => {
        this.setPosition(e);
        this.recentPoints.push(this.pos);

        // Reload from memory first
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.memCanvas, 0, 0);

        this.smoothDraw(this.ctx, 'destination-out', this.recentPoints, 25);
    }

    /**
     * Handle the mousemove event on the whiteboard
     * 
     * @param {any} e - The mouse event
     */
    handleMouseMove = e => {
        if(this.frozen) return;
        if (e.buttons !== 1){  
            // Ignore if LMB is not Pressed
            this.setPosition(e);
            return;
        }

        switch(this.toolbar.selected_tool){
            case 'wb-move-button':
                this.moveCamera(e);
                break;
            case 'wb-brush-button':
                this.fillScreen();
                this.draw(e);
                break;
            case 'wb-eraser-button':
                this.fillScreen();
                this.erase(e);
                break;
        }
    }

    /**
     * Draw a part of the whiteboard givne
     * a new mouse event
     * 
     * @param {any} e - The mouse event
     */
    draw = e => {
        this.setPosition(e);
        this.recentPoints.push(this.pos);

        // Reload from memory first
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.memCanvas, 0, 0);

        this.smoothDraw(this.ctx, 'source-over', this.recentPoints, 6, this.color);
    }

    /**
     * Smoothly draw or erase given an array of points.
     * 
     * @param {CanvasRenderingContext2D} ctx - The context to draw/erase on
     * @param {string} ctx_mode - The mode of the context (destination-out, source-over)
     * @param {Array} points - The array of points to draw/erase
     * @param {number} lineWidth - The width of the line
     * @param {string} color - The color of the line
     */
    smoothDraw(ctx, ctx_mode, points, lineWidth, color){
        // mouse left button must be pressed
        // if (e.buttons !== 1) return;
        
        // Set to ADD mode
        ctx.globalCompositeOperation=ctx_mode;
        ctx.lineWidth = lineWidth;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        if(points.length < 6){
            // Draw circle instead
            var b = points[0];
            ctx.beginPath();
            ctx.arc(b.x, b.y, ctx.lineWidth / 2, 0, Math.PI * 2, !0);
            ctx.closePath();
            ctx.fill();
            return;
        }

        ctx.beginPath(); // begin
        ctx.strokeStyle = color;

        // start point
        ctx.moveTo(points[0].x,points[0].y);

        // draw a bunch of quadratics, using the average of two points as the control point
        for (var i = 1; i < points.length - 2; i++) {
            var c = (points[i].x + points[i + 1].x) / 2;
            var d = (points[i].y + points[i + 1].y) / 2;
            ctx.quadraticCurveTo(points[i].x, points[i].y, c, d);
        }

        ctx.quadraticCurveTo(points[i].x, points[i].y, points[i + 1].x, points[i + 1].y);
        ctx.stroke();
    }

    /**
     * Add new lines from a JSON string
     * 
     * @param {data} - The JSON string storing an Array of lines to add
     */
    addLines(data){
        var lines = JSON.parse(data);

        for (let line of lines){
            let type = line[0];
            var points = [];
        
            for (let point of line[1]){
                points.push(new Pos(point[0], point[1]));
            }
            
            if(type == 'ERASE'){
                this.smoothDraw(this.ctx, 'destination-out', points, 25);
                this.smoothDraw(this.memCtx, 'destination-out', points, 25);

            }else if(type == 'DRAW'){
                let color = line[2];

                this.smoothDraw(this.ctx, 'source-over', points, 6, color);
                this.smoothDraw(this.memCtx, 'source-over', points, 6, color);
            }
        }
        this.waiting_for_server = false;
    }

    /**
     * Initialize server support for collaboartive editing.
     * Ensure that a global socket is defined before initializing
     * the server functions for the whiteboard.
     */
    setupServer(){
        this.waiting_for_server = false;
        this.lines_to_send = [];

        socket.on('draw-call-back', (data) => {
            this.addLines(data);
        });

        
        // Set to update server
        setTimeout(this.updateServer.bind(this), 1000);
    }

    /**
     * Update loop for sending lines to the server
     * or updating the client to any lines made by
     * other users.
     */
    updateServer(){
        if(!this.waiting_for_server){
            socket.emit('send-drawing', JSON.stringify(this.lines_to_send));
            this.waiting_for_server = true;
        }

        setTimeout(this.updateServer.bind(this), 1000);
    }
}