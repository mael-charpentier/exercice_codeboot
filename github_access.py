
def init_app():
    def verif(params):
        if isinstance(params.all_exercises, list):
            if len(params.all_exercises) == 0:
                return False
            
            for el in params.all_exercises:
                if isinstance(el, dict):
                    if "name" not in el or "path_content" not in el or "type_page" not in el:
                        return False
                    if not (isinstance(el["name"], str) and isinstance(el["path_content"], str) and isinstance(el["type_page"], str)):
                        return False
                    if "path_code" in el and not isinstance(el["path_code"], str):
                        return False
                else :
                    return False
        else :
            return False
        
        return True
    
    # download the code from github
    write_file('launch.py', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/launch.py'))
    write_file('markdown.py', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/markdown.py'))
    write_file('exercise.html', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/exercise.html'))
    write_file('style.css', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/style.css'))
    write_file('params.py', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/params.py'))

    import params
    
    # verify params validity
    if not verif(params):
        return
    
    # download the code for all exercises from github
    for ex in params.all_exercises:
        write_file(ex["name"] + '.md', read_file(ex["path_content"]))
        if "path_code" in ex:
            write_file(ex["name"] + '.py', read_file(ex["path_code"]))

    # launch the app
    from launch import init_launch
    t = init_launch(params)

    # delete all trace of the launch
    sys_modules = host_eval("new PyForeign(rte.sys_modules)")
    sys_modules.pop("github_access", None)
    globals().pop("github_access", None)
    sys_modules.pop("params", None)
    globals().pop("params", None)
    sys_modules.pop("launch", None)
    globals().pop("init_launch", None)
    globals().pop("console", None)
    globals().pop("setTimeout", None)
    globals().pop("split_markdown", None)
    globals().pop("parse_front_matter", None)
    
    # delete all the file from the vm
    vm = \getCodeBootVM()
    vm.fs.deleteFile("launch.py")
    vm.fs.deleteFile("markdown.py")
    vm.fs.deleteFile("exercise.html")
    vm.fs.deleteFile("style.css")
    vm.fs.deleteFile("params.py")
    vm.fs.deleteFile("github_access.py")

    for ex in params.all_exercises:
        vm.fs.deleteFile(ex["name"] + '.md')
        if "path_code" in ex:
            vm.fs.deleteFile(ex["name"] + '.py')
    
    return t

init_app()
globals().pop("init_app", None)