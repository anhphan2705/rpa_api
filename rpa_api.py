from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import rpa as r

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <html>
        <head>
            <title>Welcome Page</title>
        </head>
        <body>
            <h1>Welcome to My FastAPI Application</h1>
            <p>This is a simple welcome page.</p>
            <form action="/result" method="post">
                <label for="url">Enter a website URL:</label>
                <input type="text" id="url" name="url" required><br><br>
                <label for="button_id">Enter the button_id you want to right click (optional):</label>
                <input type="text" id="button_id" name="button_id"><br><br>
                <label for="read_id">Enter the object id to read text from (optional):</label>
                <input type="text" id="read_id" name="read_id"><br><br>
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/result", response_class=HTMLResponse)
async def submit_url(url: str = Form(...), button_id: str = Form(None), read_id: str = Form(None)):
    try:
        r.init(turbo_mode=True, headless_mode=False)
        r.url(url)
        click_message = "No button ID provided."
        read_message = "No read ID provided."

        if button_id:
            r.click(button_id)
            click_message = f"Right-clicked on button ID: {button_id}"

        if read_id:
            read_text = r.read(read_id)
            read_message = f"Read text from ID {read_id}: {read_text}"

        html_content = f"""
        <html>
            <head>
                <title>URL Submitted</title>
            </head>
            <body>
                <h1>URL Submitted</h1>
                <p>You submitted the following URL: {url}</p>
                <p>{click_message}</p>
                <p>{read_message}</p>
            </body>
        </html>
        """
    except Exception as e:
        html_content = f"""
        <html>
            <head>
                <title>Error</title>
            </head>
            <body>
                <h1>Error</h1>
                <p>There was an error processing the URL: {url}</p>
                <p>Error details: {str(e)}</p>
            </body>
        </html>
        """
    finally:
        r.close()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)