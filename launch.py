# inspired from https://github.com/belmarca/codeboot-presentation
def init_launch(all_exercises):
    """
    Initialize the CodeBoot exercise presentation environment.

    Args:
        all_exercises (list): List containing informations about all exercises.

    Returns:
        exercise_state_utils: An instance that tracks the state of exercises.
    """

    from js import console, setTimeout
    from markdown import split_markdown, parse_front_matter

    converter = host_eval("new showdown.Converter()")
    converter.setOption('parseImgDimensions', True)
    console.log(converter)

    getCodeBootVM = \getCodeBootVM

    vm = getCodeBootVM()
    cb = \CodeBoot.prototype.cb
    
    DEBUG = True
    VERSION = "0.0"

    class Exercise_final_utils():
        def __init__(self, num_exercises, current_index = -1, vm_exercises = None, exercises_funcs = None, exercises_mode = None):
            """
            Utility class that manages all logic related to exercise switching,
            solution tracking, file watching, interaction...

            Attributes:
                current_index (int): The currently selected exercise index.
                vm_exercises (list): List of VMs, one per exercise.
                resizer_done (bool): Whether the resizer listener was attached.
                solution_progress (list): Progress state per exercise (0 = not started, 1 = started, 2 = submitted).
            """
            self.num_exercises = num_exercises
            self.current_index = current_index
            self.vm_exercises = vm_exercises if vm_exercises is not None else [None] * num_exercises
            self.exercises_funcs = exercises_funcs if exercises_funcs is not None else [None] * num_exercises
            self.exercises_mode = exercises_mode if exercises_mode is not None else [None] * num_exercises
            self.resizer_done = False
            self.solution_progress = [-1] * num_exercises
            self.FILE_NAME_SOLUTION = "solution.py"
            
        def create_event_resizer(self):
            """
            Attaches mouse listeners for resizing code/editor columns.
            Only initializes once.
            """
            if self.resizer_done :
                return
            self.resizer_done = True
            
            def func_mousedown(e):
                self.isDragging = True
                document.body.style.cursor = 'col-resize'
                document.body.style.userSelect = 'none'
                
            def func_mousemove(e):
                if not self.isDragging:
                    return
                
                containerOffsetLeft = self.left.parentNode.offsetLeft
                pointerRelativeXpos = e.clientX - containerOffsetLeft
                containerWidth = self.left.parentNode.getBoundingClientRect().width
                leftWidth = (pointerRelativeXpos / containerWidth) * 100
                rightWidth = 100 - leftWidth
                
                self.left.style.width = f"{leftWidth}%"
                self.right.style.width = f"{rightWidth}%"
            
            def func_mouseup(e):
                self.isDragging = False
                document.body.style.cursor = 'default'
                document.body.style.userSelect = 'auto'
    
            self.resizer = document.getElementById('resizer')
            self.left = self.resizer.previousElementSibling
            self.right = self.resizer.nextElementSibling
            self.isDragging = False
            
            self.resizer.addEventListener('mousedown', func_mousedown)
            document.addEventListener('mousemove', func_mousemove)
            document.addEventListener('mouseup', func_mouseup)

        def change_exo(self, index):
            """
            Change the currently active exercise to the given index.
            Hides the old one and shows the new one.

            Args:
                index (int): The exercise index to activate.
            """
                
            if index < 0 or index >= len(self.vm_exercises):
                return
            
            # Hide the previous exercise UI
            if self.current_index != -1 :
                # hide the exercise markdown (left pane)
                last_ex = document.getElementById("exercise_" + str(self.current_index+1))
                last_ex.style.display = "None"
                # remove the current exercise link (class)
                last_ex_link = document.getElementById("exo_link_" + str(self.current_index+1))
                last_ex_link.classList.remove("current-exercise-link")
                # hide the exercise VM (right pane)
                vm_exo = self.vm_exercises[self.current_index]
                if vm_exo is not None:
                    vm_exo.setHidden(True)
                
            self.current_index = index
            
            # Show the new exercise UI
            new_ex = document.getElementById("exercise_" + str(self.current_index+1))
            new_ex.style.display = "block"
            new_ex_link = document.getElementById("exo_link_" + str(self.current_index+1))
            new_ex_link.classList.add("current-exercise-link")
            vm_exo = self.vm_exercises[self.current_index]
            if self.exercises_mode[self.current_index] == "codeboot_fix" :
                document.getElementById("resizer").style.display = "block"
                document.getElementById("codeboot-container").style.width = "100%"
                vm_exo.setHidden(False)
            elif self.exercises_mode[self.current_index] == "codeboot_floating" :
                document.getElementById("resizer").style.display = "none"
                document.getElementById("codeboot-container").style.width = "0%"
            elif self.exercises_mode[self.current_index] == "codeboot_without" :
                document.getElementById("resizer").style.display = "none"
                document.getElementById("codeboot-container").style.width = "0%"
            
            
            # Update navigation button visibility
            document.getElementById("previous-button").style.visibility = (
                "hidden" if self.current_index == 0 else "visible"
            )
                
            document.getElementById("next-button").style.visibility = (
                "hidden" if self.current_index == len(self.vm_exercises) - 1 else "visible"
            )
            
        def previous_exo(self):
            """Switch to the previous exercise."""
            if self.current_index == 0:
                return
            
            self.change_exo(self.current_index - 1)
            
        def next_exo(self):
            """Switch to the next exercise."""
            if self.current_index == len(self.vm_exercises) - 1:
                return
            
            self.change_exo(self.current_index + 1)
            
        def hint_exo(self):
            """(TODO) Show a hint for the current exercise."""
            id_ex = self.current_index
            if id_ex < 0 or id_ex >= len(self.exercises_funcs):
                return
            if self.exercises_funcs[id_ex] is None:
                return
            hint = self.exercises_funcs[id_ex].hint()
            # TODO : show hint
            return 
            
        def send_exo(self):
            """
            (TODO) Submit the current solution.
            Updates solution state and UI to 'submitted'.
            """
            id_ex = self.current_index
            if id_ex < 0 or id_ex >= len(self.exercises_funcs):
                return
            self.solution_progress[id_ex] = 2
            # TODO lock it
            if self.exercises_funcs[id_ex] is None:
                return
            self.exercises_funcs[id_ex].send() # TODO path file
            return
            
        def solution_exo(self):
            """(TODO) Show the final solution."""
            id_ex = self.current_index
            if id_ex < 0 or id_ex >= len(self.exercises_funcs):
                return
            if self.exercises_funcs[id_ex] is None:
                return
            solution = self.exercises_funcs[id_ex].solution()
            # TODO : show solution
            return
        
        def open_run_example_file(self, file_name):
            """
            Open and run a given example file inside an exercise VM.
            """
            id_ex = self.current_index
            if id_ex < 0 or id_ex >= len(self.vm_exercises):
                return
            
            vm_exo = self.vm_exercises[id_ex]
            if vm_exo is None:
                return
            
            if vm_exo.isHidden() :
                vm_exo.setHidden(False)

            if vm_exo.fs.files.hasOwnProperty(file_name):
                vm_exo.fs.showFile(file_name, True)
                name_module = file_name[:-3]
                vm_exo.exec()
            
        def look_file_modify(self): # TODO : don't work
            """
            Monitors the solution file for changes to update UI progress states.
            Recursively checks every 100ms.
            """
            id_ex = self.current_index
            if id_ex < 0 or id_ex >= len(self.vm_exercises):
                return
            
            vm_exo = self.vm_exercises[id_ex]
            
            if vm_exo is not None:
                content = vm_exo.fs.getContent(self.FILE_NAME_SOLUTION)
                
                if content == "" and self.solution_progress[id_ex] == 1:
                    # not started : change color to gray
                    self.solution_progress[id_ex] = 0
                    writeFile(f"config_{id_ex}.txt", "0")
                    document.getElementById("exo_link_"+str(id_ex+1)).classList.remove("started")
                
                if content != "" and self.solution_progress[id_ex] == 0:
                    # started : change color to blue
                    self.solution_progress[id_ex] = 1
                    writeFile(f"config_{id_ex}.txt", "1")
                    document.getElementById("exo_link_"+str(id_ex+1)).classList.add("started")
                
                if self.solution_progress[id_ex] == 2:
                    # solution submitted : stop looking + change color to green
                    if "started" in document.getElementById("exo_link_"+str(id_ex+1)).classList :
                        document.getElementById("exo_link_"+str(id_ex+1)).classList.remove("started")
                        
                    document.getElementById("exo_link_"+str(id_ex+1)).classList.add("submitted")
                    self.solution_progress[id_ex] = 2
                    writeFile(f"config_{id_ex}.txt", "2")
                    return
            
            
            setTimeout(lambda: self.look_file_modify(), 100)
                

    def generate_exercise(markdown, id_ex, actions, exercise_state_utils, type_page):
        """
        Parse markdown and initialize an exercise div with a VM instance.

        Args:
            markdown (str): Markdown content.
            id_ex (int): Exercise index.
            actions (list): List of post-processing callbacks.
            exercise_state_utils (Exercise_final_utils): Utility class instance.
        """
        
        nonlocal converter

        exercise_id = "exercise_" + str(id_ex+1)

        main_content = converter.makeHtml(markdown)

            
        exercise_div = document.createElement("div")
        exercise_div.id = exercise_id
        exercise_div.style.display = "None"
        exercise_div.innerHTML = main_content
        
        document.getElementById('exercise-content').appendChild(exercise_div)
        
        vm_exo = setup_vm_exercises(id_ex, type_page)
        exercise_state_utils.vm_exercises[id_ex] = vm_exo
        
        exercise = document.getElementById(exercise_id)
        for action in actions:
            action(exercise, id_ex, exercise_state_utils)

    def action_populate_code_elements(exercise, id_ex, exercise_state_utils):
        """
        Convert <code> blocks into example Python files inside the VM and attach floating run buttons.
        """
        nonlocal cb, vm
        
        vm_exo = exercise_state_utils.vm_exercises[id_ex]
        if vm_exo is None:
            return
        
        # Ensure the solution file exists
        if not vm_exo.fs.files.hasOwnProperty(exercise_state_utils.FILE_NAME_SOLUTION):
            vm_exo.fs.createFile(exercise_state_utils.FILE_NAME_SOLUTION, "")
        
        elts = exercise.querySelectorAll("code")
        
        for id_example, el in enumerate(elts):
            parent = el.parentElement
            parent.style.display = "inline-block"
            
            code = el.innerHTML
            
            file_name = "example_" + str(id_example+1) + ".py"

            div = document.createElement('div')
            div.id = file_name
            
            if not vm_exo.fs.files.hasOwnProperty(file_name):
                vm_exo.fs.createFile(file_name, code)
            
            file = vm_exo.fs.getByName(file_name)
            fe = file['fe']
            fe.enable()

            html = fe.textEditor.toHTML()
            
            file.setReadOnly(True)
            #vm_exo.fs.showFile(file_name, False)

            # Populate with the CodeMirror-generated HTML code
            div.innerHTML = html
            div.classList.add("cb-example-code")

            add_floating_icon(div, file_name, exercise_state_utils)
            parent.replaceWith(div)

        # Show the solution file
        file = vm_exo.fs.getByName(exercise_state_utils.FILE_NAME_SOLUTION)
        fe = file['fe']
        fe.enable()
        
        vm_exo.fs.showFile(exercise_state_utils.FILE_NAME_SOLUTION, True)

    def add_floating_icon(div, file_name, exercise_state_utils):
        """
        Attach a floating button to run example code files in the exercise VM.
        """
        btn = HTMLElement_from_html('<button class="btn btn-secondary cb-button" type="button"></button>')
        btn.onclick = lambda evt: exercise_state_utils.open_run_example_file(file_name)
        svg = HTMLElement_from_html(vm.getImage('clone')) # TODO : change icon
        btn.style.position = "absolute"
        btn.style.top = "0px"
        btn.style.right = "0px"
        btn.appendChild(svg)
        div.appendChild(btn)

    def HTMLElement_from_html(html, strip=True):
        """Convert HTML string to an HTMLElement."""
        html = html.strip() if strip else html

        if not html: return None

        template = document.createElement("template")
        template.innerHTML = html
        result = template.content.children

        if len(result) == 1:
            return result[0]
        return result

    def set_css():
        """Load and inject custom stylesheet."""
        css = read_file("style.css")
        style = document.getElementById("presentation_css")
        if style is None:
            style = document.createElement("style")
            style.id = "presentation_css"
            style.innerHTML = css
            document.head.appendChild(style)
            return
        style.innerHTML = css

    def set_metadata():
        """Add metadata tag to mark current exercise app version."""
        nonlocal VERSION
        meta = document.createElement('meta')
        meta.name = "cb-exercise-app-version"
        meta.content = VERSION
        document.head.appendChild(meta)
        
    def load_progress(exercise_state_utils):
        """
        Load saved progress for each exercise and apply CSS classes accordingly.
        """
        for id_ex in range(len(exercise_state_utils.vm_exercises)):
            # does the file exist and contains a number ?
            try:
                progress = int(readFile(f"config_{id_ex}.txt"))
            except:
                progress = 0
            exercise_state_utils.solution_progress[id_ex] = progress
            
            if progress == 1 :
                document.getElementById("exo_link_"+str(id_ex+1)).classList.add("started")
            elif progress == 2 :
                document.getElementById("exo_link_"+str(id_ex+1)).classList.add("submitted")
        
        exercise_state_utils.look_file_modify()

    def setup_vm_exercises(id, type_page):
        """Create and configure a new CodeBoot VM instance for an exercise."""
        vm = None
        if type_page == "codeboot_fix":
            root = document.createElement("div")
            root.classList.add("cb-vm")
            root.id = "cb-exercises-vm-"+str(id+1)

            opts = {
                "root": root,
                "hidden": True,
                "showLineNumbers": True,
                "cloned": False,
                "floating": True, # TODO : want False but crash
                "embedded": False,
                "showEditors": True
            }

            document.getElementById("codeboot-container").appendChild(root)
            
            vm = host_eval("(x) => new CodeBootVM(x)")(opts)
            vm.setFloating(False) # TODO
            
        elif type_page == "codeboot_floating":
            root = document.createElement("div")
            root.classList.add("cb-vm")
            root.id = "cb-exercises-vm-"+str(id+1)
            
            opts = {
                "root": root,
                "hidden": True,
                "showLineNumbers": True,
                "cloned": True,
                "floating": True,
                "embedded": False,
                "showEditors": True,
                "resizable": True
            }
            
            document.getElementById("codeboot-container").appendChild(root)
            
            vm = host_eval("(x) => new CodeBootVM(x)")(opts)
        return vm
        
    def add_click_handler_button(exercise_state_utils, all_exercises):
        """Attach click handlers to navigation and submission buttons."""
        document.getElementById("previous-button").addEventListener("click", lambda e:exercise_state_utils.previous_exo())
        document.getElementById("next-button").addEventListener("click", lambda e:exercise_state_utils.next_exo())
        
        for i in range(len(all_exercises)):
            document.getElementById(f"exo_link_{i+1}").addEventListener("click", lambda e, i=i:exercise_state_utils.change_exo(i))
            
        document.getElementById("send-button").addEventListener("click", lambda e:exercise_state_utils.send_exo())
        document.getElementById("solution-button").addEventListener("click", lambda e:exercise_state_utils.solution_exo())
        document.getElementById("hint-button").addEventListener("click", lambda e:exercise_state_utils.hint_exo())
        
    def add_zoom_handler():
        host_eval("""
const zoomLevels = new WeakMap();
const originalFontSizes = new WeakMap();

document.querySelectorAll('.zoom-section').forEach(section => {
    zoomLevels.set(section, 1); // default zoom

    section.addEventListener('keydown', function (e) {
        if (!e.ctrlKey) return;

        let zoom = zoomLevels.get(this);

        if (e.key === '+' || e.key === '=') {
            e.preventDefault();
            zoom += 0.1;
        } else if (e.key === '-' || e.key === '_') {
            e.preventDefault();
            zoom = Math.max(0.5, zoom - 0.1);
        } else if (e.key === '0') {
            e.preventDefault();
            zoom = 1;
        }

        zoomLevels.set(this, zoom);
        applyZoom(this, zoom);
    });
});

function applyZoom(section, zoom) {
    // First time: store original font sizes
    if (!originalFontSizes.has(section)) {
        const map = new Map();
        section.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            const size = parseFloat(style.fontSize);
            map.set(el, size);
        });
        originalFontSizes.set(section, map);
    }

    // Apply zoom to each element based on its original size
    const map = originalFontSizes.get(section);
    map.forEach((originalSize, el) => {
        el.style.fontSize = `${(originalSize * zoom).toFixed(2)}px`;
    });
}
    """)


    def init(all_exercises):
        """
        Main entry point that sets up the CodeBoot exercise system.
        """
        
        exercise_state_utils = Exercise_final_utils(len(all_exercises))

        exercise_div = document.createElement("div")
        exercise_div.id = "exercises"
        \document.body.appendChild(`exercise_div)
        
        # Required for the element to be selectable
        exercise_div.setAttribute("tabindex", 0)
        set_css()
        set_metadata()
        
        # Render navigation buttons
        all_exo = ""
        exercises_mode = []
        exercises_funcs = []
        for i, ex in enumerate(all_exercises):
            exercises_mode.append(ex["type_page"])
            exercises_funcs.append(ex["path_code"] if "path_code" in ex else None)
            all_exo += f"""
                        <button class="exercise-link"
                            id="exo_link_{i+1}"
                            data-key="{ ex["name"] }"
                        >
                            { ex["name"] }
                        </button>
                        """
        
        exercise_state_utils.exercises_mode = exercises_mode
        exercise_state_utils.exercises_funcs = exercises_funcs
        
        # create the squeleton of the page
        params = {"all_exo" : all_exo}
        template = read_file("exercise.html")
        page_div = HTMLElement_from_html(template.format(**params))
        document.getElementById('exercises').appendChild(page_div)
        
        actions = [action_populate_code_elements]
        
        # generate all the exercises
        for id_ex, ex in enumerate(all_exercises):
            markdown = read_file(ex["name"]+ ".md")
            generate_exercise(markdown, id_ex, actions, exercise_state_utils, ex["type_page"])
        
        # init the page
        exercise_state_utils.current_index = -1
        exercise_state_utils.change_exo(0) # Show the first exercise
        exercise_state_utils.create_event_resizer() # Create the event resizer
        load_progress(exercise_state_utils) # Load saved progress for each exercise
        add_click_handler_button(exercise_state_utils, all_exercises) # Attach click handlers
        add_zoom_handler() # Attach zoom handler
        # Hide the floating buttons :
        a = document.querySelectorAll('a[data-cb-setting-floating]')
        for link_floating in a:
            #link_floating.style.display = "none"
            link_floating.remove()
            
        # Be sure that the height of the content is correct
        toolbar = document.getElementById("toolbar")
        document.getElementById("container-app").style.height = str(\document.body.getBoundingClientRect().height - toolbar.getBoundingClientRect().height) + "px"
        
        exercise_div.focus()
        return exercise_state_utils

    return init(all_exercises)


# TODO : random exo par etudant (garde en memoire les exos)
# TODO : floating codeboot mode (for intro)
# TODO : style markdown
# TODO : mode edition (creer exercise) : markdown-it