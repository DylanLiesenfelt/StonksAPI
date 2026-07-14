from version import __version__

ROOT_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StonksAPI</title>
</head>
<body>
    <h1>StonksAPI</h1>
    <img src="stonks_meme.jpg" alt="stonks meme">
    <p>Buy High, Sell Low</p>
    <div>
        <button>Docs</button>
        <button>Health</button>
    </div>
    <p>Version: {__version__} </p>
</body>
</html>
"""