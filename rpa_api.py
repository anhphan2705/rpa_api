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
                var loopCounter = 0;

                function addAction(indentLevel = 0) {
                    var actionDiv = document.createElement('div');
                    actionDiv.classList.add('action-group');
                    actionDiv.style.marginLeft = `${indentLevel * 20}px`;
                    actionDiv.innerHTML = `
                        <label for="action">Choose an action:</label>
                        <select class="action" name="actions" required onchange="toggleSelectorInput(this, ${indentLevel})">
                            <option value="">Select an action</option>
                            <option value="url">Connect to URL</option>
                            <option value="click">Click on Button</option>
                            <option value="read">Read Text from Element</option>
                            <option value="type">Type into Input Field</option>
                            <option value="loop">Loop</option>
                            <option value="exit_loop">Exit Loop</option>
                            <option value="done">Done!</option>
                        </select><br><br>
                        <div class="selectorInput" style="display: none;">
                            <label for="selector">Enter the object HTML signature (optional):</label>
                            <input type="text" class="selector" name="selectors"><br><br>
                            <div class="typeInput" style="display: none;">
                                <label for="text">Enter the text to type:</label>
                                <input type="text" class="text" name="texts"><br><br>
                            </div>
                            <div class="loopInput" style="display: none;">
                                <label for="loop_count">Enter the number of times to loop:</label>
                                <input type="number" class="loop_count" name="loop_counts"><br><br>
                            </div>
                        </div>
                    `;
                    document.getElementById('actionsContainer').appendChild(actionDiv);
                }

                function toggleSelectorInput(selectElement, indentLevel) {
                    var action = selectElement.value;
                    var selectorInput = selectElement.parentElement.querySelector('.selectorInput');
                    var selectorLabel = selectorInput.querySelector('label[for="selector"]');
                    var typeInput = selectElement.parentElement.querySelector('.typeInput');
                    var loopInput = selectElement.parentElement.querySelector('.loopInput');

                    if (action === 'url' || action === 'click' || action === 'read' || action === 'type') {
                        selectorInput.style.display = 'block';
                        loopInput.style.display = 'none';
                        if (action === 'url') {
                            selectorLabel.textContent = 'Enter URL:';
                        } else {
                            selectorLabel.textContent = 'Enter the object HTML signature (optional):';
                        }
                        if (action === 'type') {
                            typeInput.style.display = 'block';
                        } else {
                            typeInput.style.display = 'none';
                        }
                        addAction(indentLevel);
                    } else if (action === 'loop') {
                        selectorInput.style.display = 'none';
                        loopInput.style.display = 'block';
                        loopCounter++;
                        addAction(indentLevel + 1);
                    } else if (action === 'exit_loop') {
                        selectorInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        loopCounter--;
                        if (loopCounter > 0) {
                            addAction(indentLevel - 1);
                        } else {
                            addAction();
                        }
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

### Backend (Python + FastAPI):

@app.post("/result", response_class=HTMLResponse)
async def submit_url(
    url: str = Form(...),
    actions: list[str] = Form(...),
    selectors: list[str] = Form(None),
    texts: list[str] = Form(None),
    loop_counts: list[str] = Form(None)
):
    try:
        r.init(turbo_mode=False, headless_mode=False)
        r.url(url)
        action_messages = []

        def execute_action(action, selector, text):
            if action == "url" and selector:
                r.url(selector)
                action_messages.append(f"Connected to URL: {selector}")
            elif action == "click" and selector:
                r.click(selector)
                action_messages.append(f"Clicked on button ID: {selector}")
            elif action == "read" and selector:
                read_text = r.read(selector)
                action_messages.append(f"Read text from ID {selector}: {read_text}")
            elif action == "type" and selector and text:
                r.type(selector, text)
                action_messages.append(f"Typed text into ID {selector}: {text}")

        i = 0
        while i < len(actions):
            action = actions[i]
            selector = selectors[i] if i < len(selectors) else None
            text = texts[i] if i < len(texts) else None
            loop_count = loop_counts[i] if i < len(loop_counts) else None

            if action == "loop" and loop_count:
                loop_actions = []
                loop_selectors = []
                loop_texts = []
                i += 1
                while i < len(actions) and actions[i] != "exit_loop":
                    loop_actions.append(actions[i])
                    loop_selectors.append(selectors[i] if i < len(selectors) else None)
                    loop_texts.append(texts[i] if i < len(texts) else None)
                    i += 1
                for _ in range(int(loop_count)):
                    for loop_action, loop_selector, loop_text in zip(loop_actions, loop_selectors, loop_texts):
                        execute_action(loop_action, loop_selector, loop_text)
            elif action != "exit_loop":
                execute_action(action, selector, text)
            i += 1

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
