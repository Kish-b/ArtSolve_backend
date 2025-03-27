*{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: black;
    color: white;
    text-align: center;
    font-family: Arial, sans-serif;
    margin: 0;
}

.canvas-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 auto;
    max-width: 100%;
    height: 100vh;
}

canvas {
    background-color: black;
    cursor: none;
    touch-action: none;
    image-rendering: -moz-crisp-edges;
    image-rendering: -webkit-crisp-edges;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    width: 100%;
    height: 100%;
}

.logo{
    position: absolute;
    top: 30px;
    left: 40px;
}

.output-display {
    font-size: 18px;
    width: 80%;
    padding: 10px;
    border: 1px solid #ffffff;
    border-radius: 10px;
    background-color: #000000;
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    margin-top: 90px;
}

.tools_container{
    width: 100px;
    height: auto;
    background-color: #393944;
    position: absolute;
    left: 70px;
    top:250px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0;
    gap: 15px;
}

button {
    border: none;
    cursor: pointer;
    border-radius: 25px;
    transition: all 0.2s;
    font-weight: bold;
    letter-spacing: 0.5px;
}

.tool_button{
    width: 60px;
    height: 60px;
    background-color: #27272e;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.tool_button svg{
    width: 40px;
    height: auto;
}

.pen-controls, .eraser-controls, .color-palette {
    display: none;
    opacity: 0;
    transition: opacity 0.2s ease, visibility 0.2s ease;
    visibility: hidden;
}

.pen-controls.active, .eraser-controls.active, .color-palette.active {
    display: flex;
    opacity: 1;
    visibility: visible;
}

.pen-controls {
    position: absolute;
    left: 120px;
    background-color: #393944;
    padding: 20px;
    flex-direction: column;
    border-radius: 14px;
    gap: 20px;
    z-index: 10;
}

.eraser-controls {
    position: absolute;
    left: 120px;
    background-color: #393944;
    padding: 20px;
    flex-direction: column;
    border-radius: 14px;
    gap: 20px;
    z-index: 10;
}

.color-palette {
    position: absolute;
    left: 120px;
    background-color: #393944;
    padding: 20px;
    border-radius: 14px;
    /* flex-wrap: wrap; */
    gap: 10px;
    flex-direction: row;
    z-index: 10;
}

.single{
    display: flex;
    align-items: center;
    position: relative;
}

.pen-controls div{
    display: flex;
    width: 100%;
    justify-content: space-between;
}

.eraser-controls div{
    display: flex;
    width: 100%;
    justify-content: space-between;
}

.colorButtondiv{
    display: flex;
    width: 100%;
    justify-content: space-between;
}

.color-option {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.color-option:hover {
    transform: scale(1.15);
}

.color-option.active {
    border-color: white;
    transform: scale(1.15);
    box-shadow: 0 0 1px #fff, 0 0 10px rgba(255,255,255,0.5);
}

.color-option.white { background-color: #ffffff; }
.color-option.red { background-color: #ff0000; }
.color-option.green { background-color: #1b8434; }
.color-option.lightblue { background-color: #45A2FF; }
.color-option.yellow { background-color: #ffff00; }
.color-option.orange { background-color: #FF7D04; }

#brushSize, #eraserSize {
    width: 180px;
    -webkit-appearance: none;
    height: 8px;
    background: #555;
    border-radius: 4px;
    outline: none;
}

#brushSize::-webkit-slider-thumb,
#eraserSize::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
}

#brushSize::-webkit-slider-thumb:hover,
#eraserSize::-webkit-slider-thumb:hover {
    transform: scale(1.1);
}

#brushSizeValue, #eraserSizeValue {
    display: inline-block;
    width: 30px;
    text-align: center;
    font-family: monospace;
    font-weight: bold;
}

.buttons button{
    padding:18px 100px;
    background-color: #292933;
    border-radius: 20px;
    color: #ffffff;
    font-size: 18px;
}

.buttons{
    display: flex;
    align-items: center;
    gap: 15px;
    position: absolute;
    bottom: 40px;
}

.tool-button.active {
    background-color:#141422;
    box-shadow: 0 0 0 2px #444, 0 4px 8px rgba(0,0,0,0.2);
}

.cursor {
    position: absolute;
    pointer-events: none;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    mix-blend-mode: difference;
    z-index: 100;
    border: 1px solid rgba(255,255,255,0.5);
}

.pen-cursor {
    background-color: white;
}

.eraser-cursor {
    background-color: black;
    border: 1px solid white;
}

.pen-cursor.white { background-color: #ffffff; }
.pen-cursor.red { background-color: #ff0000; }
.pen-cursor.green { background-color: #00ff00; }
.pen-cursor.lightblue { background-color: #00ffff; }
.pen-cursor.yellow { background-color: #ffff00; }
.pen-cursor.orange { background-color: #ffa500; }

.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: transparent;
    z-index: 5;
    display: none;
}

.overlay.active {
    display: block;
}
