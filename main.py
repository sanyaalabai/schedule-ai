from nicegui import ui
import sqlite3
import needle
from datetime import datetime

con = sqlite3.connect("schedule.db")
cursor=con.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Teachers (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
specialization TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL,
    teacher_id INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
)
''')
con.commit()

class Teacher:
    def __init__(self, name, specialization):
        self.name=name
        self.specialization=specialization

def run_raw_sql(query: str):
    cursor.execute(query)
    con.commit()

def get_teachers()->list[Teacher]:
    cursor.execute('SELECT id, name, specialization FROM Teachers')
    l=cursor.fetchall()
    o=list[Teacher]()
    for t in l:
        o.append(Teacher(t["name"],t["specialization"]))
    return o
teachers=list[Teacher]()

columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'editable': True},
    {'name': 'specialization', 'label': 'Specialization', 'field': 'specialization', 'editable': True},
]
rows = [
    {'name': 'Teacher 1', 'specialization': 'Russian'},
    {'name': 'Teacher 2', 'specialization': 'Math'},
]

@needle.tool
def get_weather(city: str):
    "Get current weather for a given city."
    print(f"[NEEDLE]: Executed `get_weather` with {city}")
    return {"city": city, "temp_c": 27, "sky": "clear", "output": f"Weather in {city} is clear 27C"}

@needle.tool
def get_time_now():
    "Get current time."
    print("[NEEDLE]: Executed `get_time_now`")
    time=datetime.now().strftime("%H:%M")
    return {"output": f"Current time is {time}"}

@needle.tool
def add_teacher(name: str, specialization: str):
    "Adds teacher to schedule database. Parameter 'name' stands for name, 'specialization' stands for subject (math, english, physics, etc.)."
    print(F"[NEEDLE]: Executed `add_teacher` with {name}, {specialization}")
    run_raw_sql(f'''
    INSERT INTO Teachers (name, specialization)
    VALUES (?, ?)
    ''', name, specialization)
    return {"success": True, "output": f"Added {name} for subject {specialization}"}

@needle.tool
def get_teachers():
    "Get all list with all teachers from application database."
    print("[NEEDLE]: Executed `get_teachers`")
    cursor.execute('SELECT id, name, specialization FROM Teachers')
    teachers=cursor.fetchall()
    return {"output": [{"id": t[0], "name": t[1], "specialization": t[2]} for t in teachers]}

@needle.tool
def execute_raw_sql(query: str):
    "Executes raw SQL code on application database."
    print(F"[NEEDLE]: Executed `execute_raw_sql` with {query}")
    run_raw_sql(query)
    return {"success": True, "output": "Given SQL command was executed successfully"}

agent = needle.Needle(tools=[get_weather, get_time_now, add_teacher, execute_raw_sql, get_teachers])

isFooterAI=False
showFooter=False

def showAI():
    global isFooterAI, showFooter
    isFooterAI=True
    showFooter=True

with ui.header().classes("w-full bg-white text-primary"):
    with ui.tabs() as tabs:
        ui.tab("Home")
        ui.tab("AI Test")
        ui.tab("Teachers")
        ui.tab("Classes")
        ui.tab("Settings")
with ui.tab_panels(tabs, value="Home").classes("w-full"):
    with ui.tab_panel("Home"):
        ui.markdown("## Welcome to Schedule.AI\nGreat solution for time and resource management.")
    with ui.tab_panel("AI Test"):
        PROVIDER_msg_column = ui.column().classes("w-full max-w-2xl mx-auto flex-grow items-stretch")
    with ui.tab_panel("Teachers"):
        ui.aggrid({
            'columnDefs': columns,
            'rowData': rows,
            'rowSelection': 'single',
        }).classes('h-64')
        with ui.row():
            task_input = ui.input(placeholder='')
            ui.button('Add to List', on_click=lambda: ui.notify(task_input.value))
    with ui.tab_panel("Classes"):
        ui.markdown("WIP")
    with ui.tab_panel("Settings"):
        ui.markdown("WIP")

with ui.footer().classes("w-full bg-white text-primary"):
    async def send():
        inputText=PROVIDER_ai_text_input.value
        if not inputText.strip(): return
        PROVIDER_ai_text_input.value=''

        with PROVIDER_msg_column:
            ui.label(inputText).classes("text-right")
            try:
                output=agent.run(inputText)
                results=output["results"]
                outputText=str(results[0]["output"])
                with ui.expansion(outputText, value=False).classes('w-full'):
                    ui.label(f"Confidence: {output['confidence']*100:.1f}%")
                    ui.label(f"Speed: {output['decode_tps']} tokens/s")
                    ui.label(f"RAM: {output['peak_ram_mb']} MB")
                    if output.get("function_calls"):
                        ui.label(f"Calls: {output['function_calls']}")
                    if output.get("reasoning"):
                        ui.label(f"Reasoning: {output['reasoning']}")
                    ui.label(f"Results: {output['results']}")
            except Exception as e:
                ui.notify(f"Error: {str(e)}", type='negative')
    with ui.row().classes('w-full no-wrap items-center'):
        placeholder='Message'
        PROVIDER_ai_text_input=ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
            .classes('w-full self-center').on('keydown.enter', send)

ui.run(title="Schedule AI")
