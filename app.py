from flask import Flask, render_template, abort
import json
import markdown
import os

app = Flask(__name__)

# Load JSON mapping file once
with open("mappings.json") as f:
    MAPPING = json.load(f)

@app.route("/<prof>/<chapter>/<exercise>")
def show_exercise(prof, chapter, exercise):
    if exercise == "course":
        return show_course(prof, chapter)
    
    # Check all keys safely
    try:
        chapter_data = MAPPING[prof][chapter]
        all_exercises = list(chapter_data.keys())
        md_path = chapter_data[exercise]
    except KeyError:
        abort(404, "Exercise not found.")

    # Check file exists
    if not os.path.isfile(md_path):
        abort(404, "Markdown file missing.")

    # Load and convert markdown
    with open(md_path, "r") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)

    current_index = all_exercises.index(exercise)

    return render_template("exercise.html",
                           html_content=html_content,
                           prof=prof,
                           chapter=chapter,
                           exercise=exercise,
                           all_exercises=all_exercises,
                           current_index=current_index)
    
@app.route("/<prof>/<chapter>")
def show_course(prof, chapter):
    # Check all keys safely
    try:
        md_path = MAPPING[prof][chapter]["course"]
    except KeyError:
        abort(404, "Exercise not found.")

    # Check file exists
    if not os.path.isfile(md_path):
        abort(404, "Markdown file missing.")

    # Load and convert markdown
    with open(md_path, "r") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)

    return render_template("course.html",
                           html_content=html_content,
                           prof=prof,
                           chapter=chapter)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
