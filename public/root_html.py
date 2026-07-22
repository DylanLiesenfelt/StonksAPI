from public.version import __version__

ROOT_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StonksAPI</title>
    <style>
        body {{
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #0f1115;
            color: #e8e8e8;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            text-align: center;
        }}
        main {{
            padding: 2rem;
        }}
        h1 {{
            margin: 0 0 0.25rem;
            font-size: 2rem;
        }}
        p {{
            color: #9a9a9a;
            margin: 0.25rem 0 1.5rem;
        }}
        img {{
            max-width: 320px;
            width: 100%;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}
        .actions a {{
            display: inline-block;
            margin: 0 0.5rem;
            padding: 0.6rem 1.4rem;
            border-radius: 8px;
            background: #2f6feb;
            color: #fff;
            text-decoration: none;
            font-weight: 600;
        }}
        .actions a:hover {{
            background: #4a83f0;
        }}
        .version {{
            margin-top: 2rem;
            font-size: 0.8rem;
            color: #555;
        }}
    </style>
</head>
<body>
    <main>
        <img src="/public/stonks_meme.jpg" alt="stonks meme">
        <h1>StonksAPI</h1>
        <p>Buy High, Sell Low</p>
        <div class="actions">
            <a href="/docs">Docs</a>
        </div>
        <p class="version">Version: {__version__}</p>
    </main>
</body>
</html>
"""
