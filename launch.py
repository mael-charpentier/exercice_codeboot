# inspired from https://github.com/belmarca/codeboot-presentation
def init_launch(params):
    DEBUG = True
    VERSION = "0.0"

    from js import console, setTimeout
    from markdown import split_markdown, parse_front_matter

    # 'new' is not supported by the grammar
    converter = host_eval("new showdown.Converter()")
    converter.setOption('parseImgDimensions', True)
    console.log(converter)

    getCodeBootVM = \getCodeBootVM

    vm = getCodeBootVM()
    cb = \CodeBoot.prototype.cb

    class Exercise_final_utils():
        def __init__(self, current_index = -1, vm_exercises = []):
            self.current_index = current_index
            self.vm_exercises = vm_exercises
            self.resizer_done = False
            self.solution_progress = [-1] * len(vm_exercises) # TODO save in file to keep progress
            
        def create_event_resizer(self):
            
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
                
            if index < 0 or index >= len(self.vm_exercises):
                return
            if self.current_index != -1 :
                last_ex = document.getElementById("exercise_" + str(self.current_index+1))
                last_ex.style.display = "None"
                last_ex_link = document.getElementById("exo_link_" + str(self.current_index+1))
                last_ex.classList.remove("current-exercise-link")
                vm_exo = self.vm_exercises[self.current_index]
                vm_exo.toggleHidden()
                
            self.current_index = index
            
            new_ex = document.getElementById("exercise_" + str(self.current_index+1))
            new_ex.style.display = "block"
            new_ex_link = document.getElementById("exo_link_" + str(self.current_index+1))
            new_ex_link.classList.add("current-exercise-link")
            vm_exo = self.vm_exercises[self.current_index]
            vm_exo.toggleHidden()
            
            if self.current_index == 0:
                document.getElementById("previous-button").style.visibility = "hidden"
            else:
                document.getElementById("previous-button").style.visibility = "visible"
                
            if self.current_index == len(self.vm_exercises) - 1:
                document.getElementById("next-button").style.visibility = "hidden"
            else:
                document.getElementById("next-button").style.visibility = "visible"
            
        def previous_exo(self):
            if self.current_index == 0:
                return
            
            self.change_exo(self.current_index - 1)
            
        def next_exo(self):
            if self.current_index == len(self.vm_exercises) - 1:
                return
            
            self.change_exo(self.current_index + 1)
            
        def hint_exo(self): # TODO
            return
            
        def send_exo(self): # TODO
            self.solution_progress[self.current_index] = 2
            return
            
        def solution_exo(self): # TODO
            return
        
        def open_run_example_file(self, id_ex, file_name):
            vm_exo = self.vm_exercises[id_ex]
            if vm_exo.fs.files.hasOwnProperty(file_name):
                vm_exo.fs.showFile(file_name, True)
                name_module = file_name[:-3]
                #vm_exo.exec(f"import {name_module}") # TODO : error : OSError : too much recursion
                #vm_exo.exec(f'host_eval("new PyForeign(rte.sys_modules)").pop({name_module}, None)')
            
        def look_file_modify(self): # TODO : don't work
            id_ex = self.current_index
            
            vm_exo = self.vm_exercises[id_ex]
            file_name = "solution.py"
            file = vm_exo.fs.getByName(file_name)
            
            if file.content == "" and self.solution_progress[id_ex] == 1:
                # change color to gray : not begin
                self.solution_progress[id_ex] = 0
                writeFile(f"config_{id_ex}.txt", "0")
                document.getElementById("exo_link_"+str(id_ex+1)).classList.remove("started")
            
            if file.content != "" and self.solution_progress[id_ex] == 0:
                # change color to blue : begin
                self.solution_progress[id_ex] = 1
                writeFile(f"config_{id_ex}.txt", "1")
                document.getElementById("exo_link_"+str(id_ex+1)).classList.add("started")
            
            if self.solution_progress[id_ex] == 2:
                # solution submitted so stop looking
                if "started" in document.getElementById("exo_link_"+str(id_ex+1)).classList :
                    document.getElementById("exo_link_"+str(id_ex+1)).classList.remove("started")
                    
                document.getElementById("exo_link_"+str(id_ex+1)).classList.add("submitted")
                self.solution_progress[id_ex] = 2
                writeFile(f"config_{id_ex}.txt", "2")
                return
            
            
            setTimeout(lambda: self.look_file_modify(), 100)
                

    def generate_exercise(markdown, id_ex, actions, exercise_class):
        nonlocal converter

        exercise_id = "exercise_" + str(id_ex+1)

        main_content = converter.makeHtml(markdown)

            
        exercise_div = document.createElement("div")
        exercise_div.id = exercise_id
        exercise_div.style.display = "None"
        exercise_div.innerHTML = main_content
        
        document.getElementById('exercise-content').appendChild(exercise_div)
        
        vm_exo = setup_vm_exercises(id_ex)
        exercise_class.vm_exercises[id_ex] = vm_exo
        
        exercise = document.getElementById(exercise_id)
        for action in actions:
            action(exercise, id_ex, exercise_class)

    def action_populate_code_elements(exercise, id_ex, exercise_class):
        nonlocal cb, vm
        
        vm_exo = exercise_class.vm_exercises[id_ex]
        
        elts = exercise.querySelectorAll("code")
        
        
        if not vm_exo.fs.files.hasOwnProperty("solution.py"):
            vm_exo.fs.createFile("solution.py", "")

        file = vm_exo.fs.getByName("solution.py")
        fe = file['fe']
        fe.enable()
        
        vm_exo.fs.showFile("solution.py", True)
        
        for id_example, el in enumerate(elts):
            parent = el.parentElement # pre element generated by showdown
            parent.style.display = "inline-block"
            
            code = el.innerHTML
            
            file_name = "example_" + str(id_example+1) + ".py"

            div = document.createElement('div')
            div.id = file_name
            
            if not vm_exo.fs.files.hasOwnProperty(file_name):
                vm_exo.fs.createFile(file_name, code)
            
            file = vm_exo.fs.getByName(file_name)
            fe = file['fe']
            # We must first enable the file editor
            fe.enable()

            html = fe.textEditor.toHTML()
            
            file.setReadOnly(True)
            #vm_exo.fs.showFile(file_name, False)

            # Populate with the CodeMirror-generated HTML code
            div.innerHTML = html
            div.classList.add("cb-example-code")

            add_floating_icon(div, file_name, id_ex, exercise_class)
            parent.replaceWith(div)

    def add_floating_icon(div, file_name, id_ex, exercise_class):
        btn = HTMLElement_from_html('<button class="btn btn-secondary cb-button" type="button"></button>')
        btn.onclick = lambda evt: exercise_class.open_run_example_file(id_ex, file_name)
        svg = HTMLElement_from_html(vm.getImage('clone')) # TODO : change icon
        btn.style.position = "absolute"
        btn.style.top = "0px"
        btn.style.right = "0px"
        btn.appendChild(svg)
        div.appendChild(btn)

    def HTMLElement_from_html(html, strip=True):
        html = html.strip() if strip else html

        if not html: return None

        template = document.createElement("template")
        template.innerHTML = html
        result = template.content.children

        if len(result) == 1:
            return result[0]
        return result

    def set_css():
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
        nonlocal VERSION
        meta = document.createElement('meta')
        meta.name = "cb-presentation-version"
        meta.content = VERSION
        document.head.appendChild(meta)
        
    def load_progress(exercise_class):
        for id_ex in range(len(exercise_class.vm_exercises)):
            try:
                progress = int(readFile(f"config_{id_ex}.txt"))
            except:
                progress = 0
            exercise_class.solution_progress[id_ex] = progress
            
            if progress == 1 :
                document.getElementById("exo_link_"+str(id_ex+1)).classList.add("started")
            elif progress == 2 :
                document.getElementById("exo_link_"+str(id_ex+1)).classList.add("submitted")
        
        exercise_class.look_file_modify()

    def setup_vm_exercises(id):
        
        root = document.createElement("div")
        root.classList.add("cb-vm")
        root.id = "cb-exercises-vm-"+str(id+1)

        # TODO : not floating
        opts = {
            "root": root,
            "hidden": True,
            "showLineNumbers": True,
            "cloned": True,
            "floating": True, # want False but fail : TODO
            "embedded": False,
            "showEditors": True
        }

        document.getElementById("codeboot-container").appendChild(root)

        return host_eval("(x) => new CodeBootVM(x)")(opts)
        
    def add_onclick_button(all_exercises):
        document.getElementById("previous-button").addEventListener("click", lambda e:__exercise_final_utils__.previous_exo())
        document.getElementById("next-button").addEventListener("click", lambda e:__exercise_final_utils__.next_exo())
        
        for i in range(len(all_exercises)):
            document.getElementById(f"exo_link_{i+1}").addEventListener("click", lambda e, i=i:__exercise_final_utils__.change_exo(i))
            
        document.getElementById("send-button").addEventListener("click", lambda e:__exercise_final_utils__.send_exo())
        document.getElementById("solution-button").addEventListener("click", lambda e:__exercise_final_utils__.solution_exo())
        document.getElementById("hint-button").addEventListener("click", lambda e:__exercise_final_utils__.hint_exo())
        
    def init(params):
        all_exercises = params.all_exercises # TODO test : isinstance ...
        exercise_class = Exercise_info(vm_exercises=[None] * len(all_exercises))

        exercise_div = document.createElement("div")
        exercise_div.id = "exercises"
        
        \document.body.appendChild(`exercise_div)
        
        # Required for the element to be selectable
        exercise_div.setAttribute("tabindex", 0)
        set_css()
        set_metadata()
        
        
        all_exo = ""
        for i, ex in enumerate(all_exercises):
            all_exo += f'<button class="exercise-link"\n'
            all_exo += f'   id="exo_link_{i+1}"\n'
            all_exo += f'   data-key="{ ex["name"] }"\n'
            all_exo += f'>'
            all_exo += f'{ ex["name"] }'
            all_exo += f'</button>'
        
        params = {
            "all_exo" : all_exo
        }
        template = read_file("exercise.html")
        page_div = HTMLElement_from_html(template.format(**params))
        document.getElementById('exercises').appendChild(page_div)
        
        actions = [
            action_populate_code_elements
        ]
        
        for id_ex, ex in enumerate(all_exercises):
            markdown = read_file(ex["name"]+ ".md")
            generate_exercise(markdown, id_ex, actions, exercise_class)
        
        exercise_class.current_index = -1
        exercise_class.change_exo(0) # show exo (+ button)
        exercise_class.create_event_resizer()
        load_progress(exercise_class)
        add_onclick_button(all_exercises)
        
        a = document.querySelectorAll('a[data-cb-setting-floating]')
        for link_floating in a:
            link_floating.click()
            #link_floating.style.display = "none"
            link_floating.remove()
        a = document.getElementsByClassName("cb-exec-btn-close")
        for link_close in a:
            #link_floating.style.display = "none"
            link_floating.remove()
            
        exercise_div.focus()
        return exercise_class

    return init(params)
