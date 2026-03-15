# pygammon

A backgammon game written in **Python**, using **PySide6** for the graphical interface and following a **Model–View–Controller (MVC)** architecture.

---

## Screenshot


<img src="board.png" width="200">

---

## Installation

### Clone the repository

```bash
git clone https://github.com/filias/pygammon.git  

cd pygammon
```
### Install dependencies
Using uv:
```bash
uv sync
```

## Run the game
```bash
python app.py
```

## Train the AI

### Install AI dependencies
```bash
uv sync --extra ai
```

### Run self-play training
```bash
uv run python -m pygammon.ai.train_selfplay --episodes 1000
```

Options:
- `--episodes N` — number of self-play games (start with 1000, more = stronger)
- `--hidden-size 80` — hidden layer neurons
- `--lr 0.1` — learning rate
- `--lamda 0.7` — TD(lambda) trace decay
- `--checkpoint-dir checkpoints` — where to save models
- `--checkpoint-every 100` — save every N episodes
- `--resume checkpoints/td_gammon_ep1000` — continue from a checkpoint
- `--logdir logs` — TensorBoard log directory

### Monitor training
```bash
uv run tensorboard --logdir logs
```

### Play against the AI
Run the game and go to **Game → Play vs AI**, then select a checkpoint file from the `checkpoints/` directory.

## Apply formatting
```bash
uv format
```

## Architecture (MVC)
Model: Game, Board, Player, Color
View: PygammonScene, CheckerItem, QGraphicsView
Controller: GameController, GameEngine, app.py

## Project Structure
<img src="structure.png" width="200">

## Authors
Developed by Filipa.
