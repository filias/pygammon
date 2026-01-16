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
## Apply formatting
```bash
uv format
```
## Architecture (MVC)
Model: Game, Board, Player, Color  
View: PygammonScene, MovableChecker, QGraphicsView  
Controller: app.py, BackgammonWindow

## Project Structure
<img src="structure.png" width="200">

## Authors
Developed by Filipa.
