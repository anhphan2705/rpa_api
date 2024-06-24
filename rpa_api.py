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
            <script>
                function addAction() {
                    var actionDiv = document.createElement('div');
                    actionDiv.classList.add('action-group');
                    actionDiv.innerHTML = `
                        <label for="action">Choose an action:</label>
                        <select class="action" name="actions" required onchange="toggleSelectorInput(this)">
                            <option value="">Select an action</option>
                            <option value="click">Click on Button</option>
                            <option value="read">Read Text</option>
                            <option value="done">Done!</option>
                        </select><br><br>
                        <div class="selectorInput" style="display: none;">
                            <label for="selector">Enter the object id for the action(optional):</label>
                            <input type="text" class="selector" name="selectors"><br><br>
                        </div>
                    `;
                    document.getElementById('actionsContainer').appendChild(actionDiv);
                }

                function toggleSelectorInput(selectElement) {
                    var action = selectElement.value;
                    var selectorInput = selectElement.parentElement.querySelector('.selectorInput');
                    if (action === 'click' || action === 'read') {
                        selectorInput.style.display = 'block';
                        addAction();
                    } else if (action === 'done') {
                        document.getElementById('submitBtn').style.display = 'block';
                    } else {
                        selectorInput.style.display = 'none';
                    }
                }

                window.onload = function() {
                    addAction();
                    document.getElementById('submitBtn').style.display = 'none';
                }
            </script>
        </head>
        <body>
            <h1>Welcome to My FastAPI Application</h1>
            <p>This is a simple welcome page.</p>
            <form action="/result" method="post">
                <label for="url">Enter a website URL:</label>
                <input type="text" id="url" name="url" required><br><br>
                <div id="actionsContainer"></div>
                <button type="submit" id="submitBtn">Submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/result", response_class=HTMLResponse)
async def submit_url(url: str = Form(...), actions: list[str] = Form(...), selectors: list[str] = Form(None)):
    try:
        r.init(turbo_mode=True)
        r.url(url)
        action_messages = []

        for action, selector in zip(actions, selectors):
            if action == "click" and selector:
                r.click(selector)
                action_messages.append(f"Clicked on button ID: {selector}")
            elif action == "read" and selector:
                read_text = r.read(selector)
                action_messages.append(f"Read text from ID {selector}: {read_text}")
            elif action == "done":
                break
            elif not selector:
                action_messages.append("No selector provided for the chosen action.")

        html_content = f"""
        <html>
            <head>
                <title>URL Submitted</title>
            </head>
            <body>
                <h1>URL Submitted</h1>
                <p>You submitted the following URL: {url}</p>
                {"".join(f"<p>{msg}</p>" for msg in action_messages)}
                <a href="/">Perform another action</a>
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
                <a href="/">Perform another action</a>
            </body>
        </html>
        """
    finally:
        r.close()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)