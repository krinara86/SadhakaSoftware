// Set up the game board
const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");
canvas.width = 800;
canvas.height = 600;

// Create the snake
let snake = [];
snake.push({ x: 100, y: 100 }); // Start at (100, 100)
snake.push({ x: 150, y: 100 });
snake.push({ x: 200, y: 100 });

// Define the food
const food = { x: 400, y: 300 };

// Set up the game loop
function update() {
  // Move the snake
  for (let i = 0; i < snake.length - 1; i++) {
    const head = snake[i];
    const tail = snake[i + 1];
    if (head.x === tail.x && head.y === tail.y) {
      // Snake has collided with itself, game over!
      alert("Game Over!");
      return;
    }
    snake[i] = { ...tail };
  }
  
  // Check for collision with walls or food
  const head = snake[0];
  if (head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height) {
    // Snake has collided with a wall, game over!
    alert("Game Over!");
    return;
  }
  if (distance(head, food) <= 50) {
    // Snake has eaten the food, increase its length
    snake.unshift({ ...food });
    food = { x: Math.floor(Math.random() * canvas.width), y: Math.floor(Math.random() * canvas.height) };
  }
}

// Draw the game
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let i = 0; i < snake.length; i++) {
    const square = snake[i];
    ctx.fillStyle = "black";
    ctx.fillRect(square.x, square.y, 10, 10);
  }
  ctx.fillStyle = "red";
  ctx.fillCircle(food.x, food.y, 10);
}

// Update and draw the game repeatedly
setInterval(() => {
  update();
  draw();
}, 16);

// Calculate the distance between two points
function distance(p1, p2) {
  return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
}