# Tetris in Python

This is a compact single-file Tetris implementation using pygame.
All created within 30 minutes with GITHUB Copilot free plan.
I also told the agent to create a web version that you can play at
https://kbtetris.vercel.app/web/
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

## Repository

https://github.com/chinesebayg/kbtetris

## Requirements

- Python 3.8+
- pygame

## Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python tetris.py
```

## Web version

There is a web version in the `web/` folder. You can open `web/index.html` in a browser or serve it locally:

```powershell
cd "c:\Users\kaibo\.vscode\projects\RPGgame1\web"
python -m http.server 8000
# then open http://localhost:8000 in your browser
```

## Controls

- Left/Right arrows: move
- Up arrow / X: rotate
- Down arrow: soft drop
- Space: hard drop
- P: pause
- Esc / Q: quit

## Contributing

Feel free to open issues or PRs. Small improvements that are welcome:
- Add next-piece and hold features
- Improve rotation to standard SRS
- Add sounds and a start/menu screen

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
