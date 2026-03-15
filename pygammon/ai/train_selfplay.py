"""CLI for TD-Gammon self-play training."""

import argparse
import os
import time

import tensorflow as tf

from pygammon.ai.model import TDGammonModel
from pygammon.ai.trainer import TDTrainer


def main():
    parser = argparse.ArgumentParser(description="Train TD-Gammon via self-play")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of episodes")
    parser.add_argument("--hidden-size", type=int, default=80, help="Hidden layer size")
    parser.add_argument("--lr", type=float, default=0.1, help="Learning rate")
    parser.add_argument("--lamda", type=float, default=0.7, help="TD(lambda) parameter")
    parser.add_argument(
        "--checkpoint-dir", type=str, default="checkpoints", help="Checkpoint directory"
    )
    parser.add_argument(
        "--checkpoint-every", type=int, default=100, help="Save every N episodes"
    )
    parser.add_argument("--resume", type=str, default=None, help="Resume from checkpoint")
    parser.add_argument("--logdir", type=str, default="logs", help="TensorBoard log dir")
    args = parser.parse_args()

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    os.makedirs(args.logdir, exist_ok=True)

    model = TDGammonModel(hidden_size=args.hidden_size)
    # Build model
    model(tf.zeros((1, 198)))

    if args.resume:
        model.load_weights(args.resume)
        print(f"Resumed from {args.resume}")

    trainer = TDTrainer(model, learning_rate=args.lr, lamda=args.lamda)

    writer = tf.summary.create_file_writer(args.logdir)

    dark_wins = 0
    total_moves = 0
    start_time = time.time()

    for episode in range(1, args.episodes + 1):
        stats = trainer.train_episode()
        total_moves += stats["moves"]
        if stats["winner"] == "dark":
            dark_wins += 1

        with writer.as_default():
            tf.summary.scalar("moves_per_game", stats["moves"], step=episode)
            tf.summary.scalar(
                "dark_win_rate", dark_wins / episode, step=episode
            )

        if episode % 10 == 0:
            elapsed = time.time() - start_time
            print(
                f"Episode {episode}/{args.episodes} | "
                f"Dark win rate: {dark_wins/episode:.2%} | "
                f"Avg moves: {total_moves/episode:.0f} | "
                f"Time: {elapsed:.1f}s"
            )

        if episode % args.checkpoint_every == 0:
            path = os.path.join(args.checkpoint_dir, f"td_gammon_ep{episode}")
            model.save_weights(path)
            print(f"Checkpoint saved: {path}")

    # Final save
    final_path = os.path.join(args.checkpoint_dir, "td_gammon_final")
    model.save_weights(final_path)
    print(f"Training complete. Final model saved: {final_path}")


if __name__ == "__main__":
    main()
