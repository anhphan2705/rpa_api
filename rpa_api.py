from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import rpa as r
import uuid

app = FastAPI()

# Ensure the 'screenshots' directory exists
os.makedirs('screenshots', exist_ok=True)

# Serve the static files in the 'screenshots' directory
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <html>
        <head>
            <title>Welcome Page</title>
            <script>
                var loopCounter = 0;
                var inLoop = false;

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
                            <option value="snap">Snap Screenshot</option>
                            <option value="select">Select from Dropdown</option>
                            <option value="loop">Start Loop</option>
                            <option value="loop_times">Loop Amount</option>
                            <option value="exit_loop">End Loop</option>
                            <option value="done">Done!</option>
                        </select><br><br>
                        <div class="selectorInput" style="display: none;">
                            <label for="selector">Enter the object HTML signature (optional):</label>
                            <input type="text" class="selector" name="selectors"><br><br>
                            <div class="typeInput" style="display: none;">
                                <label for="text">Enter the text to type:</label>
                                <input type="text" class="text" name="texts"><br><br>
                            </div>
                            <div class="selectInput" style="display: none;">
                                <label for="option">Enter the option to select:</label>
                                <input type="text" class="option" name="options"><br><br>
                            </div>
                        </div>
                        <div class="loopInput" style="display: none;">
                            <label for="loop_count">Enter the number of times to loop:</label>
                            <input type="number" class="loop_count" name="loop_counts" min="1"><br><br>
                        </div>
                    `;
                    document.getElementById('actionsContainer').appendChild(actionDiv);
                }

                function toggleSelectorInput(selectElement, indentLevel) {
                    var action = selectElement.value;
                    var selectorInput = selectElement.parentElement.querySelector('.selectorInput');
                    var selectorLabel = selectorInput.querySelector('label[for="selector"]');
                    var typeInput = selectElement.parentElement.querySelector('.typeInput');
                    var selectInput = selectElement.parentElement.querySelector('.selectInput');
                    var loopInput = selectElement.parentElement.querySelector('.loopInput');

                    if (action === 'url' || action === 'click' || action === 'read' || action === 'type' || action === 'select') {
                        selectorInput.style.display = 'block';
                        loopInput.style.display = 'none';
                        if (action === 'url') {
                            selectorLabel.textContent = 'Enter URL:';
                        } else {
                            selectorLabel.textContent = 'Enter the object HTML signature (optional):';
                        }
                        if (action === 'type') {
                            typeInput.style.display = 'block';
                            selectInput.style.display = 'none';
                        } else if (action === 'select') {
                            selectInput.style.display = 'block';
                            typeInput.style.display = 'none';
                        } else {
                            typeInput.style.display = 'none';
                            selectInput.style.display = 'none';
                        }
                        addAction(indentLevel);
                    } else if (action === 'snap') {
                        selectorInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        addAction(indentLevel);
                    } else if (action === 'loop') {
                        selectorInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        inLoop = true;
                        loopCounter++;
                        addAction(indentLevel + 1);
                    } else if (action === 'loop_times') {
                        selectorInput.style.display = 'none';
                        loopInput.style.display = 'block';
                        addAction(indentLevel);
                    } else if (action === 'exit_loop') {
                        selectorInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        inLoop = false;
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
                        loopInput.style.display = 'none';
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
async def submit_url(
    url: str = Form(...),
    actions: list[str] = Form(...),
    selectors: list[str] = Form(None),
    texts: list[str] = Form(None),
    options: list[str] = Form(None),
    loop_counts: list[str] = Form(None)
):
    try:
        r.init(turbo_mode=True, headless_mode=False)
        r.url(url)
        action_messages = []
        screenshots = []

        def execute_action(action, selector, text, option):
            if action == "url" and selector:
                r.url(selector)
                return f"Connected to URL: {selector}"
            elif action == "click" and selector:
                r.click(selector)
                return f"Clicked on button ID: {selector}"
            elif action == "read" and selector:
                read_text = r.read(selector)
                return f"Read text from ID {selector}: {read_text}"
            elif action == "type" and selector and text:
                r.type(selector, text)
                return f"Typed text into ID {selector}: {text}"
            elif action == "snap":
                filename = f"screenshot_{uuid.uuid4().hex}.png"
                file_path = os.path.join("screenshots", filename)
                r.wait(0.5)
                r.snap('page', file_path)
                screenshots.append(file_path)
                return f"Screenshot saved as {filename}"
            elif action == "select" and selector and option:
                r.select(selector, option)
                return f"Selected option {option} from ID {selector}"

        i = 0
        while i < len(actions):
            action = actions[i]
            selector = selectors[i] if i < len(selectors) else None
            text = texts[i] if i < len(texts) else None
            option = options[i] if i < len(options) else None
            loop_count = int(loop_counts[i]) if i < len(loop_counts) and loop_counts[i].isdigit() else 1

            if action == "loop_times":
                loop_actions = []
                loop_selectors = []
                loop_texts = []
                loop_options = []
                i += 1
                while i < len(actions) and actions[i] != "exit_loop":
                    loop_actions.append(actions[i])
                    loop_selectors.append(selectors[i] if i < len(selectors) else None)
                    loop_texts.append(texts[i] if i < len(texts) else None)
                    loop_options.append(options[i] if i < len(options) else None)
                    i += 1

                for _ in range(loop_count):
                    for loop_action, loop_selector, loop_text, loop_option in zip(loop_actions, loop_selectors, loop_texts, loop_options):
                        result = execute_action(loop_action, loop_selector, loop_text, loop_option)
                        if result:
                            action_messages.append(result)

                action_messages.append(f"Executed loop {loop_count} times with actions: {', '.join(loop_actions)}")
            elif action != "exit_loop":
                result = execute_action(action, selector, text, option)
                if result:
                    action_messages.append(result)
            i += 1

        screenshot_html = "".join(f'<img src="/screenshots/{os.path.basename(screenshot)}" alt="{screenshot}" style="max-width:100%"><br>' for screenshot in screenshots)

        html_content = f"""
        <html>
            <head>
                <title>URL Submitted</title>
            </head>
            <body>
                <h1>URL Submitted</h1>
                <p>You submitted the following URL: {url}</p>
                {"".join(f"<p>{msg}</p>" for msg in action_messages if not msg.startswith('Executed loop'))}
                <p>{', '.join([msg for msg in action_messages if msg.startswith('Executed loop')])}</p>
                <a href="/">Perform another action</a><br>
                {screenshot_html}
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