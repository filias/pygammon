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
uv run python app.py
```

## Train the AI

### Install AI dependencies
```bash
uv sync --extra ai
```

### Run self-play training
```bash
uv run python -u -m pygammon.ai.train_selfplay --episodes 1000
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

### How the AI works

The AI uses **TD-Gammon**, a classic reinforcement learning approach where a neural network learns to evaluate board positions by playing against itself.

**The neural network** takes a board position encoded as 198 numbers and outputs a single value between 0 and 1 — the estimated probability that Dark wins from this position.

**The encoding** converts the board into 198 features:
- For each of the 24 points, for each player: 4 features (has 1 checker?, has 2?, has 3?, how many extra)
- Bar count, borne-off count, whose turn it is
- That's 24 x 2 x 4 + 2 + 2 + 2 = 198

**Training loop** — each episode:
1. Start a new game
2. The AI plays both sides. For each move, it evaluates all legal resulting positions and picks the one with the highest value (greedy)
3. After each move, it compares what it predicted *before* the move vs *after* — this difference is the **TD error** (temporal difference)
4. It updates the network weights using this error, pushing predictions to be more consistent with each other
5. At game end, the final reward is 1 (Dark won) or 0 (Light won), which propagates back through the chain of predictions

**Eligibility traces** (the `lambda` parameter) make this faster — instead of only updating the most recent prediction, the error also partially updates earlier predictions that led to this state. It's like giving credit to moves made several turns ago.

**No exploration needed** — unlike most RL, backgammon has dice rolls which naturally inject randomness. The AI always picks the best move it knows (greedy), and the dice ensure it sees diverse positions.

**Move selection** when playing against you: the AI evaluates every legal move by simulating it on a copy of the board, encoding the result, and running it through the network. It picks the move that leads to the highest win probability for its side.

### What to expect

- ~1,000 episodes: learns basic checker movement
- ~50,000 episodes: starts playing reasonably
- ~300,000+ episodes: approaches strong play (the original TD-Gammon paper used 1.5M)

The network is small (198 → 80 → 1) so each episode is fast even on CPU.

## Apply formatting
```bash
uv run ruff format
```

## Architecture (MVC)
Model: Game, Board, Player, Color
View: PygammonScene, CheckerItem, QGraphicsView
Controller: GameController, GameEngine, app.py

## Project Structure
<img src="structure.png" width="200">
